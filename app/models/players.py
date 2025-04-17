from app.db import query_db

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
    sql = "SELECT player_id FROM players WHERE LOWER(player_name) = ? AND passcode = ?"
    result = query_db(sql, (name.lower(), passcode), one=True)
    print(f"[DEBUG] Validating login: name='{name}', passcode='{passcode}' => result: {result}")
    return result["player_id"] if result else None




