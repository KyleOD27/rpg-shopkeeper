from app.models.items import get_item_by_name, get_all_items
from app.models.parties import get_party_by_id, update_party_balance_cp, update_reputation
from app.db import execute_db
import random
from difflib import get_close_matches


def buy_item(party_id, player_id, item_name):
    item = get_item_by_name(item_name)
    if not item:
        return {'success': False, 'message':
            f"Item '{item_name}' not found in the shop."}
    price = item['base_price']
    party = get_party_by_id(party_id)
    if not party:
        return {'success': False, 'message': 'Party not found.'}
    current_balance_cp = party['party_balance_cp']
    if current_balance_cp < price:
        return {'success': False, 'message':
            f"Balance too low. You have {current_balance_cp} cp, but {item['item_name']} costs {price} cp."
            }
    new_balance_cp = current_balance_cp - price
    update_party_balance_cp(party_id, new_balance_cp)
    execute_db(
        """
        INSERT INTO transaction_ledger (party_id, player_id, action, item_name, amount, balance_after, details)
        VALUES (?, ?, 'BUY', ?, ?, ?, ?)
    """
        , (party_id, player_id, item['item_name'], -price, new_balance_cp,
        f"Purchased {item['item_name']}"))
    return {'success': True, 'message':
        f"You bought {item['item_name']} for {price} cp. Party cp remaining: {new_balance_cp}."
        , 'cost': price}


def sell_item(party_id, player_id, item_name, estimated_value):
    party = get_party_by_id(party_id)
    if not party:
        return {'success': False, 'message': 'Party not found.'}
    current_balance_cp = party['party_balance_cp']
    cp_earned = estimated_value
    new_balance_cp = current_balance_cp + cp_earned
    update_party_balance_cp(party_id, new_balance_cp)
    execute_db(
        """
        INSERT INTO transaction_ledger (party_id, player_id, action, item_name, amount, balance_after, details)
        VALUES (?, ?, 'SELL', ?, ?, ?, ?)
    """
        , (party_id, player_id, item_name, cp_earned, new_balance_cp,
        f'Sold {item_name}'))
    update_reputation(party_id, 1)
    return {'success': True, 'message':
        f'You sold {item_name} for {cp_earned} cp. Party cp now: {new_balance_cp}.'
        }


def haggle(party_id, item_name):
    item = get_item_by_name(item_name)
    if not item:
        return {'success': False, 'message':
            f"Item '{item_name}' not found in the shop."}
    base_price = item['base_price']
    party = get_party_by_id(party_id)
    if not party:
        return {'success': False, 'message': 'Party not found.'}
    rep_bonus = party['reputation_score']
    roll = random.randint(1, 20)
    total = roll + rep_bonus
    message = (
        f'Haggling roll: d20 ({roll}) + Rep Bonus ({rep_bonus}) = {total}\n')
    if roll == 1:
        final_price = int(base_price * 1.25)
        message += (
            f'Disaster! Grizzlebeard raises the price to {final_price} cp!')
    elif total <= 9:
        final_price = base_price
        message += f'No luck. The price stays at {final_price} cp.'
    elif total <= 14:
        final_price = int(base_price * 0.9)
        message += (
            f'Minor success. Grizzlebeard offers it for {final_price} cp.')
    elif total <= 19:
        final_price = int(base_price * 0.8)
        message += (
            f'Good success! Grizzlebeard offers it for {final_price} cp.')
    else:
        final_price = int(base_price * 0.7)
        message += (
            f'Critical success! Grizzlebeard is impressed. Price is {final_price} cp.'
            )
    return {'success': True, 'message': message, 'original_price':
        base_price, 'final_price': final_price}


def deposit_cp(party_id, player_id, amount):
    if amount <= 0:
        return {'success': False, 'message': 'Deposit amount must be positive.'
            }
    party = get_party_by_id(party_id)
    if not party:
        return {'success': False, 'message': 'Party not found.'}
    new_balance_cp = party['party_balance_cp'] + amount
    update_party_balance_cp(party_id, new_balance_cp)
    execute_db(
        """
        INSERT INTO transaction_ledger (party_id, player_id, action, amount, balance_after, details)
        VALUES (?, ?, 'DEPOSIT', ?, ?, ?)
    """
        , (party_id, player_id, amount, new_balance_cp,
        f'Deposited {amount} cp to the Party Stash'))
    return {'success': True, 'message':
        f'Deposited {amount} cp. Party balance now: {new_balance_cp}.'}


def withdraw_cp(party_id, player_id, amount):
    if amount <= 0:
        return {'success': False, 'message':
            'Withdraw amount must be positive.'}
    party = get_party_by_id(party_id)
    if not party:
        return {'success': False, 'message': 'Party not found.'}
    if party['party_balance_cp'] < amount:
        return {'success': False, 'message':
            f"Not enough cp. Party has {party['party_balance_cp']} cp."}
    new_balance_cp = party['party_balance_cp] - amount']
    update_party_balance_cp(party_id, new_balance_cp)
    execute_db(
        """
        INSERT INTO transaction_ledger (party_id, player_id, action, amount, balance_after, details)
        VALUES (?, ?, 'WITHDRAW', ?, ?, ?)
    """
        , (party_id, player_id, -amount, new_balance_cp,
        f'Withdrew {amount} cp from the Party Stash'))
    return {'success': True, 'message':
        f'Withdrew {amount} cp. Party balance now: {new_balance_cp} cp.'}


def find_closest_item_name(player_input: str):
    items = get_all_items()
    item_names = [item['item_name'] for item in items]
    matches = get_close_matches(player_input.lower(), item_names, n=1,
        cutoff=0.6)
    return matches[0] if matches else None
