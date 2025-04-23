from app.conversation import ConversationState
from app.models.items import get_all_items, get_items_by_category, get_all_equipment_categories
from app.interpreter import get_equipment_category_from_input
from datetime import datetime

class BaseShopkeeper:
    def shopkeeper_greeting(self, party_name: str, visit_count: int, player_name: str) -> str:
        if visit_count == 1:
            return f"Ah, {party_name} — first time in this shop? Nice to meet you, {player_name}."
        elif visit_count < 5:
            return f"{party_name} again? I think you might like it here, {player_name}."
        else:
            return f"Back already, {player_name}? I'm flattered. This is visit number {visit_count}!"

    def shopkeeper_fallback_prompt(self) -> str:
        return (
            "This is what I can do for you:\n"
            "BUY – I have items available to purchase\n"
            "SELL – Sell me unwanted goods\n"
            "DEPOSIT - Top up your party balance\n"
            "WITHDRAW – Take back deposited gold\n"
            "BALANCE – See your party balance\n"
            "LEDGER – See our trade history\n"
            "ITEMS – See what we have in stock\n"
        )

    def shopkeeper_confirmation_reply(self, item_name, item_cost, new_balance) -> str:
        return (
            f"Very well. The '{item_name}' is yours for {item_cost} gold. "
            f"You now have {new_balance} gold remaining."
        )

    def shopkeeper_clarify_item_prompt(self) -> str:
        items = get_all_items()
        if not items:
            return "Ah, it seems the shelves are bare!"

        categories = sorted(set(dict(item).get("equipment_category", "Misc") for item in items))
        lines = ["Ah, so you want to BUY something! Here's what we have in stock:\n"]
        for cat in categories:
            lines.append(f" • {cat}")
        return "\n".join(lines)

    def shopkeeper_show_items_by_category(self, player_input):
        category = player_input.get("category")
        page = player_input.get("page", 1)
        page_size = 5

        all_items = [dict(item) for item in get_all_items() if
                     dict(item).get("equipment_category", "").lower() == category.lower()]
        total_items = len(all_items)
        total_pages = max((total_items + page_size - 1) // page_size, 1)

        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        end = start + page_size
        page_items = all_items[start:end]

        if not page_items:
            return f"Hmm... looks like we don't have anything in the **{category}** category right now."

        lines = [f"📦 **{category.title()} Items (Page {page} of {total_pages})**\n"]
        for item in page_items:
            name = item.get("item_name", "Unknown Item")
            price = item.get("base_price", "?")
            lines.append(f" • {name} — {price} gold")

        if page < total_pages:
            lines.append("\nSay **next** to see more.")
        if page > 1:
            lines.append("Say **previous** to go back.")

        return "\n".join(lines)

    def shopkeeper_buy_confirm_prompt(self, item, player_gold) -> str:
        name = item.get("item_name") if isinstance(item, dict) else str(item)
        price = item.get("base_price") if isinstance(item, dict) else "???"
        return (
            f"Your current party balance is {player_gold} gold. "
            f"You want to buy {name} for {price} gold? "
            f"Say 'yes' to proceed."
        )

    def shopkeeper_buy_success_prompt(self, item, price_paid) -> str:
        name = item.get("item_name") if isinstance(item, dict) else str(item)
        base_price = item.get("base_price", price_paid)
        note = f" (discounted from {base_price}g!)" if price_paid < base_price else ""
        return f"You have just purchased a {name} for {price_paid} gold{note}. I'll add it to the ledger."

    def shopkeeper_buy_failure_prompt(self, item, result_message, player_gold) -> str:
        name = item.get("item_name") if isinstance(item, dict) else str(item)
        price = item.get("base_price") if isinstance(item, dict) else "???"
        return (
            f"Sorry, you can't afford the {name} which costs {price} gold. "
            f"You only have {player_gold}."
        )

    def shopkeeper_buy_cancel_prompt(self, item) -> str:
        name = item.get("item_name") if item and isinstance(item, dict) else None
        return f"So you don't want the {name}? As you wish." if name else "Changed your mind? No problem. Maybe next time."

    def shopkeeper_buy_enquire_item(self):
        item_names = [item["item_name"] for item in get_all_items()]
        display_items = ', '.join(item_names[:5])
        if len(item_names) > 5:
            display_items += ", and more..."
        return f"Ah so you want to BUY something! Here's what I have on offer: {display_items}"

    def shopkeeper_accept_thanks(self):
        return "No problem at all, thanks for being you!"

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

    def shopkeeper_sell_offer_prompt(self, item, offer_price):
        name = item.get("name") or item.get("title") or item.get("item_name", "item")
        return f"I’ll give you {offer_price} gold for your {name}. Deal?"

    def shopkeeper_sell_success_prompt(self, item, amount) -> str:
        name = item.get("name") or item.get("title") or item.get("item_name", "item")
        return f"Sold! I’ve taken the {name} and added {amount} gold to your party balance."

    def shopkeeper_sell_cancel_prompt(self, item_name):
        return f"Changed your mind about the {item_name}? No worries."

    def shopkeeper_deposit_gold_prompt(self):
        return "Stashing away some savings? How much gold shall I deposit for you?"

    def shopkeeper_deposit_success_prompt(self, amount, new_total):
        return f"Got it! {amount} gold safely stored in the vault. Your balance is now {new_total} gold."

    def shopkeeper_withdraw_gold_prompt(self):
        return "Taking some coin out? How much would you like to withdraw?"

    def shopkeeper_withdraw_success_prompt(self, amount, new_total):
        return f"Done! {amount} gold withdrawn. Your balance is now {new_total} gold."

    def shopkeeper_withdraw_insufficient_gold(self, requested, available):
        return f"Sorry, you only have {available} gold — not enough to withdraw {requested}."

    def shopkeeper_withdraw_insufficient_funds_prompt(self, amount, current_gold):
        return f"Sorry, you tried to withdraw {amount} gold but only have {current_gold}. Try a smaller amount?"

    def shopkeeper_check_balance_prompt(self, gold_amount: int):
        return f"Your party currently holds {gold_amount} gold."

    def shopkeeper_view_items_prompt(self):
        categories = get_all_equipment_categories()
        lines = ["Here’s what I can offer by category:\n"]
        for cat in categories:
            lines.append(f" • {cat}")
        lines.append("\nJust say the category name to see what’s inside.")
        return "\n".join(lines)

    def shopkeeper_sell_enquire_item(self):
        item_names = [item["item_name"] for item in get_all_items()]
        display_items = ', '.join(item_names[:5])
        if len(item_names) > 5:
            display_items += ", and more..."
        return f"Ah so you want to SELL something! Here's what I accept: {display_items}"

    def shopkeeper_generic_say(self, text):
        return text
