# app/conversation_service.py

from app.conversation import ConversationState, PlayerIntent
from app.interpreter import interpret_input, normalize_input, find_item_in_input
from app.shop_handlers.buy_handler import BuyHandler
from app.shop_handlers.sell_handler import SellHandler
from app.shop_handlers.deposit_handler import DepositHandler
from app.shop_handlers.withdraw_handler import WithdrawHandler
from app.shop_handlers.generic_chat_handler import GenericChatHandler
from app.shop_handlers.view_handler import ViewHandler
from commands.dm_commands import handle_dm_command
from commands.admin_commands import handle_admin_command
from typing import Callable, Dict, Tuple, Any

CATEGORY_MAPPING = {
    PlayerIntent.VIEW_ARMOUR_CATEGORY: ("armour_category", "Armor"),
    PlayerIntent.VIEW_WEAPON_CATEGORY: ("weapon_category", "Weapon"),
    PlayerIntent.VIEW_GEAR_CATEGORY: ("gear_category", "Adventuring Gear"),
    PlayerIntent.VIEW_TOOL_CATEGORY: ("tool_category", "Tools"),
    PlayerIntent.VIEW_EQUIPMENT_CATEGORY: ("current_section", "equipment"),
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

        # Instantiate handlers
        self.buy_handler = BuyHandler(convo, agent, party_id, player_id, player_name, self.party_data)
        self.sell_handler = SellHandler(convo, agent, party_id, player_id, player_name, self.party_data)
        self.deposit_handler = DepositHandler(convo, agent, party_id, player_id, player_name, self.party_data)
        self.withdraw_handler = WithdrawHandler(convo, agent, party_id, player_id, player_name, self.party_data)
        self.generic_handler = GenericChatHandler(agent, self.party_data, convo, party_id)
        self.view_handler = ViewHandler(convo, agent, self.buy_handler)

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
            normalized = normalize_input(player_input)
            self.convo.normalized_input = normalized  # ✅ Store it for debugging
        else:
            self.convo.normalized_input = "N/A"

        # --- Numeric Item ID Selection ---
        if player_input.strip().isdigit() and self.convo.state == ConversationState.AWAITING_ITEM_SELECTION:
            item_matches, _ = find_item_in_input(player_input, self.convo)
            if item_matches:
                self.convo.set_pending_item(item_matches[0])  # set item dict explicitly
                self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
                self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
                self.convo.save_state()
                return self.agent.shopkeeper_buy_confirm_prompt(
                    item_matches[0], self.party_data.get("party_gold", 0)
                )

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
            if isinstance(item, str):
                import json
                item = json.loads(item)  # 🛠 Convert from string to list/dict
            self.convo.set_pending_item(item)

        # --- Pending Confirmation Protection ---
        if self.convo.state == ConversationState.AWAITING_CONFIRMATION:
            if intent not in {PlayerIntent.CONFIRM, PlayerIntent.CANCEL, PlayerIntent.BUY_CONFIRM,
                              PlayerIntent.SELL_CONFIRM, PlayerIntent.HAGGLE}:
                self.convo.debug(
                    f"User gave input '{player_input}' while pending confirmation for '{self.convo.pending_item}'"
                )
                return self.agent.shopkeeper_pending_item_reminder(self.convo.pending_item)

        # --- Try routing normally ---
        handler = self.intent_router.get((self.convo.state, intent))

        # --- 🧠 NEW: If not found in manual intent_router, try fallback _route_intent
        if not handler:
            handler = self._route_intent(intent, self.convo.state)

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
            self.buy_handler.handle_confirm_purchase(wrapped_input)
            self.convo.set_pending_item(None)  # Reset after successful purchase
            self.convo.set_pending_action(None)  # Reset pending action
            self.convo.set_state(ConversationState.AWAITING_ACTION)  # Set state back to normal
            return self.agent.shopkeeper_confirm_purchase_response()

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

        # === INTRODUCTION STATE ===
        for intent in [
            PlayerIntent.GREETING,
            PlayerIntent.VIEW_ITEMS,
            PlayerIntent.VIEW_EQUIPMENT_CATEGORY,
            PlayerIntent.VIEW_WEAPON_CATEGORY,
            PlayerIntent.VIEW_GEAR_CATEGORY,
            PlayerIntent.VIEW_ARMOUR_CATEGORY,
            PlayerIntent.VIEW_TOOL_CATEGORY,
            PlayerIntent.VIEW_MOUNT_CATEGORY,
            PlayerIntent.DEPOSIT_GOLD,
            PlayerIntent.WITHDRAW_GOLD,
            PlayerIntent.CHECK_BALANCE,
            PlayerIntent.VIEW_LEDGER,
        ]:
            router[(ConversationState.INTRODUCTION, intent)] = self._route_intent(intent)
        router[(ConversationState.INTRODUCTION, PlayerIntent.UNKNOWN)] = self.generic_handler.handle_fallback

        # === AWAITING_ACTION STATE ===
        for intent in [
            PlayerIntent.GREETING,
            PlayerIntent.VIEW_ITEMS,
            PlayerIntent.VIEW_EQUIPMENT_CATEGORY,
            PlayerIntent.VIEW_WEAPON_CATEGORY,
            PlayerIntent.VIEW_GEAR_CATEGORY,
            PlayerIntent.VIEW_ARMOUR_CATEGORY,
            PlayerIntent.VIEW_TOOL_CATEGORY,
            PlayerIntent.VIEW_MOUNT_CATEGORY,
            PlayerIntent.BUY_ITEM,
            PlayerIntent.BUY_NEEDS_ITEM,
            PlayerIntent.SELL_ITEM,
            PlayerIntent.SELL_NEEDS_ITEM,
            PlayerIntent.DEPOSIT_GOLD,
            PlayerIntent.WITHDRAW_GOLD,
            PlayerIntent.CHECK_BALANCE,
            PlayerIntent.VIEW_LEDGER,
        ]:
            router[(ConversationState.AWAITING_ACTION, intent)] = self._route_intent(intent)
        router[(ConversationState.AWAITING_ACTION, PlayerIntent.UNKNOWN)] = self.generic_handler.handle_fallback

        # === AWAITING_ITEM_SELECTION STATE ===
        for intent in [
            PlayerIntent.GREETING,
            PlayerIntent.BUY_ITEM,
            PlayerIntent.BUY_NEEDS_ITEM,
            PlayerIntent.SELL_ITEM,
            PlayerIntent.SELL_NEEDS_ITEM,
            PlayerIntent.VIEW_ITEMS,
            PlayerIntent.VIEW_EQUIPMENT_CATEGORY,
            PlayerIntent.VIEW_WEAPON_CATEGORY,
            PlayerIntent.VIEW_GEAR_CATEGORY,
            PlayerIntent.VIEW_ARMOUR_CATEGORY,
            PlayerIntent.VIEW_TOOL_CATEGORY,
            PlayerIntent.VIEW_MOUNT_CATEGORY,
            PlayerIntent.DEPOSIT_GOLD,
            PlayerIntent.WITHDRAW_GOLD,
            PlayerIntent.CHECK_BALANCE,
            PlayerIntent.VIEW_LEDGER,
        ]:
            if intent in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_NEEDS_ITEM, PlayerIntent.SELL_ITEM,
                          PlayerIntent.SELL_NEEDS_ITEM}:
                router[(ConversationState.AWAITING_ITEM_SELECTION, intent)] = self.buy_handler.process_item_selection
            else:
                router[(ConversationState.AWAITING_ITEM_SELECTION, intent)] = self._route_intent(intent)
        router[
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.UNKNOWN)] = self.buy_handler.process_item_selection

        return router

    def _route_intent(self, intent, state=None):
        """Helper to route intents consistently based on intent and current state."""

        # Special case for BUY_ITEM / BUY_NEEDS_ITEM
        if intent in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_NEEDS_ITEM}:
            if state in {ConversationState.AWAITING_ACTION, ConversationState.VIEWING_CATEGORIES}:
                return self.smart_buy_router  # Special handling for smart buy items
            else:
                return self.buy_handler.process_buy_item_flow

        if intent in {PlayerIntent.SELL_ITEM, PlayerIntent.SELL_NEEDS_ITEM}:
            return self.sell_handler.process_sell_item_flow

        if intent in {
            PlayerIntent.VIEW_ITEMS, PlayerIntent.VIEW_EQUIPMENT_CATEGORY,
            PlayerIntent.VIEW_WEAPON_CATEGORY, PlayerIntent.VIEW_GEAR_CATEGORY,
            PlayerIntent.VIEW_ARMOUR_CATEGORY, PlayerIntent.VIEW_TOOL_CATEGORY,
            PlayerIntent.VIEW_MOUNT_CATEGORY,
            PlayerIntent.VIEW_ARMOUR_SUBCATEGORY, PlayerIntent.VIEW_WEAPON_SUBCATEGORY,
            PlayerIntent.VIEW_GEAR_SUBCATEGORY, PlayerIntent.VIEW_TOOL_SUBCATEGORY,
        }:
            return self.view_handler.process_view_items_flow

        if intent == PlayerIntent.NEXT:
            return self.generic_handler.handle_next_page
        if intent == PlayerIntent.PREVIOUS:
            return self.generic_handler.handle_previous_page
        if intent == PlayerIntent.GREETING:
            return self.generic_handler.handle_reply_to_greeting
        if intent == PlayerIntent.CONFIRM:
            return self.generic_handler.handle_confirm
        if intent in {PlayerIntent.CANCEL, PlayerIntent.BUY_CANCEL, PlayerIntent.SELL_CANCEL,
                      PlayerIntent.HAGGLE_CANCEL}:
            return self._handle_cancellation_flow
        if intent == PlayerIntent.BUY_CONFIRM:
            return self.buy_handler.handle_confirm_purchase
        if intent == PlayerIntent.SELL_CONFIRM:
            return self.sell_handler.handle_sell_confirm
        if intent == PlayerIntent.HAGGLE:
            return self.buy_handler.handle_haggle
        if intent == PlayerIntent.DEPOSIT_GOLD:
            return self.deposit_handler.process_deposit_gold_flow
        if intent == PlayerIntent.WITHDRAW_GOLD:
            return self.withdraw_handler.process_withdraw_gold_flow
        if intent == PlayerIntent.CHECK_BALANCE:
            return self.generic_handler.handle_check_balance
        if intent == PlayerIntent.VIEW_LEDGER:
            return self.generic_handler.handle_view_ledger

        return self.generic_handler.handle_fallback

    def smart_buy_router(self, player_input):
        """Decides whether to search items directly or show categories first."""
        raw_input = player_input.get("text", "") if isinstance(player_input, dict) else player_input

        # Search for matching items and categories
        item_matches, detected_category = find_item_in_input(raw_input, self.convo)

        if item_matches:
            # 🧠 ALWAYS handle item matches FIRST!
            if len(item_matches) > 1:
                self.convo.set_pending_item(item_matches)
                self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)  # 🔥 FORCE correct state
                self.convo.save_state()
                return self.agent.shopkeeper_list_matching_items(item_matches)

            elif len(item_matches) == 1:
                self.convo.set_pending_item(item_matches[0]["item_name"])
                self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
                self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)  # 🔥 FORCE correct state
                self.convo.save_state()
                return self.agent.shopkeeper_buy_confirm_prompt(item_matches[0], self.party_data.get("party_gold", 0))

        elif detected_category:
            self.convo.set_state(ConversationState.VIEWING_CATEGORIES)
            self.convo.save_state()
            return self.agent.shopkeeper_show_items_by_category({"equipment_category": detected_category})

        return self.agent.shopkeeper_view_items_prompt()

    def handle_introduction(self, player_input):
        intent = self.convo.player_intent
        if intent in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_NEEDS_ITEM}:
            return self.buy_handler.process_buy_item_flow(player_input)
        if intent in {PlayerIntent.SELL_ITEM, PlayerIntent.SELL_NEEDS_ITEM}:
            return self.sell_handler.process_sell_item_flow(player_input)
        return self.generic_handler.handle_fallback(player_input)
