"""
Download SRD equipment from dnd5eapi.co, caching every JSON file
so subsequent runs are fully offline-safe.
"""
from __future__ import annotations

import json
import sqlite3
import time
import logging
from pathlib import Path
from typing import Dict, Any

import requests
from requests.exceptions import RequestException

# ───────────────────────── Configuration ──────────────────────────
BASE_URL         = "https://www.dnd5eapi.co/api/2014"
ROOT             = Path(__file__).resolve().parents[2]
DB_PATH          = ROOT / "rpg-shopkeeper.db"

CACHE_DIR        = Path(__file__).with_suffix("").parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

MAX_RETRIES      = 5       # attempts per item
BACKOFF_FACTOR   = 2       # 1,2,4,8,16 seconds
TIMEOUT_SECONDS  = 10      # per HTTP request
SLEEP_BETWEEN    = 0.10    # polite delay between items

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# One session for all requests (re-uses TCP + TLS)
session = requests.Session()
session.headers.update({"User-Agent": "rpg-shopkeeper/1.0"})
# ──────────────────────────────────────────────────────────────────


def fetch_all_items() -> list[Dict[str, Any]]:
    """Return metadata list (name + index) for every SRD equipment item."""
    r = session.get(f"{BASE_URL}/equipment/", timeout=TIMEOUT_SECONDS)
    r.raise_for_status()
    return r.json()["results"]


def fetch_item(index: str) -> Dict[str, Any]:
    """
    Return the JSON block for one equipment item.

    1. If cached → load from disk.
    2. Else fetch with retries, save to cache, return dict.
    """
    cache_file = CACHE_DIR / f"{index}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    url = f"{BASE_URL}/equipment/{index}"
    for attempt in range(MAX_RETRIES):
        try:
            r = session.get(url, timeout=TIMEOUT_SECONDS)
            r.raise_for_status()
            cache_file.write_text(r.text, encoding="utf-8")
            return r.json()
        except RequestException as exc:
            log.warning("Fetch failed: %s (attempt %s/%s)", index, attempt + 1, MAX_RETRIES)
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(BACKOFF_FACTOR ** attempt)


def map_to_row(item: dict) -> dict:
    dmg = item.get("damage") or {}
    dmg_type = (dmg.get("damage_type") or {}).get("name")
    rng = item.get("range") or {}
    ac_block = item.get("armor_class") or {}
    dex_bonus = ac_block.get("dex_bonus")
    max_bonus = ac_block.get("max_bonus")

    return {
        "srd_index":          item["index"],
        "item_name":          item["name"],
        "equipment_category": item.get("equipment_category", {}).get("name"),
        "armour_category":    item.get("armor_category"),
        "weapon_category":    item.get("weapon_category"),
        "gear_category":      item.get("gear_category", {}).get("name"),
        "tool_category":      item.get("tool_category"),
        "weapon_range":       item.get("weapon_range"),
        "category_range":     item.get("category_range"),
        "damage_dice":        dmg.get("damage_dice"),
        "damage_type":        dmg_type,
        "range_normal":       rng.get("normal"),
        "range_long":         rng.get("long"),
        "base_ac":            ac_block.get("base"),
        "dex_bonus":          1 if dex_bonus else 0 if dex_bonus is not None else None,
        "max_dex_bonus":      max_bonus,
        "str_minimum":        item.get("str_minimum"),
        "stealth_disadvantage":
                              1 if item.get("stealth_disadvantage") else 0
                              if "stealth_disadvantage" in item else None,
        "base_price":         item.get("cost", {}).get("quantity", 0),
        "price_unit":         item.get("cost", {}).get("unit", "gp"),
        "weight":             item.get("weight"),
        "desc":               "\n".join(item.get("desc", [])),
        "rarity":             "Common",
        "item_source":        "SRD"
    }


def insert(cursor: sqlite3.Cursor, row: dict) -> None:
    fields = ", ".join(row.keys())
    placeholders = ":" + ", :".join(row.keys())
    cursor.execute(
        f"INSERT OR IGNORE INTO items ({fields}) VALUES ({placeholders})",
        row,
    )


def main() -> None:
    print(f"📂 DB: {DB_PATH}")
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        items = fetch_all_items()
        print(f"🌐 Processing {len(items)} SRD items…")

        for idx, meta in enumerate(items, 1):
            print(f"{idx:3}/{len(items):3}  {meta['name']}")
            detail = fetch_item(meta["index"])
            insert(cur, map_to_row(detail))
            time.sleep(SLEEP_BETWEEN)

        conn.commit()
        print("✅ SRD import complete.")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
