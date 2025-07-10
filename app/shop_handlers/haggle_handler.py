import random
from app.conversation import ConversationState, PlayerIntent
from app.utils.debug import HandlerDebugMixin
from app.db import record_haggle_attempt


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
        from app.db import record_haggle_attempt, get_last_haggle_attempt_time
        from datetime import datetime, timedelta
        import random

        self.debug('→ Entering attempt_haggle')
        if not item or item.get('base_price_cp') is None:
            return self.agent.shopkeeper_generic_say(
                "There's nothing to haggle over just yet.")

        can_haggle, reason = self.convo.can_attempt_haggle()
        if not can_haggle:
            return self.agent.shopkeeper_generic_say(reason)
        character_id = getattr(self, "player_id", None)

        last_attempt = get_last_haggle_attempt_time(character_id, item['item_name'])
        if last_attempt:
            now = datetime.now()
            midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            remaining = midnight - now
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes = remainder // 60
            hour_part = f"{hours} hour{'s' if hours != 1 else ''}" if hours else ""
            minute_part = f"{minutes} minute{'s' if minutes != 1 else ''}" if minutes else ""
            joiner = " and " if hours and minutes else ""
            wait_text = f"{hour_part}{joiner}{minute_part}"
            return self.agent.shopkeeper_generic_say(
                f"You've already tried haggling for this item today! Try again in {wait_text or 'less than a minute'}."
            )

        roll = random.randint(1, 20)
        curve = {10: 1, 11: 2, 12: 3, 13: 4, 14: 5, 15: 7, 16: 9, 17: 12, 18: 15, 19: 18, 20: 20}
        base_price_cp = item['base_price_cp']

        if roll >= 10:
            discount_pct = curve.get(roll, 0)
            discount_amt = int(base_price_cp * discount_pct / 100)
            discounted_cost_cp = base_price_cp - discount_amt
            self.convo.set_discount(discounted_cost_cp)
            self.convo.set_pending_action(PlayerIntent.BUY_CONFIRM)

            result = f"success (roll {roll}, -{discount_pct}%, {discount_amt} cp off)"
            record_haggle_attempt(
                character_id=character_id,
                item_name=item['item_name'],
                die_roll=roll,
                result=result,
            )

            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            self.convo.save_state()
            return self.agent.shopkeeper_buy_confirm_prompt(item, self.party_data.get('party_balance_cp', 0),
                                                            discount=discounted_cost_cp)
        else:
            result = f"fail (roll {roll})"
            record_haggle_attempt(
                character_id=character_id,
                item_name=item['item_name'],
                die_roll=roll,
                result=result,
            )
            return self.agent.shopkeeper_generic_say(
                f"You rolled a {roll} — no luck!  The price stays at {self.agent.format_gp_cp(base_price_cp)}."
            )
        self.debug('← Exiting attempt_haggle')




