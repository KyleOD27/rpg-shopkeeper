from app.models.items import get_all_items
from datetime import datetime


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
        items = get_all_items()
        if not items:
            return "Hmm… Looks like the shelves are bare right now!"

        lines = ["I'm not sure what you're after, so here's what we’ve got in stock:\n"]
        for item in items:
            name = dict(item).get("item_name", "Unknown Item")
            price = dict(item).get("base_price", "?")
            lines.append(f" • {name} — {price} gold")

        return "\n".join(lines)

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

    def shopkeeper_accept_thanks(self):
        return "No problem at all, thanks for your purchase!"

    def shopkeeper_show_ledger(self, ledger_entries: list) -> str:
        if not ledger_entries:
            return "Your ledger is empty. No purchases, sales, or deposits yet!"

        lines = ["Here's your transaction history:"]
        for entry in ledger_entries:
            e = dict(entry)
            timestamp = e.get("timestamp", "")[:16].replace("T", " ")
            player = e.get("player_name", "Unknown")
            item = e.get("item_name", "Something")
            gold = e.get("amount", 0)
            action = e.get("action", "ACTION")
            balance = e.get("balance_after", "?")
            lines.append(f" - {timestamp} | {player} | {action} '{item}' for {gold} gold (Balance: {balance})")

        return "\n".join(lines)

    def shopkeeper_sell_offer_prompt(self, item_name, price):
        return f"I’ll give you {price} gold for your {item_name}. Deal?"

    def shopkeeper_sell_success_prompt(self, item_name, amount) -> str:
        return f"Sold! I’ve taken the {item_name} and added {amount} gold to your pouch."

    def shopkeeper_sell_cancel_prompt(self, item_name):
        return f"Changed your mind about the {item_name}? No worries."

    def shopkeeper_deposit_gold_prompt(self):
        return "Stashing away some savings? How much gold shall I deposit for you?"

    def shopkeeper_deposit_success_prompt(self, amount, new_total):
        return f"Got it! {amount} gold safely stored in the vault. Your balance is now {new_total} gold."
