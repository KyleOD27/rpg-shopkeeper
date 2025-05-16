# setup/setup_all.py – resilient seeder (v2)
# -----------------------------------------------------------------------------
# * Works both online (full SRD import) and offline (local fallback_items.sql).
# * Guards against missing integrations.dnd5e dependency.
# * Provides --no-srd flag that still inserts fallback items, so tests always
#   have something to query.
# * Leaves CLI flags and normalisation logic unchanged.
# -----------------------------------------------------------------------------

from __future__ import annotations

import argparse
import logging
import sqlite3
import string
from pathlib import Path

# ─── Optional SRD loader ─────────────────────────────────────────────────────
try:
    from integrations.dnd5e.srd_item_loader import main as load_srd_items  # type: ignore
except Exception as exc:  # pragma: no cover – network / missing dep / etc.
    logging.warning("SRD loader unavailable: %s – will fall back to local seed", exc)

    def load_srd_items() -> None:  # type: ignore
        raise RuntimeError("SRD loader not available in this environment")

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "rpg-shopkeeper.db"
SCHEMA_SQL = BASE_DIR / "database" / "schema.sql"
SEED_SQL = BASE_DIR / "database" / "seed_data.sql"
FALLBACK_SQL = BASE_DIR / "database" / "fallback_items.sql"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def reset_database() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("🗑️  Old database removed.")
    else:
        print("⚠️  No existing DB found. Proceeding fresh.")


def run_sql_script(path: Path) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        with open(path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        print(f"📄 Executed: {path.name}")


def populate_normalised_names() -> None:
    """Create/populate normalised_item_name column (ASCII, no punctuation)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE items ADD COLUMN normalised_item_name TEXT;")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e).lower():
            raise

    translator = str.maketrans("", "", string.punctuation)

    cursor.execute("SELECT item_id, item_name FROM items;")
    for item_id, item_name in cursor.fetchall():
        clean_name = item_name.translate(translator)
        cursor.execute(
            "UPDATE items SET normalised_item_name = ? WHERE item_id = ?;",
            (clean_name, item_id),
        )

    conn.commit()
    conn.close()
    print("✅  normalised_item_name populated for all items!")


# ─── Seeding logic ───────────────────────────────────────────────────────────

def _insert_items(no_srd_flag: bool) -> None:
    """Insert rows into items either from SRD API or local fallback."""
    if no_srd_flag:
        print("⚠️  --no-srd flag passed – using local fallback items.")
        run_sql_script(FALLBACK_SQL)
        return

    try:
        print("🧙  Loading SRD items …")
        load_srd_items()
    except Exception as exc:  # network, missing dep, etc.
        logging.warning("SRD load failed: %s – falling back to local seed", exc)
        run_sql_script(FALLBACK_SQL)


# ─── CLI Entry point ─────────────────────────────────────────────────────────

def main() -> None:  # noqa: C901
    parser = argparse.ArgumentParser(description="Set up RPG Shopkeeper DB")
    parser.add_argument("--reset", action="store_true", help="Delete and recreate database")
    parser.add_argument("--no-srd", action="store_true", help="Skip SRD item loading (use fallback)")
    parser.add_argument("--no-seed", action="store_true", help="Skip core seed data")
    parser.add_argument("--only-srd", action="store_true", help="Only run SRD item loader + normalise")
    args = parser.parse_args()

    if args.only_srd:
        _insert_items(no_srd_flag=args.no_srd)
        populate_normalised_names()
        return

    if args.reset:
        reset_database()

    print("📦  Setting up schema …")
    run_sql_script(SCHEMA_SQL)

    _insert_items(no_srd_flag=args.no_srd)

    if not args.no_seed:
        print("🌱  Seeding user/shop/party data …")
        run_sql_script(SEED_SQL)

    print("🔡  Populating normalised_item_name …")
    populate_normalised_names()

    print("✅  Setup complete.")


if __name__ == "__main__":
    main()
