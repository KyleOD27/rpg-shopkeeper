from app.db import query_db, execute_db

def get_last_transactions(party_id, limit=10):
    sql = """
        SELECT
            l.*,
            c.player_name
        FROM transaction_ledger l
        LEFT JOIN characters c ON l.character_id = c.character_id
        WHERE l.party_id = ?
        ORDER BY l.timestamp DESC
        LIMIT ?
    """
    return query_db(sql, (party_id, limit))


def record_transaction(
    party_id,
    character_id,
    item_name,
    amount,
    action,
    balance_after=None,
    details=None
):
    execute_db("""
        INSERT INTO transaction_ledger (
            party_id, character_id, item_name, amount, action, balance_after, details
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        party_id,
        character_id,
        item_name,
        amount,
        action,
        balance_after,
        details
    ))
