import csv
from pprint import pprint
from pathlib import Path
from app import db as app_db

def test_select_all_armor() -> None:
    with app_db.get_connection() as conn:
        rows = conn.execute("SELECT * FROM items WHERE equipment_category = 'Armor'").fetchall()

    print(f"🔍 Retrieved {len(rows)} items:\n")
    for row in rows[:30]:  # 30 is plenty for smoke
        pprint(dict(row), sort_dicts=False, width=100)
        print()

    # Export to CSV
    if rows:
        keys = rows[0].keys()
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        output_path = results_dir / "armor_items_export.csv"

        with open(output_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for row in rows:
                writer.writerow(dict(row))

        print(f"✅ Exported to {output_path}")

    assert len(rows) > 0, "items table has no Armor items!"
