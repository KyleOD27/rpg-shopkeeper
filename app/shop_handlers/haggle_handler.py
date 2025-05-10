import random
from app.conversation import ConversationState, PlayerIntent
from app.utils.debug import HandlerDebugMixin


class HaggleHandler(HandlerDebugMixin):

    def __init__(self, agent, convo, party_data):
        # wire up debug proxy before any debug() calls
        self.conversation = convo
        self.debug('→ Entering __init__')

        self.agent = agent
        self.convo = convo
        self.party_data = party_data

        self.debug('← Exiting __init__')


    def attempt_haggle(self, item):
        self.debug('→ Entering attempt_haggle')
        if not item or item.get('base_price') is None:
            return self.agent.shopkeeper_generic_say(
                "There's nothing to haggle over just yet.")
        can_haggle, reason = self.convo.can_attempt_haggle()
        if not can_haggle:
            return self.agent.shopkeeper_generic_say(reason)
        roll = random.randint(1, 20)
        curve = {(10): 1, (11): 2, (12): 3, (13): 4, (14): 5, (15): 7, (16):
            9, (17): 12, (18): 15, (19): 18, (20): 20}
        if roll >= 10:
            discount_pct = curve.get(roll, 0)
            discount_amt = int(item['base_price'] * discount_pct / 100)
            discounted_cost = item['base_price'] - discount_amt
            self.convo.set_discount(discounted_cost)
            self.convo.set_pending_action(PlayerIntent.BUY_CONFIRM)
            self.convo.record_haggle_attempt(success=True)
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            self.convo.save_state()
            return self.agent.shopkeeper_buy_confirm_prompt(item, self.
                party_data.get('party_gold', 0))
        else:
            self.convo.record_haggle_attempt(success=False)
            return self.agent.shopkeeper_generic_say(
                f"You rolled a {roll} — no luck!  The price stays at {item['base_price']} gold."
                )
        self.debug('← Exiting attempt_haggle')
