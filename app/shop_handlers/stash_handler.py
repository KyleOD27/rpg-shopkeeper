from app.interpreter import find_item_in_input, normalize_input
from app.models.party_stash import add_item_to_stash, get_party_stash, remove_item_from_stash
from app.models.ledger import record_transaction
from app.conversation import PlayerIntent, ConversationState
from app.utils.debug import HandlerDebugMixin

class StashHandler(HandlerDebugMixin):
    def __init__(self, agent, party_data, convo, party_id, character_id):
        self.conversation = convo
        self.convo = convo
        self.agent = agent
        self.party_data = party_data
        self.party_id = party_id
        self.character_id = character_id
        self.character_name = self.party_data.get('character_name', 'Someone')

    def process_stash_add_flow(self, player_input):
        self.debug('→ Entering process_stash_add_flow')
        raw = player_input.get('text', '') if isinstance(player_input, dict) else player_input
        item_name = player_input.get('item') if isinstance(player_input, dict) else None
        self.convo.clear_pending()
        if not item_name:
            matches, _ = find_item_in_input(raw, self.convo)
            if matches:
                if len(matches) == 1:
                    item = matches[0]
                    self._stash_and_confirm(item)
                    return self.agent.shopkeeper_generic_say(
                        f"Add *{item['item_name']}* to the party stash? (yes/no)")
                self.convo.set_pending_item(matches)
                self.convo.set_pending_action(PlayerIntent.STASH_ADD)
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                self.convo.save_state()
                return self.agent.shopkeeper_list_matching_items(matches)
            else:
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                self.convo.save_state()
                return self.agent.shopkeeper_generic_say(
                    "What item would you like to add to the stash?")
        item = item_name
        if isinstance(item, list):
            if len(item) == 1:
                item = item[0]
            elif len(item) > 1:
                item = item[0]
        self._stash_and_confirm(item)
        return self.agent.shopkeeper_generic_say(
            f"Add *{item['item_name']}* to the party stash? (yes/no)")

    def process_stash_item_selection(self, player_input):
        self.debug('→ Entering process_stash_item_selection')
        choice = player_input.get('text', '').strip()
        for p in ('stash ', 'add ', 'select ', 'pick ', 'choose '):
            if choice.lower().startswith(p):
                choice = choice[len(p):].lstrip()
                break
        pending = self.convo.pending_item
        if not pending:
            return self.agent.shopkeeper_generic_say(
                'I’m not sure which item you mean. Try the full name or its ID number.')
        norm = normalize_input(choice)
        item = None
        if isinstance(pending, list):
            item = next((i for i in pending if str(i['item_id']) == norm or
                         normalize_input(i['item_name']) == norm), None)
        else:
            item = pending
        if not item:
            return self.agent.shopkeeper_generic_say(
                "I couldn't find that item in the options. Please say the full name or ID.")
        self._stash_and_confirm(item)
        return self.agent.shopkeeper_generic_say(
            f"Add *{item['item_name']}* to the party stash? (yes/no)")

    def _stash_and_confirm(self, item):
        self.debug('→ Entering _stash_and_confirm')
        self.convo.set_pending_item(item)
        self.convo.set_pending_action(PlayerIntent.STASH_ADD)
        self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
        self.convo.save_state()
        self.debug('← Exiting _stash_and_confirm')

    def handle_confirm_stash_add(self, player_input):
        self.debug('→ Entering handle_confirm_stash_add')
        item = self.convo.pending_item
        if not item:
            return self.agent.shopkeeper_generic_say(
                "Something went wrong—no item selected for stashing.")
        add_item_to_stash(self.party_id, self.character_id, item['item_id'], item['item_name'])
        # === Ledger: record stash add ===
        record_transaction(
            party_id=self.party_id,
            character_id=self.character_id,
            item_name=item['item_name'],
            amount=None,
            action='STASH_ADD',
            balance_after=None,
            details=f"{self.character_name} added to party stash"
        )
        self.convo.reset_state()
        self.convo.set_pending_item(None)
        self.convo.set_state(ConversationState.AWAITING_ACTION)
        self.convo.save_state()
        self.debug('← Exiting handle_confirm_stash_add')
        return self.agent.shopkeeper_generic_say(
            f"Added *{item['item_name']}* to the party stash!")

    def handle_view_stash(self, player_input):
        self.debug('→ Entering handle_view_stash')
        stash = get_party_stash(self.party_id)
        if not stash:
            return self.agent.shopkeeper_generic_say("🧰 Your party stash is empty!")
        lines = ["🧰 *Party Stash:*"]
        for entry in stash:
            qty = entry.get('quantity', 1)
            item_name = entry['item_name']
            lines.append(f"• {item_name} x{qty}")
        self.debug('← Exiting handle_view_stash')
        return "\n".join(lines)

    def process_stash_remove_flow(self, player_input):
        self.debug('→ Entering process_stash_remove_flow')
        raw = player_input.get('text', '') if isinstance(player_input, dict) else player_input
        item_name = player_input.get('item') if isinstance(player_input, dict) else None
        self.convo.clear_pending()
        if not item_name:
            matches, _ = find_item_in_input(raw, self.convo)
            if matches:
                if len(matches) == 1:
                    item = matches[0]
                    self._unstash_and_confirm(item)
                    return self.agent.shopkeeper_generic_say(
                        f"Remove *{item['item_name']}* from the party stash? (yes/no)")
                self.convo.set_pending_item(matches)
                self.convo.set_pending_action(PlayerIntent.STASH_REMOVE)
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                self.convo.save_state()
                return self.agent.shopkeeper_list_matching_items(matches)
            else:
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                self.convo.save_state()
                return self.agent.shopkeeper_generic_say(
                    "What item would you like to remove from the stash?")
        item = item_name
        if isinstance(item, list) and len(item) > 0:
            item = item[0]
        self._unstash_and_confirm(item)
        return self.agent.shopkeeper_generic_say(
            f"Remove *{item['item_name']}* from the party stash? (yes/no)")

    def process_stash_remove_item_selection(self, player_input):
        self.debug('→ Entering process_stash_remove_item_selection')
        choice = player_input.get('text', '').strip()
        for p in ('unstash ', 'remove ', 'select ', 'pick ', 'choose '):
            if choice.lower().startswith(p):
                choice = choice[len(p):].lstrip()
                break
        pending = self.convo.pending_item
        if not pending:
            return self.agent.shopkeeper_generic_say(
                'I’m not sure which item you mean. Try the full name or its ID number.')
        norm = normalize_input(choice)
        item = None
        if isinstance(pending, list):
            item = next((i for i in pending if str(i['item_id']) == norm or
                         normalize_input(i['item_name']) == norm), None)
        else:
            item = pending
        if not item:
            return self.agent.shopkeeper_generic_say(
                "I couldn't find that item in the options. Please say the full name or ID.")
        self._unstash_and_confirm(item)
        return self.agent.shopkeeper_generic_say(
            f"Remove *{item['item_name']}* from the party stash? (yes/no)")

    def _unstash_and_confirm(self, item):
        self.debug('→ Entering _unstash_and_confirm')
        self.convo.set_pending_item(item)
        self.convo.set_pending_action(PlayerIntent.STASH_REMOVE)
        self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
        self.convo.save_state()
        self.debug('← Exiting _unstash_and_confirm')

    def handle_confirm_stash_remove(self, player_input):
        self.debug('→ Entering handle_confirm_stash_remove')
        item = self.convo.pending_item
        if not item:
            return self.agent.shopkeeper_generic_say(
                "Something went wrong—no item selected for removal.")
        success = remove_item_from_stash(self.party_id, item['item_id'])
        if success:
            record_transaction(
                party_id=self.party_id,
                character_id=self.character_id,
                item_name=item['item_name'],
                amount=None,
                action='STASH_REMOVE',
                balance_after=None,
                details=f"{self.character_name} removed from party stash"
            )
        self.convo.reset_state()
        self.convo.set_pending_item(None)
        self.convo.set_state(ConversationState.AWAITING_ACTION)
        self.convo.save_state()
        self.debug('← Exiting handle_confirm_stash_remove')
        if success:
            return self.agent.shopkeeper_generic_say(
                f"Removed *{item['item_name']}* from the party stash!")
        else:
            return self.agent.shopkeeper_generic_say(
                f"That item wasn’t found in the party stash.")
