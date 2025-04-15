# app/engine.py

from app.models.items import get_item_by_name
from app.models.parties import get_party_by_id, update_party_gold
from app.db import execute_db
from app.dm_commands import handle_dm_command
from app.interpreter import interpret_input, find_item_in_input
from app.conversation import ConversationState, PlayerIntent
from app.gpt_agent import generate_agent_reply


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

        # Debug state before logic
        convo.debug()

        # Confirmation Flow
        if convo.state == ConversationState.AWAITING_CONFIRMATION and convo.pending_action == 'BUY_ITEM' and convo.pending_item:
            if intent == PlayerIntent.CONFIRM:
                return self.handle_buy_confirmation(player, convo)

            elif intent == PlayerIntent.CANCEL:
                self.agent_says(self.agent.generate_buy_cancel_prompt({'item_name': convo.pending_item}))
                convo.reset_state()
                return

            else:
                item = get_item_by_name(convo.pending_item)
                self.agent_says(self.agent.generate_buy_confirmation_prompt(item, player['party_gold']))
                return

        # Awaiting item choice
        if convo.state == ConversationState.AWAITING_ITEM_SELECTION and convo.pending_action == 'BUY_ITEM':
            return self.handle_buy_item_selection(player_input, player, convo)

        # Handle Buy Intent Without Item
        if intent == 'BUY_NEEDS_ITEM':
            convo.set_intent(PlayerIntent.BUY_ITEM)
            convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
            self.agent_says(self.agent.generate_clarify_item_prompt())
            return

        # Handle Buy Intent With Item
        if intent == PlayerIntent.BUY_ITEM:
            if not item_name:
                convo.set_intent(PlayerIntent.BUY_ITEM)
                convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                self.agent_says(self.agent.generate_clarify_item_prompt())
                return

            item = get_item_by_name(item_name)
            if not item:
                self.agent_says(f"Hmph. '{item_name}' isn't something I sell. Try again.")
                convo.set_intent(PlayerIntent.BUY_ITEM)
                convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                return

            return self.handle_buy_intent(player, convo, item)

        # Fallback: Small Talk / Unknown
        self.agent_says(generate_agent_reply(player_input, state=convo)['data'])

    def handle_buy_intent(self, player, convo, item):
        convo.set_intent(PlayerIntent.BUY_ITEM)
        convo.set_pending_item(item)
        convo.set_state(ConversationState.AWAITING_CONFIRMATION)

        self.agent_says(self.agent.generate_buy_confirmation_prompt(item, player['party_gold']))

    def handle_buy_item_selection(self, player_input, player, convo):
        item_name, _ = find_item_in_input(player_input)
        if not item_name:
            self.agent_says(self.agent.generate_clarify_item_prompt())
            return

        item = get_item_by_name(item_name)
        if not item:
            self.agent_says(self.agent.generate_clarify_item_prompt())
            return

        self.handle_buy_intent(player, convo, item)

    def handle_buy_confirmation(self, player, convo):
        item_name = convo.pending_item
        item = get_item_by_name(item_name)

        if not item:
            self.agent_says("Something went wrong — item vanished from the shelf. Try again.")
            convo.reset_state()
            return

        result = self.buy_item(player['party_id'], self.player_id, item)

        if result['success']:
            self.agent_says(self.agent.generate_buy_success_prompt(item, result['message']))
        else:
            self.agent_says(self.agent.generate_buy_failure_prompt(item, result['message']))

        convo.reset_state()

    def buy_item(self, party_id, player_id, item):
        price = item['base_price']
        party = get_party_by_id(party_id)

        if not party:
            return {"success": False, "message": "Party not found."}

        if party['party_gold'] < price:
            return {"success": False, "message": f"Not enough gold. You have {party['party_gold']} gold."}

        new_gold = party['party_gold'] - price
        update_party_gold(party_id, new_gold)

        execute_db(
            '''
            INSERT INTO transaction_ledger (party_id, player_id, action, item_name, amount, balance_after, details)
            VALUES (?, ?, 'BUY', ?, ?, ?, ?)
            ''',
            (party_id, player_id, item['item_name'], -price, new_gold, f"Purchased {item['item_name']}")
        )

        return {"success": True, "message": f"Bought {item['item_name']} for {price} gold. Remaining gold: {new_gold}."}
