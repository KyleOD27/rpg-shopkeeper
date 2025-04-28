# app/shop_handlers/view_handler.py

from app.conversation import ConversationState, PlayerIntent
from app.interpreter import normalize_input
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

        self.convo.metadata["current_page"] = 1

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
        self.convo.metadata["current_section"] = section_name
        self.convo.state = ConversationState.VIEWING_CATEGORIES
        self.convo.save_state()

    def _handle_subcategory_selection(self, section, raw_text):
        text = normalize_input(raw_text)

        category_mapping = {
            "armor": {
                "get_func": self.agent.get_armour_categories,
                "process_func": self.process_view_armour_subcategory,
                "subcategory_intent": PlayerIntent.VIEW_ARMOUR_SUBCATEGORY,
                "payload_key": "armour_category"
            },
            "weapon": {
                "get_func": self.agent.get_weapon_categories,
                "process_func": self.process_view_weapon_subcategory,
                "subcategory_intent": PlayerIntent.VIEW_WEAPON_SUBCATEGORY,
                "payload_key": "weapon_category"
            },
            "gear": {
                "get_func": self.agent.get_gear_categories,
                "process_func": self.process_view_gear_subcategory,
                "subcategory_intent": PlayerIntent.VIEW_GEAR_SUBCATEGORY,
                "payload_key": "gear_category"
            },
            "tool": {
                "get_func": self.agent.get_tool_categories,
                "process_func": self.process_view_tool_subcategory,
                "subcategory_intent": PlayerIntent.VIEW_TOOL_SUBCATEGORY,
                "payload_key": "tool_category"
            }
        }

        section_info = category_mapping.get(section)
        if not section_info:
            return self.agent.shopkeeper_view_items_prompt()

        valid_categories = [normalize_input(c) for c in section_info["get_func"]()]

        for category in valid_categories:
            if category in text:
                return section_info["process_func"]({
                    section_info["payload_key"]: category.title(),
                    "page": 1
                })

        intent_keywords = INTENT_KEYWORDS.get(section_info["subcategory_intent"], [])
        for keyword in intent_keywords:
            if normalize_input(keyword) in text:
                return section_info["process_func"]({
                    section_info["payload_key"]: keyword.title(),
                    "page": 1
                })

        matching_items = self.agent.search_items_by_name(text)

        # 🛠️ ADD THIS small wrapper:
        if isinstance(matching_items, dict):
            matching_items = [matching_items]

        # now matching_items is ALWAYS a list

        if matching_items:
            if len(matching_items) == 1:
                self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
                self.convo.metadata["pending_item"] = matching_items[0]
                return self.agent.shopkeeper_buy_confirm_prompt(
                    matching_items[0], self.agent.party_data.get("party_gold", 0)
                )
            else:
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                self.convo.metadata["matching_items"] = matching_items
                return self.agent.shopkeeper_list_matching_items(matching_items)

        categories = section_info["get_func"]()
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
        return self._handle_view_subcategory(payload, "weapon", "weapon_category", self.agent.shopkeeper_show_items_by_weapon_category, self.agent.get_weapon_categories, self.agent.shopkeeper_list_weapon_categories)

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
