# app/shop_service.py

from app.shop import buy_item, sell_item, haggle, deposit_gold, withdraw_gold
from app.models.items import get_all_items
from app.models.ledger import get_last_transactions
from app.models.parties import get_party_by_id

def handle_buy(party_id, player_id, item_name):
    result = buy_item(party_id, player_id, item_name)
    if result['success']:
        return result['message'], f"[-{result['cost']} Gold] [+1 {item_name}] Party Gold: {get_party_by_id(party_id)['party_gold']}"
    else:
        return result['message'], None

def handle_sell(party_id, player_id, item_name, estimated_value):
    result = sell_item(party_id, player_id, item_name, estimated_value)
    return result['message']

def handle_haggle(party_id, item_name):
    result = haggle(party_id, item_name)
    return result['message']

def handle_view_items():
    items = get_all_items()
    item_list = "\n=== Shop Items ===\n"
    for item in items:
        item_list += f"{item['item_name']} - {item['base_price']} gold - {item['rarity']}\n"
    return item_list

def handle_view_ledger(party_id):
    transactions = get_last_transactions(party_id)
    if not transactions:
        return "Hah! No transactions yet."

    output = "\n=== Recent Transactions ===\n"
    for t in transactions:
        output += (
            f"{t['timestamp']} | {t['action']} | {t['item_name'] or ''} | {t['amount']} gold | Balance After: {t['balance_after']} | {t['details']}\n"
        )
    return output

def handle_check_balance(party_id):
    party = get_party_by_id(party_id)
    return f"Your party has {party['party_gold']} gold."
