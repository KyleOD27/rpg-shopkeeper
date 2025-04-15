# app/actions/buy.py

from app.models.items import get_item_by_name
from app.models.parties import get_party_by_id, update_party_gold
from app.db import execute_db
from app.interpreter import find_item_in_input
from app.conversation import ConversationState, PlayerIntent


def handle_buy_intent(player_input, player, convo, engine, item_name):
    item = get_item_by_name(item_name)
    if not item:
        engine.agent_says(engine.agent.generate_clarify_item_prompt())
        convo.set_intent(PlayerIntent.BUY_ITEM)
        convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
        return

    # Set only the item name (string) in conversation state
    convo.set_intent(PlayerIntent.BUY_ITEM)
    convo.set_pending_item(item_name)
    convo.set_state(ConversationState.AWAITING_CONFIRMATION)

    engine.agent_says(engine.agent.generate_buy_confirmation_prompt(item, player['party_gold']))


def handle_buy_item_selection(player_input, player, convo, engine):
    item_name, _ = find_item_in_input(player_input)
    if not item_name:
        engine.agent_says(engine.agent.generate_clarify_item_prompt())
        return

    handle_buy_intent(player_input, player, convo, engine, item_name)


def handle_buy_confirmation(player_input, player, convo, engine):
    item_name = convo.pending_item
    item = get_item_by_name(item_name)

    if not item:
        engine.agent_says("Something went wrong — item not found.")
        convo.reset_state()
        return

    result = buy_item(player['party_id'], player['id'], item_name)

    if result['success']:
        engine.agent_says(engine.agent.generate_buy_success_prompt(item, result['message']))
    else:
        engine.agent_says(engine.agent.generate_buy_failure_prompt(item, result['message']))

    convo.reset_state()


def buy_item(party_id, player_id, item_name):
    item = get_item_by_name(item_name)
    if not item:
        return {"success": False, "message": f"Item '{item_name}' not found."}

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
        (party_id, player_id, item_name, -price, new_gold, f"Purchased {item_name}")
    )

    return {"success": True, "message": f"Bought {item_name} for {price} gold. Remaining gold: {new_gold}."}
