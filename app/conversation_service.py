# app/conversation_service.py

from app.conversation import ConversationState, PlayerIntent
from app.interpreter import interpret_input, find_item_in_input

class ConversationService:
    def __init__(self, convo, agent, party_id, player_id):
        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.player_id = player_id

    def handle_introduction(self, player_input):
        intent_data = interpret_input(player_input)
        intent = intent_data['intent']

        if intent in [
            PlayerIntent.VIEW_ITEMS,
            PlayerIntent.BUY_ITEM,
            PlayerIntent.SELL_ITEM,
            PlayerIntent.HAGGLE,
            PlayerIntent.CHECK_BALANCE,
            PlayerIntent.VIEW_LEDGER,
            PlayerIntent.DEPOSIT_GOLD,
            PlayerIntent.WITHDRAW_GOLD
        ]:
            self.convo.state = ConversationState.AWAITING_ACTION
            return intent

        self.convo.debug("Player hasn't engaged properly yet. Staying in INTRODUCTION.")
        return PlayerIntent.UNKNOWN

    def handle_awaiting_action(self, player_input):
        intent_data = interpret_input(player_input)
        intent = intent_data['intent']

        if intent == PlayerIntent.BUY_ITEM:
            item_name = find_item_in_input(player_input)
            if not item_name:
                return self.agent.reply("I don't stock that. Did you mean something else?")
            self.convo.pending_action = 'buy'
            self.convo.pending_item = item_name
            self.convo.state = ConversationState.AWAITING_CONFIRMATION
            return self.agent.reply(f"Ah, looking to buy a {item_name}? It'll cost you. Deal or no deal?")

        return intent

    def handle_awaiting_confirmation(self, player_input):
        intent_data = interpret_input(player_input)

        if intent_data['intent'] == "CONFIRM":
            return 'CONFIRM'

        if intent_data['intent'] == "CANCEL":
            self.convo.reset_state()
            return self.agent.reply("Transaction cancelled.")

        return self.agent.reply("Well? Yes or no?")

    def handle_in_transaction(self, player_input):
        # For now, reuse handle_awaiting_action logic
        return self.handle_awaiting_action(player_input)

    def clarify_item_selection(self, possible_matches):
        matches_list = ', '.join(possible_matches)
        return self.agent.reply(f"Did you mean: {matches_list}?")
