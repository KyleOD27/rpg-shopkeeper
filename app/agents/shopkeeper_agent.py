from app.conversation import ConversationState
from app.models.items import (
    get_all_items,
    get_all_equipment_categories,
    get_weapon_categories,
    get_armour_categories,
    get_gear_categories,
    get_tool_categories,
    get_items_by_armour_category, get_items_by_weapon_category, get_items_by_gear_category, get_items_by_tool_category,
    get_items_by_mount_category,
    search_items_by_name_fuzzy
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
        items = get_all_items()

        # Map emoji per category
        emoji_map = {
            "Armor": "🛡️",
            "Weapons": "🗡️",
            "Weapon": "🗡️",
            "Adventuring Gear": "🎒",
            "Tools": "🧰",
            "Mounts and Vehicles": "🐎",
        }

        # Count items per category
        category_counts = {cat: 0 for cat in categories}
        for item in items:
            category = item["equipment_category"]
            if category in category_counts:
                category_counts[category] += 1

        lines = ["🧙‍♂️ What can I interest you in today, adventurer?\n"]
        for cat in categories:
            emoji = emoji_map.get(cat, "📦")
            count = category_counts.get(cat, 0)
            lines.append(f"{emoji} {cat} ({count} items)")

        lines.append("\n💬 Just say the category name to see what’s in stock!")
        return "\n".join(lines)


    def shopkeeper_list_weapon_categories(self, categories):
        items = [dict(item) for item in get_all_items()]
        return self.show_weapon_category_menu(categories, items)

    def shopkeeper_list_armour_categories(self, categories):
        items = [dict(item) for item in get_all_items()]
        return self.show_armor_category_menu(categories, items)

    def shopkeeper_list_gear_categories(self, categories):
        items = [dict(item) for item in get_all_items()]
        return self.show_gear_category_menu(categories, items)

    def shopkeeper_list_tool_categories(self, categories):
        items = [dict(item) for item in get_all_items()]
        return self.show_tool_category_menu(categories, items)

    def show_weapon_category_menu(self, categories, items):
        counts = {cat: 0 for cat in categories}
        for item in items:
            cat = item["weapon_category"]
            if cat in counts:
                counts[cat] += 1

        lines = [
            "⚔️ Looking for something specific? Weapon types:"
        ]
        for cat in categories:
            lines.append(f"• {cat} ({counts[cat]} items)")

        lines.append("\nJust say one to browse.")
        return "\n".join(lines)

    def show_armor_category_menu(self, categories, items):
        # Count how many items per armour subcategory
        counts = {cat: 0 for cat in categories}
        for item in items:
            cat = item["armour_category"]
            if cat in counts:
                counts[cat] += 1

        lines = [
            "🛡️ Protective gear available:"
        ]
        for cat in categories:
            lines.append(f"• {cat} ({counts[cat]} items)")

        lines.append("\nPick one to browse.")
        return "\n".join(lines)

    def show_gear_category_menu(self, categories, items):
        counts = {cat: 0 for cat in categories}
        for item in items:
            cat = item["gear_category"]
            if cat in counts:
                counts[cat] += 1

        lines = [
            "🎒 Gear types available:"
        ]
        for cat in categories:
            lines.append(f"• {cat} ({counts[cat]} items)")

        lines.append("\nPick one to browse.")
        return "\n".join(lines)

    def show_tool_category_menu(self, categories, items):
        counts = {cat: 0 for cat in categories}
        for item in items:
            cat = item["tool_category"]
            if cat in counts:
                counts[cat] += 1

        lines = [
            "🧰 Tool types available:"
        ]
        for cat in categories:
            lines.append(f"• {cat} ({counts[cat]} items)")

        lines.append("\nPick one to browse.")
        return "\n".join(lines)

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
            return self.shopkeeper_view_items_prompt()

        page = player_input.get("page", 1)
        filtered_items = self._filter_items_by_category(field, category_value)
        page_items, page, total_pages = self._paginate(filtered_items, page)

        # 🛠 If no category items found, try fuzzy search instead
        if not page_items:
            matching_items = self.search_items_by_name(category_value)
            if matching_items:
                lines = [f"🔎 **Search Results for '{category_value.title()}'**\n"]
                for item in matching_items:
                    name = item.get("item_name", "Unknown Item")
                    price = item.get("base_price", "?")
                    lines.append(f" • {name} — {price} gold")
                return "\n".join(lines)

            return f"Hmm... looks like we don't have anything matching **{category_value}** right now."

        # ✅ Normal item list
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

        # ➡️ Normal paginated results
        rows = get_items_by_weapon_category(weapon_category, page, page_size=5)

        if not rows:
            return f"Hmm... looks like we don't have any **{weapon_category}** weapons in stock right now."

        all_rows = get_items_by_weapon_category(weapon_category, page=1, page_size=9999)
        total_pages = max(1, (len(all_rows) + 4) // 5)

        lines = [f"⚔️ {weapon_category.title()} Weapons (Page {page} of {total_pages})\n"]
        for row in rows:

            item = dict(row)
            item_id = item.get("item_id", "?")
            name = item.get("item_name", "Unknown Item")
            price = item.get("base_price", "?")
            lines.append(f" • [{item_id}] {name} — {price} gold")

        if page < total_pages:
            lines.append("\nSay next to see more.")
        if page > 1:
            lines.append("Say previous to go back.")

        return "\n".join(lines)

    def shopkeeper_show_items_by_armour_category(self, player_input):
        armour_category = player_input.get("armour_category")
        page = player_input.get("page", 1)

        if not armour_category:
            return "⚠️ I didn't quite catch which armour type you meant. Try saying it again?"

        # ➡️ Paginated page
        rows = get_items_by_armour_category(armour_category, page, page_size=5)

        if not rows:
            return f"Hmm... looks like we don't have any **{armour_category}** armour in stock right now."

        # 🔥 Fetch all items to calculate total pages
        all_rows = get_items_by_armour_category(armour_category, page=1, page_size=9999)
        total_pages = max(1, (len(all_rows) + 4) // 5)

        lines = [f"🛡️ {armour_category.title()} Armour (Page {page} of {total_pages})\n"]
        for row in rows:
            item = dict(row)  # convert Row → dict
            item_id = item.get("item_id", "?")
            name = item.get("item_name", "Unknown Item")
            price = item.get("base_price", "?")
            lines.append(f" • [{item_id}] {name} — {price} gold")

        if page < total_pages:
            lines.append("\nSay next to see more.")
        if page > 1:
            lines.append("Say previous to go back.")

        return "\n".join(lines)

    def shopkeeper_show_items_by_gear_category(self, player_input):
        gear_category = player_input.get("gear_category")
        page = player_input.get("page", 1)

        if not gear_category:
            return "⚠️ I didn't quite catch which gear type you meant. Try saying it again?"

        # ➡️ Paginated fetch
        rows = get_items_by_gear_category(gear_category, page, page_size=5)

        if not rows:
            return f"Hmm... looks like we don't have any {gear_category} gear in stock right now."

        # 🔥 Fetch all to compute pages
        all_rows = get_items_by_gear_category(gear_category, page=1, page_size=9999)
        total_pages = max(1, (len(all_rows) + 4) // 5)

        lines = [f"🎒 **{gear_category.title()} Gear (Page {page} of {total_pages})**\n"]
        for row in rows:
            item = dict(row)  # sqlite3.Row → dict
            item_id = item.get("item_id", "?")
            name = item.get("item_name", "Unknown Item")
            price = item.get("base_price", "?")
            lines.append(f" • [{item_id}] {name} — {price} gold")

        if page < total_pages:
            lines.append("\nSay next to see more.")
        if page > 1:
            lines.append("Say previous to go back.")

        return "\n".join(lines)

    def shopkeeper_show_items_by_tool_category(self, player_input):
        tool_category = player_input.get("tool_category")
        page = player_input.get("page", 1)

        if not tool_category:
            return "⚠️ I didn't catch which tool type you meant. Try that again?"

        # ➡️ Paginated fetch
        rows = get_items_by_tool_category(tool_category, page, page_size=5)

        if not rows:
            return f"Hmm... looks like we don't have any {tool_category} tools in stock right now."

        # 🔥 Fetch all to compute total pages
        all_rows = get_items_by_tool_category(tool_category, page=1, page_size=9999)
        total_pages = max(1, (len(all_rows) + 4) // 5)

        lines = [f"🧰 {tool_category.title()} Tools (Page {page} of {total_pages})\n"]
        for row in rows:
            item = dict(row)  # sqlite3.Row → dict
            item_id = item.get("item_id", "?")
            name = item.get("item_name", "Unknown Item")
            price = item.get("base_price", "?")
            lines.append(f" • [{item_id}] {name} — {price} gold")

        if page < total_pages:
            lines.append("\nSay next to see more.")
        if page > 1:
            lines.append("Say previous to go back.")

        return "\n".join(lines)

    def shopkeeper_show_items_by_mount_category(self, player_input):
        page = player_input.get("page", 1)

        # fetch paginated rows
        rows = get_items_by_mount_category("Mounts and Vehicles", page=page, page_size=5)
        if not rows:
            return "Hmm... looks like we don't have any mounts or vehicles in stock right now."

        # fetch all to calculate total pages
        all_rows = get_items_by_mount_category("Mounts and Vehicles", page=1, page_size=9999)
        total_pages = max(1, (len(all_rows) + 4) // 5)

        lines = [f"🏇 Mounts & Vehicles (Page {page} of {total_pages})\n"]
        for row in rows:
            item = dict(row)  # sqlite3.Row → dict
            item_id = item.get("item_id", "?")
            name = item.get("item_name", "Unknown Item")
            price = item.get("base_price", "?")
            lines.append(f" • [{item_id}] {name} — {price} gold")

        if page < total_pages:
            lines.append("\nSay next to see more.")
        if page > 1:
            lines.append("Say previous to go back.")

        return "\n".join(lines)

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

    # --- NEW: Category Access Wrappers ---
    def get_equipment_categories(self):
        return get_all_equipment_categories()

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
            "📜 Here's what I can help you with:\n\n"
            "🛒 BUY – I have items available to purchase\n"
            "📦 SELL – Sell me unwanted goods\n"
            "💰 DEPOSIT – Top up your party balance\n"
            "💸 WITHDRAW – Take back deposited gold\n"
            "🪙 BALANCE – See your party balance\n"
            "📚 LEDGER – See our trade history\n"
            "📋 BROWSE – See what we have in stock\n"
        )

    def shopkeeper_buy_confirm_prompt(self, item, party_gold, discount=None):
        # pick the right cost
        base = item.get("base_price", 0)
        cost = discount if discount is not None else base
        saved = base - cost if discount is not None else 0

        discount_note = f" (you saved {saved}g!)" if saved > 0 else ""
        name = item.get("item_name", "Unknown Item")
        cat = item.get("equipment_category", "")
        rar = item.get("rarity", "")

        lines = [
            f"🛒 You're about to buy a {name} ({cat}, {rar}).",
            f"💰 Price: {cost} gold{discount_note} | ⚖️ Weight: {item.get('weight', 0)} lbs",
        ]

        # 📜 Description
        if item.get("desc"):
            lines.append(f"📜 {item['desc']}")

        # ⚔️ Weapon stats
        if item.get("damage_dice"):
            dmg_type = item.get("damage_type", "")
            lines.append(f"⚔️ Damage: {item['damage_dice']} {dmg_type}".strip())

        if item.get("weapon_range"):
            lines.append(f"🎯 Weapon Range: {item['weapon_range']}")

        if item.get("range_normal"):
            span = f"{item['range_normal']} ft"
            if item.get("range_long"):
                span += f" / {item['range_long']} ft"
            lines.append(f"📏 Range: {span}")

        # 🎒 Your gold + confirm prompt
        lines.append(f"🎒 Your gold: {party_gold}")
        lines.append("")  # blank line before the question
        lines.append("Would you like to proceed? (Say yes ✅ or no ❌)")

        return "\n".join(lines)

    def shopkeeper_generic_say(self, message):
        return message

    def shopkeeper_buy_success_prompt(self, item, cost):
        item_name = item.get("item_name", "the item")
        return (f"✅ You successfully "
                f"bought a {item_name} for {cost}🪙 gold! Enjoy!")

    def shopkeeper_deposit_success_prompt(self, amount, new_total):
        return f" You deposited {amount}🪙 gold! Party balance is now {new_total} gold. ️💰"

    def shopkeeper_withdraw_success_prompt(self, amount, new_total):
        return f"You withdrew {amount}🪙 gold! Party balance is now {new_total} gold. 💸"

    def search_items_by_name(self, query, page=1):
        query = normalize_input(query)
        rows = search_items_by_name_fuzzy(query, page=page)
        return [dict(row) for row in rows] if rows else []

    def shopkeeper_list_matching_items(self, matching_items):
        if isinstance(matching_items, dict):
            matching_items = [matching_items]

        lines = ["🔎 Here's what I found:"]

        for item in matching_items:
            item_id = item.get("item_id", "?")
            name = item.get("item_name", "Unknown Item")
            price = item.get("base_price", "?")
            lines.append(f" • [{item_id}] {name} — {price} gold")

        lines.append("\n I like to be sure, just say the item number of the item you'd like to buy!")
        return "\n".join(lines)

    def shopkeeper_say(self, text):
        return text

    def shopkeeper_farewell(self):
        return "Safe travels, adventurer! Come back soon. 🌟"

    # After (matching the call)
    def shopkeeper_buy_failure_prompt(self, item, message, party_gold):
        """
        item: the item dict the player tried to buy
        message: a short error message or reason
        party_gold: the player's current gold total
        """
        item_name = item.get("item_name", "that item")
        return (
            f"{message} You have {party_gold} gp but the {item_name} costs "
            f"{item.get('base_price', 0)} gp."
        )

    def shopkeeper_inspect_item_prompt(self, lines: list[str]) -> str:
        """
        Turn the list of emoji-rich lines from InspectHandler
        into one block of text to send back to the user.
        """
        return "\n".join(lines)






