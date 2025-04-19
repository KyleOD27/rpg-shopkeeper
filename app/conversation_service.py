# app/conversation_service.py

from app.conversation import ConversationState, PlayerIntent
from app.interpreter import interpret_input
from app.models.items import get_item_by_name
from app.dm_commands import handle_dm_command
from app.models.ledger import get_last_transactions
from app.models.players import get_player_by_id
from app.shop_handlers.buy_handler import BuyHandler
from app.shop_handlers.sell_handler import SellHandler
from app.shop_handlers.deposit_handler import DepositHandler
from app.shop_handlers.withdraw_handler import WithdrawHandler


class ConversationService:
    def __init__(self, convo, agent, party_id, player_id, player_name, party_data):
        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.player_id = player_id
        self.party_data = dict(party_data)
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
            return handle_dm_command(self.party_id, self.player_id, player_input)

        self.convo.set_input(player_input)
        intent_data = interpret_input(player_input, self.convo)
        intent = intent_data.get("intent")
        item = intent_data.get("item")
        self.convo.set_intent(intent)

        if item:
            self.convo.set_pending_item(item)

        if intent == PlayerIntent.VIEW_LEDGER:
            return self.handle_view_ledger(player_input)

        if intent in {PlayerIntent.CONFIRM, PlayerIntent.CANCEL} and self.convo.state != ConversationState.AWAITING_CONFIRMATION:
            self.convo.debug(f"Ignoring {intent} — not in confirmation state.")
            self.convo.set_intent(PlayerIntent.UNKNOWN)
            intent = PlayerIntent.UNKNOWN

        # Handle directly if matched in router
        handler = self.intent_router.get((self.convo.state, intent))
        if handler:
            return handler(player_input)

        # Intro logic including fallback for UNKNOWN
        if self.convo.state == ConversationState.INTRODUCTION:
            return self.handle_introduction()

        # Final fallback
        return self.handle_fallback()

    def _build_router(self):
        return {

            # Greeting
            (ConversationState.INTRODUCTION, PlayerIntent.GREETING): self.handle_reply_to_greeting,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.GREETING): self.handle_reply_to_greeting,
            (ConversationState.AWAITING_ACTION, PlayerIntent.GREETING): self.handle_reply_to_greeting,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.GREETING): self.handle_reply_to_greeting,

            # Gratitude
            (ConversationState.INTRODUCTION, PlayerIntent.SHOW_GRATITUDE): self.handle_accept_thanks,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.SHOW_GRATITUDE): self.handle_accept_thanks,
            (ConversationState.AWAITING_ACTION, PlayerIntent.SHOW_GRATITUDE): self.handle_accept_thanks,
            (ConversationState.INTRODUCTION, PlayerIntent.UNKNOWN): self.handle_fallback,

            # View ledger
            (ConversationState.AWAITING_ACTION, PlayerIntent.VIEW_LEDGER): self.handle_view_ledger,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.VIEW_LEDGER): self.handle_view_ledger,

            # Buy flow
            (ConversationState.AWAITING_ACTION, PlayerIntent.BUY_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.BUY_NEEDS_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.BUY_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.BUY_NEEDS_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.BUY_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.BUY_NEEDS_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.BUY_CONFIRM): self.buy_handler.handle_confirm_purchase,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.BUY_CANCEL): self.buy_handler.handle_cancel_purchase,

            # Sell flow
            (ConversationState.AWAITING_ACTION, PlayerIntent.SELL_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.SELL_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.SELL_NEEDS_ITEM): self.sell_handler.process_sell_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.SELL_CONFIRM): self.sell_handler.handle_confirm_sale,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.SELL_CANCEL): self.sell_handler.handle_cancel_sale,

            # Deposit flow
            (ConversationState.AWAITING_ACTION, PlayerIntent.DEPOSIT_GOLD): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.DEPOSIT_GOLD): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.DEPOSIT_NEEDS_AMOUNT): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.DEPOSIT_NEEDS_AMOUNT): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.INTRODUCTION, PlayerIntent.DEPOSIT_NEEDS_AMOUNT): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.INTRODUCTION, PlayerIntent.DEPOSIT_GOLD): self.deposit_handler.process_deposit_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.DEPOSIT_CONFIRM): self.deposit_handler.handle_confirm_deposit,

            # Withdraw flow
            (ConversationState.AWAITING_ACTION, PlayerIntent.WITHDRAW_GOLD): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.WITHDRAW_GOLD): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.WITHDRAW_NEEDS_AMOUNT): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.WITHDRAW_NEEDS_AMOUNT): self.withdraw_handler.process_withdraw_gold_flow,

            (ConversationState.INTRODUCTION, PlayerIntent.WITHDRAW_NEEDS_AMOUNT): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.INTRODUCTION, PlayerIntent.WITHDRAW_GOLD): self.withdraw_handler.process_withdraw_gold_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.WITHDRAW_CONFIRM): self.withdraw_handler.handle_confirm_withdraw,

            (ConversationState.AWAITING_ACTION, PlayerIntent.CHECK_BALANCE): self.handle_check_balance,
            (ConversationState.INTRODUCTION, PlayerIntent.CHECK_BALANCE): self.handle_check_balance,

            (ConversationState.INTRODUCTION, PlayerIntent.VIEW_ITEMS): self.handle_view_items,
            (ConversationState.AWAITING_ACTION, PlayerIntent.VIEW_ITEMS): self.handle_view_items,

        }

    def handle_introduction(self):
        intent = self.convo.player_intent

        # 🛒 Buy flow
        if intent in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_NEEDS_ITEM} and self.convo.pending_item:
            self.convo.debug("Player wants to buy and item was identified. Moving to AWAITING_CONFIRMATION.")
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            item = self.get_dict_item(self.convo.pending_item)
            return self.agent.shopkeeper_buy_confirm_prompt(item, self.party_data["party_gold"])

        elif intent == PlayerIntent.BUY_NEEDS_ITEM:
            self.convo.debug("Player wants to buy but no item was identified. Asking for clarification.")
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            return self.agent.shopkeeper_buy_enquire_item()

        # 💰 Sell flow
        elif intent in {PlayerIntent.SELL_ITEM, PlayerIntent.SELL_NEEDS_ITEM} and self.convo.pending_item:
            self.convo.debug("Player wants to sell and item was identified. Moving to AWAITING_CONFIRMATION.")
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            item = self.get_dict_item(self.convo.pending_item)
            offer_price = item.get("sell_price") or round(item.get("base_price", 0) * 0.5)
            return self.agent.shopkeeper_sell_offer_prompt(item["item_name"], offer_price)

        elif intent == PlayerIntent.SELL_NEEDS_ITEM:
            self.convo.debug("Player wants to sell but no item was identified. Asking for clarification.")
            self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
            return self.agent.shopkeeper_clarify_item_prompt()

        self.convo.debug("Player hasn't engaged properly yet. Staying in INTRODUCTION.")
        return self.agent.shopkeeper_fallback_prompt()

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

    def handle_view_items(self, _):
        return self.agent.shopkeeper_view_items_prompt()

    def handle_reply_to_greeting(self, _):
        return self.agent.shopkeeper_intro_prompt()


