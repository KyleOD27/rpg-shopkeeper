from app.models.items import get_item_by_name, get_all_items
from app.models.parties import get_party_by_id, update_party_gold, update_reputation
from app.db import execute_db
import random
from difflib import get_close_matches

# Buy Item Function
def buy_item(party_id, player_id, item_name):
    item = get_item_by_name(item_name)

    if not item:
        return {
            "success": False,
            "message": f"Item '{item_name}' not found in the shop."
        }

    price = item['base_price']

    party = get_party_by_id(party_id)

    if not party:
        return {
            "success": False,
            "message": "Party not found."
        }

    current_gold = party['party_gold']

    if current_gold < price:
        return {
            "success": False,
            "message": f"Not enough gold. You have {current_gold} gold, but {item['item_name']} costs {price} gold."
        }

    new_gold = current_gold - price
    update_party_gold(party_id, new_gold)

    execute_db("""
        INSERT INTO transaction_ledger (party_id, player_id, action, item_name, amount, balance_after, details)
        VALUES (?, ?, 'BUY', ?, ?, ?, ?)
    """, (party_id, player_id, item['item_name'], -price, new_gold, f"Purchased {item['item_name']}"))

    return {
        "success": True,
        "message": f"You bought {item['item_name']} for {price} gold. Party gold remaining: {new_gold}.",
        "cost": price
    }


# Sell Item Function
def sell_item(party_id, player_id, item_name, estimated_value):
    party = get_party_by_id(party_id)

    if not party:
        return {"success": False, "message": "Party not found."}

    current_gold = party['party_gold']

    gold_earned = estimated_value
    new_gold = current_gold + gold_earned

    update_party_gold(party_id, new_gold)

    execute_db("""
        INSERT INTO transaction_ledger (party_id, player_id, action, item_name, amount, balance_after, details)
        VALUES (?, ?, 'SELL', ?, ?, ?, ?)
    """, (party_id, player_id, item_name, gold_earned, new_gold, f"Sold {item_name}"))

    update_reputation(party_id, 1)

    return {"success": True, "message": f"You sold {item_name} for {gold_earned} gold. Party gold now: {new_gold}."}


# Haggle Function
def haggle(party_id, item_name):
    item = get_item_by_name(item_name)

    if not item:
        return {"success": False, "message": f"Item '{item_name}' not found in the shop."}

    base_price = item['base_price']
    party = get_party_by_id(party_id)

    if not party:
        return {"success": False, "message": "Party not found."}

    rep_bonus = party['reputation_score']
    roll = random.randint(1, 20)
    total = roll + rep_bonus

    message = f"Haggling roll: d20 ({roll}) + Rep Bonus ({rep_bonus}) = {total}\n"

    if roll == 1:
        final_price = int(base_price * 1.25)
        message += f"Disaster! Grizzlebeard raises the price to {final_price} gold!"
    elif total <= 9:
        final_price = base_price
        message += f"No luck. The price stays at {final_price} gold."
    elif total <= 14:
        final_price = int(base_price * 0.9)
        message += f"Minor success. Grizzlebeard offers it for {final_price} gold."
    elif total <= 19:
        final_price = int(base_price * 0.8)
        message += f"Good success! Grizzlebeard offers it for {final_price} gold."
    else:
        final_price = int(base_price * 0.7)
        message += f"Critical success! Grizzlebeard is impressed. Price is {final_price} gold."

    return {"success": True, "message": message, "original_price": base_price, "final_price": final_price}


# Deposit Gold Function
def deposit_gold(party_id, player_id, amount):
    if amount <= 0:
        return {"success": False, "message": "Deposit amount must be positive."}

    party = get_party_by_id(party_id)

    if not party:
        return {"success": False, "message": "Party not found."}

    new_gold = party['party_gold'] + amount
    update_party_gold(party_id, new_gold)

    execute_db("""
        INSERT INTO transaction_ledger (party_id, player_id, action, amount, balance_after, details)
        VALUES (?, ?, 'DEPOSIT', ?, ?, ?)
    """, (party_id, player_id, amount, new_gold, f"Deposited {amount} gold to the Party Stash"))

    return {"success": True, "message": f"Deposited {amount} gold. Party gold now: {new_gold}."}


# Withdraw Gold Function
def withdraw_gold(party_id, player_id, amount):
    if amount <= 0:
        return {"success": False, "message": "Withdraw amount must be positive."}

    party = get_party_by_id(party_id)

    if not party:
        return {"success": False, "message": "Party not found."}

    if party['party_gold'] < amount:
        return {"success": False, "message": f"Not enough gold. Party has {party['party_gold']} gold."}

    new_gold = party['party_gold'] - amount
    update_party_gold(party_id, new_gold)

    execute_db("""
        INSERT INTO transaction_ledger (party_id, player_id, action, amount, balance_after, details)
        VALUES (?, ?, 'WITHDRAW', ?, ?, ?)
    """, (party_id, player_id, -amount, new_gold, f"Withdrew {amount} gold from the Party Stash"))

    return {"success": True, "message": f"Withdrew {amount} gold. Party gold now: {new_gold}."}

# Fuzzy match item name from player input
def find_closest_item_name(player_input: str):
    items = get_all_items()
    item_names = [item['item_name'] for item in items]

    matches = get_close_matches(player_input.lower(), item_names, n=1, cutoff=0.6)

    return matches[0] if matches else None
