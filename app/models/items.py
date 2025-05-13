from app.db import query_db


def get_all_items():
    sql = 'SELECT * FROM items'
    return query_db(sql)


def get_item_by_name(item_name):
    sql = """
    SELECT * FROM items
    WHERE LOWER(item_name) = LOWER(?)
    """
    return query_db(sql, (item_name,), one=True)

def get_item_by_normalised_name(item_name):
    sql = """
    SELECT * FROM items
    WHERE LOWER(normalised_item_name) = LOWER(?)
    """
    return query_db(sql, (item_name,), one=True)


def get_item_by_id(item_id):
    sql = """
    SELECT * FROM items
    WHERE item_id = ?
    """
    return query_db(sql, (item_id,), one=True)


def get_items_by_category(category):
    sql = """
    SELECT item_name, base_price
    FROM items
    WHERE LOWER(equipment_category) LIKE LOWER(?) OR LOWER(item_name) LIKE LOWER(?)
    ORDER BY item_name
    """
    return query_db(sql, (f'%{category}%', f'%{category}%'))
    if not rows:
        return [
            f"Hmm... looks like we don't have anything in the '{category}' category right now."
            ]
    lines = [f"Here's what we have in the **{category}** category:\n"]
    for row in rows:
        item = dict(row)
        name = item.get('item_name', 'Unknown Item')
        price = item.get('base_price', '?')
        lines.append(f' • {name} — {price} gold')
    return lines


def get_all_equipment_categories():
    sql = """
    SELECT DISTINCT equipment_category
    FROM items
    WHERE equipment_category IS NOT NULL
    ORDER BY equipment_category
    """
    rows = query_db(sql)
    return [row['equipment_category'] for row in rows if row[
        'equipment_category']]


def get_weapon_categories():
    """Return distinct category_range values (lower-case)."""
    rows = query_db(
        """
        SELECT DISTINCT LOWER(category_range) AS cr
        FROM items
        WHERE category_range IS NOT NULL
        ORDER BY cr
        """
        )
    return [r['cr'] for r in rows]


def get_armour_categories():
    sql = """
    SELECT DISTINCT armour_category
    FROM items
    WHERE equipment_category = 'Armor'
      AND armour_category IS NOT NULL
    ORDER BY armour_category
    """
    rows = query_db(sql)
    return [row['armour_category'] for row in rows if row['armour_category']]


def get_weapon_categories_from_db():
    sql = """
    SELECT DISTINCT weapon_category
    FROM items
    WHERE weapon_category IS NOT NULL
    ORDER BY weapon_category
    """
    rows = query_db(sql)
    return [row['weapon_category'] for row in rows if row['weapon_category']]


def get_gear_categories():
    sql = """
    SELECT DISTINCT gear_category
    FROM items
    WHERE gear_category IS NOT NULL
      AND TRIM(gear_category) != ''
    ORDER BY gear_category
    """
    rows = query_db(sql)
    return [row['gear_category'] for row in rows if row['gear_category']]


def get_tool_categories():
    sql = """
    SELECT DISTINCT tool_category
    FROM items
    WHERE tool_category IS NOT NULL
      AND TRIM(tool_category) != ''
    ORDER BY tool_category
    """
    rows = query_db(sql)
    return [row['tool_category'] for row in rows if row['tool_category']]


def get_items_by_armour_category(armour_category, page=1, page_size=10):
    offset = (page - 1) * page_size
    query = """
        SELECT item_id, item_name, base_price
        FROM items
        WHERE LOWER(armour_category) LIKE LOWER(?)
        ORDER BY item_name
        LIMIT ? OFFSET ?
    """
    return query_db(query, (f'%{armour_category}%', page_size, offset))


def get_items_by_weapon_category(weapon_category, page=1, page_size=10):
    offset = (page - 1) * page_size
    query = """
        SELECT item_id, item_name, base_price
        FROM items
        WHERE LOWER(weapon_category) LIKE LOWER(?)
        ORDER BY item_name
        LIMIT ? OFFSET ?
    """
    return query_db(query, (f'%{weapon_category}%', page_size, offset))


def get_items_by_gear_category(gear_category, page=1, page_size=10):
    offset = (page - 1) * page_size
    query = """
        SELECT item_id, item_name, base_price
        FROM items
        WHERE LOWER(gear_category) LIKE LOWER(?)
        ORDER BY item_name
        LIMIT ? OFFSET ?
    """
    return query_db(query, (f'%{gear_category}%', page_size, offset))


def get_items_by_tool_category(gear_category, page=1, page_size=10):
    offset = (page - 1) * page_size
    query = """
        SELECT item_id, item_name, base_price
        FROM items
        WHERE LOWER(tool_category) LIKE LOWER(?)
        ORDER BY item_name
        LIMIT ? OFFSET ?
    """
    return query_db(query, (f'%{gear_category}%', page_size, offset))


def get_items_by_mount_category(equipment_category, page=1, page_size=10):
    offset = (page - 1) * page_size
    query = """
        SELECT item_id, item_name, base_price
        FROM items
        WHERE LOWER(equipment_category) LIKE LOWER(?)
        ORDER BY item_name
        LIMIT ? OFFSET ?
    """
    return query_db(query, (f'%{equipment_category}%', page_size, offset))


def search_items_by_name_fuzzy(item_name, page=1, page_size=10):
    offset = (page - 1) * page_size
    sql = """
        SELECT item_id, item_name, base_price
        FROM items
        WHERE LOWER(item_name) LIKE LOWER(?)
        ORDER BY item_name
        LIMIT ? OFFSET ?
    """
    return query_db(sql, (f'%{item_name}%', page_size, offset))


def get_items_by_weapon_range(cat_range: str, page=1, page_size=10):
    offset = (page - 1) * page_size
    return query_db(
        """
        SELECT item_id, item_name, base_price
        FROM items
        WHERE LOWER(category_range) = LOWER(?)
        ORDER BY item_name
        LIMIT ? OFFSET ?
        """
        , (cat_range, page_size, offset))
