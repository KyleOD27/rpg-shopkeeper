# app/agents/shopkeeper_agent.py

from app.models.items import get_all_items

class BaseShopkeeper:
    def shopkeeper_greeting(self, party_name: str, visit_count: int, player_name: str) -> str:
        if visit_count == 1:
            return f"Ah, {party_name} — first time in this shop? Nice to meet you, {player_name}."
        elif visit_count < 5:
            return f"{party_name} again? I think you might like it here, {player_name}."
        else:
            return f"Back already, {player_name}? I'm flattered. This is visit number {visit_count}!"

    def shopkeeper_intro_prompt(self) -> str:
        return (
            "Welcome to the RPG store. I handle BUY, SELL, HAGGLE, DEPOSIT, WITHDRAW, CHECK_BALANCE, and LEDGER actions."
        )

    def shopkeeper_fallback_prompt(self) -> str:
        item_names = [item["item_name"] for item in get_all_items()]
        return f"I’m not sure what you’re after, so here’s what we’ve got: {', '.join(item_names)}"

    def shopkeeper_confirmation_reply(self, item_name, item_cost, new_balance) -> str:
        return (
            f"Very well. The '{item_name}' is yours for {item_cost} gold. "
            f"You now have {new_balance} gold remaining."
        )

    def shopkeeper_clarify_item_prompt(self) -> str:
        item_names = [item["item_name"] for item in get_all_items()]
        return (
            f"I'm not sure which item you want. Here's what we have: {', '.join(item_names)}"
        )

    def shopkeeper_buy_confirm_prompt(self, item, player_gold) -> str:
        name = item.get("item_name") if isinstance(item, dict) else str(item)
        price = item.get("base_price") if isinstance(item, dict) else "???"
        return (
            f"Your current party balance is {player_gold} gold. "
            f"You want to buy {name} for {price} gold? "
            f"Say 'yes' to proceed."
        )

    def shopkeeper_buy_success_prompt(self, item, result_message) -> str:
        name = item.get("item_name") if isinstance(item, dict) else str(item)
        price = item.get("base_price") if isinstance(item, dict) else "???"
        return (
            f"You have just purchased a {name} for {price} gold. "
            f"I'll add it to the list."
        )

    def shopkeeper_buy_failure_prompt(self, item, result_message, player_gold) -> str:
        name = item.get("item_name") if isinstance(item, dict) else str(item)
        price = item.get("base_price") if isinstance(item, dict) else "???"
        return (
            f"Sorry, you can't afford the {name} which costs {price} gold. "
            f"You only have {player_gold}."
        )

    def shopkeeper_buy_cancel_prompt(self, item) -> str:
        name = item.get("item_name") if item and isinstance(item, dict) else None
        if not name:
            return "Changed your mind? No problem. Maybe next time."
        return f"So you don't want the {name}? As you wish."

    def shopkeeper_buy_enquire_item(self):
        return "Looking to buy something? Tell me what you're after — I've got potions, scrolls, and more!"
