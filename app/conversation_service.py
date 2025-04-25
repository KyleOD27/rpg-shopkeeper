# app/conversation_service.py

from app.conversation import ConversationState, PlayerIntent
from app.interpreter import interpret_input, get_equipment_category_from_input, normalize_input
from app.models.items import get_item_by_name, get_weapon_categories, get_armour_categories, get_gear_categories, \
    get_tool_categories
from commands.dm_commands import handle_dm_command
from app.shop_handlers.buy_handler import BuyHandler
from app.shop_handlers.sell_handler import SellHandler
from app.shop_handlers.deposit_handler import DepositHandler
from app.shop_handlers.withdraw_handler import WithdrawHandler
from commands.admin_commands import handle_admin_command
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

    def say(self, message):
        return message

    def get_dict_item(self, item_reference):
        name = str(item_reference)
        return dict(get_item_by_name(name) or {})

    def handle(self, player_input):
        if player_input.strip().lower().startswith("dm "):
            return handle_dm_command(self.party_id, self.player_id, player_input, party_data=self.party_data)

        if player_input.strip().lower().startswith("admin "):
            return handle_admin_command(player_input)

        self.convo.set_input(player_input)

        # 🧠 Always work with a wrapped version
        if isinstance(player_input, str):
            raw_text = player_input
            intent_data = interpret_input(player_input, self.convo)
        elif isinstance(player_input, dict):
            raw_text = player_input.get("text", "")
            intent_data = player_input  # already parsed
        else:
            raw_text = str(player_input)
            intent_data = interpret_input(raw_text, self.convo)

        intent = intent_data.get("intent")
        item = intent_data.get("item")
        self.convo.set_intent(intent)

        if item:
            self.convo.set_pending_item(item)

        wrapped_input = {
            "text": raw_text,
            "intent": intent,
            "item": item,
            **intent_data,
            **intent_data.get("metadata", {})
        }

        if intent == PlayerIntent.VIEW_LEDGER:
            return self.generic_handler.handle_view_ledger(wrapped_input)

        # Handle misaligned confirmation outside of CONFIRMATION state
        if intent in {PlayerIntent.CONFIRM,
                      PlayerIntent.CANCEL} and self.convo.state != ConversationState.AWAITING_CONFIRMATION:
            if self.convo.player_intent == PlayerIntent.BUY_ITEM and intent == PlayerIntent.CONFIRM:
                self.convo.debug(f"User reconfirmed purchase outside of confirmation state — rerouting to BUY_CONFIRM.")
                intent = PlayerIntent.BUY_CONFIRM
            elif self.convo.player_intent == PlayerIntent.SELL_ITEM and intent == PlayerIntent.CONFIRM:
                self.convo.debug(f"User reconfirmed sale outside of confirmation state — rerouting to SELL_CONFIRM.")
                intent = PlayerIntent.SELL_CONFIRM
            else:
                self.convo.debug(f"Ignoring {intent} — not in confirmation state.")
                self.convo.set_intent(PlayerIntent.UNKNOWN)
                intent = PlayerIntent.UNKNOWN

        handler = self.intent_router.get((self.convo.state, intent))
        if handler:
            return handler(wrapped_input)  # ✅ wrapped_input includes text + metadata

        if self.convo.state == ConversationState.INTRODUCTION:
            return self.handle_introduction(player_input)

        return self.generic_handler.handle_fallback(player_input)

    def _build_router(self):

        def view_items_handler(player_input):
            if isinstance(player_input, dict):
                input_text = player_input.get("text", "")
            else:
                input_text = str(player_input)

            input_normalized = normalize_input(input_text)

            # ✅ FIRST: Handle subcategory if already detected
            subcategory = player_input.get("subcategory")
            if subcategory:
                self.convo.metadata["current_weapon_category"] = subcategory
                self.convo.metadata["current_page"] = 1
                self.convo.save_state()
                return self.agent.shopkeeper_show_items_by_weapon_category({
                    "weapon_category": subcategory,
                    "page": 1
                })

            # 1. Top-level category match (e.g. "weapons", "armor", "gear", etc.)
            category = get_equipment_category_from_input(input_text)
            if category:
                self.convo.metadata["current_category"] = category
                self.convo.metadata["current_page"] = 1
                self.convo.save_state()

                if category.lower() == "weapon":
                    return self.agent.shopkeeper_list_weapon_categories(get_weapon_categories())
                elif category.lower() == "armor" or category.lower() == "armour":
                    return self.agent.shopkeeper_list_armour_categories(get_armour_categories())
                elif category.lower() == "adventuring gear":
                    return self.agent.shopkeeper_list_gear_categories(get_gear_categories())
                elif category.lower() == "tools":
                    return self.agent.shopkeeper_list_gear_categories(get_tool_categories())

                return self.agent.shopkeeper_show_items_by_category({"category": category, "page": 1})

            # 2. Match weapon subcategory (e.g. "martial", "simple")
            for weapon_cat in get_weapon_categories():
                weapon_cat_norm = normalize_input(weapon_cat)
                if weapon_cat_norm in input_normalized or (weapon_cat_norm + " weapons") in input_normalized:
                    self.convo.metadata["current_weapon_category"] = weapon_cat
                    self.convo.metadata["current_page"] = 1
                    self.convo.save_state()
                    return self.agent.shopkeeper_show_items_by_weapon_category({
                        "weapon_category": weapon_cat,
                        "page": 1
                    })

            # 3. Match armour subcategory (e.g. "light", "medium", "heavy", "shield")
            for armour_cat in get_armour_categories():
                armour_cat_norm = normalize_input(armour_cat)
                if (
                        armour_cat_norm in input_normalized
                        or (armour_cat_norm + " armor") in input_normalized
                        or (armour_cat_norm + " armour") in input_normalized
                ):
                    self.convo.metadata["current_armour_category"] = armour_cat
                    self.convo.metadata["current_page"] = 1
                    self.convo.save_state()
                    return self.agent.shopkeeper_show_items_by_armour_category({
                        "armour_category": armour_cat,
                        "page": 1
                    })

            # 4. Match gear subcategory (e.g. "ammunition", "kits", etc.)
            for gear_cat in get_gear_categories():
                gear_cat_norm = normalize_input(gear_cat)
                if gear_cat_norm in input_normalized:
                    self.convo.metadata["current_gear_category"] = gear_cat
                    self.convo.metadata["current_page"] = 1
                    self.convo.save_state()
                    return self.agent.shopkeeper_show_items_by_gear_category({
                        "gear_category": gear_cat,
                        "page": 1
                    })

            # 5. Match tool subcategory (e.g. "Artisan's Tools" etc)
            for tool_cat in get_tool_categories():
                tool_cat_norm = normalize_input(tool_cat)
                if tool_cat_norm in input_normalized:
                    self.convo.metadata["current_tool_category"] = tool_cat
                    self.convo.metadata["current_page"] = 1
                    self.convo.save_state()
                    return self.agent.shopkeeper_show_items_by_tool_category({
                        "tool_category": tool_cat,
                        "page": 1
                   })

            # ❌ Nothing matched, fallback
            return self.agent.shopkeeper_view_items_prompt()

        def view_subcategory_handler(player_input):
            text = player_input["text"] if isinstance(player_input, dict) else str(player_input)
            lowered = normalize_input(text)

            # Check if it matches weapon category
            for cat in get_weapon_categories():
                if normalize_input(cat) in lowered:
                    self.convo.metadata["weapon_category"] = cat
                    self.convo.metadata["current_page"] = 1
                    self.convo.save_state()
                    return self.agent.shopkeeper_show_items_by_category({"category": cat, "page": 1})

            # Check if it matches armour category
            for cat in get_armour_categories():
                if normalize_input(cat) in lowered:
                    self.convo.metadata["armour_category"] = cat
                    self.convo.metadata["current_page"] = 1
                    self.convo.save_state()
                    return self.agent.shopkeeper_show_items_by_category({"category": cat, "page": 1})

            return self.agent.shopkeeper_generic_say("Hmm, I didn’t catch that subcategory. Could you try again?")

        def next_page_handler(_):
            category = self.convo.metadata.get("current_category")
            if not category:
                return self.agent.shopkeeper_generic_say("Next what? I’m not sure what you’re looking at!")

            current_page = self.convo.metadata.get("current_page", 1)
            next_page = current_page + 1

            self.convo.metadata["current_page"] = next_page
            self.convo.save_state()

            return self.agent.shopkeeper_show_items_by_category({
                "category": category,
                "page": next_page
            })

        def handle_previous_page(_):
            category = self.convo.metadata.get("current_category")
            if not category:
                return self.agent.shopkeeper_view_items_prompt()

            current_page = self.convo.metadata.get("current_page", 1)
            new_page = max(current_page - 1, 1)

            self.convo.metadata["current_page"] = new_page
            self.convo.save_state()

            return self.agent.shopkeeper_show_items_by_category({
                "category": category,
                "page": new_page
            })

        return {
            (ConversationState.INTRODUCTION, PlayerIntent.GREETING): self.generic_handler.handle_reply_to_greeting,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.GREETING): self.generic_handler.handle_reply_to_greeting,
            (ConversationState.AWAITING_ACTION, PlayerIntent.GREETING): self.generic_handler.handle_reply_to_greeting,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.GREETING): self.generic_handler.handle_reply_to_greeting,

            (ConversationState.INTRODUCTION, PlayerIntent.SHOW_GRATITUDE): self.generic_handler.handle_accept_thanks,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.SHOW_GRATITUDE): self.generic_handler.handle_accept_thanks,
            (ConversationState.AWAITING_ACTION, PlayerIntent.SHOW_GRATITUDE): self.generic_handler.handle_accept_thanks,
            (ConversationState.INTRODUCTION, PlayerIntent.UNKNOWN): self.generic_handler.handle_fallback,

            (ConversationState.INTRODUCTION, PlayerIntent.VIEW_LEDGER): self.generic_handler.handle_view_ledger,
            (ConversationState.AWAITING_ACTION, PlayerIntent.VIEW_LEDGER): self.generic_handler.handle_view_ledger,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.VIEW_LEDGER): self.generic_handler.handle_view_ledger,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.VIEW_LEDGER): self.generic_handler.handle_view_ledger,

            (ConversationState.INTRODUCTION, PlayerIntent.VIEW_ITEMS): view_items_handler,
            (ConversationState.AWAITING_ACTION, PlayerIntent.VIEW_ITEMS): view_items_handler,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.VIEW_ITEMS): view_items_handler,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.VIEW_ITEMS): view_items_handler,
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.VIEW_ITEMS): self.buy_handler.process_buy_item_flow,
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.BUY_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.BUY_NEEDS_ITEM): self.buy_handler.process_buy_item_flow,

            (ConversationState.INTRODUCTION, PlayerIntent.NEXT): next_page_handler,
            (ConversationState.AWAITING_ACTION, PlayerIntent.NEXT): next_page_handler,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.NEXT): next_page_handler,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.NEXT): next_page_handler,
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.NEXT): next_page_handler,

            (ConversationState.INTRODUCTION, PlayerIntent.VIEW_ITEMS): view_items_handler,
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.VIEW_ITEMS): view_subcategory_handler,
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.BUY_ITEM): view_subcategory_handler,

            (ConversationState.AWAITING_ACTION, PlayerIntent.PREVIOUS): handle_previous_page,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.PREVIOUS): handle_previous_page,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.PREVIOUS): handle_previous_page,
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.PREVIOUS): handle_previous_page,

            (ConversationState.INTRODUCTION, PlayerIntent.CHECK_BALANCE): self.generic_handler.handle_check_balance,
            (ConversationState.AWAITING_ACTION, PlayerIntent.CHECK_BALANCE): self.generic_handler.handle_check_balance,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.CHECK_BALANCE): self.generic_handler.handle_check_balance,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.CHECK_BALANCE): self.generic_handler.handle_check_balance,

            (ConversationState.INTRODUCTION, PlayerIntent.BUY_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.INTRODUCTION, PlayerIntent.BUY_NEEDS_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.BUY_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.BUY_NEEDS_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.BUY_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.BUY_NEEDS_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.BUY_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.BUY_NEEDS_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.BUY_CONFIRM): self.buy_handler.handle_confirm_purchase,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.BUY_CANCEL): self.buy_handler.handle_cancel_purchase,

            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.HAGGLE): self.buy_handler.handle_haggle,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.HAGGLE_CONFIRM): self.buy_handler.handle_confirm_purchase,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.HAGGLE_CANCEL): self.buy_handler.handle_cancel_purchase,

            (ConversationState.INTRODUCTION, PlayerIntent.SELL_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.INTRODUCTION, PlayerIntent.SELL_NEEDS_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.SELL_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.SELL_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.SELL_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.SELL_NEEDS_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.SELL_NEEDS_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.SELL_CONFIRM): self.sell_handler.handle_confirm_sale,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.SELL_CANCEL): self.sell_handler.handle_cancel_sale,

            (ConversationState.INTRODUCTION, PlayerIntent.DEPOSIT_GOLD): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.DEPOSIT_GOLD): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.DEPOSIT_GOLD): self.deposit_handler.process_deposit_gold_flow,

            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.DEPOSIT_CONFIRM): self.deposit_handler.handle_confirm_deposit,

            (ConversationState.INTRODUCTION, PlayerIntent.DEPOSIT_NEEDS_AMOUNT): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.DEPOSIT_NEEDS_AMOUNT): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.DEPOSIT_NEEDS_AMOUNT): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.DEPOSIT_NEEDS_AMOUNT): self.deposit_handler.process_deposit_gold_flow,


            (ConversationState.INTRODUCTION, PlayerIntent.WITHDRAW_GOLD): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.INTRODUCTION, PlayerIntent.WITHDRAW_NEEDS_AMOUNT): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.WITHDRAW_GOLD): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.WITHDRAW_NEEDS_AMOUNT): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.WITHDRAW_GOLD): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.WITHDRAW_NEEDS_AMOUNT): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.WITHDRAW_CONFIRM): self.withdraw_handler.handle_confirm_withdraw,
        }

    def handle_introduction(self, player_input):
        intent = self.convo.player_intent
        if intent in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_NEEDS_ITEM}:
            return self.buy_handler.process_buy_item_flow(self.convo.input_text)
        elif intent in {PlayerIntent.SELL_ITEM, PlayerIntent.SELL_NEEDS_ITEM}:
            return self.sell_handler.process_sell_item_flow(self.convo.input_text)
        return self.generic_handler.handle_fallback(player_input)



