# tests/select_all_items_test.py
from pprint import pprint
from app import db as app_db   # ensures schema + seeded data

def test_select_all_items() -> None:          # ← no arg
    with app_db.get_connection() as conn:
        rows = conn.execute("SELECT * FROM items").fetchall()

    print(f"🔍 Retrieved {len(rows)} items:\n")
    for row in rows[:30]:                     # 30 is plenty for smoke
        pprint(dict(row), sort_dicts=False, width=100)
        print()

    assert len(rows) > 0, "items table is empty!"
