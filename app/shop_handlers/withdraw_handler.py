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

    CURRENCY_CP = {
        "cp": 1,
        "sp": 10,
        "ep": 50,
        "gp": 100,
        "pp": 1000
    }

    CURRENCY_ALIASES = {
        "cp": "cp", "copper": "cp",
        "sp": "sp", "silver": "sp",
        "ep": "ep", "electrum": "ep",
        "gp": "gp", "gold": "gp",
        "pp": "pp", "platinum": "pp",
    }

    def process_withdraw_balance_cp_flow(self, player_input):
        self.debug('→ Entering process_withdraw_balance_cp_flow')
        raw_text = player_input['text'] if isinstance(player_input, dict) else player_input
        lowered = raw_text.lower()

        # Extract amount and currency (defaulting to cp)
        amount, currency = self._extract_amount_and_currency(lowered)
        if amount is None:
            self.convo.debug('Withdraw amount missing — asking for it.')
            self.convo.set_state(ConversationState.AWAITING_WITHDRAW_AMOUNT)  # <--- correct state!
            self.convo.set_intent(PlayerIntent.WITHDRAW_NEEDS_AMOUNT)
            self.convo.save_state()
            return self.agent.shopkeeper_withdraw_balance_cp_prompt()

        # You could prompt for invalid currency, but defaulting to cp is fine

        amount_cp = amount * self.CURRENCY_CP[currency]
        current_balance_cp = self.party_data.get('party_balance_cp', 0)

        if amount_cp > current_balance_cp:
            return self.agent.shopkeeper_withdraw_insufficient_balance_cp(amount_cp, current_balance_cp)

        self.party_data['party_balance_cp'] -= amount_cp
        update_party_balance_cp(self.party_id, self.party_data['party_balance_cp'])
        record_transaction(
            party_id=self.party_id,
            character_id=self.character_id,
            item_name=None,
            amount=-amount_cp,
            action='WITHDRAW',
            balance_after=self.party_data['party_balance_cp'],
            details=f'{self.player_name} withdrew {amount} {currency} ({amount_cp} cp)'
        )
        self.convo.debug(
            f"{self.player_name} withdrew {amount} {currency}. New total: {self.party_data['party_balance_cp']}"
        )
        self.convo.set_state(ConversationState.INTRODUCTION)
        self.debug('← Exiting process_withdraw_balance_cp_flow')
        return self.agent.shopkeeper_withdraw_success_prompt(amount_cp, self.party_data['party_balance_cp'])


    def handle_confirm_withdraw(self, player_input):
        self.debug('→ Entering handle_confirm_withdraw')
        raw_text = player_input['text'] if isinstance(player_input, dict) else player_input
        amount, currency = self._extract_amount_and_currency(raw_text.lower())
        if amount is None:
            return self.agent.shopkeeper_withdraw_balance_cp_prompt()
        amount_cp = amount * self.CURRENCY_CP[currency]
        current_balance_cp = self.party_data.get('party_balance_cp', 0)
        if amount_cp > current_balance_cp:
            return self.agent.shopkeeper_withdraw_insufficient_balance_cp(amount_cp, current_balance_cp)
        self.party_data['party_balance_cp'] -= amount_cp
        update_party_balance_cp(self.party_id, self.party_data['party_balance_cp'])
        record_transaction(
            party_id=self.party_id,
            character_id=self.character_id,
            item_name=None,
            amount=-amount_cp,
            action='WITHDRAW',
            balance_after=self.party_data['party_balance_cp'],
            details=f'{self.player_name} withdrew {amount} {currency} ({amount_cp} cp)'
        )
        self.convo.reset_state()
        self.debug('← Exiting handle_confirm_withdraw')
        return self.agent.shopkeeper_withdraw_success_prompt(amount_cp, self.party_data['party_balance_cp'])

    def _extract_amount(self, text):
        self.debug('→ Entering _extract_amount')
        match = re.search('\\b\\d+\\b', text)
        if match:
            return int(match.group())
        self.debug('← Exiting _extract_amount')
        return None

    def _extract_amount_and_currency(self, lowered):
        m = re.search(r'(\d+)\s*(cp|copper|sp|silver|ep|electrum|gp|gold|pp|platinum)?', lowered)
        if not m:
            return None, None
        amount = int(m.group(1))
        currency_raw = m.group(2)
        if not currency_raw:
            # No currency specified: default to cp, or handle as you wish
            return amount, "cp"
        # Now check if it's a recognized currency
        currency = self.CURRENCY_ALIASES.get(currency_raw)
        if not currency:
            # Currency was given, but not recognized!
            return amount, None
        return amount, currency
