# ✅ FULL NEW conversation_service.py

from app.conversation import ConversationState, PlayerIntent
from app.interpreter import interpret_input
from commands.dm_commands import handle_dm_command
from commands.admin_commands import handle_admin_command
from app.shop_handlers.buy_handler import BuyHandler
from app.shop_handlers.sell_handler import SellHandler
from app.shop_handlers.deposit_handler import DepositHandler
from app.shop_handlers.withdraw_handler import WithdrawHandler
from app.shop_handlers.generic_chat_handler import GenericChatHandler
from app.shop_handlers.view_handler import ViewHandler
from typing import Callable, Dict, Tuple, Any

CATEGORY_MAPPING = {
    PlayerIntent.VIEW_ARMOUR_CATEGORY: ("armour_category", "Armor"),
    PlayerIntent.VIEW_WEAPON_CATEGORY: ("weapon_category", "Weapon"),
    PlayerIntent.VIEW_GEAR_CATEGORY: ("gear_category", "Adventuring Gear"),
    PlayerIntent.VIEW_TOOL_CATEGORY: ("tool_category", "Tools"),
    PlayerIntent.VIEW_EQUIPMENT_CATEGORY: ("equipment_category", "Mounts and Vehicles"),
}

class ConversationService:
    def __init__(self, convo, agent, party_id, player_id, player_name, party_data):
        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.player_id = player_id

        self.party_data = dict(party_data)
        self.party_data["player_name"] = player_name
        self.party_data["visit_count"] = self.party_data.get("visit_count", 1)

        self.buy_handler = BuyHandler(convo, agent, party_id, player_id, player_name, self.party_data)
        self.sell_handler = SellHandler(convo, agent, party_id, player_id, player_name, self.party_data)
        self.deposit_handler = DepositHandler(convo, agent, party_id, player_id, player_name, self.party_data)
        self.withdraw_handler = WithdrawHandler(convo, agent, party_id, player_id, player_name, self.party_data)
        self.generic_handler = GenericChatHandler(agent, self.party_data, convo, party_id)
        self.view_handler = ViewHandler(convo, agent)

        self.intent_router: Dict[Tuple[str, str], Callable[[dict], Any]] = self._build_router()

    def handle(self, player_input):
        # --- Admin / DM Early Commands ---
        if player_input.strip().lower().startswith("dm "):
            return handle_dm_command(self.party_id, self.player_id, player_input, party_data=self.party_data)

        if player_input.strip().lower().startswith("admin "):
            admin_response = handle_admin_command(player_input)
            if "reset" in player_input.lower():
                self.convo.reset_state()
                self.convo.set_pending_item(None)
                self.convo.set_discount(None)
                self.convo.save_state()
            return admin_response

        # --- Normal Input ---
        self.convo.set_input(player_input)

        if isinstance(player_input, str):
            raw_text = player_input
            intent_data = interpret_input(player_input, self.convo)
        else:
            raw_text = str(player_input)
            intent_data = player_input

        intent = intent_data.get("intent")
        metadata = intent_data.get("metadata", {}) or {}
        item = metadata.get("item")
        self.convo.set_intent(intent)

        if intent in CATEGORY_MAPPING:
            field, value = CATEGORY_MAPPING[intent]
            metadata[field] = value

        wrapped_input = {
            "text": raw_text,
            "intent": intent,
            "item": item,
            **metadata,
        }

        if item:
            self.convo.set_pending_item(item)

        # --- Pending Confirmation Protection ---
        if self.convo.state == ConversationState.AWAITING_CONFIRMATION:
            if intent not in {PlayerIntent.CONFIRM, PlayerIntent.CANCEL, PlayerIntent.BUY_CONFIRM,
                              PlayerIntent.SELL_CONFIRM, PlayerIntent.HAGGLE}:
                self.convo.debug(
                    f"User gave input '{player_input}' while pending confirmation for '{self.convo.pending_item}'"
                )

                # Explicitly set the new player intent
                # --- Upgrade the STATE properly ---
                if self.convo.pending_action == PlayerIntent.BUY_ITEM:
                    self.convo.set_state(ConversationState.AWAITING_PURCHASE_CONFIRMATION)
                    self.convo.set_intent(PlayerIntent.BUY_CONFIRM)

                elif self.convo.pending_action == PlayerIntent.SELL_ITEM:
                    self.convo.set_state(ConversationState.AWAITING_SALE_CONFIRMATION)
                    self.convo.set_intent(PlayerIntent.SELL_CONFIRM)

                elif self.convo.pending_action == PlayerIntent.HAGGLE:
                    self.convo.set_state(ConversationState.AWAITING_HAGGLE_CONFIRMATION)
                    self.convo.set_intent(PlayerIntent.HAGGLE_CONFIRM)

                # 🚨 IMPORTANT: Do NOT continue routing, return early!
                return self.agent.shopkeeper_pending_item_reminder(self.convo.pending_item)

        # --- Normal Routing ---
        handler = self.intent_router.get((self.convo.state, intent))
        if handler:
            return handler(wrapped_input)

        # --- Fallbacks ---
        if self.convo.state == ConversationState.INTRODUCTION:
            return self.handle_introduction(player_input)

        return self.generic_handler.handle_fallback(player_input)

    def _handle_confirmation_flow(self, wrapped_input):
        intent = wrapped_input.get("intent")

        if self.convo.pending_action in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_CONFIRM}:
            self.convo.debug("User confirmed BUY_ITEM — completing purchase.")
            return self.buy_handler.handle_confirm_purchase(wrapped_input)

        if self.convo.pending_action in {PlayerIntent.SELL_ITEM, PlayerIntent.SELL_CONFIRM}:
            self.convo.debug("User confirmed SELL_ITEM — completing sale.")
            return self.sell_handler.handle_sell_confirm(wrapped_input)

        self.convo.debug("Confirmation flow reached but no matching pending action found.")
        return self.generic_handler.handle_fallback(wrapped_input)

    def _handle_cancellation_flow(self, wrapped_input):
        self.convo.debug("User cancelled — resetting conversation state.")
        self.convo.set_pending_item(None)
        self.convo.set_pending_action(None)
        self.convo.set_discount(None)
        self.convo.reset_state()
        self.convo.set_state(ConversationState.AWAITING_ACTION)
        self.convo.save_state()
        return self.generic_handler.handle_cancel(wrapped_input)

    def _build_router(self):
        router = {}

        # --- Greetings ---
        for state in [ConversationState.INTRODUCTION, ConversationState.AWAITING_ACTION,
                      ConversationState.AWAITING_ITEM_SELECTION, ConversationState.AWAITING_CONFIRMATION]:
            router[(state, PlayerIntent.GREETING)] = self.generic_handler.handle_reply_to_greeting

        # --- Viewing Items ---
        for state in [ConversationState.INTRODUCTION, ConversationState.AWAITING_ACTION,
                      ConversationState.AWAITING_ITEM_SELECTION, ConversationState.VIEWING_CATEGORIES]:
            router[(state, PlayerIntent.VIEW_ITEMS)] = self.view_handler.process_view_items_flow
            router[(state, PlayerIntent.VIEW_EQUIPMENT_CATEGORY)] = self.view_handler.process_view_items_flow
            router[(state, PlayerIntent.VIEW_WEAPON_CATEGORY)] = self.view_handler.process_view_items_flow
            router[(state, PlayerIntent.VIEW_GEAR_CATEGORY)] = self.view_handler.process_view_items_flow
            router[(state, PlayerIntent.VIEW_ARMOUR_CATEGORY)] = self.view_handler.process_view_items_flow
            router[(state, PlayerIntent.VIEW_TOOL_CATEGORY)] = self.view_handler.process_view_items_flow

        # --- Subcategories ---
        router[(ConversationState.VIEWING_CATEGORIES,
                PlayerIntent.VIEW_ARMOUR_SUBCATEGORY)] = self.view_handler.process_view_armour_subcategory
        router[(ConversationState.VIEWING_CATEGORIES,
                PlayerIntent.VIEW_WEAPON_SUBCATEGORY)] = self.view_handler.process_view_weapon_subcategory
        router[(ConversationState.VIEWING_CATEGORIES,
                PlayerIntent.VIEW_GEAR_SUBCATEGORY)] = self.view_handler.process_view_gear_subcategory
        router[(ConversationState.VIEWING_CATEGORIES,
                PlayerIntent.VIEW_TOOL_SUBCATEGORY)] = self.view_handler.process_view_tool_subcategory

        # --- Pagination ---
        router[(ConversationState.VIEWING_CATEGORIES, PlayerIntent.NEXT)] = self.generic_handler.handle_next_page
        router[(ConversationState.VIEWING_CATEGORIES, PlayerIntent.PREVIOUS)] = self.generic_handler.handle_previous_page

        # --- Buy / Sell Routing ---
        router[(ConversationState.VIEWING_CATEGORIES, PlayerIntent.BUY_ITEM)] = self.buy_handler.process_buy_item_flow
        router[(ConversationState.VIEWING_CATEGORIES, PlayerIntent.BUY_NEEDS_ITEM)] = self.buy_handler.process_buy_item_flow
        router[(ConversationState.VIEWING_CATEGORIES, PlayerIntent.SELL_ITEM)] = self.sell_handler.process_sell_item_flow
        router[(ConversationState.VIEWING_CATEGORIES, PlayerIntent.SELL_NEEDS_ITEM)] = self.sell_handler.process_sell_item_flow
        router[(ConversationState.AWAITING_ACTION, PlayerIntent.BUY_ITEM)] = self.buy_handler.process_buy_item_flow
        router[(ConversationState.AWAITING_ACTION, PlayerIntent.BUY_NEEDS_ITEM)] = self.buy_handler.process_buy_item_flow
        router[(ConversationState.AWAITING_ACTION, PlayerIntent.SELL_ITEM)] = self.sell_handler.process_sell_item_flow
        router[(ConversationState.AWAITING_ACTION, PlayerIntent.SELL_NEEDS_ITEM)] = self.sell_handler.process_sell_item_flow

        # --- Confirm / Cancel ---
        router[(ConversationState.AWAITING_CONFIRMATION, PlayerIntent.BUY_CONFIRM)] = self.buy_handler.handle_confirm_purchase
        router[(ConversationState.AWAITING_CONFIRMATION, PlayerIntent.SELL_CONFIRM)] = self.sell_handler.handle_sell_confirm
        router[(ConversationState.AWAITING_CONFIRMATION, PlayerIntent.CONFIRM)] = self.generic_handler.handle_confirm
        router[(ConversationState.AWAITING_CONFIRMATION, PlayerIntent.CANCEL)] = self._handle_cancellation_flow
        router[(ConversationState.AWAITING_CONFIRMATION, PlayerIntent.BUY_CANCEL)] = self._handle_cancellation_flow
        router[(ConversationState.AWAITING_CONFIRMATION, PlayerIntent.SELL_CANCEL)] = self._handle_cancellation_flow
        router[(ConversationState.AWAITING_CONFIRMATION, PlayerIntent.HAGGLE_CANCEL)] = self._handle_cancellation_flow
        router[(ConversationState.AWAITING_CONFIRMATION, PlayerIntent.HAGGLE_CANCEL)] = self._handle_cancellation_flow

        # --- Haggle During Confirmation ---
        router[(ConversationState.AWAITING_CONFIRMATION, PlayerIntent.HAGGLE)] = self.buy_handler.handle_haggle

        # --- Fallbacks ---
        router[(ConversationState.AWAITING_CONFIRMATION, PlayerIntent.UNKNOWN)] = self.generic_handler.handle_fallback
        router[(ConversationState.INTRODUCTION, PlayerIntent.UNKNOWN)] = self.generic_handler.handle_fallback
        router[(ConversationState.VIEWING_CATEGORIES, PlayerIntent.UNKNOWN)] = self.view_handler.process_view_items_flow

        return router

    def handle_introduction(self, player_input):
        intent = self.convo.player_intent
        if intent in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_NEEDS_ITEM}:
            return self.buy_handler.process_buy_item_flow(player_input)
        if intent in {PlayerIntent.SELL_ITEM, PlayerIntent.SELL_NEEDS_ITEM}:
            return self.sell_handler.process_sell_item_flow(player_input)
        return self.generic_handler.handle_fallback(player_input)


