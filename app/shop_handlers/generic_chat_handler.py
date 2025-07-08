from collections import ChainMap
from app.conversation import PlayerIntent, ConversationState
from app.models.ledger import get_last_transactions
from app.models.items import get_items_by_weapon_range
from app.interpreter import get_equipment_category_from_input
from app.db import get_item_details, get_connection, get_account_profile
from app.utils.debug import HandlerDebugMixin

class GenericChatHandler(HandlerDebugMixin):

    def __init__(self, agent, party_data, convo, party_id, player_id):
        # wire up debug proxy before any debug() calls
        self.conversation = convo
        self.debug('→ Entering __init__')
        self.agent = agent
        self.party_data = party_data
        self.convo = convo
        self.party_id = party_id
        self.player_id = player_id

        self.debug('← Exiting __init__')


    def handle_reply_to_greeting(self, player_input):
        self.debug('→ Entering handle_reply_to_greeting')
        self.debug('← Exiting handle_reply_to_greeting')
        return self.agent.shopkeeper_greeting(party_name=self.party_data[
            'party_name'], visit_count=self.party_data['visit_count'],
            player_name=self.party_data['player_name'], character_name=self.party_data['character_name'],)

    def handle_fallback(self, player_input):
        self.debug('→ Entering handle_fallback')
        self.debug('← Exiting handle_fallback')
        return self.agent.shopkeeper_fallback_prompt()

    def handle_view_ledger(self, player_input):
        self.debug('→ Entering handle_view_ledger')
        raw_entries = get_last_transactions(self.party_id)
        entries = [dict(row) for row in raw_entries]
        self.convo.metadata.update({'current_section': 'ledger',
            'current_page': 1, 'ledger_entries': entries})
        self.convo.save_state()
        self.debug('← Exiting handle_view_ledger')
        return self.agent.shopkeeper_show_ledger(entries, page=1)

    def handle_accept_thanks(self, player_input):
        self.debug('→ Entering handle_accept_thanks')
        self.debug('← Exiting handle_accept_thanks')
        return self.agent.shopkeeper_accept_thanks()

    def handle_check_balance(self, player_input):
        self.debug('→ Entering handle_check_balance')
        current_balance_cp = self.party_data.get('party_balance_cp', 0)
        self.debug('← Exiting handle_check_balance')
        return self.agent.shopkeeper_check_balance_prompt(current_balance_cp)

    def handle_next_page(self, _input):
        self.debug('→ Entering handle_next_page')
        section = self.convo.metadata.get('current_section', 'equipment')
        current_page = self.convo.metadata.get('current_page', 1)
        next_page = current_page + 1
        if section == 'ledger':
            ledger_entries = self.convo.metadata.get('ledger_entries', [])
            self.convo.metadata['current_page'] = next_page
            self.convo.save_state()
            return self.agent.shopkeeper_show_ledger(ledger_entries, page=
                next_page)
        self.convo.metadata['current_page'] = next_page
        self.convo.save_state()
        if section == 'mount':
            return self.agent.shopkeeper_show_items_by_mount_category({
                'page': next_page})
        category = self.convo.metadata.get('current_category_range'
            ) or self.convo.metadata.get('current_weapon_category'
            ) or self.convo.metadata.get('current_armour_category'
            ) or self.convo.metadata.get('current_gear_category'
            ) or self.convo.metadata.get('current_tool_category'
            ) or self.convo.metadata.get('current_treasure_category')
        if not category:
            return self.agent.shopkeeper_generic_say(
                'Next what? I’m not sure what you’re looking at!')
        if section == 'weapon':
            if self.convo.metadata.get('current_category_range'):
                return self.agent.shopkeeper_show_items_by_weapon_range({
                    'category_range': category, 'page': next_page})
            return self.agent.shopkeeper_show_items_by_weapon_category({
                'weapon_category': category, 'page': next_page})
        elif section == 'armor':
            return self.agent.shopkeeper_show_items_by_armour_category({
                'armour_category': category, 'page': next_page})
        elif section == 'gear':
            return self.agent.shopkeeper_show_items_by_gear_category({
                'gear_category': category, 'page': next_page})
        elif section == 'treasure':
            return self.agent.shopkeeper_show_items_by_treasure_category({
                'treasure_category': category, 'page': next_page})
        self.debug('← Exiting handle_next_page')
        return self.agent.shopkeeper_generic_say(
            'Next what? I’m not sure what you’re looking at!')

    def handle_previous_page(self, _input):
        self.debug('→ Entering handle_previous_page')
        section = self.convo.metadata.get('current_section', 'equipment')
        current_page = self.convo.metadata.get('current_page', 1)
        prev_page = max(current_page - 1, 1)
        if section == 'ledger':
            ledger_entries = self.convo.metadata.get('ledger_entries', [])
            self.convo.metadata['current_page'] = prev_page
            self.convo.save_state()
            return self.agent.shopkeeper_show_ledger(ledger_entries, page=
                prev_page)
        self.convo.metadata['current_page'] = prev_page
        self.convo.save_state()
        if section == 'mount':
            return self.agent.shopkeeper_show_items_by_mount_category({
                'page': prev_page})
        category = self.convo.metadata.get('current_category_range'
            ) or self.convo.metadata.get('current_weapon_category'
            ) or self.convo.metadata.get('current_armour_category'
            ) or self.convo.metadata.get('current_gear_category'
            ) or self.convo.metadata.get('current_tool_category'
            ) or self.convo.metadata.get('current_treasure_category')
        if not category:
            return self.agent.shopkeeper_generic_say(
                'Previous what? I’m not sure what you’re looking at!')
        if section == 'weapon':
            if self.convo.metadata.get('current_category_range'):
                return self.agent.shopkeeper_show_items_by_weapon_range({
                    'category_range': category, 'page': prev_page})
            return self.agent.shopkeeper_show_items_by_weapon_category({
                'weapon_category': category, 'page': prev_page})
        elif section == 'armor':
            return self.agent.shopkeeper_show_items_by_armour_category({
                'armour_category': category, 'page': prev_page})
        elif section == 'gear':
            return self.agent.shopkeeper_show_items_by_gear_category({
                'gear_category': category, 'page': prev_page})
        elif section == 'tool':
            return self.agent.shopkeeper_show_items_by_tool_category({
                'tool_category': category, 'page': prev_page})
        elif section == 'treasure':
            return self.agent.shopkeeper_show_items_by_treasure_category({
                'treasure_category': category, 'page': prev_page})
        self.debug('← Exiting handle_previous_page')
        return self.agent.shopkeeper_generic_say(
            'Previous what? I’m not sure what you’re looking at!')

    def handle_confirm(self, player_input):
        self.debug('→ Entering handle_confirm')
        self.debug('← Exiting handle_confirm')
        return self.agent.shopkeeper_generic_say('Thanks for confirming!')

    def handle_cancel(self, player_input):
        self.debug('→ Entering handle_cancel')
        self.debug('← Exiting handle_cancel')
        return self.agent.shopkeeper_generic_say(
            'Alright, I’ve cancelled that action.')

    def handle_farewell(self, player_input):
        self.debug('→ Entering handle_farewell')
        self.debug('← Exiting handle_farewell')
        return self.agent.shopkeeper_farewell()

    def handle_view_profile(self, player_input=None):
        self.debug('→ Entering handle_view_profile')
        """
        Show the full profile (account + current party data).

        • Pull the account row.
        • Merge it with the party-session snapshot.
        • Stash the characters list so the user can still choose “1 / 2 / 3…”.
        """
        acct = get_account_profile(self.player_id)
        full_profile = dict(ChainMap(self.party_data, acct))
        self.convo.set_pending_item(full_profile.get('characters', []))
        self.convo.set_pending_action(PlayerIntent.VIEW_CHARACTER)
        self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
        self.convo.save_state()
        self.debug('← Exiting handle_view_profile')
        return self.agent.shopkeeper_show_profile(full_profile)

    def handle_view_character(self, char_dict):
        self.debug('→ Entering handle_view_character')
        """
        After the player replies “1”, “2”, … send the selected character
        _through the same_ profile prompt. The unified viewer is robust
        enough to print either a bare character dict or the merged account.
        """
        self.debug('← Exiting handle_view_character')
        return self.agent.shopkeeper_show_profile(char_dict)
