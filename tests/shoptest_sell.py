from app.shop_functions import sell_item
from app.models.parties import get_party_by_id
party_id = 'group_001'
player_id = 1
print("=== Attempt to Sell 'Goblin Tooth Necklace' for 10 gold ===")
result = sell_item(party_id, player_id, 'Goblin Tooth Necklace', 10)
print(result['message'])
party = get_party_by_id(party_id)
print(f"Party Gold After Sale: {party['party_gold']}")
