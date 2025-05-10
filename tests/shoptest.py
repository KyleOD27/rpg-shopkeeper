from app.shop_functions import buy_item
from app.models.parties import get_party_by_id
party_id = 'group_001'
player_id = 1
print("=== Attempt to Buy 'Bag of Holding' ===")
result = buy_item(party_id, player_id, 'Bag of Holding')
print(result['message'])
party = get_party_by_id(party_id)
print(f"Party Gold After Purchase: {party['party_gold']}")
