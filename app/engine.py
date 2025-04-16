# app/engine.py

from app.models.items import get_item_by_name
from app.models.parties import get_party_by_id, update_party_gold
from app.db import execute_db
from app.dm_commands import handle_dm_command
from app.interpreter import interpret_input, find_item_in_input
from app.conversation import ConversationState, PlayerIntent


class GameEngine:
    def __init__(self, party_id, player_id, agent):
        self.party_id = party_id
        self.player_id = player_id
        self.agent = agent

    def agent_says(self, message):
        print(message)

    def handle_player_input(self, player_input, player, convo):
        # Handle DM Command override
        if player_input.lower().startswith("dm "):
            response = handle_dm_command(self.party_id, self.player_id, player_input)
            self.agent_says(response)
            return

        interpreted = interpret_input(player_input)
        intent = interpreted['intent']
        item_name = interpreted.get('item')

        convo.set_intent(intent)
        convo.set_input(player_input)

        # Debug state before logic
        convo.debug()

        # BUY CONFIRMATION
        if convo.state == ConversationState.AWAITING_CONFIRMATION and convo.pending_action == 'BUY_ITEM' and convo.pending_item:
            if intent == PlayerIntent.CONFIRM:
                return self.handle_buy_confirmation(player, convo)

            elif intent == PlayerIntent.CANCEL:
                self.agent_says(self.agent.shopkeeper_buy_cancel_prompt({'item_name': convo.pending_item}))
                convo.reset_state()
                return

            else:
                item = get_item_by_name(convo.pending_item)
                self.agent_says(self.agent.shopkeeper_buy_confirm_prompt(item, player['party_gold']))
                return

        # AWAITING ITEM CHOICE
        if convo.state == ConversationState.AWAITING_ITEM_SELECTION and convo.pending_action == 'BUY_ITEM':
            return self.handle_buy_item_selection(player_input, player, convo)

        # BUY WITHOUT ITEM
        if intent == PlayerIntent.BUY_NEEDS_ITEM:
            convo.set_intent(PlayerIntent.BUY_ITEM)
            convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
            self.agent_says(self.agent.shopkeeper_buy_enquire_item())
            return

        # BUY WITH ITEM
        if intent == PlayerIntent.BUY_ITEM:
            if not item_name:
                convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                self.agent_says(self.agent.shopkeeper_clarify_item_prompt())
                return

            item = get_item_by_name(item_name)
            if not item:
                self.agent_says(f"'{item_name}' isn't something I sell. Try again.")
                convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                return

            return self.handle_buy_intent
