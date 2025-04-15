from app.models.items import get_all_items, get_item_by_name

items = get_all_items()

print("=== All Items in Shop ===")
for item in items:
    print(f"{item['item_name']} - {item['base_price']} gold")

print("\n=== Search for 'Bag of Holding' ===")
item = get_item_by_name('Bag of Holding')

if item:
    print(f"Found: {item['item_name']} - {item['description']} - {item['base_price']} gold")
else:
    print("Item not found!")
