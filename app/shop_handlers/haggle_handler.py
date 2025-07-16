import random
from app.conversation import ConversationState, PlayerIntent
from app.utils.debug import HandlerDebugMixin
from app.db import record_haggle_attempt


class HaggleHandler(HandlerDebugMixin):

    def __init__(self, agent, convo, party_data, character_id):
        # wire up debug proxy before any debug() calls
        self.conversation = convo
        self.debug('→ Entering __init__')

        self.agent = agent
        self.convo = convo
        self.party_data = party_data
        self.character_id = character_id

        self.debug('← Exiting __init__')

    def attempt_haggle(self, item):
        from app.db import record_haggle_attempt, get_haggle_attempts_today
        from datetime import datetime, timedelta
        import random

        self.debug('→ Entering attempt_haggle')
        if not item or item.get('base_price_cp') is None:
            return self.agent.shopkeeper_generic_say(
                "There's nothing to haggle over just yet."
            )

        can_haggle, reason = self.convo.can_attempt_haggle()
        if not can_haggle:
            return self.agent.shopkeeper_generic_say(reason)

        character_id = getattr(self, "character_id", None)
        if isinstance(character_id, dict):
            character_id = character_id.get("id") or character_id.get("character_id")

        # 1. Get all attempts today for this character (any item)
        attempts = get_haggle_attempts_today(character_id)
        attempt_count = len(attempts)
        has_success = any('success' in row['result'] for row in attempts)

        # Ensure purchase confirmation is possible even after haggle limit
        def set_pending_buy():
            self.convo.set_pending_action(PlayerIntent.BUY_CONFIRM)
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            self.convo.save_state()

        if has_success:
            full_price_cp = item['base_price_cp']
            item_name = item['item_name']
            balance_cp = self.party_data.get('party_balance_cp', 0)
            set_pending_buy()
            return self.agent.shopkeeper_generic_say(
                f"😎 You've already had the best of me once today, no more deals 'til tomorrow!\n\n"
                f"The *{item_name}* still costs *{self.agent.format_gp_cp(full_price_cp)}*.\n\n"
                f"Your balance is *{self.agent.format_gp_cp(balance_cp)}*. Would you like to proceed with the purchase at full price?"
            )

        if attempt_count >= 3:
            full_price_cp = item['base_price_cp']
            item_name = item['item_name']
            balance_cp = self.party_data.get('party_balance_cp', 0)
            set_pending_buy()
            return self.agent.shopkeeper_generic_say(
                f"🙅‍♂️ That was your third and final haggle for today—no more haggling on any item 'til tomorrow!\n\n"
                f"The *{item_name}* still costs *{self.agent.format_gp_cp(full_price_cp)}*.\n\n"
                f"Your balance is *{self.agent.format_gp_cp(balance_cp)}*. Would you like to proceed with the purchase at full price?"
            )

        # Otherwise, allow a new attempt as normal
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
            # Flair for a win!
            return self.agent.shopkeeper_generic_say(
                f"🤑 _You rolled a *{roll}*!_\n\n"
                f"Alright, alright, you twisted my arm!\n\n"
                f"How about *{self.agent.format_gp_cp(discounted_cost_cp)}* for the *{item['item_name']}*?\n\n"
                f"Would you like to buy it at this new price?\n\n"
                f"Your balance: *{self.agent.format_gp_cp(self.party_data.get('party_balance_cp', 0))}*"
            )
        else:
            result = f"fail (roll {roll})"
            record_haggle_attempt(
                character_id=character_id,
                item_name=item['item_name'],
                die_roll=roll,
                result=result,
            )
            remaining_attempts = 3 - (attempt_count + 1)  # +1 for this attempt
            if remaining_attempts > 0:
                return self.agent.shopkeeper_generic_say(
                    f"😅 _You rolled a *{roll}*_\n"
                    f"Bad luck. You have {remaining_attempts} more haggle attempt{'s' if remaining_attempts > 1 else ''} today.\n"
                    f"The *{item['item_name']}* still costs *{self.agent.format_gp_cp(base_price_cp)}*."
                )
            else:
                # Final fail - offer to buy at full price, set confirmation state
                full_price_cp = item['base_price_cp']
                item_name = item['item_name']
                balance_cp = self.party_data.get('party_balance_cp', 0)
                set_pending_buy()
                return self.agent.shopkeeper_generic_say(
                    f"🙅‍♂️ _You rolled a *{roll}*_"
                    f" — that's your third attempt today!\n"
                    f"I'm not budging any more on price—try again tomorrow.\n\n"
                    f"The *{item_name}* still costs *{self.agent.format_gp_cp(full_price_cp)}*.\n\n"
                    f"Your balance is *{self.agent.format_gp_cp(balance_cp)}*. Would you like to proceed with the purchase at full price?"
                )

        self.debug('← Exiting attempt_haggle')








