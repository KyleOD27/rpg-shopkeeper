import sqlite3
import string
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
DB_PATH    = BASE_DIR / 'rpg-shopkeeper.db'
SCHEMA_PATH = BASE_DIR / 'database' / 'schema.sql'
SEED_PATH   = BASE_DIR / 'database' / 'seed_data.sql'

# ─── Step 1: create schema ─────────────────────────────────────────────────────
with sqlite3.connect(DB_PATH) as conn:
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    print('✅ Schema created successfully!')

# ─── Step 2: seed data ─────────────────────────────────────────────────────────
with sqlite3.connect(DB_PATH) as conn:
    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    print('✅ Database seeded with test data!')

# ─── Step 3: add & populate normalised_item_name ──────────────────────────────
def step2_add_normalised_column(db_path: Path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 3.1) add the new column (ignore if already exists)
    try:
        cursor.execute("""
            ALTER TABLE items
            ADD COLUMN normalised_item_name TEXT;
        """)
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            # already ran once, ignore
            pass
        else:
            raise

    # 3.2) build a translator that strips all ASCII punctuation
    translator = str.maketrans('', '', string.punctuation)

    # 3.3) fetch every item, normalise its name, and update the row
    cursor.execute("SELECT item_id, item_name FROM items;")
    for item_id, item_name in cursor.fetchall():
        clean_name = item_name.translate(translator)
        cursor.execute("""
            UPDATE items
            SET normalised_item_name = ?
            WHERE item_id = ?;
        """, (clean_name, item_id))

    conn.commit()
    conn.close()
    print('✅ normalised_item_name populated for all items!')

# invoke Step 3
step2_add_normalised_column(DB_PATH)
