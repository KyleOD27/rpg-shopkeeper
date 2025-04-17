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

def get_shop_names():
    shops = get_all_shops()
    return [shop["shop_name"] for shop in shops]
