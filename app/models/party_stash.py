from app.db import query_db, execute_db
from datetime import datetime

__all__ = [
    "add_item_to_stash",
    "get_party_stash",
    "remove_item_from_stash",
    "clear_stash",
]

def add_item_to_stash(party_id, character_id, item_id, item_name, quantity=1):
    # Check if already exists → increment, else insert
    row = query_db(
        """
        SELECT stash_id, quantity FROM party_stash
         WHERE party_id = ? AND item_id = ?
        """,
        (party_id, item_id),
        one=True,
    )
    if row:
        new_qty = row['quantity'] + quantity
        execute_db(
            "UPDATE party_stash SET quantity = ? WHERE stash_id = ?",
            (new_qty, row['stash_id'])
        )
    else:
        execute_db(
            """
            INSERT INTO party_stash
                (party_id, character_id, item_id, item_name, quantity, added_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (party_id, character_id, item_id, item_name, quantity, datetime.utcnow())
        )

def get_party_stash(party_id):
    rows = query_db(
        """
        SELECT * FROM party_stash WHERE party_id = ? ORDER BY added_at DESC
        """,
        (party_id,)
    )
    return [dict(row) for row in rows] if rows else []

def remove_item_from_stash(party_id, item_id, quantity=1):
    row = query_db(
        "SELECT stash_id, quantity FROM party_stash WHERE party_id = ? AND item_id = ?",
        (party_id, item_id),
        one=True,
    )
    if not row:
        return False
    current_qty = row['quantity']
    if current_qty > quantity:
        execute_db(
            "UPDATE party_stash SET quantity = ? WHERE stash_id = ?",
            (current_qty - quantity, row['stash_id'])
        )
    else:
        execute_db(
            "DELETE FROM party_stash WHERE stash_id = ?",
            (row['stash_id'],)
        )
    return True

def clear_stash(party_id):
    execute_db("DELETE FROM party_stash WHERE party_id = ?", (party_id,))
