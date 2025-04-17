from app.db import query_db

def get_last_transactions(party_id, limit=10):
    sql = """
        SELECT
            l.*,
            p.player_name
        FROM transaction_ledger l
        LEFT JOIN players p ON l.player_id = p.player_id
        WHERE l.party_id = ?
        ORDER BY l.timestamp DESC
        LIMIT ?
    """
    return query_db(sql, (party_id, limit))


from app.db import execute_db  # Make sure this is available for write ops

def record_transaction(
    party_id,
    player_id,
    item_name,
    amount,
    action,
    balance_after=None,
    details=None
):
    execute_db("""
        INSERT INTO transaction_ledger (
            party_id, player_id, item_name, amount, action, balance_after, details
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        party_id,
        player_id,
        item_name,
        amount,
        action,
        balance_after,
        details
    ))

