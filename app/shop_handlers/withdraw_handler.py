from app.conversation import ConversationState, PlayerIntent
from app.models.ledger import record_transaction
from app.models.parties import update_party_balance_cp
import re
from app.utils.debug import HandlerDebugMixin


class WithdrawHandler(HandlerDebugMixin):

    def __init__(self, convo, agent, party_id, character_id, player_name,
                 party_data):
        # wire up debug proxy before any debug() calls
        self.conversation = convo
        self.debug('→ Entering __init__')

        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.character_id = character_id
        self.player_name = player_name
        self.party_data = party_data

        self.debug('← Exiting __init__')


    def process_withdraw_balance_cp_flow(self, player_input):
        self.debug('→ Entering process_withdraw_balance_cp_flow')
        raw_text = player_input['text'] if isinstance(player_input, dict
            ) else player_input
        lowered = raw_text.lower()
        amount = self._extract_amount(lowered)
        if amount is None:
            self.convo.debug('Withdraw amount missing — asking for it.')
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            self.convo.set_intent(PlayerIntent.WITHDRAW_NEEDS_AMOUNT)
            return self.agent.shopkeeper_withdraw_balance_cp_prompt()
        current_balance_cp = self.party_data.get('party_balance_cp', 0)
        if amount > current_balance_cp:
            return self.agent.shopkeeper_withdraw_insufficient_balance_cp(amount,
                current_balance_cp)
        self.party_data['party_balance_cp'] -= amount
        update_party_balance_cp(self.party_id, self.party_data['party_balance_cp'])
        record_transaction(party_id=self.party_id, character_id=self.
            character_id, item_name=None, amount=-amount, action='WITHDRAW',
            balance_after=self.party_data['party_balance_cp'], details=
            f'{self.player_name} withdrew balance_cp')
        self.convo.debug(
            f"{self.player_name} withdrew {amount}g. New total: {self.party_data['party_balance_cp']}"
            )
        self.convo.set_state(ConversationState.INTRODUCTION)
        self.debug('← Exiting process_withdraw_balance_cp_flow')
        return self.agent.shopkeeper_withdraw_success_prompt(amount, self.
            party_data['party_balance_cp'])

    def handle_confirm_withdraw(self, player_input):
        self.debug('→ Entering handle_confirm_withdraw')
        raw_text = player_input['text'] if isinstance(player_input, dict
            ) else player_input
        match = re.search('\\d+', raw_text)
        if not match:
            return self.agent.shopkeeper_withdraw_balance_cp_prompt()
        amount = int(match.group())
        current_balance_cp = self.party_data.get('party_balance_cp', 0)
        if amount > current_balance_cp:
            return self.agent.shopkeeper_withdraw_insufficient_balance_cp(amount,
                current_balance_cp)
        self.party_data['party_balance_cp'] -= amount
        update_party_balance_cp(self.party_id, self.party_data['party_balance_cp'])
        record_transaction(party_id=self.party_id, character_id=self.
            character_id, item_name=None, amount=-amount, action='WITHDRAW',
            balance_after=self.party_data['party_balance_cp'], details=
            f'{self.player_name} withdrew balance_cp')
        self.convo.reset_state()
        self.debug('← Exiting handle_confirm_withdraw')
        return self.agent.shopkeeper_withdraw_success_prompt(amount, self.
            party_data['party_balance_cp'])

    def _extract_amount(self, text):
        self.debug('→ Entering _extract_amount')
        match = re.search('\\b\\d+\\b', text)
        if match:
            return int(match.group())
        self.debug('← Exiting _extract_amount')
        return None
