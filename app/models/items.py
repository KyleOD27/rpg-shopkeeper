from app.db import query_db

# Get all items in Grizzlebeard's shop
def get_all_items():
    sql = "SELECT * FROM items"
    return query_db(sql)

# Get a single item by its name (case-insensitive search)
def get_item_by_name(item_name):
    sql = """
    SELECT * FROM items
    WHERE LOWER(item_name) = LOWER(?)
    """
    return query_db(sql, (item_name,), one=True)

# Optional: Get a single item by its ID
def get_item_by_id(item_id):
    sql = """
    SELECT * FROM items
    WHERE item_id = ?
    """
    return query_db(sql, (item_id,), one=True)
