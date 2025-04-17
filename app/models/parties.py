from app.db import query_db, execute_db

# Get a party's data by ID (gold, reputation etc.)
def get_party_by_id(party_id):
    sql = "SELECT * FROM parties WHERE party_id = ?"
    return query_db(sql, (party_id,), one=True)

# Update a party's gold balance
def update_party_gold(party_id, new_gold_amount):
    sql = "UPDATE parties SET party_gold = ? WHERE party_id = ?"
    execute_db(sql, (new_gold_amount, party_id))

# Update a party's reputation score (change can be + or -)
def update_reputation(party_id, change):
    # Get current reputation
    party = get_party_by_id(party_id)
    if not party:
        raise ValueError("Party not found")

    current_rep = party['reputation_score']
    new_rep = current_rep + change

    # Enforce limits (-5 to +5)
    new_rep = max(-5, min(new_rep, 5))

    sql = "UPDATE parties SET reputation_score = ? WHERE party_id = ?"
    execute_db(sql, (new_rep, party_id))

# Create New Party
def create_party(party_id, party_name, starting_gold=100):
    sql = """
        INSERT INTO parties (party_id, party_name, party_gold, reputation_score)
        VALUES (?, ?, ?, 0)
    """
    execute_db(sql, (party_id, party_name, starting_gold))

# Add Player to Existing Party
def add_player_to_party(party_id, player_name, character_name, role, passcode):
    sql = """
        INSERT INTO players (party_id, player_name, character_name, role, passcode)
        VALUES (?, ?, ?, ?, ?)
    """
    try:
        execute_db(sql, (party_id, player_name, character_name, role, passcode))
        print(f"[DEBUG] Player '{player_name}' added to party '{party_id}'.")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to add player to party: {e}")
        return False

def get_party_by_id(party_id: str):
    return query_db(
        "SELECT * FROM parties WHERE party_id = ?", (party_id,), one=True
    )

def update_party_gold(party_id: str, new_gold: int):
    execute_db(
        "UPDATE parties SET party_gold = ? WHERE party_id = ?",
        (new_gold, party_id)
    )

def get_all_parties():
    sql = "SELECT party_id, party_name FROM parties"
    return query_db(sql)

def generate_next_party_id():
    result = query_db("SELECT COUNT(*) as count FROM parties", one=True)
    next_id = result["count"] + 1
    return f"group_{str(next_id).zfill(3)}"  # e.g. group_001, group_002

def add_new_party(party_name):
    party_id = generate_next_party_id()
    try:
        sql = """
            INSERT INTO parties (party_id, party_name, party_gold, reputation_score)
            VALUES (?, ?, 100, 0)
        """
        execute_db(sql, (party_id, party_name))
        print(f"[INFO] Party '{party_name}' created with ID '{party_id}'")
        return party_id
    except Exception as e:
        print(f"[ERROR] Failed to add party: {e}")
        return None


