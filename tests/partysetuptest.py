from app.models.parties import create_party, add_player_to_party, get_party_by_id
from app.models.characters import get_all_players_in_party

party_id = 'group_002'

print("=== Creating New Party ===")

create_party(party_id, 'The Ale-Forged')

add_player_to_party(party_id, 'Daisy', 'Petalstorm', 'Druid')
add_player_to_party(party_id, 'Ragnar', 'The Red', 'Fighter')

party = get_party_by_id(party_id)
print(f"Party Created: {party['party_name']} with {party['party_gold']} gold.")

print("\n=== Party Members ===")
players = get_all_players_in_party(party_id)

for p in players:
    print(f"{p['character_name']} ({p['role']})")
