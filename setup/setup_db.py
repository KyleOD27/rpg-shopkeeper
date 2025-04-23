import sqlite3
from pathlib import Path

# Always resolve from script location upward
BASE_DIR = Path(__file__).resolve().parent.parent  # go from /setup to project root
DB_PATH = BASE_DIR / "rpg-shopkeeper.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
SEED_PATH = BASE_DIR / "database" / "seed_data.sql"

# Create or connect to DB
with sqlite3.connect(DB_PATH) as conn:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    print("✅ Schema created successfully!")

with sqlite3.connect(DB_PATH) as conn:
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    print("✅ Database seeded with test data!")
