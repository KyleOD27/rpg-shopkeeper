from app.conversation import ConversationState, PlayerIntent
from app.interpreter import normalize_input, get_subcategory_match
from app.interpreter import INTENT_KEYWORDS
from app.utils.debug import HandlerDebugMixin

class ViewHandler(HandlerDebugMixin):

    def __init__(self, convo, agent, buy_handler):
        # wire up debug proxy before any debug() calls
        self.conversation = convo
        self.debug('→ Entering __init__')
        self.convo = convo
        self.agent = agent
        self.buy_handler = buy_handler
        self.debug('← Exiting __init__')

    def process_view_items_flow(self, player_input: dict):
        """
        Decides which list (or sub-list) to show.

        Rules
        ─────
        • Top-level “buy gear/armour/weapons/tools”  → VIEWING_CATEGORIES
        • Named sub-category (“standard gear”, …)    → VIEWING_ITEMS
        """
        self.debug('→ Entering process_view_items_flow')

        intent = self.convo.player_intent
        raw_text = player_input.get('text', '')
        section = self.convo.metadata.get('current_section')

        # ── 1. already in the same section → drill deeper ───────────────────
        repeated_section = (
                section == 'armor' and intent == PlayerIntent.VIEW_ARMOUR_CATEGORY or
                section == 'weapon' and intent == PlayerIntent.VIEW_WEAPON_CATEGORY or
                section == 'gear' and intent == PlayerIntent.VIEW_GEAR_CATEGORY or
                section == 'tool' and intent == PlayerIntent.VIEW_TOOL_CATEGORY or
                section == 'reasure' and intent == PlayerIntent.VIEW_TREASURE_CATEGORY
        )
        if repeated_section:
            return self._handle_subcategory_selection(section, raw_text)

        # ── 2. top-level category intents → show category grid ──────────────
        main_categories = {
            PlayerIntent.VIEW_ARMOUR_CATEGORY: ('armor', self.agent.get_armour_categories,
                                                self.agent.shopkeeper_list_armour_categories),
            PlayerIntent.VIEW_WEAPON_CATEGORY: ('weapon', self.agent.get_weapon_categories,
                                                self.agent.shopkeeper_list_weapon_categories),
            PlayerIntent.VIEW_GEAR_CATEGORY: ('gear', self.agent.get_gear_categories,
                                              self.agent.shopkeeper_list_gear_categories),
            PlayerIntent.VIEW_TOOL_CATEGORY: ('tool', self.agent.get_tool_categories,
                                              self.agent.shopkeeper_list_tool_categories),
            PlayerIntent.VIEW_TREASURE_CATEGORY: ('treasure', self.agent.get_treasure_categories,
                                              self.agent.shopkeeper_list_treasure_categories),
            PlayerIntent.VIEW_MOUNT_CATEGORY: ('mount', None,
                                               self.agent.shopkeeper_show_items_by_mount_category),
            PlayerIntent.VIEW_EQUIPMENT_CATEGORY: ('equipment', None,
                                                   self.agent.shopkeeper_view_items_prompt),
        }

        if intent in main_categories:
            section, get_func, view_func = main_categories[intent]
            self._set_section(section)
            self.convo.set_state(ConversationState.VIEWING_CATEGORIES)
            self.convo.save_state()

            if get_func:  # armour / weapon / gear / tool
                categories = get_func()
                return view_func(categories)
            else:
                # No get_func means either EQUIPMENT or MOUNT
                if intent == PlayerIntent.VIEW_EQUIPMENT_CATEGORY:
                    return view_func()  # ← **zero args**
                return view_func(player_input)  # mount payload

        # ── 3. sub-category intents → item list ─────────────────────────────
        subcategory_intents = {
            PlayerIntent.VIEW_ARMOUR_SUBCATEGORY: ('armor', 'armour_category',
                                                   self.process_view_armour_subcategory),
            PlayerIntent.VIEW_WEAPON_SUBCATEGORY: ('weapon', 'category_range',
                                                   self.process_view_weapon_subcategory),
            PlayerIntent.VIEW_GEAR_SUBCATEGORY: ('gear', 'gear_category',
                                                 self.process_view_gear_subcategory),
            PlayerIntent.VIEW_TOOL_SUBCATEGORY: ('tool', 'tool_category',
                                                 self.process_view_tool_subcategory),
            PlayerIntent.VIEW_TREASURE_SUBCATEGORY: ('treasure', 'treasure_category',
                                                 self.process_view_treasure_subcategory),
        }
        if intent in subcategory_intents:
            section, payload_key, handler = subcategory_intents[intent]
            match = get_subcategory_match(section, raw_text)  # e.g. "standard gear"
            if match:
                self.convo.set_state(ConversationState.VIEWING_ITEMS)
                self.convo.save_state()
                return handler({payload_key: match, 'page': 1})
            # fallback heuristic
            return self._handle_subcategory_selection(section, raw_text)

        # ── 4. anything else → generic prompt ───────────────────────────────
        self.convo.set_state(ConversationState.VIEWING_CATEGORIES)
        self.convo.save_state()
        self.debug('← Exiting process_view_items_flow')
        return self.agent.shopkeeper_view_items_prompt()

    def _set_section(self, section_name):
        self.debug('→ Entering _set_section')
        self.convo.metadata.clear()
        self.convo.metadata['current_section'] = section_name
        self.convo.state = ConversationState.VIEWING_CATEGORIES
        self.convo.save_state()
        self.debug('← Exiting _set_section')

    def _handle_subcategory_selection(self, section: str, raw_text: str):
        self.debug('→ Entering _handle_subcategory_selection')
        """
        Resolve a user phrase like “artisan's tools” or “simple ranged” to the
        correct sub-category payload, then delegate to the section-specific
        process_*_subcategory() helper.

        Works for armour, weapons, gear, and tools.
        """
        text = normalize_input(raw_text)
        match = get_subcategory_match(section, raw_text)
        if match:
            handler_map = {'armor': self.process_view_armour_subcategory,
                'weapon': self.process_view_weapon_subcategory, 'gear':
                self.process_view_gear_subcategory, 'tool': self.
                process_view_tool_subcategory}
            key_map = {'armor': 'armour_category', 'weapon':
                'category_range', 'gear': 'gear_category', 'tool':
                'tool_category'}
            payload = {key_map[section]: match, 'page': 1}
            return handler_map[section](payload)
        category_mapping = {'armor': {'get_func': self.agent.
            get_armour_categories, 'process_func': self.
            process_view_armour_subcategory, 'subcategory_intent':
            PlayerIntent.VIEW_ARMOUR_SUBCATEGORY, 'payload_key':
            'armour_category'}, 'weapon': {'get_func': self.agent.
            get_weapon_categories, 'process_func': self.
            process_view_weapon_subcategory, 'subcategory_intent':
            PlayerIntent.VIEW_WEAPON_SUBCATEGORY, 'payload_key':
            'category_range'}, 'gear': {'get_func': self.agent.
            get_gear_categories, 'process_func': self.
            process_view_gear_subcategory, 'subcategory_intent':
            PlayerIntent.VIEW_GEAR_SUBCATEGORY, 'payload_key':
            'gear_category'}, 'tool': {'get_func': self.agent.
            get_tool_categories, 'process_func': self.
            process_view_tool_subcategory, 'subcategory_intent':
            PlayerIntent.VIEW_TOOL_SUBCATEGORY, 'payload_key': 'tool_category'}
            }
        section_info = category_mapping.get(section)
        if not section_info:
            return self.agent.shopkeeper_view_items_prompt()
        original_cats = section_info['get_func']()
        cat_map = {normalize_input(c): c for c in original_cats}
        for norm, orig in cat_map.items():
            if norm in text:
                return section_info['process_func']({section_info[
                    'payload_key']: orig, 'page': 1})
        intent_keywords = INTENT_KEYWORDS.get(section_info[
            'subcategory_intent'], [])
        for kw in intent_keywords:
            norm_kw = normalize_input(kw)
            if norm_kw in text:
                chosen = cat_map.get(norm_kw, kw)
                return section_info['process_func']({section_info[
                    'payload_key']: chosen, 'page': 1})
        from difflib import get_close_matches
        close = get_close_matches(text, cat_map.keys(), n=1, cutoff=0.75)
        if close:
            chosen = cat_map[close[0]]
            return section_info['process_func']({section_info['payload_key'
                ]: chosen, 'page': 1})
        matching_items = self.agent.search_items_by_name(text)
        if isinstance(matching_items, dict):
            matching_items = [matching_items]
        if matching_items:
            if len(matching_items) == 1:
                self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
                self.convo.metadata['pending_item'] = matching_items[0]
                return self.agent.shopkeeper_buy_confirm_prompt(matching_items
                    [0], self.agent.party_data.get('party_balance_cp', 0))
            else:
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                self.convo.metadata['matching_items'] = matching_items
                return self.agent.shopkeeper_list_matching_items(matching_items
                    )
        categories = original_cats
        if section == 'armor':
            return self.agent.shopkeeper_list_armour_categories(categories)
        elif section == 'weapon':
            return self.agent.shopkeeper_list_weapon_categories(categories)
        elif section == 'gear':
            return self.agent.shopkeeper_list_gear_categories(categories)
        elif section == 'tool':
            return self.agent.shopkeeper_list_tool_categories(categories)
        elif section == 'treasure':
            return self.agent.shopkeeper_list_treasure_categories(categories)
        else:
            return self.agent.shopkeeper_view_items_prompt()
        self.debug('← Exiting _handle_subcategory_selection')

    def process_view_armour_subcategory(self, payload):
        self.debug('→ Entering process_view_armour_subcategory')
        self.debug('← Exiting process_view_armour_subcategory')
        return self._handle_view_subcategory(payload, 'armor',
            'armour_category', self.agent.
            shopkeeper_show_items_by_armour_category, self.agent.
            get_armour_categories, self.agent.shopkeeper_list_armour_categories
            )

    def process_view_weapon_subcategory(self, payload):
        self.debug('→ Entering process_view_weapon_subcategory')
        self.debug('← Exiting process_view_weapon_subcategory')
        return self._handle_view_subcategory(payload, section='weapon', key
            ='category_range', show_func=self.agent.
            shopkeeper_show_items_by_weapon_range, get_func=self.agent.
            get_weapon_categories, list_func=self.agent.
            shopkeeper_list_weapon_categories)

    def process_view_gear_subcategory(self, payload):
        self.debug('→ Entering process_view_gear_subcategory')
        self.debug('← Exiting process_view_gear_subcategory')
        return self._handle_view_subcategory(payload, 'gear',
            'gear_category', self.agent.
            shopkeeper_show_items_by_gear_category, self.agent.
            get_gear_categories, self.agent.shopkeeper_list_gear_categories)

    def process_view_tool_subcategory(self, payload):
        self.debug('→ Entering process_view_tool_subcategory')
        self.debug('← Exiting process_view_tool_subcategory')
        return self._handle_view_subcategory(payload, 'tool',
            'tool_category', self.agent.
            shopkeeper_show_items_by_tool_category, self.agent.
            get_tool_categories, self.agent.shopkeeper_list_tool_categories)

    def process_view_treasure_subcategory(self, payload):
        self.debug('→ Entering process_view_treasure_subcategory')
        self.debug('← Exiting process_view_treasure_subcategory')
        return self._handle_view_subcategory(payload, 'treasure',
            'treasure_category', self.agent.
            shopkeeper_show_items_by_treasure_category, self.agent.
            get_treasure_categories, self.agent.shopkeeper_list_treasure_categories)

    def _handle_view_subcategory(self, payload, section, key, show_func,
        get_func, list_func):
        self.debug('→ Entering _handle_view_subcategory')
        category = payload.get(key)
        page = payload.get('page', 1)
        if not category:
            categories = get_func()
            return list_func(categories)
        self.convo.metadata[f'current_{key}'] = category
        self.convo.metadata['current_page'] = page
        self.convo.metadata['current_section'] = section
        self.convo.state = ConversationState.VIEWING_CATEGORIES
        self.convo.save_state()
        self.debug('← Exiting _handle_view_subcategory')
        return show_func({key: category, 'page': page})
