from app.db import query_db, execute_db

def get_all_players_in_party(party_id):
    sql = "SELECT * FROM players WHERE party_id = ?"
    return query_db(sql, (party_id,))

def get_player_by_id(player_id):
    sql = "SELECT * FROM players WHERE player_id = ?"
    return query_db(sql, (player_id,), one=True)


def get_player_name_by_id(player_id):
    sql = "SELECT player_name FROM players WHERE player_id = ?"
    return query_db(sql, (player_id,), one=True)

def get_player_id_by_name(player_name):
    sql = "SELECT player_id FROM players WHERE player_name = ?"
    row = query_db(sql, (player_name,), one=True)
    return row["player_id"] if row else None

def validate_login_credentials(name, passcode):
    sql = "SELECT player_id FROM players WHERE LOWER(player_name) = LOWER(?) AND passcode = ?"
    result = query_db(sql, (name, passcode), one=True)
    print(f"[DEBUG] Validating login: name='{name}', passcode='{passcode}' => result: {result}")
    return result["player_id"] if result else None

def add_player_to_party(party_id, player_name, passcode, character_name=None, role=None):
    # Check if user already exists
    sql_check = "SELECT player_id FROM players WHERE LOWER(player_name) = ? AND party_id = ?"
    existing = query_db(sql_check, (player_name.lower(), party_id), one=True)

    if existing:
        print(f"[INFO] Player '{player_name}' already exists in this party.")
        return None

    sql_insert = """
        INSERT INTO players (party_id, player_name, character_name, role, passcode)
        VALUES (?, ?, ?, ?, ?)
    """
    execute_db(sql_insert, (party_id, player_name, character_name, role, passcode))

    print(f"[INFO] New player '{player_name}' added successfully!")
    # Fetch the new player ID
    new_player = query_db("SELECT player_id FROM players WHERE LOWER(player_name) = ? AND party_id = ?",
                          (player_name.lower(), party_id), one=True)
    return new_player["player_id"] if new_player else None



