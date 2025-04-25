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

# Get all items in a given equipment category (case-insensitive match)
def get_items_by_category(category):
    sql = """
    SELECT item_name, base_price
    FROM items
    WHERE LOWER(equipment_category) LIKE LOWER(?) OR LOWER(item_name) LIKE LOWER(?)
    ORDER BY item_name
    """
    return query_db(sql, (f"%{category}%", f"%{category}%"))


    if not rows:
        return [f"Hmm... looks like we don't have anything in the '{category}' category right now."]

    lines = [f"Here's what we have in the **{category}** category:\n"]
    for row in rows:
        item = dict(row)
        name = item.get("item_name", "Unknown Item")
        price = item.get("base_price", "?")
        lines.append(f" • {name} — {price} gold")

    return lines

def get_all_equipment_categories():
    sql = """
    SELECT DISTINCT equipment_category
    FROM items
    WHERE equipment_category IS NOT NULL
    ORDER BY equipment_category
    """
    rows = query_db(sql)
    return [row["equipment_category"] for row in rows if row["equipment_category"]]


def get_weapon_categories():
    sql = """
    SELECT DISTINCT weapon_category
    FROM items
    WHERE equipment_category = 'Weapon'
      AND weapon_category IS NOT NULL
    ORDER BY weapon_category
    """
    rows = query_db(sql)
    return [row["weapon_category"] for row in rows if row["weapon_category"]]



def get_armour_categories():
    return [
        "Light Armor",
        "Medium Armor",
        "Heavy Armor",
        "Shield"
    ]

def get_items_by_weapon_category(weapon_category, page=1, page_size=10):
    offset = (page - 1) * page_size
    query = """
        SELECT item_name, base_price
        FROM items
        WHERE LOWER(weapon_category) LIKE LOWER(?)
        ORDER BY item_name
        LIMIT ? OFFSET ?
    """
    return query_db(query, (f"%{weapon_category}%", page_size, offset))

def get_weapon_categories_from_db():
    sql = """
    SELECT DISTINCT weapon_category
    FROM items
    WHERE weapon_category IS NOT NULL
    ORDER BY weapon_category
    """
    rows = query_db(sql)
    return [row["weapon_category"] for row in rows if row["weapon_category"]]

