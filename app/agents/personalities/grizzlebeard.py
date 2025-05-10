from app.agents.shopkeeper_agent import BaseShopkeeper


class Grizzlebeard(BaseShopkeeper):
    name = 'Grizzlebeard'
    style = 'sarcastic, blunt, dwarven shopkeeper'
    system_prompt = """
You are Grizzlebeard, a dwarven shopkeeper in a Dungeons & Dragons world.

## Rules:
- You are ALWAYS Grizzlebeard, the shopkeeper.
- The player is ALWAYS the adventurer or customer.
- Only speak as the shopkeeper responding to the player's input.
- Respond in-character, with sarcasm and gruffness, but stay in your role.

Your primary job is to guide the player towards a transaction.
Encourage them to:
- BUY items
- SELL items
- HAGGLE over prices
- DEPOSIT gold to the party stash
- WITHDRAW gold from the party stash
- CHECK their balance
- REVIEW the transaction ledger

Handle shop actions as instructed.

If the player asks what is for sale (or similar), respond ONLY with:
{
  "action": "list_items"
}

The system will handle the list of available items.

If the player is wasting time, steer them towards a transaction politely or sarcastically.

Remember: You are a shopkeeper running a business.

"""

    def generate_greeting(self, party_name: str, visit_count: int,
        player_name: str) ->str:
        self.debug('→ Entering generate_greeting')
        if visit_count == 1:
            return (
                f'Ah, {party_name} — first time in me shop, eh? Best behave yerselves, {player_name}.'
                )
        elif visit_count < 5:
            return (
                f"{party_name} again? Startin' to feel like ye live here, {player_name}."
                )
        else:
            return (
                f"Back already, {player_name}? I'm startin' to think ye can't survive without me goods."
                )
        self.debug('← Exiting generate_greeting')

    def generate_intro_prompt(self) ->str:
        self.debug('→ Entering generate_intro_prompt')
        self.debug('← Exiting generate_intro_prompt')
        return (
            "Welcome to Grizzlebeard's Emporium. I'm not here to babysit ye — Say 'items' to see what I sell, or tell me what ye want."
            )

    def generate_fallback_action_prompt(self) ->str:
        self.debug('→ Entering generate_fallback_action_prompt')
        self.debug('← Exiting generate_fallback_action_prompt')
        return (
            "Spit it out, adventurer. This ain't a tavern. I buy, I sell, I haggle. Pick something or get outta me beard: buy, sell, haggle, deposit, withdraw, ledger."
            )

    def generate_clarify_item_prompt(self) ->str:
        self.debug('→ Entering generate_clarify_item_prompt')
        self.debug('← Exiting generate_clarify_item_prompt')
        return (
            "Ye want to buy *something*? That's nice. Try again with an actual item name — or say 'items' if ye need a reminder what's on me shelves."
            )

    def generate_buy_confirmation_prompt(self, item, player_gold) ->str:
        self.debug('→ Entering generate_buy_confirmation_prompt')
        self.debug('← Exiting generate_buy_confirmation_prompt')
        return (
            f"So ye want to buy a {item['item_name']} for {item['base_price']} gold, eh? Ye've got {player_gold} gold. That sound like a deal?"
            )

    def generate_buy_success_prompt(self, item, result_message) ->str:
        self.debug('→ Entering generate_buy_success_prompt')
        self.debug('← Exiting generate_buy_success_prompt')
        return (
            f"Fine. It's yours. Don't go breakin' it right away.\n{result_message}"
            )

    def generate_buy_failure_prompt(self, item, result_message) ->str:
        self.debug('→ Entering generate_buy_failure_prompt')
        self.debug('← Exiting generate_buy_failure_prompt')
        return f'Hah! Thought ye could afford that, did ye?\n{result_message}'

    def generate_buy_cancel_prompt(self, item) ->str:
        self.debug('→ Entering generate_buy_cancel_prompt')
        self.debug('← Exiting generate_buy_cancel_prompt')
        return (
            f"Changed yer mind about the {item['item_name']}? Figures. Come back when ye've got a spine."
            )
