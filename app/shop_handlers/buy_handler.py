import re
from app.interpreter import find_item_in_input, normalize_input
from app.models.items import get_item_by_name
from app.models.parties import update_party_balance_cp
from app.models.ledger import record_transaction
from app.conversation import ConversationState, PlayerIntent
from app.shop_handlers.haggle_handler import HaggleHandler
from app.utils.debug import HandlerDebugMixin
import copy


class BuyHandler(HandlerDebugMixin):

    def __init__(self, convo, agent, party_id, player_id, player_name,
                 party_data):
        # wire up debug proxy before any debug() calls
        self.conversation = convo
        self.debug('→ Entering __init__')

        # keep the old reference if you still use it elsewhere
        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.player_id = player_id
        self.player_name = player_name
        self.party_data = party_data

        self.debug('← Exiting __init__')


    def get_dict_item(self, item_reference):
        self.debug('→ Entering get_dict_item')
        if isinstance(item_reference, dict):
            return item_reference
        self.debug('← Exiting get_dict_item')
        return dict(get_item_by_name(str(item_reference)) or {})

    def process_buy_item_flow(self, player_input):
        self.debug('→ Entering process_buy_item_flow')
        raw = player_input.get('text', '') if isinstance(player_input, dict
            ) else player_input
        item_name = player_input.get('item') if isinstance(player_input, dict
            ) else None
        category = player_input.get('category') if isinstance(player_input,
            dict) else None
        self.convo.clear_pending()
        if not item_name and not category:
            matches, detected_category = find_item_in_input(raw, self.convo)
            if matches:
                if len(matches) == 1:
                    item = matches[0]
                    self._stash_and_confirm(item)
                    return self.agent.shopkeeper_buy_confirm_prompt(item,
                        self.party_data['party_balance_cp'], self.convo.discount)
                self.convo.set_pending_item(matches)
                self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                self.convo.name_to_item = {re.sub('[^\\w\\s]', '', m[
                    'item_name'].lower()).strip(): m for m in matches}
                self.convo.save_state()
                return self.agent.shopkeeper_list_matching_items(matches)
            elif detected_category:
                self.convo.set_state(ConversationState.VIEWING_CATEGORIES)
                return self.agent.shopkeeper_show_items_by_category({
                    'equipment_category': detected_category})
            else:
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                return self.agent.get_equipment_categories()
        if item_name:
            item = self.get_dict_item(item_name)
            if item:
                self._stash_and_confirm(item)
                return self.agent.shopkeeper_buy_confirm_prompt(item, self.
                    party_data['party_balance_cp'], self.convo.discount)
        self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
        self.debug('← Exiting process_buy_item_flow')
        return self.agent.get_equipment_categories()

    def _stash_and_confirm(self, item):
        self.debug('→ Entering _stash_and_confirm')
        """Put item into convo and prepare for confirmation."""
        self.convo.set_pending_item(item)
        self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
        self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
        self.convo.save_state()
        self.debug('← Exiting _stash_and_confirm')

    def process_item_selection(self, player_input):
        self.debug('→ Entering process_item_selection')
        choice = player_input.get('text', '').strip()
        for p in ('buy ', 'get ', 'select ', 'take ', 'pick '):
            if choice.lower().startswith(p):
                choice = choice[len(p):].lstrip()
                break
        pending = self.convo.get_pending_item()
        if not pending:
            matches, detected_category = find_item_in_input(choice, self.convo)
            if matches:
                if len(matches) == 1:
                    item = matches[0]
                    self._stash_and_confirm(item)
                    return self.agent.shopkeeper_buy_confirm_prompt(item,
                        self.party_data['party_balance_cp'], self.convo.discount)
                self.convo.set_pending_item(matches)
                self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                self.convo.save_state()
                return self.agent.shopkeeper_list_matching_items(matches)
            return self.agent.shopkeeper_say(
                'I’m not sure which item you mean. Try the full name or its ID number.'
                )
        norm = normalize_input(choice)
        if isinstance(pending, list):
            item = next((i for i in pending if str(i['item_id']) == norm or
                normalize_input(i['item_name']) == norm), None)
        else:
            item = pending
        if not item:
            return self.agent.shopkeeper_say(
                "I couldn't find that item in the options. Please say the full name or ID."
                )
        self._stash_and_confirm(item)
        self.debug('← Exiting process_item_selection')
        return self.agent.shopkeeper_buy_confirm_prompt(item, self.
            party_data['party_balance_cp'], self.convo.discount)

    def handle_haggle(self, player_input):
        self.debug('→ Entering handle_haggle')
        item = self.get_dict_item(self.convo.pending_item)
        if not item or item.get('base_price') is None:
            return self.agent.shopkeeper_generic_say(
                "There's nothing to haggle over just yet.")
        if self.convo.state != ConversationState.AWAITING_CONFIRMATION:
            return self.agent.shopkeeper_generic_say(
                'Let’s decide what you’re buying first, then we can haggle!')
        haggle = HaggleHandler(self.agent, self.convo, self.party_data)
        result = haggle.attempt_haggle(item)
        if self.convo.discount is not None:
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            self.convo.set_pending_item(item)
            self.convo.set_pending_action(PlayerIntent.BUY_CONFIRM)
            self.convo.save_state()
            discounted_price = self.convo.discount or item.get('base_price', 0)
            unit = item.get('price_unit', 0)
            item_name = item['item_name']
            balance = self.party_data['party_balance_cp']
            return f"""Alright, alright, you twisted my arm.
 
How about *{discounted_price}* {unit} for the *{item_name}*?
 
Your balance is *{balance}* CP. Would you like to proceed with the purchase?"""
        self.convo.set_discount(None)
        self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
        self.convo.set_pending_item(item)
        self.convo.set_pending_action(PlayerIntent.BUY_CONFIRM)
        self.convo.save_state()
        full_price = item.get('base_price', 0)
        item_name = item['item_name']
        unit = item.get('price_unit', 0)
        balance = self.party_data['party_balance_cp']
        self.debug('← Exiting handle_haggle')
        return f"""😅 Nice try, but that price is already a bargain.
 
The *{item_name}* still costs *{full_price}* {unit}.
 
Your balance is *{balance}* gp. Would you like to proceed with the purchase?"""

    def handle_confirm_purchase(self, player_input):
        self.debug('→ Entering handle_confirm_purchase')
        pending = self.convo.pending_item
        item = pending[0] if isinstance(pending, list) and len(pending
            ) == 1 else pending if isinstance(pending, dict) else None
        if not item or not item.get('item_name'):
            self.convo.debug(f'Purchase failed: no valid item. State={pending}'
                )
            return self.agent.shopkeeper_say(
                "Something went wrong — I can't find that item in stock.")
        response = self.finalise_purchase(item)
        self.convo.reset_state()
        self.convo.set_pending_item(None)
        self.convo.set_discount(None)
        self.convo.set_state(ConversationState.AWAITING_ACTION)
        self.convo.save_state()
        self.debug('← Exiting handle_confirm_purchase')
        return response

    def handle_cancel_purchase(self, player_input):
        self.debug('→ Entering handle_cancel_purchase')
        item = self.get_dict_item(self.convo.pending_item)
        self.convo.reset_state()
        self.convo.set_pending_item(None)
        self.convo.set_discount(None)
        self.convo.set_state(ConversationState.AWAITING_ACTION)
        self.convo.save_state()
        self.debug('← Exiting handle_cancel_purchase')
        return self.agent.shopkeeper_buy_cancel_prompt(item)

    def finalise_purchase(self, item):
        self.debug('→ Entering finalise_purchase')

        # Always calculate in cp
        cost_cp = self.convo.discount if self.convo.discount is not None else item['base_price_cp']

        if self.party_data['party_balance_cp'] < cost_cp:
            return self.agent.shopkeeper_buy_failure_prompt(
                item,
                'Balance too low.',
                self.party_data['party_balance_cp']
            )

        self.party_data['party_balance_cp'] -= cost_cp
        update_party_balance_cp(self.party_id, self.party_data['party_balance_cp'])

        saved_cp = item['base_price_cp'] - cost_cp
        note = f' (you saved {self.agent.format_gp_cp(saved_cp)})' if saved_cp > 0 else ''

        record_transaction(
            party_id=self.party_id,
            character_id=self.player_id,
            item_name=item['item_name'],
            amount=-cost_cp,
            action='BUY',
            balance_after=self.party_data['party_balance_cp'],
            details=f'Purchased item{note}'
        )

        self.debug('← Exiting finalise_purchase')
        return self.agent.shopkeeper_buy_success_prompt(item, cost_cp)

    handle_buy_confirm = handle_confirm_purchase
