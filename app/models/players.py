from app.db import query_db

def get_all_players_in_party(party_id):
    sql = "SELECT * FROM players WHERE party_id = ?"
    return query_db(sql, (party_id,))
