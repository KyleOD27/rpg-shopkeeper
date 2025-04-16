# app/conversation_service.py

from app.conversation import ConversationState, PlayerIntent
from app.interpreter import interpret_input, find_item_in_input
from app.models.items import get_all_items


class ConversationService:
    def __init__(self, convo, agent, party_id, player_id, party_data):
        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.player_id = player_id
        self.party_data = party_data

    def say(self, message):
        return self.agent.generate_agent_reply(
            message,
            state=self.convo.state,
            intent=self.convo.player_intent,
            action=self.convo.pending_action,
            item=self.convo.pending_item
        )["data"]

    def handle(self, player_input):
        self.convo.set_input(player_input)
        intent_data = interpret_input(player_input)
        intent = intent_data.get("intent")
        item = intent_data.get("item")

        self.convo.set_intent(intent)
        self.convo.set_pending_item({"item_name": item} if item else None)

        if self.convo.state == ConversationState.INTRODUCTION:
            return self.handle_introduction()

        elif self.convo.state == ConversationState.AWAITING_ACTION:
            return self.handle_awaiting_action(player_input)

        elif self.convo.state == ConversationState.AWAITING_CONFIRMATION:
            return self.handle_awaiting_confirmation(player_input)

        elif self.convo.state == ConversationState.IN_TRANSACTION:
            return self.handle_in_transaction(player_input)

        return self.say("I'm not sure what state we're in. Try again.")

    def handle_introduction(self):
        intent = self.convo.player_intent

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
            self.convo.set_state(ConversationState.AWAITING_ACTION)
            return self.say("Right then, what’re you here for? Buying, selling, or just lookin'?")

        self.convo.debug("Player hasn't engaged properly yet. Staying in INTRODUCTION.")
        return self.say("Speak up, adventurer. I haven't got all day.")

    def handle_awaiting_action(self, player_input):
        intent = self.convo.player_intent

        if intent == PlayerIntent.BUY_ITEM or intent == PlayerIntent.BUY_NEEDS_ITEM:
            item_name, possible_matches = find_item_in_input(player_input)

            if not item_name:
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                return self.agent.shopkeeper_buy_enquire_item()

            self.convo.set_pending_item({"item_name": item_name})
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            return self.agent.shopkeeper_buy_confirm_prompt(
                {"item_name": item_name}, self.party_data['party_gold']
            )

        return self.say("Hmm. That's not something I do. Try saying what you want more clearly.")

    def handle_awaiting_confirmation(self, player_input):
        intent = self.convo.player_intent

        if intent == PlayerIntent.CONFIRM:
            pending = self.convo.pending_item
            item_name = pending.get("item_name") if isinstance(pending, dict) else pending

            item = next((i for i in get_all_items() if i["item_name"] == item_name), None)
            if not item:
                return self.say("Something went wrong — I can't find that item in stock.")

            cost = item.get("base_price", 0)
            new_balance = self.party_data.get("party_gold", 0) - cost
            self.convo.reset_state()

            return self.agent.shopkeeper_confirmation_reply(item_name, cost, new_balance)

        if intent == PlayerIntent.CANCEL:
            self.convo.reset_state()
            return self.say("Transaction cancelled.")

        return self.say("Well? Yes or no?")

    def handle_in_transaction(self, player_input):
        return self.handle_awaiting_action(player_input)

    def clarify_item_selection(self, possible_matches):
        matches_list = ', '.join(possible_matches)
        return self.say(f"Did you mean: {matches_list}?")
