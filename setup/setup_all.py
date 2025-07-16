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

from setup.seed.seed_treasure import GEM_ROWS, TRADEBAR_ROWS, TRADEGOODS_ROWS, ARTOBJECTS_ROWS
from setup.seed.seed_magicitems import ARMOR_ROWS, WEAPON_ROWS, CONSUMABLE_MAGIC_ITEMS_ROWS, RING_ROWS, ROD_ROWS, \
    EQUIPABLE_MAGIC_ITEMS_ROWS, WEARABLE_MAGIC_ITEMS_ROWS

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

def insert_gemstones(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        for srd_index, name, price_gp, description, rarity in GEM_ROWS:
            try:
                conn.execute(
                    """
                    INSERT INTO items
                      (srd_index, item_name,
                       equipment_category, treasure_category,
                       base_price, price_unit, weight, desc, rarity, item_source)
                    VALUES (?, ?, 'Treasure', 'Gemstones',
                            ?, 'gp', 0, ?, ?, 'DM-GUIDE-2024' );
                    """,
                    (srd_index, name, price_gp, description, rarity),
                )
                print(f"✅ added → {srd_index:<15}  {name}")
            except sqlite3.IntegrityError:
                print(f"⚠️  skipped duplicate → {srd_index:<15}  {name}")
        conn.commit()
    print("💎  Gemstone seeding finished!")

def insert_tradebars(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        for srd_index, name, price_gp, description, rarity in TRADEBAR_ROWS:
            try:
                conn.execute(
                    """
                    INSERT INTO items
                      (srd_index, item_name,
                       equipment_category, treasure_category,
                       base_price, price_unit, weight, desc, rarity, item_source)
                    VALUES (?, ?, 'Treasure', 'Trade Bars',
                            ?, 'gp', 0, ?, ?, 'DM-GUIDE-2024');
                    """,
                    (srd_index, name, price_gp, description, rarity),
                )
                print(f"✅ added → {srd_index:<15}  {name}")
            except sqlite3.IntegrityError:
                print(f"⚠️  skipped duplicate → {srd_index:<15}  {name}")
        conn.commit()
    print("💰 Trade bar seeding finished!")

def insert_tradegoods(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        for srd_index, name, price_cp, description, rarity in TRADEGOODS_ROWS:
            try:
                conn.execute(
                    """
                    INSERT INTO items
                      (srd_index, item_name,
                       equipment_category, treasure_category,
                       base_price, price_unit, weight, desc, rarity, item_source)
                    VALUES (?, ?, 'Treasure', 'Trade Goods',
                            ?, 'cp', 0, ?, ?, 'DM-GUIDE-2024');
                    """,
                    (srd_index, name, price_cp, description, rarity),
                )
                print(f"✅ added → {srd_index:<15}  {name}")
            except sqlite3.IntegrityError:
                print(f"⚠️  skipped duplicate → {srd_index:<15}  {name}")
        conn.commit()
    print("📦  Trade goods seeding finished!")

def insert_artobjects(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        for srd_index, name, price_gp, description, rarity in ARTOBJECTS_ROWS:
            try:
                conn.execute(
                    """
                    INSERT INTO items
                      (srd_index, item_name,
                       equipment_category, treasure_category,
                       base_price, price_unit, weight, desc, rarity, item_source)
                    VALUES (?, ?, 'Treasure', 'Art Objects',
                            ?, 'gp', 0, ?, ?, 'DM-GUIDE-2024');
                    """,
                    (srd_index, name, price_gp, description, rarity),
                )
                print(f"✅ added → {srd_index:<15}  {name}")
            except sqlite3.IntegrityError:
                print(f"⚠️  skipped duplicate → {srd_index:<15}  {name}")
        conn.commit()
    print("🖼️  Art object seeding finished!")

def insert_wearable_magic_items(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        for (
            srd_index, item_name, base_price, price_unit,
            weight, description, magic_bonus, is_magical,
            rarity, wearable_category, subtype_data
        ) in WEARABLE_MAGIC_ITEMS_ROWS:
            try:
                if wearable_category == 'Armor':
                    conn.execute(
                        """
                        INSERT INTO items (
                            srd_index, item_name, item_source,
                            equipment_category, armour_category,
                            base_price, price_unit, weight,
                            desc, rarity,
                            base_ac, dex_bonus, max_dex_bonus,
                            str_minimum, stealth_disadvantage,
                            magic_bonus, is_magical
                        ) VALUES (?, ?, 'DM-GUIDE-2024',
                                  'Armor', ?,
                                  ?, ?, ?,
                                  ?, ?,
                                  ?, ?, ?,
                                  ?, ?,
                                  ?, ?);
                        """,
                        (
                            srd_index, item_name, subtype_data['armour_category'],
                            base_price, price_unit, weight,
                            description, rarity,
                            subtype_data['base_ac'], int(subtype_data['dex_bonus']), subtype_data['max_dex_bonus'],
                            subtype_data['str_minimum'], int(subtype_data['stealth_disadvantage']),
                            magic_bonus, int(is_magical)
                        )
                    )
                elif wearable_category == 'Weapon':
                    conn.execute(
                        """
                        INSERT INTO items (
                            srd_index, item_name, item_source,
                            equipment_category, weapon_category,
                            base_price, price_unit,
                            weapon_range, category_range,
                            damage_dice, damage_type,
                            range_normal, range_long,
                            weight,
                            desc, rarity,
                            magic_bonus, is_magical
                        ) VALUES (?, ?, 'DM-GUIDE-2024',
                                  'Weapon', ?,
                                  ?, ?,
                                  ?, ?,
                                  ?, ?,
                                  ?, ?,
                                  ?, 
                                  ?, ?,
                                  ?, ?);
                        """,
                        (
                            srd_index, item_name, subtype_data['weapon_category'],
                            base_price, price_unit,
                            subtype_data['weapon_range'], subtype_data['category_range'],
                            subtype_data['damage_dice'], subtype_data['damage_type'],
                            subtype_data['range_normal'], subtype_data['range_long'],
                            weight,
                            description, rarity,
                            magic_bonus, int(is_magical)
                        )
                    )
                print(f"🧤  added → {srd_index:<30} {item_name}")
            except sqlite3.IntegrityError:
                print(f"⚠️  skipped duplicate → {srd_index:<30} {item_name}")
        conn.commit()
    print("🪖 Wearable magic item seeding finished!")

def insert_consumable_magic_items(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        for (
            srd_index, item_name, base_price, price_unit,
            weight, description, magic_bonus, is_magical,
            rarity, gear_category
        ) in CONSUMABLE_MAGIC_ITEMS_ROWS:
            try:
                conn.execute(
                    """
                    INSERT INTO items (
                        srd_index, item_name, item_source,
                        equipment_category, gear_category,
                        base_price, price_unit, weight,
                        desc, rarity,
                        magic_bonus, is_magical
                    )
                    VALUES (?, ?, 'DM-GUIDE-2024',
                            'Adventuring Gear', ?,
                            ?, ?, ?,
                            ?, ?,
                            ?, ?);
                    """,
                    (
                        srd_index, item_name, gear_category,
                        base_price, price_unit, weight,
                        description, rarity,
                        magic_bonus, int(is_magical)
                    )
                )
                print(f"🎒  added → {srd_index:<30} {item_name}")
            except sqlite3.IntegrityError:
                print(f"⚠️  skipped duplicate → {srd_index:<30} {item_name}")
        conn.commit()
    print("🎒 Adventuring Gear seeding finished!")

def insert_equipable_magic_items(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        for (
            srd_index, item_name, base_price, price_unit,
            weight, description, magic_bonus, is_magical,
            rarity, treasure_category
        ) in EQUIPABLE_MAGIC_ITEMS_ROWS:
            try:
                conn.execute(
                    """
                    INSERT INTO items (
                        srd_index, item_name, item_source,
                        equipment_category, treasure_category,
                        base_price, price_unit, weight,
                        desc, rarity,
                        magic_bonus, is_magical
                    )
                    VALUES (?, ?, 'DM-GUIDE-2024',
                            'Treasure', ?,
                            ?, ?, ?,
                            ?, ?,
                            ?, ?);
                    """,
                    (
                        srd_index, item_name, treasure_category,
                        base_price, price_unit, weight,
                        description, rarity,
                        magic_bonus, int(is_magical)
                    )
                )
                print(f"🪄  added → {srd_index:<30} {item_name}")
            except sqlite3.IntegrityError:
                print(f"⚠️  skipped duplicate → {srd_index:<30} {item_name}")
        conn.commit()
    print("✨ Equipable magic item seeding finished!")

def update_base_price_cp(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            UPDATE items
            SET base_price_cp = base_price * (
                SELECT value_in_cp
                FROM currencies
                WHERE currencies.unit = items.price_unit
            )
            WHERE base_price IS NOT NULL AND price_unit IS NOT NULL;
        """)
        conn.commit()
    print("🧮 base_price_cp column updated!")

# ---- Image population logic ----
import os
IMAGE_DIR = r"C:\Users\win11\PycharmProjects\rpg-shopkeeper-project\tools\images\items"
IMAGE_URL_PREFIX = "img"


def slugify(name):
    import re
    return re.sub(r'[^a-z0-9_]', '', name.replace(' ', '_').replace('-', '_').lower())

def update_item_images():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT item_id, item_name FROM items")
    updated = 0
    for item_id, item_name in cursor.fetchall():
        slug = slugify(item_name)
        for ext in ['.png', '.jpg', '.jpeg', '.webp']:
            filename = slug + ext
            image_path = os.path.join(IMAGE_DIR, filename)
            if os.path.isfile(image_path):
                image_url = f"{IMAGE_URL_PREFIX}/{filename}"
                cursor.execute(
                    "UPDATE items SET image_url = ? WHERE item_id = ?",
                    (image_url, item_id)
                )
                updated += 1
                break
    conn.commit()
    conn.close()
    print(f"✅ Set image_url for {updated} items.")

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
        insert_gemstones(DB_PATH)
        insert_tradebars(DB_PATH)
        insert_tradegoods(DB_PATH)
        insert_artobjects(DB_PATH)
        insert_wearable_magic_items(DB_PATH)
        insert_consumable_magic_items(DB_PATH)
        insert_equipable_magic_items(DB_PATH)
        update_base_price_cp(DB_PATH)

    print("🔡  Populating normalised_item_name …")
    populate_normalised_names()

    # --- Add image URL population here ---
    update_item_images()

    print("✅  Setup complete.")

if __name__ == "__main__":
    main()
