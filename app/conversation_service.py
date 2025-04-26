# app/conversation_service.py

from app.conversation import ConversationState, PlayerIntent
from app.interpreter import interpret_input, normalize_input
from commands.dm_commands import handle_dm_command
from commands.admin_commands import handle_admin_command
from app.shop_handlers.buy_handler import BuyHandler
from app.shop_handlers.sell_handler import SellHandler
from app.shop_handlers.deposit_handler import DepositHandler
from app.shop_handlers.withdraw_handler import WithdrawHandler
from app.shop_handlers.generic_chat_handler import GenericChatHandler
from typing import Callable, Dict, Tuple, Any

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
        self.generic_handler = GenericChatHandler(agent, self.party_data, self.convo, party_id)
        self.intent_router: Dict[Tuple[str, str], Callable[[dict], Any]] = self._build_router()

    def handle(self, player_input):
        # --- Early admin/dm commands ---
        if player_input.strip().lower().startswith("dm "):
            return handle_dm_command(self.party_id, self.player_id, player_input, party_data=self.party_data)

        if player_input.strip().lower().startswith("admin "):
            admin_response = handle_admin_command(player_input)

            # 🧹 Reset conversation memory if reset was triggered
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
        elif isinstance(player_input, dict):
            raw_text = player_input.get("text", "")
            intent_data = player_input
        else:
            raw_text = str(player_input)
            intent_data = interpret_input(raw_text, self.convo)

        intent = intent_data.get("intent")
        metadata = intent_data.get("metadata", {})
        item = metadata.get("item")
        self.convo.set_intent(intent)

        if item:
            self.convo.set_pending_item(item)

        # 🛡️ Capture categories
        equipment_category = metadata.get("equipment_category")
        weapon_category = metadata.get("weapon_category")
        gear_category = metadata.get("gear_category")
        armour_category = metadata.get("armour_category")
        tool_category = metadata.get("tool_category")

        wrapped_input = {
            "text": raw_text,
            "intent": intent,
            "item": item,
            **intent_data,
            **metadata
        }

        wrapped_input = {
            "text": raw_text,
            "intent": intent,
            "item": item,
            **intent_data,
            **metadata
        }

        # 🛑 Critical intent early handling (starts here)
        if intent in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_NEEDS_ITEM}:
            ...

        # 🛡️ If they asked for a category, show items by category first
        if equipment_category:
            return self.agent.shopkeeper_show_items_by_category({"category": equipment_category})
        if weapon_category:
            return self.agent.shopkeeper_show_items_by_weapon_category({"weapon_category": weapon_category})
        if gear_category:
            return self.agent.shopkeeper_show_items_by_gear_category({"gear_category": gear_category})
        if armour_category:
            return self.agent.shopkeeper_show_items_by_armour_category({"armour_category": armour_category})
        if tool_category:
            return self.agent.shopkeeper_show_items_by_tool_category({"tool_category": tool_category})

        # 🛑 Critical intent early handling
        if intent in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_NEEDS_ITEM}:
            return self.buy_handler.process_buy_item_flow(wrapped_input)
        if intent in {PlayerIntent.SELL_ITEM, PlayerIntent.SELL_NEEDS_ITEM}:
            return self.sell_handler.process_sell_item_flow(wrapped_input)
        if intent in {PlayerIntent.DEPOSIT_GOLD, PlayerIntent.DEPOSIT_NEEDS_AMOUNT}:
            return self.deposit_handler.process_deposit_gold_flow(wrapped_input)
        if intent in {PlayerIntent.WITHDRAW_GOLD, PlayerIntent.WITHDRAW_NEEDS_AMOUNT}:
            return self.withdraw_handler.process_withdraw_gold_flow(wrapped_input)

        # 🛡️ Misaligned confirm/cancel protections
        if intent in {PlayerIntent.CONFIRM, PlayerIntent.CANCEL, PlayerIntent.BUY_CANCEL,
                      PlayerIntent.SELL_CANCEL, PlayerIntent.HAGGLE_CANCEL}:
            if self.convo.player_intent == PlayerIntent.BUY_ITEM and intent in {PlayerIntent.CONFIRM,
                                                                                PlayerIntent.BUY_CONFIRM}:
                self.convo.debug("User reconfirmed purchase outside confirmation — rerouting to BUY_CONFIRM.")
                intent = PlayerIntent.BUY_CONFIRM
            elif self.convo.player_intent == PlayerIntent.SELL_ITEM and intent in {PlayerIntent.CONFIRM,
                                                                                   PlayerIntent.SELL_CONFIRM}:
                self.convo.debug("User reconfirmed sale outside confirmation — rerouting to SELL_CONFIRM.")
                intent = PlayerIntent.SELL_CONFIRM
            elif intent in {PlayerIntent.CANCEL, PlayerIntent.BUY_CANCEL, PlayerIntent.SELL_CANCEL,
                            PlayerIntent.HAGGLE_CANCEL}:
                self.convo.debug("User cancelled — clearing pending item and resetting state.")
                self.convo.set_pending_item(None)
                self.convo.set_discount(None)
                self.convo.reset_state()
                self.convo.set_state(ConversationState.AWAITING_ACTION)
                self.convo.save_state()
                return self.generic_handler.handle_cancel(wrapped_input)
            else:
                self.convo.debug(f"Ignoring {intent} — not in confirmation state.")
                self.convo.set_intent(PlayerIntent.UNKNOWN)
                intent = PlayerIntent.UNKNOWN

        # ⚡ Polished Pending Confirmation Protection
        if self.convo.state == ConversationState.AWAITING_CONFIRMATION:
            if intent not in {PlayerIntent.CONFIRM, PlayerIntent.CANCEL, PlayerIntent.UNKNOWN}:
                self.convo.debug(
                    f"User gave new input '{player_input}' while pending confirmation for '{self.convo.pending_item}'."
                )
                # 🌟 Gently warn the user
                return self.agent.shopkeeper_pending_item_reminder(self.convo.pending_item)

        # 🧭 Normal routing
        handler = self.intent_router.get((self.convo.state, intent))
        if handler:
            return handler(wrapped_input)

        # Handle introduction
        if self.convo.state == ConversationState.INTRODUCTION:
            return self.handle_introduction(player_input)

        return self.generic_handler.handle_fallback(player_input)

    def _build_router(self):
        return {
            # Greetings
            (ConversationState.INTRODUCTION, PlayerIntent.GREETING): self.generic_handler.handle_reply_to_greeting,
            (ConversationState.AWAITING_ACTION, PlayerIntent.GREETING): self.generic_handler.handle_reply_to_greeting,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.GREETING): self.generic_handler.handle_reply_to_greeting,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.GREETING): self.generic_handler.handle_reply_to_greeting,

            # Viewing Items
            (ConversationState.INTRODUCTION, PlayerIntent.VIEW_ITEMS): self.view_items_handler,
            (ConversationState.AWAITING_ACTION, PlayerIntent.VIEW_ITEMS): self.view_items_handler,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.VIEW_ITEMS): self.view_items_handler,
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.VIEW_ITEMS): self.view_items_handler,

            # Moving through pages
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.NEXT): self.generic_handler.handle_next_page,
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.PREVIOUS): self.generic_handler.handle_previous_page,

            # Buy/Sell inside categories
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.BUY_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.BUY_NEEDS_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.SELL_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.SELL_NEEDS_ITEM): self.sell_handler.process_sell_item_flow,

            # Confirm/Cancel
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.CONFIRM): self.generic_handler.handle_confirm,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.CANCEL): self.generic_handler.handle_cancel,

            # Fallback
            (ConversationState.INTRODUCTION, PlayerIntent.UNKNOWN): self.generic_handler.handle_fallback,
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.UNKNOWN): self.generic_handler.handle_fallback,
        }

    def view_items_handler(self, player_input):
        metadata = player_input if isinstance(player_input, dict) else {}

        if metadata.get("weapon_category"):
            self.convo.metadata["current_weapon_category"] = metadata["weapon_category"]
            self.convo.metadata["current_page"] = 1
            self.convo.state = ConversationState.VIEWING_CATEGORIES
            self.convo.save_state()
            return self.agent.shopkeeper_show_items_by_weapon_category({
                "weapon_category": metadata["weapon_category"],
                "page": 1
            })

        if metadata.get("armour_category"):
            self.convo.metadata["current_armour_category"] = metadata["armour_category"]
            self.convo.metadata["current_page"] = 1
            self.convo.state = ConversationState.VIEWING_CATEGORIES
            self.convo.save_state()
            return self.agent.shopkeeper_show_items_by_armour_category({
                "armour_category": metadata["armour_category"],
                "page": 1
            })

        if metadata.get("gear_category"):
            self.convo.metadata["current_gear_category"] = metadata["gear_category"]
            self.convo.metadata["current_page"] = 1
            self.convo.state = ConversationState.VIEWING_CATEGORIES
            self.convo.save_state()
            return self.agent.shopkeeper_show_items_by_gear_category({
                "gear_category": metadata["gear_category"],
                "page": 1
            })

        if metadata.get("tool_category"):
            self.convo.metadata["current_tool_category"] = metadata["tool_category"]
            self.convo.metadata["current_page"] = 1
            self.convo.state = ConversationState.VIEWING_CATEGORIES
            self.convo.save_state()
            return self.agent.shopkeeper_show_items_by_tool_category({
                "tool_category": metadata["tool_category"],
                "page": 1
            })

        if metadata.get("equipment_category"):
            self.convo.metadata["current_category"] = metadata["equipment_category"]
            self.convo.metadata["current_page"] = 1
            self.convo.state = ConversationState.VIEWING_CATEGORIES
            self.convo.save_state()
            return self.agent.shopkeeper_show_items_by_category({
                "category": metadata["equipment_category"],
                "page": 1
            })

        return self.agent.shopkeeper_view_items_prompt()

    def handle_introduction(self, player_input):
        intent = self.convo.player_intent
        if intent in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_NEEDS_ITEM}:
            return self.buy_handler.process_buy_item_flow(self.convo.input_text)
        elif intent in {PlayerIntent.SELL_ITEM, PlayerIntent.SELL_NEEDS_ITEM}:
            return self.sell_handler.process_sell_item_flow(self.convo.input_text)
        return self.generic_handler.handle_fallback(player_input)
