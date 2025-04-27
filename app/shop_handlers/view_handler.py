# app/shop_handlers/view_handler.py

from app.conversation import ConversationState, PlayerIntent
from app.interpreter import normalize_input

class ViewHandler:
    def __init__(self, convo, agent):
        self.convo = convo
        self.agent = agent

    def process_view_items_flow(self, player_input):
        intent = self.convo.player_intent
        raw_text = player_input.get("text", "")

        self.convo.metadata["current_page"] = 1

        # Main categories
        if intent == PlayerIntent.VIEW_ARMOUR_CATEGORY:
            self._set_section("armor")
            armour_categories = self.agent.get_armour_categories()
            return self.agent.shopkeeper_list_armour_categories(armour_categories)

        if intent == PlayerIntent.VIEW_WEAPON_CATEGORY:
            self._set_section("weapon")
            weapon_categories = self.agent.get_weapon_categories()
            return self.agent.shopkeeper_list_weapon_categories(weapon_categories)

        if intent == PlayerIntent.VIEW_GEAR_CATEGORY:
            self._set_section("gear")
            gear_categories = self.agent.get_gear_categories()
            return self.agent.shopkeeper_list_gear_categories(gear_categories)

        if intent == PlayerIntent.VIEW_TOOL_CATEGORY:
            self._set_section("tool")
            tool_categories = self.agent.get_tool_categories()
            return self.agent.shopkeeper_list_tool_categories(tool_categories)

        if intent == PlayerIntent.VIEW_MOUNT_CATEGORY:
            self._set_section("mount")
            return self.agent. shopkeeper_show_items_by_mount_category(player_input)

        if intent == PlayerIntent.VIEW_EQUIPMENT_CATEGORY:
            self._set_section("equipment")
            return self.agent.shopkeeper_view_items_prompt()


        # Subcategory selection (user says "heavy", "light", etc)
        if intent == PlayerIntent.UNKNOWN:
            current_section = self.convo.metadata.get("current_section")
            if current_section:
                return self._handle_subcategory_selection(current_section, raw_text)

        # Default
        self.convo.state = ConversationState.VIEWING_CATEGORIES
        self.convo.save_state()
        return self.agent.shopkeeper_view_items_prompt()

    def _set_section(self, section_name):
        self.convo.metadata["current_section"] = section_name
        self.convo.state = ConversationState.VIEWING_CATEGORIES
        self.convo.save_state()

    def _handle_subcategory_selection(self, section, raw_text):
        text = normalize_input(raw_text)

        if section == "armor":
            valid_categories = [normalize_input(c) for c in self.agent.get_armour_categories()]
            for category in valid_categories:
                if category in text:
                    return self.process_view_armour_subcategory({
                        "armour_category": category.title(),
                        "page": 1
                    })

        if section == "weapon":
            valid_categories = [normalize_input(c) for c in self.agent.get_weapon_categories()]
            for category in valid_categories:
                if category in text:
                    return self.process_view_weapon_subcategory({
                        "weapon_category": category.title(),
                        "page": 1
                    })

        if section == "gear":
            valid_categories = [normalize_input(c) for c in self.agent.get_gear_categories()]
            for category in valid_categories:
                if category in text:
                    return self.process_view_gear_subcategory({
                        "gear_category": category.title(),
                        "page": 1
                    })

        if section == "tool":
            valid_categories = [normalize_input(c) for c in self.agent.get_tool_categories()]
            for category in valid_categories:
                if category in text:
                    return self.process_view_tool_subcategory({
                        "tool_category": category.title(),
                        "page": 1
                    })

        return "⚠️ I didn't quite catch which type you meant. Try saying it again?"

    # ----- Subcategory handlers -----

    def process_view_armour_subcategory(self, payload):
        armour_category = payload.get("armour_category")  # direct
        page = payload.get("page", 1)  # direct

        if not armour_category:
            return "⚠️ I didn't quite catch which armour type you meant. Try saying it again?"

        self.convo.metadata["current_armour_category"] = armour_category
        self.convo.metadata["current_page"] = page
        self.convo.metadata["current_section"] = "armor"
        self.convo.state = ConversationState.VIEWING_CATEGORIES
        self.convo.save_state()

        return self.agent.shopkeeper_show_items_by_armour_category({
            "armour_category": armour_category,
            "page": page
        })


    def process_view_weapon_subcategory(self, payload):
        weapon_category = payload.get("weapon_category")  # direct
        page = payload.get("page", 1)  # direct

        if not weapon_category:
            return "⚠️ I didn't quite catch which weapon type you meant. Try saying it again?"

        self.convo.metadata["current_weapon_category"] = weapon_category
        self.convo.metadata["current_page"] = page
        self.convo.metadata["current_section"] = "weapon"
        self.convo.state = ConversationState.VIEWING_CATEGORIES
        self.convo.save_state()

        return self.agent.shopkeeper_show_items_by_weapon_category({
            "weapon_category": weapon_category,
            "page": page
        })

    def process_view_gear_subcategory(self, player_input):
        from app.models.items import get_gear_categories

        gear_category = player_input.get("gear_category")
        page = player_input.get("page", 1)

        if not gear_category:
            return "⚠️ I didn't quite catch which gear type you meant. Try saying it again?"

        valid_categories = get_gear_categories()
        normalized_valid = [c.lower() for c in valid_categories]
        selected = gear_category.lower()

        if selected not in normalized_valid:
            return "⚠️ I didn't quite catch which gear type you meant. Try saying it again?"

        idx = normalized_valid.index(selected)
        proper_category = valid_categories[idx]

        self.convo.metadata["current_gear_category"] = proper_category
        self.convo.metadata["current_page"] = page
        self.convo.state = ConversationState.VIEWING_CATEGORIES
        self.convo.save_state()

        return self.agent.shopkeeper_show_items_by_gear_category({
            "gear_category": proper_category,
            "page": page
        })

    def process_view_tool_subcategory(self, player_input):
        from app.models.items import get_tool_categories

        tool_category = player_input.get("tool_category")
        page = player_input.get("page", 1)

        if not tool_category:
            return "⚠️ I didn't quite catch which tool type you meant. Try saying it again?"

        valid_categories = get_tool_categories()
        normalized_valid = [c.lower() for c in valid_categories]
        selected = tool_category.lower()

        if selected not in normalized_valid:
            return "⚠️ I didn't quite catch which tool type you meant. Try saying it again?"

        idx = normalized_valid.index(selected)
        proper_category = valid_categories[idx]

        self.convo.metadata["current_tool_category"] = proper_category
        self.convo.metadata["current_page"] = page
        self.convo.state = ConversationState.VIEWING_CATEGORIES
        self.convo.save_state()

        return self.agent.shopkeeper_show_items_by_tool_category({
            "tool_category": proper_category,
            "page": page
        })

