from app.models.parties import get_party_by_id, update_party_gold, update_reputation

party_id = 'group_001'

party = get_party_by_id(party_id)

print("=== Party Details ===")
print(f"Name: {party['party_name']}")
print(f"Gold: {party['party_gold']}")
print(f"Reputation: {party['reputation_score']}")

print("\n=== Spend 50 Gold ===")
update_party_gold(party_id, party['party_gold'] - 50)

party = get_party_by_id(party_id)
print(f"New Gold Balance: {party['party_gold']}")

print("\n=== Increase Reputation by 2 ===")
update_reputation(party_id, 2)

party = get_party_by_id(party_id)
print(f"New Reputation: {party['reputation_score']}")
