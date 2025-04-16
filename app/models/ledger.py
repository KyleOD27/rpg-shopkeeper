from app.db import query_db

def get_last_transactions(party_id, limit=10):
    sql = """
        SELECT * FROM transaction_ledger
        WHERE party_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """
    return query_db(sql, (party_id, limit))

from app.db import execute_db  # Make sure this is available for write ops

def record_transaction(party_id, player_id, item_name, amount, action):
    sql = """
        INSERT INTO transaction_ledger (party_id, player_id, item_name, amount, action, timestamp)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """
    params = (party_id, player_id, item_name, amount, action)
    execute_db(sql, params)
