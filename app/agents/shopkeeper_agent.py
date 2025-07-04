from locale import currency

from app.conversation import ConversationState
from app.models.items import get_all_items, get_all_equipment_categories, get_weapon_categories, get_armour_categories, \
    get_gear_categories, get_tool_categories, get_items_by_armour_category, get_items_by_weapon_category, \
    get_items_by_gear_category, get_items_by_tool_category, get_items_by_mount_category, search_items_by_name_fuzzy, \
    get_items_by_weapon_range, get_treasure_categories, get_items_by_treasure_category
from app.interpreter import normalize_input
from datetime import datetime, timedelta
from collections import defaultdict
from app.utils.debug import HandlerDebugMixin
from app.conversation import Conversation  # for type clarity (optional)

def safe_normalized_field(item, field_name):
    if not item:
        return ''
    value = dict(item).get(field_name)
    if value and isinstance(value, str):
        return normalize_input(value)
    return ''


def join_lines(*parts: str) ->str:
    return '\n'.join(p.strip() for p in parts if p).rstrip()


class BaseShopkeeper(HandlerDebugMixin):
    def __init__(self, conversation: Conversation):
        self.conversation = conversation

    def shopkeeper_greeting(self, party_name: str, visit_count: int, player_name: str) -> str:
        # entry trace
        self.debug('→ Entering shopkeeper_greeting')

        # pick the correct message
        if visit_count == 1:
            msg = join_lines(
                f'Ah, {player_name} of {party_name}.',
                'First time at this shop? Nice to meet you.',
                '',
                'To get started, just say _menu_'
            )
        elif visit_count < 5:
            msg = join_lines(
                f'{party_name} again?',
                f'I think you might like it here, {player_name}.'
            )
        else:
            msg = join_lines(
                f"Back already, {player_name}? I'm flattered, this is visit {visit_count}!",
                '',
                'What can I do for you today?'
            )

        # exit trace
        self.debug('← Exiting shopkeeper_greeting')
        return msg

    def shopkeeper_view_items_prompt(self) ->str:
        self.debug('→ Entering shopkeeper_view_items_prompt')
        categories = get_all_equipment_categories()
        items = get_all_items()
        emoji_map = {'Armor': '🛡️', 'Weapons': '🗡️', 'Weapon': '🗡️',
            'Adventuring Gear': '🎒', 'Tools': '🧰', 'Mounts and Vehicles': '🐎', 'Treasure': '💎'}
        category_counts = {cat: (0) for cat in categories}
        for item in items:
            category = item['equipment_category']
            if category in category_counts:
                category_counts[category] += 1
        lines = ["Okay, here's what I have..\n"]
        for cat in categories:
            emoji = emoji_map.get(cat, '📦')
            count = category_counts.get(cat, 0)
            lines.append(f'{emoji} {cat} _({count} items)_')
        lines.append('\nJust say the category name to see what’s in stock!')
        self.debug('← Exiting shopkeeper_view_items_prompt')
        return '\n'.join(lines)

    def shopkeeper_list_weapon_categories(self, categories):
        self.debug('→ Entering shopkeeper_list_weapon_categories')
        items = [dict(itm) for itm in get_all_items()]
        self.debug('← Exiting shopkeeper_list_weapon_categories')
        return self.show_weapon_category_menu(categories, items)

    def shopkeeper_list_armour_categories(self, categories):
        self.debug('→ Entering shopkeeper_list_armour_categories')
        items = [dict(item) for item in get_all_items()]
        self.debug('← Exiting shopkeeper_list_armour_categories')
        return self.show_armor_category_menu(categories, items)

    def shopkeeper_list_gear_categories(self, categories):
        self.debug('→ Entering shopkeeper_list_gear_categories')
        items = [dict(item) for item in get_all_items()]
        self.debug('← Exiting shopkeeper_list_gear_categories')
        return self.show_gear_category_menu(categories, items)

    def shopkeeper_list_tool_categories(self, categories):
        self.debug('→ Entering shopkeeper_list_tool_categories')
        items = [dict(item) for item in get_all_items()]
        self.debug('← Exiting shopkeeper_list_tool_categories')
        return self.show_tool_category_menu(categories, items)

    def shopkeeper_list_treasure_categories(self, categories):
        self.debug('→ Entering shopkeeper_list_treasure_categories')
        items = [dict(item) for item in get_all_items()]
        self.debug('← Exiting shopkeeper_list_treasure_categories')
        return self.show_treasure_category_menu(categories, items)

    def show_weapon_category_menu(self, categories, items):
        self.debug('→ Entering show_weapon_category_menu')
        """
        Show weapon types sorted by the cheapest item (by base_price_cp) in each category_range.
        """

        # Build a dict of category → list of base_price_cp values
        category_prices = {cat: [] for cat in categories}
        for itm in items:
            cat = (itm.get('category_range') or '').lower()
            if cat in category_prices:
                try:
                    price_cp = int(itm.get('base_price_cp', 0))
                    category_prices[cat].append(price_cp)
                except (ValueError, TypeError):
                    pass  # ignore bad data

        # Build a sorted list of categories by min price
        sorted_categories = sorted(
            category_prices.items(),
            key=lambda kv: min(kv[1]) if kv[1] else float('inf')
        )

        lines = ['⚔️ What type of weapon are you looking for?', ' ']
        for cat, prices in sorted_categories:
            pretty = cat.title()
            count = len(prices)
            if count > 0:
                lines.append(f'• {pretty} ({count} items)')
        lines.append('\nJust say one to browse.')
        self.debug('← Exiting show_weapon_category_menu')
        return '\n'.join(lines)

    def show_armor_category_menu(self, categories, items):
        self.debug('→ Entering show_armor_category_menu')

        # Step 1: Collect price_cp values for each category
        category_prices = {cat: [] for cat in categories}
        for item in items:
            cat = item.get('armour_category')
            if cat in category_prices:
                try:
                    price_cp = int(item.get('base_price_cp', 0))
                    category_prices[cat].append(price_cp)
                except (TypeError, ValueError):
                    pass

        # Step 2: Sort categories by their minimum price
        sorted_categories = sorted(
            category_prices.items(),
            key=lambda kv: min(kv[1]) if kv[1] else float('inf')
        )

        # Step 3: Build output lines
        lines = ['🛡️ Protective gear available:', ' ']
        for cat, prices in sorted_categories:
            count = len(prices)
            if count > 0:
                lines.append(f'• {cat} ({count} items)')
        lines.append('\nPick one to browse.')

        self.debug('← Exiting show_armor_category_menu')
        return '\n'.join(lines)

    def show_gear_category_menu(self, categories, items):
        self.debug('→ Entering show_gear_category_menu')

        # Step 1: Build a dict of gear_category → list of prices
        category_prices = {cat: [] for cat in categories}
        for item in items:
            cat = item.get('gear_category')
            if cat in category_prices:
                try:
                    price_cp = int(item.get('base_price_cp', 0))
                    category_prices[cat].append(price_cp)
                except (TypeError, ValueError):
                    pass

        # Step 2: Sort categories by minimum price
        sorted_categories = sorted(
            category_prices.items(),
            key=lambda kv: min(kv[1]) if kv[1] else float('inf')
        )

        # Step 3: Format output
        lines = ['🎒 Gear types available:', ' ']
        for cat, prices in sorted_categories:
            count = len(prices)
            if count > 0:
                lines.append(f'• {cat} ({count} items)')
        lines.append('\nPick one to browse.')

        self.debug('← Exiting show_gear_category_menu')
        return '\n'.join(lines)

    def show_tool_category_menu(self, categories, items):
        self.debug('→ Entering show_tool_category_menu')

        # Step 1: Gather price_cp for each tool category
        category_prices = {cat: [] for cat in categories}
        for item in items:
            cat = item.get('tool_category')
            if cat in category_prices:
                try:
                    price_cp = int(item.get('base_price_cp', 0))
                    category_prices[cat].append(price_cp)
                except (TypeError, ValueError):
                    pass

        # Step 2: Sort categories by lowest price
        sorted_categories = sorted(
            category_prices.items(),
            key=lambda kv: min(kv[1]) if kv[1] else float('inf')
        )

        # Step 3: Build output
        lines = ['🧰 Tool types available:', ' ']
        for cat, prices in sorted_categories:
            count = len(prices)
            if count > 0:
                lines.append(f'• {cat} ({count} items)')
        lines.append('\nPick one to browse.')

        self.debug('← Exiting show_tool_category_menu')
        return '\n'.join(lines)

    def show_treasure_category_menu(self, categories, items):
        self.debug('→ Entering show_treasure_category_menu')

        # Step 1: Map treasure category → list of prices
        category_prices = {cat: [] for cat in categories}
        for item in items:
            cat = item.get('treasure_category')
            if cat in category_prices:
                try:
                    price_cp = int(item.get('base_price_cp', 0))
                    category_prices[cat].append(price_cp)
                except (TypeError, ValueError):
                    pass

        # Step 2: Sort by min price_cp
        sorted_categories = sorted(
            category_prices.items(),
            key=lambda kv: min(kv[1]) if kv[1] else float('inf')
        )

        # Step 3: Format the menu
        lines = ['💎 Treasure types available:', '']
        for cat, prices in sorted_categories:
            count = len(prices)
            if count > 0:
                lines.append(f'• {cat} ({count} items)')
        lines.append('\nPick one to browse.')

        self.debug('← Exiting show_treasure_category_menu')
        return '\n'.join(lines)

    def _filter_items_by_category(self, field, category_value):
        self.debug('→ Entering _filter_items_by_category')
        self.debug('← Exiting _filter_items_by_category')
        return [dict(item) for item in get_all_items() if 
            safe_normalized_field(item, field) == normalize_input(
            category_value)]

    def _paginate(self, items, page, page_size=5):
        self.debug('→ Entering _paginate')
        total_items = len(items)
        total_pages = max((total_items + page_size - 1) // page_size, 1)
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        end = start + page_size
        self.debug('← Exiting _paginate')
        return items[start:end], page, total_pages

    def _add_navigation_lines(
            self,
            lines: list[str],
            page: int,
            total_pages: int,
            *,
            include_buy_prompt: bool = False
    ) -> None:
        """
        Appends the standard paging hints (and, optionally, the “buy by id”
        prompt) to *lines*.

        ─ page / total_pages are the same values you already have.
        ─ include_buy_prompt=True adds the “Give the item _id_ to buy!” line.
        """
        # spacer only when at least one nav message will appear
        if page < total_pages or page > 1:
            lines.append('')

        if page < total_pages:
            lines.append('Say _next_ to see more.')
        if page > 1:
            lines.append('Say _previous_ to go back.')

        if include_buy_prompt:
            lines.append('Just say the item *id* or *name* if you are interested..')

    def _show_items(self, player_input, field, emoji, label):
        self.debug('→ Entering _show_items')
        category_value = player_input.get(field.replace('_category', ''))
        if not category_value:
            return self.shopkeeper_view_items_prompt()
        page = player_input.get('page', 1)
        filtered_items = self._filter_items_by_category(field, category_value)
        page_items, page, total_pages = self._paginate(filtered_items, page)
        if not page_items:
            matching_items = self.search_items_by_name(category_value)
            if matching_items:
                lines = [
                    f"🔎 **Search Results for '{category_value.title()}'**\n"]
                for item in matching_items:
                    name = item.get('item_name', 'Unknown Item')
                    price = item.get('base_price', '?')
                    price_unit = item.get('price_unit', '?')
                    price_cp = item.get('base_price_cp', '?')
                    lines.append(f" • {name} — {price} {price_unit} ({price_cp} CP)")
                return '\n'.join(lines)
            return (
                f"Hmm... looks like we don't have anything matching **{category_value}** right now."
                )
        lines = [
            f'{emoji} **{category_value.title()} {label} (Page {page} of {total_pages})**\n'
            ]
        for item in page_items:
            name = item.get('item_name', 'Unknown Item')
            price = item.get('base_price', '?')
            price_unit = item.get('price_unit', '?')
            price_cp = item.get('base_price_cp', '?')
            lines.append(f' • {name} — {price} {price_unit} ({price_cp} CP)')
        self._add_navigation_lines(lines, page, total_pages)
        self.debug('← Exiting _show_items')
        return '\n'.join(lines)

    def shopkeeper_show_items_by_category(self, player_input):
        self.debug('→ Entering shopkeeper_show_items_by_category')
        self.debug('← Exiting shopkeeper_show_items_by_category')
        return self._show_items(player_input, field='equipment_category',
            emoji='📦', label='Items')

    def shopkeeper_show_items_by_weapon_category(self, player_input):
        self.debug('→ Entering shopkeeper_show_items_by_weapon_category')
        weapon_category = player_input.get('weapon_category')
        page = player_input.get('page', 1)
        if not weapon_category:
            return (
                "⚠️ I didn't quite catch which weapon type you meant. Try saying it again?"
                )
        rows = get_items_by_weapon_category(weapon_category, page, page_size=5)
        if not rows:
            return (
                f"Hmm... looks like we don't have any **{weapon_category}** weapons in stock right now."
                )
        all_rows = get_items_by_weapon_category(weapon_category, page=1,
            page_size=9999)
        total_pages = max(1, (len(all_rows) + 4) // 5)
        lines = [
            f'⚔️ *{weapon_category.title()} Weapons*  _(Page {page} of {total_pages})_'
            , '']
        for row in rows:
            item = dict(row)
            item_id = item.get('item_id', '?')
            name = item.get('item_name', 'Unknown Item')
            price = item.get('base_price', '?')
            price_unit = item.get('price_unit', '?')
            price_cp = item.get('base_price_cp', '?')
            lines.append(f'id: *{item_id}* | {name} | {price} {price_unit} _({price_cp} CP)_')
        self._add_navigation_lines(lines, page, total_pages, include_buy_prompt=True)
        self.debug('← Exiting shopkeeper_show_items_by_weapon_category')
        return '\n'.join(lines)

    def shopkeeper_show_items_by_armour_category(self, player_input):
        self.debug('→ Entering shopkeeper_show_items_by_armour_category')
        armour_category = player_input.get('armour_category')
        page = player_input.get('page', 1)

        if not armour_category:
            return "⚠️ I didn't quite catch which armour type you meant. Try saying it again?"

        # Get all matching items, then sort and paginate manually
        all_rows = get_items_by_armour_category(armour_category, page=1, page_size=9999)
        all_items = [dict(row) for row in all_rows]
        all_items.sort(key=lambda x: x.get('base_price_cp') or 0)

        total_pages = max(1, (len(all_items) + 4) // 5)
        start = (page - 1) * 5
        end = start + 5
        page_items = all_items[start:end]

        if not page_items:
            return f"Hmm... looks like we don't have any **{armour_category}** armour in stock right now."

        lines = [f'🛡️ {armour_category.title()} Armour (Page {page} of {total_pages})\n']
        for item in page_items:
            item_id = item.get('item_id', '?')
            name = item.get('item_name', 'Unknown Item')
            price = item.get('base_price', '?')
            price_unit = item.get('price_unit', '?')
            price_cp = item.get('base_price_cp', '?')
            lines.append(f'id: *{item_id}* | {name} | {price} {price_unit} _({price_cp} CP)_')
        lines.append(' ')
        self._add_navigation_lines(lines, page, total_pages, include_buy_prompt=True)
        self.debug("← Exiting shopkeeper_show_items_by_armour_category")
        return '\n'.join(lines)

    def shopkeeper_show_items_by_gear_category(self, player_input):
        self.debug('→ Entering shopkeeper_show_items_by_gear_category')

        gear_category = player_input.get('gear_category')
        page = max(int(player_input.get('page', 1)), 1)

        if not gear_category:
            return "⚠️ I didn't quite catch which gear type you meant. Try saying it again?"

        # Fetch all items in the category
        all_rows = get_items_by_gear_category(gear_category, page=1, page_size=9999)
        all_items = [dict(row) for row in all_rows]

        # Sort by base_price_cp
        all_items.sort(key=lambda x: x.get('base_price_cp') or 0)

        # Manual pagination
        total_pages = max(1, (len(all_items) + 4) // 5)
        start = (page - 1) * 5
        end = start + 5
        page_items = all_items[start:end]

        if not page_items:
            return f"Hmm... looks like we don't have any {gear_category} gear in stock right now."

        lines = [f'🎒 {gear_category.title()} Gear (Pg {page} of {total_pages})\n']
        for item in page_items:
            item_id = item.get('item_id', '?')
            name = item.get('item_name', 'Unknown Item')
            price = item.get('base_price', '?')
            price_unit = item.get('price_unit', '?')
            price_cp = item.get('base_price_cp', '?')
            lines.append(f'id: *{item_id}* | {name} | {price} {price_unit} _({price_cp} CP)_')

        lines.append(' ')
        self._add_navigation_lines(lines, page, total_pages, include_buy_prompt=True)

        self.debug('← Exiting shopkeeper_show_items_by_gear_category')
        return '\n'.join(lines)

    def shopkeeper_show_items_by_tool_category(self, player_input):
        self.debug('→ Entering shopkeeper_show_items_by_tool_category')

        tool_category = player_input.get('tool_category')
        page = max(int(player_input.get('page', 1)), 1)

        if not tool_category:
            return "⚠️ I didn't catch which tool type you meant. Try that again?"

        # Fetch all matching items
        all_rows = get_items_by_tool_category(tool_category, page=1, page_size=9999)
        all_items = [dict(row) for row in all_rows]

        # Sort by base_price_cp (ascending)
        all_items.sort(key=lambda x: x.get('base_price_cp') or 0)

        # Manual pagination
        total_pages = max(1, (len(all_items) + 4) // 5)
        start = (page - 1) * 5
        end = start + 5
        page_items = all_items[start:end]

        if not page_items:
            return f"Hmm... looks like we don't have any {tool_category} tools in stock right now."

        lines = [f'🧰 {tool_category.title()} | Tools (Pg {page} of {total_pages})\n']
        for item in page_items:
            item_id = item.get('item_id', '?')
            name = item.get('item_name', 'Unknown Item')
            price = item.get('base_price', '?')
            price_unit = item.get('price_unit', '?')
            price_cp = item.get('base_price_cp', '?')
            lines.append(f'id: *{item_id}* | {name} | {price} {price_unit} _({price_cp} CP)_')

        lines.append(' ')
        self._add_navigation_lines(lines, page, total_pages, include_buy_prompt=True)

        self.debug('← Exiting shopkeeper_show_items_by_tool_category')
        return '\n'.join(lines)

    def shopkeeper_show_items_by_treasure_category(self, player_input):
        self.debug('→ Entering shopkeeper_show_items_by_treasure_category')

        treasure_category = player_input.get('treasure_category')
        page = max(int(player_input.get('page', 1)), 1)

        if not treasure_category:
            return "⚠️ I didn't catch which treasure type you meant. Try that again?"

        # Get all items
        all_rows = get_items_by_treasure_category(treasure_category, page=1, page_size=9999)
        all_items = [dict(row) for row in all_rows]

        # Sort by price_cp ascending
        all_items.sort(key=lambda x: x.get('base_price_cp') or 0)

        # Manual pagination
        total_pages = max(1, (len(all_items) + 4) // 5)
        start = (page - 1) * 5
        end = start + 5
        page_items = all_items[start:end]

        if not page_items:
            return f"Hmm... looks like we don't have any {treasure_category} treasures in stock right now."

        lines = [f'💎 {treasure_category.title()} | Treasure (Pg {page} of {total_pages})\n']
        for item in page_items:
            item_id = item.get('item_id', '?')
            name = item.get('item_name', 'Unknown Item')
            price = item.get('base_price', '?')
            unit = item.get('price_unit', '?')
            price_cp = item.get('base_price_cp', '?')
            lines.append(f'id: *{item_id}* | {name} | {price} {unit} _({price_cp} CP)_')

        lines.append(' ')
        self._add_navigation_lines(lines, page, total_pages, include_buy_prompt=True)

        self.debug('← Exiting shopkeeper_show_items_by_treasure_category')
        return '\n'.join(lines)

    def shopkeeper_show_items_by_mount_category(self, player_input):
        self.debug('→ Entering shopkeeper_show_items_by_mount_category')

        page = max(int(player_input.get('page', 1)), 1)
        category = 'Mounts and Vehicles'

        # Fetch all items
        all_rows = get_items_by_mount_category(category, page=1, page_size=9999)
        all_items = [dict(row) for row in all_rows]

        # Sort by copper price
        all_items.sort(key=lambda x: x.get('base_price_cp') or 0)

        # Paginate manually
        total_pages = max(1, (len(all_items) + 4) // 5)
        start = (page - 1) * 5
        end = start + 5
        page_items = all_items[start:end]

        if not page_items:
            return "Hmm... looks like we don't have any mounts or vehicles in stock right now."

        lines = [f'🏇 *Mounts & Vehicles*  _(Page {page} of {total_pages})_', '']
        for item in page_items:
            item_id = item.get('item_id', '?')
            name = item.get('item_name', 'Unknown Item')
            price = item.get('base_price', '?')
            price_unit = item.get('price_unit', '?')
            price_cp = item.get('base_price_cp', '?')
            lines.append(f'id: *{item_id}* | {name} | {price} {price_unit} _({price_cp} CP)_')

        self._add_navigation_lines(lines, page, total_pages, include_buy_prompt=True)

        self.debug('← Exiting shopkeeper_show_items_by_mount_category')
        return '\n'.join(lines)

    def shopkeeper_accept_thanks(self) ->str:
        self.debug('→ Entering shopkeeper_accept_thanks')
        self.debug('← Exiting shopkeeper_accept_thanks')
        return 'No problem at all, thanks for being you!'

    def shopkeeper_deposit_balance_cp_prompt(self) ->str:
        self.debug('→ Entering shopkeeper_deposit_balance_cp_prompt')
        self.debug('← Exiting shopkeeper_deposit_balance_cp_prompt')
        return (
            'Stashing away some savings? How much CP shall I deposit for you?'
            )

    def shopkeeper_withdraw_balance_cp_prompt(self) ->str:
        self.debug('→ Entering shopkeeper_withdraw_balance_cp_prompt')
        self.debug('← Exiting shopkeeper_withdraw_balance_cp_prompt')
        return 'Taking some coin out? How much would you like to withdraw?'

    def shopkeeper_check_balance_prompt(self, cp_amount: int) -> str:
        self.debug('→ Entering shopkeeper_check_balance_prompt')

        # Breakdown by currency
        remaining_cp = cp_amount
        breakdown = {
            'pp': remaining_cp // 1000,
            'gp': (remaining_cp % 1000) // 100,
            'ep': (remaining_cp % 100) // 50,
            'cp': remaining_cp % 50,
        }

        # Helpful summary
        total_gp = cp_amount / 100
        total_pp = cp_amount / 1000

        # Format output
        lines = [
            '💰 *Party Balance Summary*',
            '',
            f"🪙 Platinum: *{breakdown['pp']} PP*",
            f"🟡 Gold:     *{breakdown['gp']} GP*",
            f"🔷 Electrum: *{breakdown['ep']} EP*",
            f"🟤 Copper:   *{breakdown['cp']} CP*",
            '',
            f"📏 Total Value: *{total_gp:.2f} GP*  /  *{cp_amount} CP*",
            '',
            "_Use 'buy' or 'deposit' to continue shopping._"
        ]

        self.debug('← Exiting shopkeeper_check_balance_prompt')
        return '\n'.join(lines)

    def shopkeeper_show_ledger(self, ledger_entries: list, page: int=1) ->str:
        self.debug('→ Entering shopkeeper_show_ledger')
        """
        Same pagination as before (5 records/page) but the output is grouped by the
        human-readable timestamp, e.g.

          📜 Transaction History (Page 1 of 2)

          **6 hours ago**
          • Kyle withdrew 10 CP
          • Kyle deposited 1 000 CP
          • Kyle sold Plate Armor for 900 CP
          …

        The helper `humanize` is unchanged.
        """
        if not ledger_entries:
            return 'Your ledger is empty—no purchases, sales, or deposits yet!'

        def humanize(ts_str: str) ->str:
            try:
                ts_utc = datetime.fromisoformat(ts_str)
            except Exception:
                return ts_str
            now_local = datetime.now()
            offset = now_local - datetime.utcnow()
            ts_local = ts_utc + offset
            delta = now_local - ts_local
            if delta < timedelta(seconds=60):
                return 'just now'
            if delta < timedelta(hours=1):
                mins = int(delta.total_seconds() // 60)
                return f"{mins} minute{'s' if mins != 1 else ''} ago"
            if delta < timedelta(hours=24):
                hrs = int(delta.total_seconds() // 3600)
                return f"{hrs} hour{'s' if hrs != 1 else ''} ago"

            def ordinal(n: int) ->str:
                if 10 <= n % 100 <= 20:
                    suf = 'th'
                else:
                    suf = {(1): 'st', (2): 'nd', (3): 'rd'}.get(n % 10, 'th')
                return f'{n}{suf}'
            weekday = ts_local.strftime('%a')
            day = ordinal(ts_local.day)
            time = ts_local.strftime('%I:%M %p').lstrip('0').lower()
            return f'{weekday} {day} at {time}'
        entries_sorted = sorted((dict(e) for e in ledger_entries), key=lambda
            e: e.get('timestamp', ''), reverse=True)
        page_items, page, total_pages = self._paginate(entries_sorted, page,
            page_size=5)
        grouped: dict[str, list[str]] = defaultdict(list)
        for entry in page_items:
            ts_human = humanize(entry.get('timestamp', ''))
            player = entry.get('player_name', 'Someone')
            action = (entry.get('action') or '').lower()
            item = entry.get('item_name', '')
            amount = entry.get('amount', 0)
            currency = entry.get('currency', '')
            if action in {'buy', 'bought'}:
                verb, what = 'bought', f'{item} for {amount} {currency}'
            elif action in {'sell', 'sold'}:
                verb, what = 'sold', f'{item} for {amount} {currency}'
            elif action == 'deposit':
                verb, what = 'deposited', f'{amount} CP'
            elif action == 'withdraw':
                verb, what = 'withdrew', f'{amount} CP'
            else:
                verb = action or 'did something with'
                what = f'{item} for {amount} {currency}' if item else f'{amount} {currency}'
            grouped[ts_human].append(f'• {player} {verb} {what}')
        lines = [f'📜 Transaction History (Page {page} of {total_pages})', '']
        for ts_human, rows in grouped.items():
            lines.append(f'*{ts_human}*')
            lines.append(' ')
            lines.extend(rows)
            lines.append(' ')
        self._add_navigation_lines(lines, page, total_pages)
        self.debug('← Exiting shopkeeper_show_ledger')
        return '\n'.join(lines).rstrip()

    def get_equipment_categories(self):
        self.debug('→ Entering get_equipment_categories')
        self.debug('← Exiting get_equipment_categories')
        return get_all_equipment_categories()

    def get_weapon_categories(self):
        self.debug('→ Entering get_weapon_categories')
        self.debug('← Exiting get_weapon_categories')
        return get_weapon_categories()

    def get_armour_categories(self):
        self.debug('→ Entering get_armour_categories')
        self.debug('← Exiting get_armour_categories')
        return get_armour_categories()

    def get_gear_categories(self):
        self.debug('→ Entering get_gear_categories')
        self.debug('← Exiting get_gear_categories')
        return get_gear_categories()

    def get_tool_categories(self):
        self.debug('→ Entering get_tool_categories')
        self.debug('← Exiting get_tool_categories')
        return get_tool_categories()

    def get_treasure_categories(self):
        self.debug('→ Entering get_treasure_categories')
        self.debug('← Exiting get_treasure_categories')
        return get_treasure_categories()


    def shopkeeper_fallback_prompt(self) ->str:
        self.debug('→ Entering shopkeeper_fallback_prompt')
        self.debug('← Exiting shopkeeper_fallback_prompt')
        return join_lines('Here’s what I can do for you:', ' ',
            '• *BROWSE*  see what’s in stock', '• *BUY*  purchase an item',
            '• *SELL*  trade in your loot',
            '• *INSPECT*  details for one item',
            '• *BALANCE*  check party balance',
            '• *DEPOSIT*  add to the fund',
            '• *WITHDRAW* take out of the fund',
            '• *LEDGER*  view our trade history', ' ', 'Just let me know! ')

    def shopkeeper_buy_confirm_prompt(self, item, party_balance_cp, discount=None):
        self.debug('→ Entering shopkeeper_buy_confirm_prompt')

        base = item.get('base_price', 0)
        price_unit = item.get('price_unit', '?')
        base_cp = item.get('base_price_cp', 0)
        cost = discount if discount is not None else base
        saved = base - cost if discount is not None else 0
        discount_note = f' (you saved {saved} {price_unit}!)' if saved > 0 else ''

        name = item.get('item_name', 'Unknown Item')
        cat = item.get('equipment_category', '')
        rar = item.get('rarity', '')

        lines = [
            f"You're about to buy a *{name}* ({cat}, {rar}).",
            '',
            f'💰 Price: {cost} {price_unit}{discount_note}',
            f"⚖️ Weight: {item.get('weight', 0)} lb",
            ''
        ]

        if item.get('desc'):
            lines.append(f"📜 _{item['desc']}_")
        if item.get('damage_dice'):
            dmg_type = item.get('damage_type', '')
            lines.append(f"⚔️ Damage: {item['damage_dice']} {dmg_type}".strip())
        if item.get('weapon_range'):
            lines.append(f"🎯 Weapon Range: {item['weapon_range']}")
        if item.get('range_normal'):
            span = f"{item['range_normal']} ft"
            if item.get('range_long'):
                span += f" / {item['range_long']} ft"
            lines.append(f'📏 Range: {span}')
        if cat.lower() == 'armor' or item.get('armour_category'):
            armour_cat = item.get('armour_category', 'Unknown')
            lines.append(f'🛡️ Category: {armour_cat}')
            ac = item.get('base_ac')
            if ac is not None:
                dex_bonus = item.get('dex_bonus')
                max_bonus = item.get('max_dex_bonus')
                ac_line = f'🎲️ Base AC: {ac}'
                if dex_bonus:
                    if max_bonus:
                        ac_line += f' + Dex mod (max {max_bonus})'
                    else:
                        ac_line += ' + Dex mod'
                lines.append(ac_line)
            str_min = item.get('str_minimum')
            if str_min:
                lines.append(f'💪 Requires STR {str_min}')
            if item.get('stealth_disadvantage'):
                lines.append('🥷 Disadvantage on Stealth checks')

        # 💰 Add breakdown of balance
        remaining_cp = party_balance_cp
        breakdown = {
            'pp': remaining_cp // 1000,
            'gp': (remaining_cp % 1000) // 100,
            'ep': ((remaining_cp % 100) // 50),
            'cp': remaining_cp % 50,
            'gp_alone': remaining_cp // 100

        }

        lines.extend([
            '',
            f'Your party balance is *{breakdown['gp_alone']}* GP.',
            f"_That’s 🪙 {breakdown['pp']} Platinum, 🟡 {breakdown['gp']} Gold, ⚪ {breakdown['ep']} Electrum, 🟤 {breakdown['cp']} Copper._"

            '',
            'Would you like to proceed with the purchase?'
        ])

        self.debug('← Exiting shopkeeper_buy_confirm_prompt')
        return '\n'.join(lines)

    def shopkeeper_generic_say(self, message):
        self.debug('→ Entering shopkeeper_generic_say')
        self.debug('← Exiting shopkeeper_generic_say')
        return message

    def shopkeeper_buy_success_prompt(self, item, cost, unit):
        self.debug('→ Entering shopkeeper_buy_success_prompt')
        item_name = item.get('item_name', 'the item')
        self.debug('← Exiting shopkeeper_buy_success_prompt')
        return join_lines(f'💰 That’ll be *{cost}* {unit}, thanks..', ' ',
            f'Here you go. This *{item_name}* is now yours.', ' ',
            f'_You gained a {item_name}!_')

    def shopkeeper_deposit_success_prompt(self, amount, new_total):
        self.debug('→ Entering shopkeeper_deposit_success_prompt')
        self.debug('← Exiting shopkeeper_deposit_success_prompt')
        return (
            f' You deposited *{amount}* CP! Party balance is now *{new_total}* CP.'
            )

    def shopkeeper_withdraw_success_prompt(self, amount, new_total):
        self.debug('→ Entering shopkeeper_withdraw_success_prompt')
        self.debug('← Exiting shopkeeper_withdraw_success_prompt')
        return (
            f'You withdrew *{amount}* CP! Party balance is now *{new_total}* CP.' )

    def shopkeeper_withdraw_insufficient_balance_cp(self, requested: int, available: int) -> str:
        self.debug('→ Entering shopkeeper_withdraw_insufficient_balance_cp')
        message = (
               f"You tried to withdraw *{requested} CP*, but you only have *{available} CP* available. "
               "Try a smaller amount or deposit more first!"
           )
        self.debug('← Exiting shopkeeper_withdraw_insufficient_balance_cp')
        return message

    def search_items_by_name(self, query, page=1):
        self.debug('→ Entering search_items_by_name')
        query = normalize_input(query)
        rows = search_items_by_name_fuzzy(query, page=page)
        self.debug('← Exiting search_items_by_name')
        return [dict(row) for row in rows] if rows else []

    def shopkeeper_list_matching_items(self, matching_items):
        self.debug('→ Entering shopkeeper_list_matching_items')
        """
        Build a WhatsApp‑friendly list of matching items with richer emoji and clearer formatting.

        Example output:

        🔎 Here's what I have like that:

         • 🆔 _42_ | 🏷️ *Longsword* | 💰 *150* gold
         • 🆔 _17_ | 🏷️ *Healing Potion* | 💰 *50* gold

        Just say the item *name* or _number_ to see more details..
        """
        if isinstance(matching_items, dict):
            matching_items = [matching_items]
        lines = ["🔎 Here's what I have like that:", '']
        for item in matching_items:
            item_id = item.get('item_id', '?')
            name = item.get('item_name', 'Unknown Item')
            price = item.get('base_price', '?')
            unit = item.get('price_unit', '?')
            price_cp = item.get('base_price_cp', '?')
            lines.append(f' • _{item_id}_ | *{name}* | *{price}* {unit} _({price_cp} CP)_')
        lines.append(
            '\nJust say the item _number_ or *name* or  to see more details..')
        self.debug('← Exiting shopkeeper_list_matching_items')
        return '\n'.join(lines)

    def shopkeeper_say(self, text):
        self.debug('→ Entering shopkeeper_say')
        self.debug('← Exiting shopkeeper_say')
        return text

    def shopkeeper_farewell(self):
        self.debug('→ Entering shopkeeper_farewell')
        self.debug('← Exiting shopkeeper_farewell')
        return 'Safe travels, adventurer! Come back soon. 🌟'

    def shopkeeper_buy_failure_prompt(self, item, message, party_balance_cp):
        self.debug('→ Entering shopkeeper_buy_failure_prompt')
        """
        item: the item dict the player tried to buy
        message: a short error message or reason
        party_balance_cp: the player's current gold total
        """
        item_name = item.get('item_name', 'that item')
        self.debug('← Exiting shopkeeper_buy_failure_prompt')
        return (
            f"{message} You have {party_balance_cp} CP but the {item_name} costs {item.get('base_price', 0)} CP."
            )

    def shopkeeper_inspect_item_prompt(self, lines: list[str]) ->str:
        self.debug('→ Entering shopkeeper_inspect_item_prompt')
        """
        Turn the list of emoji-rich lines from InspectHandler
        into one block of text to send back to the user.
        """
        self.debug('← Exiting shopkeeper_inspect_item_prompt')
        return '\n'.join(lines)

    def shopkeeper_show_profile(self, data: dict) -> str:
        self.debug("→ Entering shopkeeper_show_profile")

        # ─── account / party fields ─────────────────────────────
        user_name = data.get("user_name", "unknown-user")
        phone = data.get("phone_number", "N/A")
        tier = data.get("subscription_tier", "free")

        name = data.get("player_name", "Unknown Adventurer")
        party_name = data.get("party_name", "Unnamed Party")
        gold = data.get("party_balance_cp", 0)
        visits = data.get("visit_count", 1)
        members = data.get("party_members") or data.get("members") or []

        level = data.get("level")
        klass = data.get("class") or data.get("character_class")

        owner_name = data.get("party_owner_name", "Unknown")

        # ─── assemble lines ────────────────────────────────────
        lines = [
            f"🪪 *Profile for {name}*",
            f"👤 Account: {user_name}\u2003|\u2003💎 Tier: {tier}",
            f"📱 Phone: {phone}",
            "",
            f"🛡️ Party: {party_name}",
            f"👑 Owner: {owner_name}",
            f"👥 Members: {', '.join(members) if members else 'Just you so far'}",
            f"💰 Gold on hand: {gold}",
            f"🏪 Visits to this shop: {visits}",
        ]
        if level is not None:
            lines.append(f"✨ Level: {level}")
        if klass:
            lines.append(f"⚔️ Class: {klass}")

        # ─── owned characters block (unchanged) ────────────────
        chars = data.get("characters") or []
        if chars:
            lines.append("\n*Owned characters:*")
            for idx, ch in enumerate(chars, start=1):
                char_name = ch.get("character_name") or ch.get("player_name", "Unknown")
                char_party = ch.get("party_name", "No party")
                role = ch.get("role") or "N/A"
                lines.append(
                    f"{idx}. {char_name}\u2003|\u2003Party: {char_party}\u2003|\u2003Role: {role}"
                )

        self.debug("← Exiting shopkeeper_show_profile")
        return "\n".join(lines)

    def shopkeeper_show_items_by_weapon_range(self, player_input):
        self.debug('→ Entering shopkeeper_show_items_by_weapon_range')

        cat_range = (player_input.get('category_range') or '').lower()
        page = max(int(player_input.get('page', 1)), 1)
        if not cat_range:
            return '⚠️ I didn’t catch which weapon group you meant.'

        # Step 1: Get all matching items
        all_rows = get_items_by_weapon_range(cat_range, page=1, page_size=9999)
        all_items = [dict(row) for row in all_rows]

        # Step 2: Sort by base_price_cp
        all_items.sort(key=lambda x: x.get('base_price_cp') or 0)

        # Step 3: Paginate manually
        total_pages = max(1, (len(all_items) + 4) // 5)
        start = (page - 1) * 5
        end = start + 5
        page_items = all_items[start:end]

        if not page_items:
            return f'Hmm… looks like we don’t have any **{cat_range.title()}** weapons in stock right now.'

        lines = [f'⚔️ *{cat_range.title()} Weapons*  _(Pg {page} of {total_pages})_']
        for item in page_items:
            item_id = item.get('item_id', '?')
            name = item.get('item_name', 'Unknown Item')
            price = item.get('base_price', '?')
            unit = item.get('price_unit', '?')
            price_cp = item.get('base_price_cp', '?')
            lines.append(f'id: *{item_id}* | {name} | {price} {unit} _({price_cp} CP)_')

        self._add_navigation_lines(lines, page, total_pages, include_buy_prompt=True)
        self.debug('← Exiting shopkeeper_show_items_by_weapon_range')
        return '\n'.join(lines)

    def shopkeeper_sell_offer_prompt(self, item: dict, offer_price: int,
        gold_before: int) ->str:
        self.debug('→ Entering shopkeeper_sell_offer_prompt')
        """
        First message when the player chooses an item to sell.
        Shows the offer and asks for confirmation.
        """
        name = item.get('item_name') or item.get('name') or 'that item'
        future_balance = gold_before + offer_price
        self.debug('← Exiting shopkeeper_sell_offer_prompt')
        return f"""I’ll give you *{offer_price} CP* for your *{name}*.
That would bring your purse to *{future_balance} CP*.
Deal?"""

    def shopkeeper_sell_success_prompt(self, item: dict, price: int,
        gold_after: int) ->str:
        self.debug('→ Entering shopkeeper_sell_success_prompt')
        """
        Confirmation after the sale has been booked.
        """
        name = item.get('item_name') or 'item'
        self.debug('← Exiting shopkeeper_sell_success_prompt')
        return f"""Pleasure doing business!  Here’s *{price} CP* for the *{name}*.
Your new balance is *{gold_after} CP*."""

    def shopkeeper_sell_cancel_prompt(self, item: (dict | None)) ->str:
        self.debug('→ Entering shopkeeper_sell_cancel_prompt')
        """Used when the player declines the offer."""
        name = (item or {}).get('item_name') or 'that item'
        self.debug('← Exiting shopkeeper_sell_cancel_prompt')
        return f'All right, we’ll keep the *{name}* off the counter then.'
    shopkeeper_sell_confirm_prompt = shopkeeper_sell_offer_prompt

    def shopkeeper_sell_enquire_item(self) ->str:
        self.debug('→ Entering shopkeeper_sell_enquire_item')
        """
        Called when the player says just 'sell' (or the matcher found nothing)
        so we need to ask which item they’d like to trade.
        """
        self.debug('← Exiting shopkeeper_sell_enquire_item')
        return (
            'Sure thing! What are you looking to sell?\n• Say the item’s *name* or *ID number*.'
            )
