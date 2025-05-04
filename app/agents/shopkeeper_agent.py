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
    search_items_by_name_fuzzy,
    get_items_by_weapon_range
)
from app.interpreter import normalize_input
from datetime import datetime, timedelta


# --- Safe field normalizer ---
def safe_normalized_field(item, field_name):
    if not item:
        return ""
    value = dict(item).get(field_name)
    if value and isinstance(value, str):
        return normalize_input(value)
    return ""

# ─── utility ────────────────────────────────────────────────
def join_lines(*parts: str) -> str:
    return "\n".join(p.strip() for p in parts if p).rstrip()
# ────────────────────────────────────────────────────────────

class BaseShopkeeper:
    # --- Shop Greeting ---
    def shopkeeper_greeting(self, party_name: str, visit_count: int,
                            player_name: str) -> str:
        if visit_count == 1:
            return join_lines(
                f"Ah, {player_name} of {party_name}.",
                "First time at this shop? Nice to meet you.",
                "To see what I can do just say *menu*."
            )
        elif visit_count < 5:
            return join_lines(
                f"{party_name} again?",
                f"I think you might like it here, {player_name}."
            )
        else:
            return join_lines(
                f"Back already, {player_name}?",
                f"I'm flattered—this is visit number {visit_count}!"
            )

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
        items = [dict(itm) for itm in get_all_items()]
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
        """
        Build the weapon-menu using item['category_range'] instead of
        item['weapon_category'].

        `categories` should now be the distinct list of category_range
        strings you pulled from the DB, e.g.:
            ['simple melee', 'simple ranged', 'martial melee', 'martial ranged']
        """
        # ── 1. count items per category_range ─────────────────────────
        counts = {cat: 0 for cat in categories}
        for itm in items:
            cat = (itm.get("category_range") or "").lower()
            if cat in counts:
                counts[cat] += 1

        # ── 2. render menu ────────────────────────────────────────────
        lines = ["⚔️ Looking for something specific? Weapon groups:"]
        for cat in categories:
            pretty = cat.title()  # capitalise nicely
            lines.append(f"• {pretty} ({counts[cat]} items)")

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

    from datetime import datetime, timedelta

    from datetime import datetime, timedelta

    def shopkeeper_show_ledger(self, ledger_entries: list) -> str:
        if not ledger_entries:
            return "Your ledger is empty—no purchases, sales, or deposits yet!"

        def humanize(ts_str: str) -> str:
            try:
                ts_utc = datetime.fromisoformat(ts_str)
            except Exception:
                return ts_str

            now_local = datetime.now()
            offset = now_local - datetime.utcnow()
            ts_local = ts_utc + offset
            delta = now_local - ts_local

            if delta < timedelta(seconds=60):
                return "just now"
            if delta < timedelta(hours=1):
                mins = int(delta.total_seconds() // 60)
                return f"{mins} minute{'s' if mins != 1 else ''} ago"
            if delta < timedelta(hours=24):
                hrs = int(delta.total_seconds() // 3600)
                return f"{hrs} hour{'s' if hrs != 1 else ''} ago"

            # beyond 24h, format like “Wed 5th at 9:00 am”
            def ordinal(n: int) -> str:
                if 10 <= n % 100 <= 20:
                    suf = "th"
                else:
                    suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
                return f"{n}{suf}"

            weekday = ts_local.strftime("%a")  # e.g. “Wed”
            day = ordinal(ts_local.day)  # e.g. “5th”
            time = ts_local.strftime("%I:%M %p").lstrip("0").lower()  # “9:00 am”
            return f"{weekday} {day} at {time}"

        lines = ["📜 Transaction History:"]
        for idx, entry in enumerate(ledger_entries, start=1):
            e = dict(entry)
            ts_human = humanize(e.get("timestamp", ""))
            player = e.get("player_name", "Someone")
            action = e.get("action", "").lower()
            item = e.get("item_name", "")
            amount = e.get("amount", 0)
            balance = e.get("balance_after", "?")

            # Verb and what
            if action in ("buy", "bought"):
                verb = "bought"
                what = f"{item} for {amount} gp"
            elif action in ("sell", "sold"):
                verb = "sold"
                what = f"{item} for {amount} gp"
            elif action == "deposit":
                verb = "deposited"
                what = f"{amount} gp"
            elif action == "withdraw":
                verb = "withdrew"
                what = f"{amount} gp"
            else:
                verb = action or "did something with"
                what = f"{item} for {amount} gp" if item else f"{amount} gp"

            lines.append(
                f"{idx}. ({ts_human}) {player} {verb} {what}."
            )

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
            "Here's what I can help you with:\n\n"
            "🛒 BUY – I have items available to purchase\n"
            "📦 SELL – Sell me unwanted goods\n"
            "💰 DEPOSIT – Top up your party balance\n"
            "💸 WITHDRAW – Take back deposited gold\n"
            "🪙 BALANCE – See your party balance\n"
            "📚 LEDGER – See our trade history\n"
            "📋 BROWSE – See what we have in stock\n"
            "🔎 INSPECT – See specific item details\n"
        )

    def shopkeeper_buy_confirm_prompt(self, item, party_gold, discount=None):
        # ── price block ─────────────────────────────────────────
        base = item.get("base_price", 0)
        cost = discount if discount is not None else base
        saved = base - cost if discount is not None else 0
        discount_note = f" (you saved {saved} gp!)" if saved > 0 else ""

        name = item.get("item_name", "Unknown Item")
        cat = item.get("equipment_category", "")
        rar = item.get("rarity", "")
        lines = [
            f"You're about to buy a {name} ({cat}, {rar}).",
            f"💰 Price: {cost} gp{discount_note}",
            f"⚖️ Weight: {item.get('weight', 0)} lb",
        ]

        # ── description (if any) ───────────────────────────────
        if item.get("desc"):
            lines.append(f"📜 {item['desc']}")

        # ── weapon extras ──────────────────────────────────────
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

        # ── armour extras ──────────────────────────────────────
        if cat.lower() == "armor" or item.get("armour_category"):
            armour_cat = item.get("armour_category", "Unknown")
            lines.append(f"🛡️ Category: {armour_cat}")

            # base AC & Dex rules
            ac = item.get("base_ac")
            if ac is not None:
                dex_bonus = item.get("dex_bonus")  # 0 / 1 / None
                max_bonus = item.get("max_dex_bonus")
                ac_line = f"🛡️ Base AC: {ac}"
                if dex_bonus:  # Dex allowed
                    if max_bonus:
                        ac_line += f" + Dex mod (max {max_bonus})"
                    else:
                        ac_line += " + Dex mod"
                lines.append(ac_line)

            # strength req (ignore 0 / None)
            str_min = item.get("str_minimum")
            if str_min:
                lines.append(f"💪 Requires STR {str_min}")

            # stealth
            if item.get("stealth_disadvantage"):
                lines.append("🥷 Disadvantage on Stealth checks")

        # ── balance + confirmation prompt ──────────────────────
        lines.extend([
            f"🎒 Party balance: {party_gold} gp",
            "",
            "Would you like to proceed? (yes ✅ / no ❌)"
        ])

        return "\n".join(lines)

    def shopkeeper_generic_say(self, message):
        return message

    def shopkeeper_buy_success_prompt(self, item, cost):
        item_name = item.get("item_name", "the item")
        return (f"Okay that will be *{cost}* gold..."
                f"Here you go, this is now yours *{item_name}*."
                f"Enjoy!")

    def shopkeeper_deposit_success_prompt(self, amount, new_total):
        return f" You deposited *{amount}* gold! Party balance is now *{new_total}* gold."

    def shopkeeper_withdraw_success_prompt(self, amount, new_total):
        return f"You withdrew *{amount}* gold! Party balance is now *{new_total}* gold."

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
            lines.append(f" • [{item_id}] *{name}*. Costs *{price}* gold")

        lines.append("\n Just say the name or number to buy.. or would you like to see the full inventory?")
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

    # --- Profile Viewer ---
    def shopkeeper_show_profile(self, party_data: dict) -> str:
        """
        Pretty print the player's profile / party info.
        Only uses keys that already exist in `party_data`,
        so it’s safe even if some are missing.
        """
        name        = party_data.get("player_name",  "Unknown Adventurer")
        party_name  = party_data.get("party_name",   "Unnamed Party")
        gold        = party_data.get("party_gold",   0)
        visits      = party_data.get("visit_count",  1)
        members     = party_data.get("party_members") or party_data.get("members") or []
        lvl         = party_data.get("level")
        klass       = party_data.get("class") or party_data.get("character_class")

        lines = [
            f"🪪 *Profile for {name}*",
            f"🛡️ Party: {party_name}",
            f"👥 Members: {', '.join(members) if members else 'Just you so far'}",
            f"💰 Gold on hand: {gold}",
            f"🏪 Visits to this shop: {visits}",
        ]
        if lvl is not None:
            lines.append(f"✨ Level: {lvl}")
        if klass:
            lines.append(f"⚔️ Class: {klass}")

        return "\n".join(lines)

    # --- User-account overview ----------------------------------------
    def shopkeeper_show_account(self, acct: dict) -> str:
        lines = [
            f"👤 username: {acct['user_name']}",
            f"📱 phone: {acct['phone_number']}",
            f"💎 tier: {acct['subscription_tier']}",
            f" ",
            f"*owned characters:*",
        ]
        for idx, ch in enumerate(acct["characters"], start=1):
            nm  = ch["character_name"] or ch["player_name"]
            pty = ch["party_name"]
            lines.append(f"{idx}.Name: {nm}. Party: {pty})")
        lines.append("\nReply with character number for more details.")
        return "\n".join(lines)

    # --- Single-character detail --------------------------------------
    def shopkeeper_show_character(self, ch: dict) -> str:
        nm = ch["character_name"] or ch["player_name"]
        lines = [
            f"🪪 *Character: {nm}*",
            f"🙍 Player name: {ch['player_name']}",
            f"🛡️ Party: {ch['party_name']}",
            f"🎭 Role: {ch['role'] or 'N/A'}",
        ]
        return "\n".join(lines)

    def shopkeeper_show_items_by_weapon_range(self, player_input):
        """
        Display weapons filtered by category_range
        (e.g. 'martial melee', 'simple ranged').
        """
        cat_range = player_input.get("category_range")
        page      = int(player_input.get("page", 1))
        if not cat_range:
            return "⚠️ I didn’t catch which weapon group you meant."
        rows = get_items_by_weapon_range(cat_range, page, page_size=5)
        if not rows:
            return f"Hmm… looks like we don’t have any **{cat_range.title()}** weapons in stock right now."
        # total pages for the nav prompt
        total = get_items_by_weapon_range(cat_range, 1, 9999)
        total_pages = max(1, (len(total) + 4) // 5)
        header = f"⚔️ {cat_range.title()} Weapons (Page {page} of {total_pages})\n"
        body = [ f" • [{r['item_id']}] {r['item_name']} — {r['base_price']} gp"
            for r in map(dict, rows) ]
        if page < total_pages:
            body.append("\nSay **next** to see more.")
        if page > 1:
            body.append("Say **previous** to go back.")
        return header + "\n".join(body)