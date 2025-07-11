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


def record_transaction(party_id, character_id, item_name, amount, action,
                      balance_after=None, details=None, currency='gp'):
    execute_db(
        """
        INSERT INTO transaction_ledger (
            party_id, character_id, item_name, amount, action, balance_after, details, currency
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (party_id, character_id, item_name, amount, action, balance_after, details, currency)
    )

def get_last_transaction_for_party(party_id):
    sql = """
        SELECT l.*
        FROM transaction_ledger l
        WHERE l.party_id = ?
        ORDER BY l.timestamp DESC, l.id DESC
        LIMIT 1
    """
    rows = query_db(sql, (party_id,))
    return rows[0] if rows else None

def get_previous_balance_for_party(party_id, before_timestamp):
    sql = """
        SELECT balance_after
        FROM transaction_ledger
        WHERE party_id = ?
          AND timestamp < ?
        ORDER BY timestamp DESC, id DESC
        LIMIT 1
    """
    rows = query_db(sql, (party_id, before_timestamp))
    return rows[0]['balance_after'] if rows else None

def get_last_transaction_for_character(party_id, character_id):
    sql = """
        SELECT l.*
        FROM transaction_ledger l
        WHERE l.party_id = ?
          AND l.character_id = ?
        ORDER BY l.timestamp DESC, l.id DESC
        LIMIT 1
    """
    rows = query_db(sql, (party_id, character_id))
    return rows[0] if rows else None
