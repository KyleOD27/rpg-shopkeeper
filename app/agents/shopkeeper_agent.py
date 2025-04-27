from app.conversation import ConversationState
from app.models.items import (
    get_all_items,
    get_all_equipment_categories,
    get_weapon_categories,
    get_armour_categories,
    get_gear_categories,
    get_tool_categories,
    get_items_by_armour_category, get_items_by_weapon_category
)
from app.interpreter import normalize_input
from datetime import datetime

# --- Safe field normalizer ---
def safe_normalized_field(item, field_name):
    if not item:
        return ""
    value = dict(item).get(field_name)
    if value and isinstance(value, str):
        return normalize_input(value)
    return ""

class BaseShopkeeper:
    # --- Shop Greeting ---
    def shopkeeper_greeting(self, party_name: str, visit_count: int, player_name: str) -> str:
        if visit_count == 1:
            return f"Ah, {party_name} — first time in this shop? Nice to meet you, {player_name}."
        elif visit_count < 5:
            return f"{party_name} again? I think you might like it here, {player_name}."
        else:
            return f"Back already, {player_name}? I'm flattered. This is visit number {visit_count}!"

    # --- Category Menus ---
    def shopkeeper_view_items_prompt(self) -> str:
        categories = get_all_equipment_categories()
        lines = ["Here’s what I can offer by category:\n"]
        for cat in categories:
            lines.append(f" • {cat}")
        lines.append("\nJust say the category name to see what’s inside.")
        return "\n".join(lines)

    def shopkeeper_list_weapon_categories(self, categories):
        return self.show_weapon_category_menu(categories)

    def shopkeeper_list_armour_categories(self, categories):
        return self.show_armor_category_menu(categories)

    def shopkeeper_list_gear_categories(self, categories):
        lines = "\n • " + "\n • ".join(categories)
        return f"🎒 Gear types we carry:\n{lines}\n\nTell me which one to show!"

    def show_weapon_category_menu(self, categories):
        lines = "\n • " + "\n • ".join(categories)
        return f"⚔️ Looking for something specific? Weapon types:\n{lines}\n\nJust say one to browse."

    def show_armor_category_menu(self, categories):
        lines = "\n • " + "\n • ".join(categories)
        return f"🛡️ Protective gear available:\n{lines}\n\nPick one to browse."

    # --- Inventory Filtering ---
    def _filter_items_by_category(self, field, category_value):
        return [
            dict(item) for item in get_all_items()
            if safe_normalized_field(item, field) == normalize_input(category_value)
        ]

    def _paginate(self, items, page, page_size=5):
        total_items = len(items)
        total_pages = max((total_items + page_size - 1) // page_size, 1)
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        end = start + page_size
        return items[start:end], page, total_pages

    # --- Item Viewers ---
    def _show_items(self, player_input, field, emoji, label):
        category_value = player_input.get(field.replace("_category", ""))
        if not category_value:
            return "⚠️ I didn't quite catch which category you meant. Try saying it again?"

        page = player_input.get("page", 1)
        filtered_items = self._filter_items_by_category(field, category_value)
        page_items, page, total_pages = self._paginate(filtered_items, page)

        if not page_items:
            return f"Hmm... looks like we don't have any **{category_value}** {label.lower()} in stock right now."

        lines = [f"{emoji} **{category_value.title()} {label} (Page {page} of {total_pages})**\n"]
        for item in page_items:
            name = item.get("item_name", "Unknown Item")
            price = item.get("base_price", "?")
            lines.append(f" • {name} — {price} gold")

        if page < total_pages:
            lines.append("\nSay **next** to see more.")
        if page > 1:
            lines.append("Say **previous** to go back.")

        return "\n".join(lines)

    def shopkeeper_show_items_by_category(self, player_input):
        return self._show_items(player_input, field="equipment_category", emoji="📦", label="Items")

    def shopkeeper_show_items_by_weapon_category(self, player_input):
        weapon_category = player_input.get("weapon_category")
        page = player_input.get("page", 1)

        if not weapon_category:
            return "⚠️ I didn't quite catch which weapon type you meant. Try saying it again?"

        items = get_items_by_weapon_category(weapon_category, page, page_size=5)

        if not items:
            return f"Hmm... looks like we don't have any **{weapon_category}** armour in stock right now."

        lines = [f"⚔️ **{weapon_category.title()} Armour (Page {page})**\n"]
        for item in items:
            name = item["item_name"]
            price = item["base_price"]
            lines.append(f" • {name} — {price} gold")

        if len(items) == 5:
            lines.append("\nSay **next** to see more.")
        if page > 1:
            lines.append("Say **previous** to go back.")

        return "\n".join(lines)

    def shopkeeper_show_items_by_armour_category(self, player_input):
        armour_category = player_input.get("armour_category")
        page = player_input.get("page", 1)

        if not armour_category:
            return "⚠️ I didn't quite catch which armour type you meant. Try saying it again?"

        items = get_items_by_armour_category(armour_category, page, page_size=5)

        if not items:
            return f"Hmm... looks like we don't have any **{armour_category}** armour in stock right now."

        lines = [f"🛡️ **{armour_category.title()} Armour (Page {page})**\n"]
        for item in items:
            name = item["item_name"]
            price = item["base_price"]
            lines.append(f" • {name} — {price} gold")

        if len(items) == 5:
            lines.append("\nSay **next** to see more.")
        if page > 1:
            lines.append("Say **previous** to go back.")

        return "\n".join(lines)

    def shopkeeper_show_items_by_gear_category(self, player_input):
        return self._show_items(player_input, field="gear_category", emoji="🎒", label="Gear")

    def shopkeeper_show_items_by_tool_category(self, player_input):
        return self._show_items(player_input, field="tool_category", emoji="🛠️", label="Tools")

    # --- Thanks ---
    def shopkeeper_accept_thanks(self) -> str:
        return "No problem at all, thanks for being you!"

    # --- Banking / Ledger / Misc ---
    def shopkeeper_deposit_gold_prompt(self) -> str:
        return "Stashing away some savings? How much gold shall I deposit for you?"

    def shopkeeper_withdraw_gold_prompt(self) -> str:
        return "Taking some coin out? How much would you like to withdraw?"

    def shopkeeper_check_balance_prompt(self, gold_amount: int) -> str:
        return f"Your party currently holds {gold_amount} gold."

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

    def shopkeeper_pending_item_reminder(self, pending_item):
        return (
            f"⚠️ Hold on! You were about to buy **{pending_item}**. "
            "Let's finish that first! (Say 'yes' to confirm or 'no' to cancel.)"
        )

    # --- NEW: Category Access Wrappers ---
    def get_weapon_categories(self):
        return get_weapon_categories()

    def get_armour_categories(self):
        return get_armour_categories()

    def get_gear_categories(self):
        return get_gear_categories()

    def get_tool_categories(self):
        return get_tool_categories()

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

    def shopkeeper_buy_confirm_prompt(self, item_name, player_gold):
        return (
            f"You're looking to buy **{item_name}**.\n"
            f"You currently have {player_gold} gold.\n"
            "Would you like to proceed? (Say 'yes' or 'no')"
        )

    def shopkeeper_generic_say(self, message):
        return message

    def shopkeeper_buy_success_prompt(self, item, cost):
        item_name = item.get("item_name", "the item")
        return f"✅ You successfully bought **{item_name}** for **{cost}** gold! Enjoy!"

    def shopkeeper_clarify_item_prompt(self):
        return "⚠️ What would you like to buy? Please tell me the item name."

    def shopkeeper_buy_enquire_item(self):
        return "🛒 Sure, what exactly would you like to buy? Name the item and I'll fetch it!"

    def shopkeeper_deposit_success_prompt(self, amount, new_total):
        return f"💰 You deposited **{amount}** gold! Your new party balance is **{new_total}** gold."

    def shopkeeper_withdraw_success_prompt(self, amount, new_total):
        return f"🏦 You withdrew **{amount}** gold! Your new party balance is **{new_total}** gold."
