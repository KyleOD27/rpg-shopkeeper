import random
from app.conversation import ConversationState

MAX_DISCOUNT_PERCENT = 20

class HaggleHandler:
    def __init__(self, agent, convo, party_data):
        self.agent = agent
        self.convo = convo
        self.party_data = party_data

    def attempt_haggle(self, item):
        roll = random.randint(1, 20)

        if roll >= 15:
            discount_percent = random.randint(1, MAX_DISCOUNT_PERCENT)
            discount_amount = int(item["base_price"] * (discount_percent / 100))
            discounted_price = item["base_price"] - discount_amount

            self.convo.set_discount(discounted_price)
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)

            return (
                f"You rolled a {roll} — success! "
                f"I'll knock off {discount_percent}%.\n"
                f"That brings the price down to {discounted_price} gold. Deal?"
            )

        else:
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            return (
                f"You rolled a {roll} — no luck! "
                f"The price stays at {item['base_price']} gold."
            )
