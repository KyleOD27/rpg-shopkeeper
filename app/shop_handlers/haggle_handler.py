import random
from app.conversation import ConversationState


class HaggleHandler:
    def __init__(self, agent, convo, party_data):
        self.agent = agent
        self.convo = convo
        self.party_data = party_data

    def attempt_haggle(self, player_input):
        item = player_input
        if not item:
            return self.agent.shopkeeper_generic_say("There's nothing to haggle over just yet.")

        can_haggle, reason = self.convo.can_attempt_haggle()
        if not can_haggle:
            return self.agent.shopkeeper_generic_say(reason)

        roll = random.randint(1, 20)

        # Discount curve: 10–20 maps to 1–20%
        curve = {
            10: 1,
            11: 2,
            12: 3,
            13: 4,
            14: 5,
            15: 7,
            16: 9,
            17: 12,
            18: 15,
            19: 18,
            20: 20
        }

        if roll >= 10:
            discount_percent = curve.get(roll, 0)
            discount_amount = int(item["base_price"] * (discount_percent / 100))
            discounted_price = item["base_price"] - discount_amount

            self.convo.set_discount(discounted_price)
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            self.convo.record_haggle_attempt(success=True)

            return self.agent.shopkeeper_generic_say(
                f"You rolled a {roll} — success! "
                f"I'll knock off {discount_percent}%.\n"
                f"That brings the price down to {discounted_price} gold. Deal?"
            )

        else:
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            self.convo.record_haggle_attempt(success=False)

            return self.agent.shopkeeper_generic_say(
                f"You rolled a {roll} — no luck! "
                f"The price stays at {item['base_price']} gold."
            )
