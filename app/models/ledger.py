from app.db import query_db

def get_last_transactions(party_id, limit=10):
    sql = """
        SELECT * FROM transaction_ledger
        WHERE party_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """
    return query_db(sql, (party_id, limit))
