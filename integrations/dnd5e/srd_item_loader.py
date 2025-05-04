# srd_item_loader.py  – armour-aware rewrite
import sqlite3, requests, json, time
from pathlib import Path

BASE_URL = "https://www.dnd5eapi.co/api/2014"
DB_PATH  = Path(__file__).resolve().parents[2] / "rpg-shopkeeper.db"

def fetch_all_items():
    r = requests.get(f"{BASE_URL}/equipment/")
    r.raise_for_status()
    return r.json()["results"]

def fetch_item(index: str) -> dict:
    r = requests.get(f"{BASE_URL}/equipment/{index}")
    r.raise_for_status()
    return r.json()

def map_to_row(item: dict) -> dict:
    # weapon helpers
    dmg         = item.get("damage") or {}
    dmg_type    = (dmg.get("damage_type") or {}).get("name")
    rng         = item.get("range") or {}
    # armour helpers
    ac_block    = item.get("armor_class") or {}
    dex_bonus   = ac_block.get("dex_bonus")          # bool
    max_bonus   = ac_block.get("max_bonus")          # int | None

    return {
        "srd_index":         item["index"],
        "item_name":         item["name"],
        "equipment_category":item.get("equipment_category", {}).get("name"),
        "armour_category":   item.get("armor_category"),        # note API uses US spelling
        "weapon_category":   item.get("weapon_category"),
        "gear_category":     item.get("gear_category", {}).get("name"),
        "tool_category":     item.get("tool_category"),

        # weapon
        "weapon_range":  item.get("weapon_range"),
        "category_range":item.get("category_range"),
        "damage_dice":   dmg.get("damage_dice"),
        "damage_type":   dmg_type,
        "range_normal":  rng.get("normal"),
        "range_long":    rng.get("long"),

        # armour
        "base_ac":              ac_block.get("base"),
        "dex_bonus":            1 if dex_bonus else 0 if dex_bonus is not None else None,
        "max_dex_bonus":        max_bonus,
        "str_minimum":          item.get("str_minimum"),
        "stealth_disadvantage": 1 if item.get("stealth_disadvantage") else 0
                                 if "stealth_disadvantage" in item else None,

        # misc
        "base_price": item.get("cost", {}).get("quantity", 0),
        "price_unit": item.get("cost", {}).get("unit", "gp"),
        "weight":     item.get("weight"),
        "desc":       "\n".join(item.get("desc", [])),
        "rarity":     "Common",
    }

def insert(cursor, row: dict):
    fields = ", ".join(row.keys())
    placeholders = ":" + ", :".join(row.keys())
    cursor.execute(f"INSERT OR IGNORE INTO items ({fields}) VALUES ({placeholders})", row)

def main():
    print(f"📂 DB: {DB_PATH}")
    conn, cur = sqlite3.connect(DB_PATH), None
    try:
        cur = conn.cursor()
        items = fetch_all_items()
        print(f"🌐 Fetching {len(items)} SRD items…")
        for idx, meta in enumerate(items, 1):
            print(f"  {idx}/{len(items):3}  {meta['name']}")
            detail = fetch_item(meta["index"])
            insert(cur, map_to_row(detail))
            time.sleep(0.15)
        conn.commit()
        print("✅  Done.")
    finally:
        if cur:
            cur.close()
        conn.close()

if __name__ == "__main__":
    main()
