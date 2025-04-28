# app/shop_handlers/haggle_handler.py

import random
from app.conversation import ConversationState, PlayerIntent

class HaggleHandler:
    def __init__(self, agent, convo, party_data):
        self.agent = agent
        self.convo = convo
        self.party_data = party_data

    def attempt_haggle(self, item):
        if not item or item.get("base_price") is None:
            return self.agent.shopkeeper_generic_say("There's nothing to haggle over just yet.")

        can_haggle, reason = self.convo.can_attempt_haggle()
        if not can_haggle:
            return self.agent.shopkeeper_generic_say(reason)

        roll = random.randint(1, 20)
        curve = {
            10: 1, 11: 2, 12: 3, 13: 4, 14: 5,
            15: 7, 16: 9, 17: 12, 18: 15, 19: 18, 20: 20
        }

        if roll >= 10:
            # Success!
            discount_pct   = curve.get(roll, 0)
            discount_amt   = int(item["base_price"] * discount_pct / 100)
            discounted_cost = item["base_price"] - discount_amt

            # Store discount and switch to confirm state
            self.convo.set_discount(discounted_cost)
            self.convo.set_pending_action(PlayerIntent.BUY_CONFIRM)
            self.convo.record_haggle_attempt(success=True)
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            self.convo.save_state()

            # Now use the same buy_confirm prompt so "deal"/"yes" goes into handle_confirm_purchase
            return self.agent.shopkeeper_buy_confirm_prompt(item, self.party_data.get("party_gold", 0))

        else:
            # Failed haggle: no discount
            self.convo.record_haggle_attempt(success=False)
            return self.agent.shopkeeper_generic_say(
                f"You rolled a {roll} — no luck!  The price stays at {item['base_price']} gold."
            )
