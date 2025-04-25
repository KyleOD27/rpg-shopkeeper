import sqlite3
from pathlib import Path
from pprint import pprint

# Locate the DB
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "rpg-shopkeeper.db"

def test_select_equipment_categories(pretty=True):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT armour_category FROM items")
        rows = cursor.fetchall()

        print(f"🔍 Retrieved {len(rows)} items:\n")
        for row in rows[:300]:  # Show top 10 for sanity
            item = dict(row)
            if pretty:
                pprint(item, sort_dicts=False, width=100)
                print()
            else:
                print(item)

if __name__ == "__main__":
    test_select_equipment_categories()
