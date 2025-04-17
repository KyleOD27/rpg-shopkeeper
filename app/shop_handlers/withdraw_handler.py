from app.conversation import ConversationState, PlayerIntent
from app.models.ledger import record_transaction
from app.models.parties import update_party_gold
import re

class WithdrawHandler:
    def __init__(self, convo, agent, party_id, player_id, player_name, party_data):
        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.player_id = player_id
        self.player_name = player_name
        self.party_data = party_data

    def process_withdraw_gold_flow(self, player_input):
        lowered = player_input.lower()
        amount = self._extract_amount(lowered)

        if amount is None:
            self.convo.debug("Withdraw amount missing — asking for it.")
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            self.convo.set_intent(PlayerIntent.WITHDRAW_NEEDS_AMOUNT)
            return self.agent.shopkeeper_withdraw_gold_prompt()

        current_gold = self.party_data.get("party_gold", 0)
        if amount > current_gold:
            return self.agent.shopkeeper_withdraw_insufficient_gold(amount, current_gold)

        self.party_data["party_gold"] -= amount
        update_party_gold(self.party_id, self.party_data["party_gold"])

        record_transaction(
            party_id=self.party_id,
            player_id=self.player_id,
            item_name=None,
            amount=-amount,
            action="WITHDRAW",
            balance_after=self.party_data["party_gold"],
            details=f"{self.player_name} withdrew gold"
        )

        self.convo.debug(f"{self.player_name} withdrew {amount}g. New total: {self.party_data['party_gold']}")
        self.convo.set_state(ConversationState.INTRODUCTION)
        return self.agent.shopkeeper_withdraw_success_prompt(amount, self.party_data["party_gold"])

    def handle_confirm_withdraw(self, player_input):
        match = re.search(r'\d+', player_input)
        if not match:
            return self.agent.shopkeeper_withdraw_gold_prompt()

        amount = int(match.group())
        current_gold = self.party_data.get("party_gold", 0)

        if amount > current_gold:
            return self.agent.shopkeeper_withdraw_insufficient_gold(amount, current_gold)

        self.party_data["party_gold"] -= amount
        update_party_gold(self.party_id, self.party_data["party_gold"])

        record_transaction(
            party_id=self.party_id,
            player_id=self.player_id,
            item_name=None,
            amount=-amount,
            action="WITHDRAW",
            balance_after=self.party_data["party_gold"],
            details=f"{self.player_name} withdrew gold"
        )

        self.convo.reset_state()
        return self.agent.shopkeeper_withdraw_success_prompt(amount, self.party_data["party_gold"])

    def _extract_amount(self, text):
        match = re.search(r'\b\d+\b', text)
        if match:
            return int(match.group())
        return None
