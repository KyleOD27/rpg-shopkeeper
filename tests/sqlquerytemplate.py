from app.db import query_db
items = query_db('SELECT * FROM items')
for item in items:
    print(item['item_name'], '-', item['base_price'], 'cp')
