from app.db import query_db, execute_db


def get_visit_count(party_id, shop_id):
    result = query_db(
        """
        SELECT visit_count
        FROM shop_visits
        WHERE party_id = ? AND shop_id = ?
    """
        , (party_id, shop_id), one=True)
    return result['visit_count'] if result else 0


def increment_visit_count(party_id, shop_id):
    current = get_visit_count(party_id, shop_id)
    if current == 0:
        execute_db(
            """
            INSERT INTO shop_visits (party_id, shop_id, visit_count)
            VALUES (?, ?, 1)
        """
            , (party_id, shop_id))
    else:
        execute_db(
            """
            UPDATE shop_visits
            SET visit_count = visit_count + 1
            WHERE party_id = ? AND shop_id = ?
        """
            , (party_id, shop_id))
