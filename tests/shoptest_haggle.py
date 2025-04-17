from app.shop_functions import haggle

party_id = 'group_001'

print("=== Attempt to Haggle for 'Bag of Holding' ===")

result = haggle(party_id, 'Bag of Holding')

print(result['message'])
