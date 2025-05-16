"""
Initialises the SQLite database with the tables the app expects.
Run once:  python tools/init_db.py
"""

from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
DB    = ROOT / "data" / "shopkeeper.db"        # tweak the path if needed

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    phone       TEXT UNIQUE NOT NULL,
    name        TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- add more tables here (inventory, orders, etc.)
"""

def main():
    DB.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB) as conn:
        conn.executescript(SCHEMA)
    print(f"✓ Database initialised at {DB}")

if __name__ == "__main__":
    main()
