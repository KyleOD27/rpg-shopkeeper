from app.interpreter import find_item_in_input, normalize_input
from app.models.items import get_item_by_name
from app.models.parties import update_party_gold
from app.models.ledger import record_transaction
from app.conversation import ConversationState, PlayerIntent
from app.utils.debug import HandlerDebugMixin


class SellHandler(HandlerDebugMixin):

    def __init__(self, convo, agent, party_id, player_id, player_name,
                 party_data):
        # wire up debug proxy before any debug() calls
        self.conversation = convo
        self.debug('→ Entering __init__')

        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.player_id = player_id
        self.player_name = player_name
        self.party_data = party_data
        self.debug('← Exiting __init__')

    def _to_item_dict(self, ref):
        self.debug('→ Entering _to_item_dict')
        if isinstance(ref, dict):
            return ref
        self.debug('← Exiting _to_item_dict')
        return dict(get_item_by_name(str(ref)) or {})

    def _stash_and_confirm(self, item):
        self.debug('→ Entering _stash_and_confirm')
        """Cache the item & move convo into CONFIRM state."""
        self.convo.set_pending_item(item)
        self.convo.set_pending_action(PlayerIntent.SELL_ITEM)
        self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
        self.convo.save_state()
        self.debug('← Exiting _stash_and_confirm')

    def process_sell_item_flow(self, player_input):
        self.debug('→ Entering process_sell_item_flow')
        raw = player_input.get('text', '') if isinstance(player_input, dict
            ) else str(player_input)
        self.convo.clear_pending()
        matches, _ = find_item_in_input(raw, self.convo)
        if not matches:
            self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
            return self.agent.shopkeeper_sell_enquire_item()
        if len(matches) == 1:
            item = self._to_item_dict(matches[0])
            if not item:
                return self.agent.shopkeeper_say(
                    'I don’t recognise that item, sorry!')
            offer_price = round(item.get('base_price', 0) * 0.6)
            self._stash_and_confirm(item)
            return self.agent.shopkeeper_sell_confirm_prompt(item,
                offer_price, self.party_data['party_gold'])
        self.convo.set_pending_item(matches)
        self.convo.set_pending_action(PlayerIntent.SELL_ITEM)
        self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
        self.convo.save_state()
        self.debug('← Exiting process_sell_item_flow')
        return self.agent.shopkeeper_list_matching_items(matches)

    def process_item_selection(self, player_input):
        self.debug('→ Entering process_item_selection')
        choice = player_input.get('text', '').strip()
        pending = self.convo.get_pending_item()
        if not pending:
            self.convo.reset_state()
            return self.agent.shopkeeper_fallback_prompt()
        norm = normalize_input(choice)
        if isinstance(pending, list):
            item = next((i for i in pending if str(i['item_id']) == norm or
                normalize_input(i['item_name']) == norm), None)
        else:
            item = pending
        if not item:
            return self.agent.shopkeeper_say(
                'I couldn’t find that in your inventory — try the full name or ID.'
                )
        offer = round(item.get('base_price', 0) * 0.6)
        self._stash_and_confirm(item)
        self.debug('← Exiting process_item_selection')
        return self.agent.shopkeeper_sell_confirm_prompt(item, offer)

    def handle_confirm_sale(self, _):
        self.debug('→ Entering handle_confirm_sale')
        item = self._to_item_dict(self.convo.pending_item)
        if not item:
            return self.agent.shopkeeper_say(
                'Something went wrong — I can’t find that item.')
        self.debug('← Exiting handle_confirm_sale')
        return self._finalise_sale(item)

    def handle_cancel_sale(self, _):
        self.debug('→ Entering handle_cancel_sale')
        item = self._to_item_dict(self.convo.pending_item)
        self.convo.reset_state()
        self.convo.clear_pending()
        self.debug('← Exiting handle_cancel_sale')
        return self.agent.shopkeeper_sell_cancel_prompt(item)

    def _finalise_sale(self, item):
        self.debug('→ Entering _finalise_sale')
        offer_price = round(item.get('base_price', 0) * 0.6)
        name = item.get('item_name') or item.get('name') or item.get('title')
        self.party_data['party_gold'] += offer_price
        update_party_gold(self.party_id, self.party_data['party_gold'])
        record_transaction(party_id=self.party_id, character_id=self.
            player_id, item_name=name, amount=offer_price, action='SELL',
            balance_after=self.party_data['party_gold'], details='Sold item')
        self.convo.reset_state()
        self.convo.clear_pending()
        self.debug('← Exiting _finalise_sale')
        return self.agent.shopkeeper_sell_success_prompt(item, offer_price,
            self.party_data['party_gold'])
