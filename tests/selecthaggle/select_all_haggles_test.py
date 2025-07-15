# tests/select_all_ledger_test.py
import csv
from pprint import pprint
from pathlib import Path
from app import db as app_db

def test_select_all_haggle_attempts() -> None:
    with app_db.get_connection() as conn:
        rows = conn.execute("SELECT * FROM haggle_attempts").fetchall()

    print(f"🔍 Retrieved {len(rows)} haggle_attempts:\n")
    for row in rows[:30]:  # 30 is plenty for smoke
        pprint(dict(row), sort_dicts=False, width=100)
        print()

    # Export to CSV
    if rows:
        keys = rows[0].keys()
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        output_path = results_dir / "full_haggle_attempts_export.csv"

        with open(output_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for row in rows:
                writer.writerow(dict(row))

    assert len(rows) > 0, "haggle_attempts table has no haggle attempts!"
