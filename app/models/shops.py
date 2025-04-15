# app/models/shops.py

from app.db import query_db


def get_all_shops():
    sql = """
        SELECT shop_id, shop_name, agent_name, location
        FROM shops
        ORDER BY shop_id ASC
    """
    return query_db(sql)


def get_shop_by_id(shop_id):
    sql = """
        SELECT shop_id, shop_name, agent_name, location
        FROM shops
        WHERE shop_id = ?
    """
    return query_db(sql, (shop_id,), one=True)

# app/models/shops.py

def get_all_shops():
    return [
        {"shop_id": 1, "shop_name": "Grizzlebeard's Emporium", "location": "Stonehelm Market", "agent_name": "Grizzlebeard"},
        {"shop_id": 2, "shop_name": "Merlinda's Curios", "location": "Everspring Forest", "agent_name": "Merlinda"},
        {"shop_id": 3, "shop_name": "Skabfang's Shack", "location": "Goblin Warrens", "agent_name": "Skabfang"},
    ]


def get_shop_by_id(shop_id):
    shops = get_all_shops()
    return next((shop for shop in shops if shop["shop_id"] == shop_id), None)


# Add this:
SHOP_NAMES = [shop["shop_name"] for shop in get_all_shops()]
