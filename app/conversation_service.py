# app/conversation_service.py

from app.conversation import ConversationState, PlayerIntent
from app.interpreter import interpret_input
from app.models.items import get_item_by_name
from app.dm_commands import handle_dm_command
from app.models.ledger import get_last_transactions
from app.shop_handlers.buy_handler import BuyHandler
from app.models.players import get_player_by_id

class ConversationService:
    def __init__(self, convo, agent, party_id, player_id, player_name, party_data):
        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.player_id = player_id
        self.party_data = dict(party_data)
        self.buy_handler = BuyHandler(convo, agent, party_id, player_id, player_name, self.party_data)
        self.intent_router = self._build_router()


    def say(self, message):
        return message

    # 🔧 Ensures sqlite3.Row becomes a dict
    def get_dict_item(self, item_reference):
        name = str(item_reference)
        return dict(get_item_by_name(name) or {})

    # 🧠 Central handler
    def handle(self, player_input):
        # 1. DM commands
        if player_input.strip().lower().startswith("dm "):
            return handle_dm_command(self.party_id, self.player_id, player_input)

        # 2. Interpret intent
        self.convo.set_input(player_input)
        intent_data = interpret_input(player_input)
        intent = intent_data.get("intent")
        item = intent_data.get("item")
        self.convo.set_intent(intent)

        if item:
            self.convo.set_pending_item(item)

        # 3. Ledger — always available
        if intent == PlayerIntent.VIEW_LEDGER:
            return self.handle_view_ledger(player_input)

        # 4. Misplaced CONFIRM/CANCEL
        if intent in {PlayerIntent.CONFIRM,
                      PlayerIntent.CANCEL} and self.convo.state != ConversationState.AWAITING_CONFIRMATION:
            self.convo.debug(f"Ignoring {intent} — not in confirmation state.")
            self.convo.set_intent(PlayerIntent.UNKNOWN)
            intent = PlayerIntent.UNKNOWN

        # 5. Match to router (even in INTRODUCTION)
        handler = self.intent_router.get((self.convo.state, intent))
        if handler:
            return handler(player_input)

        # 6. If still in INTRO and no match above, handle manually
        if self.convo.state == ConversationState.INTRODUCTION:
            return self.handle_introduction()

        # 7. Fallback
        return self.handle_fallback()

    # 📍 Routing table setup
    def _build_router(self):
        return {
            (ConversationState.INTRODUCTION, PlayerIntent.SHOW_GRATITUDE): self.handle_accept_thanks,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.SHOW_GRATITUDE): self.handle_accept_thanks,
            (ConversationState.AWAITING_ACTION, PlayerIntent.SHOW_GRATITUDE): self.handle_accept_thanks,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.SHOW_GRATITUDE): self.handle_accept_thanks,
            (ConversationState.AWAITING_ACTION, PlayerIntent.VIEW_LEDGER): self.handle_view_ledger,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.VIEW_LEDGER): self.handle_view_ledger,
            (ConversationState.AWAITING_ACTION, PlayerIntent.BUY_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.BUY_NEEDS_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.BUY_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_ITEM_SELECTION,
             PlayerIntent.BUY_NEEDS_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.CONFIRM): self.buy_handler.handle_confirm_purchase,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.CANCEL): self.buy_handler.handle_cancel_purchase,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.BUY_ITEM): self.buy_handler.process_buy_item_flow,
            (ConversationState.AWAITING_CONFIRMATION,
             PlayerIntent.BUY_NEEDS_ITEM): self.buy_handler.process_buy_item_flow,
        }

    # 🧭 INTRO flow
    def handle_introduction(self):
        intent = self.convo.player_intent

        if intent in {
            PlayerIntent.BUY_ITEM,
            PlayerIntent.BUY_NEEDS_ITEM,
        } and self.convo.pending_item:
            self.convo.debug("Player wants to buy and item was identified. Moving to AWAITING_CONFIRMATION.")
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            item = self.get_dict_item(self.convo.pending_item)
            return self.agent.shopkeeper_buy_confirm_prompt(item, self.party_data["party_gold"])

        elif intent == PlayerIntent.BUY_NEEDS_ITEM:
            self.convo.debug("Player wants to buy but no item was identified. Asking for clarification.")
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            return self.agent.shopkeeper_buy_enquire_item()

        if intent in {
            PlayerIntent.VIEW_ITEMS,
            PlayerIntent.BUY_ITEM,
            PlayerIntent.SELL_ITEM,
            PlayerIntent.HAGGLE,
            PlayerIntent.CHECK_BALANCE,
            PlayerIntent.VIEW_LEDGER,
            PlayerIntent.DEPOSIT_GOLD,
            PlayerIntent.WITHDRAW_GOLD,
        }:
            self.convo.debug(f"Player initiated an action ({intent}). Moving to AWAITING_ACTION.")
            self.convo.set_state(ConversationState.AWAITING_ACTION)
            return self.agent.shopkeeper_intro_prompt()

        self.convo.debug("Player hasn't engaged properly yet. Staying in INTRODUCTION.")
        return self.agent.shopkeeper_intro_prompt()

    # 💬 Default backup
    def handle_fallback(self, *_):
        return self.agent.shopkeeper_fallback_prompt()


    from app.models.ledger import get_last_transactions  # If not already imported

    def handle_view_ledger(self, _):
        raw_entries = get_last_transactions(self.party_id)
        entries = [dict(row) for row in raw_entries]
        return self.agent.shopkeeper_show_ledger(entries)

    def handle_accept_thanks(self, _):
        return self.agent.shopkeeper_accept_thanks()