from app.shop_functions import deposit_gold, withdraw_gold
from app.models.parties import get_party_by_id
party_id = 'group_001'
player_id = 1
print('=== Deposit 30 Gold ===')
result = deposit_gold(party_id, player_id, 30)
print(result['message'])
print('=== Withdraw 20 Gold ===')
result = withdraw_gold(party_id, player_id, 20)
print(result['message'])
party = get_party_by_id(party_id)
print(f"Party Gold After Transactions: {party['party_gold']}")
