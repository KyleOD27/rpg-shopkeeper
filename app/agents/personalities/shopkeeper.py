# app/agents/personalities/shopkeeper.py

from app.agents.shopkeeper_agent import BaseShopkeeper

class Shopkeeper(BaseShopkeeper):
    name = "RPG Shop"

    def shopkeeper_greeting(self, party_name, visit_count, player_name):
        return (
            f"Welcome back, {player_name}! The {party_name} are always welcome at the RPG Shop. "
            f"This is visit number {visit_count} — let’s make it count!"
        )
