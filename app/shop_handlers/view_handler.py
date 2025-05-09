# app/shop_handlers/view_handler.py

from app.conversation import ConversationState, PlayerIntent
from app.interpreter import normalize_input, get_subcategory_match
from app.interpreter import INTENT_KEYWORDS
from app.agents.shopkeeper_agent import BaseShopkeeper


class ViewHandler:
    def __init__(self, convo, agent, buy_handler):
        self.convo = convo
        self.agent = agent
        self.buy_handler = buy_handler

    def process_view_items_flow(self, player_input):
        intent = self.convo.player_intent
        raw_text = player_input.get("text", "")
        section = self.convo.metadata.get("current_section")  # ← current context

        # ────────────────────────────────────────────────────────────────
        # 0️⃣  *Already* in a section?  Treat repeated section-intent as a
        #     sub-category choice (“artisan’s tools”, “martial melee”, …)
        # ----------------------------------------------------------------
        repeated_section = (
                (section == "armor" and intent == PlayerIntent.VIEW_ARMOUR_CATEGORY) or
                (section == "weapon" and intent == PlayerIntent.VIEW_WEAPON_CATEGORY) or
                (section == "gear" and intent == PlayerIntent.VIEW_GEAR_CATEGORY) or
                (section == "tool" and intent == PlayerIntent.VIEW_TOOL_CATEGORY)
        )
        if repeated_section:
            return self._handle_subcategory_selection(section, raw_text)
        # ────────────────────────────────────────────────────────────────

        self.convo.metadata["current_page"] = 1
        ...
        # (rest of your existing process_view_items_flow stays unchanged)

        main_categories = {
            PlayerIntent.VIEW_ARMOUR_CATEGORY: ("armor", self.agent.get_armour_categories,
                                                self.agent.shopkeeper_list_armour_categories),
            PlayerIntent.VIEW_WEAPON_CATEGORY: ("weapon", self.agent.get_weapon_categories,
                                                self.agent.shopkeeper_list_weapon_categories),
            PlayerIntent.VIEW_GEAR_CATEGORY: ("gear", self.agent.get_gear_categories,
                                              self.agent.shopkeeper_list_gear_categories),
            PlayerIntent.VIEW_TOOL_CATEGORY: ("tool", self.agent.get_tool_categories,
                                              self.agent.shopkeeper_list_tool_categories),
            PlayerIntent.VIEW_MOUNT_CATEGORY: ("mount", None, self.agent.shopkeeper_show_items_by_mount_category),
            PlayerIntent.VIEW_EQUIPMENT_CATEGORY: ("equipment", None, self.agent.shopkeeper_view_items_prompt),
        }

        subcategory_intents = {
            PlayerIntent.VIEW_ARMOUR_SUBCATEGORY,
            PlayerIntent.VIEW_WEAPON_SUBCATEGORY,
            PlayerIntent.VIEW_GEAR_SUBCATEGORY,
            PlayerIntent.VIEW_TOOL_SUBCATEGORY,
        }

        if intent in main_categories:
            section, get_func, view_func = main_categories[intent]
            self._set_section(section)


            if get_func:
                # armor/weapon/gear/tool all take a list of categories
                categories = get_func()
                return view_func(categories)
            else:
                # only VIEW_EQUIPMENT_CATEGORY (the “see items” prompt) takes zero args
                if intent == PlayerIntent.VIEW_EQUIPMENT_CATEGORY:
                    return view_func()
                # everything else (mounts in particular) wants the raw player_input
                return view_func(player_input)

        if intent in subcategory_intents or intent == PlayerIntent.UNKNOWN:
            current_section = self.convo.metadata.get("current_section")
            if current_section:
                return self._handle_subcategory_selection(current_section, raw_text)

        self.convo.state = ConversationState.VIEWING_CATEGORIES
        self.convo.save_state()
        return self.agent.shopkeeper_view_items_prompt()

    def _set_section(self, section_name):
        self.convo.metadata.clear()
        self.convo.metadata["current_section"] = section_name
        self.convo.state = ConversationState.VIEWING_CATEGORIES
        self.convo.save_state()

    def _handle_subcategory_selection(self, section: str, raw_text: str):
        """
        Resolve a user phrase like “artisan's tools” or “simple ranged” to the
        correct sub-category payload, then delegate to the section-specific
        process_*_subcategory() helper.

        Works for armour, weapons, gear, and tools.
        """

        text = normalize_input(raw_text)

        match = get_subcategory_match(section, raw_text)
        if match:
            handler_map = {
                "armor": self.process_view_armour_subcategory,
                "weapon": self.process_view_weapon_subcategory,
                "gear": self.process_view_gear_subcategory,
                "tool": self.process_view_tool_subcategory,
            }
            key_map = {
                "armor": "armour_category",
                "weapon": "category_range",
                "gear": "gear_category",
                "tool": "tool_category",
            }

            payload = {  # ← build dict first
                key_map[section]: match,
                "page": 1,
            }
            return handler_map[section](payload)  # only one positional arg

        # ── section-specific wiring ─────────────────────────────────────────
        category_mapping = {
            "armor": {
                "get_func": self.agent.get_armour_categories,
                "process_func": self.process_view_armour_subcategory,
                "subcategory_intent": PlayerIntent.VIEW_ARMOUR_SUBCATEGORY,
                "payload_key": "armour_category",
            },
            "weapon": {
                "get_func": self.agent.get_weapon_categories,
                "process_func": self.process_view_weapon_subcategory,
                "subcategory_intent": PlayerIntent.VIEW_WEAPON_SUBCATEGORY,
                "payload_key": "category_range",
            },
            "gear": {
                "get_func": self.agent.get_gear_categories,
                "process_func": self.process_view_gear_subcategory,
                "subcategory_intent": PlayerIntent.VIEW_GEAR_SUBCATEGORY,
                "payload_key": "gear_category",
            },
            "tool": {
                "get_func": self.agent.get_tool_categories,
                "process_func": self.process_view_tool_subcategory,
                "subcategory_intent": PlayerIntent.VIEW_TOOL_SUBCATEGORY,
                "payload_key": "tool_category",
            },
        }

        section_info = category_mapping.get(section)
        if not section_info:
            return self.agent.shopkeeper_view_items_prompt()

        # ── 1️⃣  build <normalised → original> map once ────────────────────
        original_cats = section_info["get_func"]()  # e.g. ["Artisan's Tools", …]
        cat_map = {normalize_input(c): c for c in original_cats}

        # ── 2️⃣  direct “contains” match against user text ─────────────────
        for norm, orig in cat_map.items():
            if norm in text:
                return section_info["process_func"]({
                    section_info["payload_key"]: orig,  # keep exact spelling
                    "page": 1,
                })

        # ── 3️⃣  keyword / alias match (INTENT_KEYWORDS) ───────────────────
        intent_keywords = INTENT_KEYWORDS.get(section_info["subcategory_intent"], [])
        for kw in intent_keywords:
            norm_kw = normalize_input(kw)
            if norm_kw in text:
                chosen = cat_map.get(norm_kw, kw)  # use DB spelling if known
                return section_info["process_func"]({
                    section_info["payload_key"]: chosen,
                    "page": 1,
                })

        # ── 3️⃣½  fuzzy whole-phrase match (handles missing/extra letters) ──
        from difflib import get_close_matches

        close = get_close_matches(text, cat_map.keys(), n=1, cutoff=0.75)
        if close:
            chosen = cat_map[close[0]]
            return section_info["process_func"]({
                section_info["payload_key"]: chosen,
                "page": 1,
            })

        # ── 4️⃣  item-name search fallback ─────────────────────────────────
        matching_items = self.agent.search_items_by_name(text)
        if isinstance(matching_items, dict):  # normalise to list
            matching_items = [matching_items]

        if matching_items:
            if len(matching_items) == 1:
                self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
                self.convo.metadata["pending_item"] = matching_items[0]
                return self.agent.shopkeeper_buy_confirm_prompt(
                    matching_items[0],
                    self.agent.party_data.get("party_gold", 0),
                )
            else:
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                self.convo.metadata["matching_items"] = matching_items
                return self.agent.shopkeeper_list_matching_items(matching_items)

        # ── 5️⃣  nothing matched: re-list the sub-categories ───────────────
        categories = original_cats
        if section == "armor":
            return self.agent.shopkeeper_list_armour_categories(categories)
        elif section == "weapon":
            return self.agent.shopkeeper_list_weapon_categories(categories)
        elif section == "gear":
            return self.agent.shopkeeper_list_gear_categories(categories)
        elif section == "tool":
            return self.agent.shopkeeper_list_tool_categories(categories)
        else:
            return self.agent.shopkeeper_view_items_prompt()

    def process_view_armour_subcategory(self, payload):
        return self._handle_view_subcategory(payload, "armor", "armour_category", self.agent.shopkeeper_show_items_by_armour_category, self.agent.get_armour_categories, self.agent.shopkeeper_list_armour_categories)

    def process_view_weapon_subcategory(self, payload):
        return self._handle_view_subcategory(
            payload,
            section="weapon",
            key="category_range",  # ✅ keep: we’re keying on range
            show_func=self.agent.shopkeeper_show_items_by_weapon_range,
            get_func=self.agent.get_weapon_categories,  # 🔄 FIXED: was get_items_by_weapon_range
            list_func=self.agent.shopkeeper_list_weapon_categories
        )

    def process_view_gear_subcategory(self, payload):
        return self._handle_view_subcategory(payload, "gear", "gear_category", self.agent.shopkeeper_show_items_by_gear_category, self.agent.get_gear_categories, self.agent.shopkeeper_list_gear_categories)

    def process_view_tool_subcategory(self, payload):
        return self._handle_view_subcategory(payload, "tool", "tool_category", self.agent.shopkeeper_show_items_by_tool_category, self.agent.get_tool_categories, self.agent.shopkeeper_list_tool_categories)

    def _handle_view_subcategory(self, payload, section, key, show_func, get_func, list_func):
        category = payload.get(key)
        page = payload.get("page", 1)

        if not category:
            categories = get_func()
            return list_func(categories)

        self.convo.metadata[f"current_{key}"] = category
        self.convo.metadata["current_page"] = page
        self.convo.metadata["current_section"] = section
        self.convo.state = ConversationState.VIEWING_CATEGORIES
        self.convo.save_state()

        return show_func({key: category, "page": page})
