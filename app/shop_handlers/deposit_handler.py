from app.conversation import ConversationState, PlayerIntent
from app.models.ledger import record_transaction
from app.models.parties import update_party_gold
import re
from app.utils.debug import HandlerDebugMixin


class DepositHandler(HandlerDebugMixin):

    def __init__(self, convo, agent, party_id, character_id, player_name,
                 party_data):
        # wire up debug proxy before any debug() calls
        self.conversation = convo
        self.debug('→ Entering __init__')

        # keep the old reference if you still use it elsewhere
        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.character_id = character_id
        self.player_name = player_name
        self.party_data = party_data

        self.debug('← Exiting __init__')


    def process_deposit_gold_flow(self, player_input):
        self.debug('→ Entering process_deposit_gold_flow')
        text = player_input['text'] if isinstance(player_input, dict) else str(
            player_input)
        lowered = text.lower()
        amount = self._extract_amount(lowered)
        if amount is None:
            self.convo.debug('Deposit amount missing — asking for it.')
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            self.convo.set_intent(PlayerIntent.DEPOSIT_NEEDS_AMOUNT)
            return self.agent.shopkeeper_deposit_gold_prompt()
        party_gold = self.party_data.get('party_gold', 0)
        new_total = party_gold + amount
        self.party_data['party_gold'] = new_total
        update_party_gold(self.party_id, new_total)
        record_transaction(party_id=self.party_id, character_id=self.
            character_id, item_name=None, amount=amount, action='DEPOSIT',
            balance_after=new_total, details=
            f'{self.player_name} deposited gold')
        self.convo.debug(
            f'{self.player_name} deposited {amount}g. New total: {new_total}')
        self.convo.set_state(ConversationState.INTRODUCTION)
        self.debug('← Exiting process_deposit_gold_flow')
        return self.agent.shopkeeper_deposit_success_prompt(amount, new_total)

    def _extract_amount(self, text):
        self.debug('→ Entering _extract_amount')
        match = re.search('\\b\\d+\\b', text)
        if match:
            return int(match.group())
        self.debug('← Exiting _extract_amount')
        return None

    def handle_confirm_deposit(self, player_input):
        self.debug('→ Entering handle_confirm_deposit')
        text = player_input['text'] if isinstance(player_input, dict) else str(
            player_input)
        match = re.search('\\d+', text)
        if not match:
            return self.agent.shopkeeper_deposit_gold_prompt()
        amount = int(match.group())
        self.party_data['party_gold'] += amount
        update_party_gold(self.party_id, self.party_data['party_gold'])
        new_total = self.party_data['party_gold']
        record_transaction(party_id=self.party_id, character_id=self.
            character_id, item_name=None, amount=amount, action='DEPOSIT',
            balance_after=new_total, details=
            f'{self.player_name} deposited gold')
        self.convo.reset_state()
        self.debug('← Exiting handle_confirm_deposit')
        return self.agent.shopkeeper_deposit_success_prompt(amount, new_total)

    def handle_confirm_withdraw(self, player_input):
        self.debug('→ Entering handle_confirm_withdraw')
        text = player_input['text'] if isinstance(player_input, dict) else str(
            player_input)
        match = re.search('\\d+', text)
        if not match:
            return self.agent.shopkeeper_withdraw_gold_prompt()
        amount = int(match.group())
        current_gold = self.party_data.get('party_gold', 0)
        if amount > current_gold:
            return self.agent.shopkeeper_withdraw_insufficient_funds_prompt(
                amount, current_gold)
        self.party_data['party_gold'] -= amount
        update_party_gold(self.party_id, self.party_data['party_gold'])
        record_transaction(party_id=self.party_id, character_id=self.
            character_id, item_name=None, amount=amount, action='WITHDRAW',
            balance_after=self.party_data['party_gold'], details=
            f'{self.player_name} withdrew gold')
        self.convo.reset_state()
        self.debug('← Exiting handle_confirm_withdraw')
        return self.agent.shopkeeper_withdraw_success_prompt(amount, self.
            party_data['party_gold'])
