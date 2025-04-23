# app/conversation_service.py

from app.conversation import ConversationState, PlayerIntent
from app.interpreter import interpret_input, get_equipment_category_from_input
from app.models.items import get_item_by_name
from commands.dm_commands import handle_dm_command
from app.models.ledger import get_last_transactions
from app.shop_handlers.buy_handler import BuyHandler
from app.shop_handlers.sell_handler import SellHandler
from app.shop_handlers.deposit_handler import DepositHandler
from app.shop_handlers.withdraw_handler import WithdrawHandler
from commands.admin_commands import handle_admin_command


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

        self.intent_router = self._build_router()

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

        # Wrap everything into a dict consistently
        wrapped_input = {
            "text": raw_text,
            "intent": intent,
            "item": item,
            **intent_data
        }

        if intent == PlayerIntent.VIEW_LEDGER:
            return self.handle_view_ledger(wrapped_input)

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
            return handler(wrapped_input)

        if self.convo.state == ConversationState.INTRODUCTION:
            return self.handle_introduction()

        return self.handle_fallback()

    def _build_router(self):

        def view_items_handler(player_input):
            if isinstance(player_input, dict):
                category = player_input.get("category")
            else:
                category = get_equipment_category_from_input(player_input)

            if category:
                # Start at page 1 and store state
                self.convo.metadata["current_category"] = category
                self.convo.metadata["current_page"] = 1
                self.convo.save_state()

                # Send paginated response (first page)
                return self.agent.shopkeeper_show_items_by_category({"category": category, "page": 1})


            return self.agent.shopkeeper_view_items_prompt()

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
            (ConversationState.INTRODUCTION, PlayerIntent.GREETING): self.handle_reply_to_greeting,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.GREETING): self.handle_reply_to_greeting,
            (ConversationState.AWAITING_ACTION, PlayerIntent.GREETING): self.handle_reply_to_greeting,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.GREETING): self.handle_reply_to_greeting,

            (ConversationState.INTRODUCTION, PlayerIntent.SHOW_GRATITUDE): self.handle_accept_thanks,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.SHOW_GRATITUDE): self.handle_accept_thanks,
            (ConversationState.AWAITING_ACTION, PlayerIntent.SHOW_GRATITUDE): self.handle_accept_thanks,
            (ConversationState.INTRODUCTION, PlayerIntent.UNKNOWN): self.handle_fallback,

            (ConversationState.INTRODUCTION, PlayerIntent.VIEW_LEDGER): self.handle_view_ledger,
            (ConversationState.AWAITING_ACTION, PlayerIntent.VIEW_LEDGER): self.handle_view_ledger,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.VIEW_LEDGER): self.handle_view_ledger,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.VIEW_LEDGER): self.handle_view_ledger,

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

            (ConversationState.AWAITING_ACTION, PlayerIntent.PREVIOUS): handle_previous_page,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.PREVIOUS): handle_previous_page,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.PREVIOUS): handle_previous_page,
            (ConversationState.VIEWING_CATEGORIES, PlayerIntent.PREVIOUS): handle_previous_page,

            (ConversationState.INTRODUCTION, PlayerIntent.CHECK_BALANCE): self.handle_check_balance,
            (ConversationState.AWAITING_ACTION, PlayerIntent.CHECK_BALANCE): self.handle_check_balance,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.CHECK_BALANCE): self.handle_check_balance,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.CHECK_BALANCE): self.handle_check_balance,

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
            (ConversationState.AWAITING_ACTION, PlayerIntent.SELL_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.SELL_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.SELL_NEEDS_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.SELL_NEEDS_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.SELL_CONFIRM): self.sell_handler.handle_confirm_sale,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.SELL_CANCEL): self.sell_handler.handle_cancel_sale,

            (ConversationState.INTRODUCTION, PlayerIntent.DEPOSIT_GOLD): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.INTRODUCTION, PlayerIntent.DEPOSIT_NEEDS_AMOUNT): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.DEPOSIT_GOLD): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.DEPOSIT_NEEDS_AMOUNT): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.DEPOSIT_NEEDS_AMOUNT): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.DEPOSIT_GOLD): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.DEPOSIT_NEEDS_AMOUNT): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.DEPOSIT_CONFIRM): self.deposit_handler.handle_confirm_deposit,

            (ConversationState.INTRODUCTION, PlayerIntent.WITHDRAW_GOLD): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.INTRODUCTION, PlayerIntent.WITHDRAW_NEEDS_AMOUNT): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.WITHDRAW_GOLD): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.WITHDRAW_NEEDS_AMOUNT): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.WITHDRAW_GOLD): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.WITHDRAW_NEEDS_AMOUNT): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.WITHDRAW_CONFIRM): self.withdraw_handler.handle_confirm_withdraw,
        }

    def handle_introduction(self):
        intent = self.convo.player_intent
        if intent in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_NEEDS_ITEM}:
            return self.buy_handler.process_buy_item_flow(self.convo.input_text)
        elif intent in {PlayerIntent.SELL_ITEM, PlayerIntent.SELL_NEEDS_ITEM}:
            return self.sell_handler.process_sell_item_flow(self.convo.input_text)
        return self.handle_fallback()

    def handle_reply_to_greeting(self, _):
        return self.agent.shopkeeper_greeting(
            party_name=self.party_data["party_name"],
            visit_count=self.party_data["visit_count"],
            player_name=self.party_data["player_name"]
        )

    def handle_fallback(self, *_):
        return self.agent.shopkeeper_fallback_prompt()

    def handle_view_ledger(self, _):
        raw_entries = get_last_transactions(self.party_id)
        entries = [dict(row) for row in raw_entries]
        return self.agent.shopkeeper_show_ledger(entries)

    def handle_accept_thanks(self, _):
        return self.agent.shopkeeper_accept_thanks()

    def handle_check_balance(self, _):
        current_gold = self.party_data.get("party_gold", 0)
        return self.agent.shopkeeper_check_balance_prompt(current_gold)

    def handle_view_items(self, player_input):
        if isinstance(player_input, dict) and "category" in player_input:
            return self.agent.shopkeeper_show_items_by_category(player_input["category"])
        return self.agent.shopkeeper_view_items_prompt()
