# app/agents/rpg_shop.py

from app.agents.base_agent import BaseAgent
from app.agents.shopkeeper_agent import shopkeeper_greeting

class RPGShop(BaseAgent):
    name = "RPGShop"
    style = "straight forward, and professional style"

    system_prompt = """
You are a shopkeeper in a Dungeons & Dragons world.
"""

    # === Static Prompts ===

    def rpgshop_generate_greeting(self, party_name: str, visit_count: int, player_name: str) -> str:
        if visit_count == 1:
            return f"Ah, {party_name} — first time in me shop, eh? Best behave yerselves, {player_name}."
        elif visit_count < 5:
            return f"{party_name} again? Startin' to feel like ye live here, {player_name}."
        else:
            return f"Back already, {player_name}? I'm startin' to think ye can't survive without me goods."

    def rpgshop_generate_intro_prompt(self) -> str:
        return (
            "Welcome to Grizzlebeard's Emporium. I'm not here to babysit ye — "
            "Say 'items' to see what I sell, or tell me what ye want."
        )

    def rpgshop_generate_fallback_action_prompt(self) -> str:
        return (
            "Spit it out, adventurer. This ain't a tavern. I buy, I sell, I haggle. "
            "Pick something or get outta me beard: buy, sell, haggle, deposit, withdraw, ledger."
        )

    # === Buy Item Prompts ===

    def rpgshop_generate_clarify_item_prompt(self) -> str:
        return (
            "Ye want to buy *something*? That's nice. Try again with an actual item name — "
            "or say 'items' if ye need a reminder what's on me shelves."
        )

    def rpgshop_generate_buy_confirmation_prompt(self, item, player_gold) -> str:
        return (
            f"So ye want to buy a {item['item_name']} for {item['base_price']} gold, eh? "
            f"Ye've got {player_gold} gold. That sound like a deal?"
        )

    def rpgshop_generate_buy_success_prompt(self, item, result_message) -> str:
        return (
            f"Fine. It's yours. Don't go breakin' it right away.\n{result_message}"
        )

    def rpgshop_generate_buy_failure_prompt(self, item, result_message) -> str:
        return (
            f"Hah! Thought ye could afford that, did ye?\n{result_message}"
        )

    def rpgshop_generate_buy_cancel_prompt(self, item) -> str:
        return (
            f"Changed yer mind about the {item['item_name']}? Figures. Come back when ye've got a spine."
        )
