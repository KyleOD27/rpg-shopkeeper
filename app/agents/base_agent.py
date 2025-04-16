# app/agents/base_agent.py
from app.agents.shopkeeper_agent import BaseShopkeeper


class BaseAgent:
    """
    All shop agents inherit from this.
    """

    def reply(self, message: str) -> str:
        raise NotImplementedError("Each agent must implement the reply method.")

    def generate_greeting(self, party_name: str, visit_count: int, player_name: str) -> str:
        raise NotImplementedError("Each agent must implement the generate_greeting method.")

    def generate_intro_prompt(self) -> str:
        """
        Generic fallback introduction prompt if the player is stuck.
        Can be overridden by specific agents.
        """
        return "Welcome to the shop. Ask for 'items' if you need help — or tell me what you're after."

    def generate_fallback_action_prompt(self) -> str:
        """
        Returns flavour text for when the player input was unclear or invalid.
        Can be overridden by specific agents.
        """
        return "Spit it out. Here's what I actually do around here: buy, sell, haggle, deposit, withdraw, ledger."