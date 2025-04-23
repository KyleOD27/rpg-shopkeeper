# srd_item_loader.py

import sqlite3
import requests
import time
from pathlib import Path

# Configuration
BASE_URL = "https://www.dnd5eapi.co"
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # adjust if needed
DB_PATH = BASE_DIR / 'rpg-shopkeeper.db'

def fetch_all_items():
    response = requests.get(f"{BASE_URL}/api/equipment/")
    response.raise_for_status()
    return response.json()["results"]

def fetch_item_detail(index):
    response = requests.get(f"{BASE_URL}/api/equipment/{index}")
    response.raise_for_status()
    return response.json()

def map_to_srd_schema(item):
    return {
        "srd_index": item.get("index"),
        "item_name": item.get("name"),
        "equipment_category": item.get("equipment_category", {}).get("name"),
        "gear_category": item.get("gear_category", {}).get("name") if "gear_category" in item else None,
        "tool_category": item.get("tool_category") if "tool_category" in item else None,
        "weapon_category": item.get("weapon_category") if "weapon_category" in item else None,
        "armour_category": item.get("armor_category") if "armor_category" in item else None,
        "base_price": item.get("cost", {}).get("quantity", 0),      # numeric value
        "price_unit": item.get("cost", {}).get("unit", "gp"),       # cp/sp/gp/etc.
        "weight": item.get("weight"),
        "desc": "\n".join(item.get("desc", [])) if "desc" in item else None,
        "rarity": "Common"
    }


def insert_item(cursor, mapped):
    cursor.execute("""
        INSERT OR IGNORE INTO items (
            srd_index, item_name, equipment_category, gear_category, tool_category,
            weapon_category, armour_category, base_price, price_unit,
            weight, desc, rarity
        ) VALUES (
            :srd_index, :item_name, :equipment_category, :gear_category, :tool_category,
            :weapon_category, :armour_category, :base_price, :price_unit,
            :weight, :desc, :rarity
        )
    """, mapped)

def main():
    print(f"📂 Using database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🌐 Fetching SRD item list...")
    item_list = fetch_all_items()
    print(f"🔎 Found {len(item_list)} items.")

    for i, item in enumerate(item_list, start=1):
        try:
            print(f"➡️ {i}/{len(item_list)} - {item['name']}")
            detail = fetch_item_detail(item["index"])
            mapped = map_to_srd_schema(detail)
            insert_item(cursor, mapped)
            time.sleep(0.2)
        except Exception as e:
            print(f"❌ Error on item {item['name']}: {e}")

    conn.commit()
    conn.close()
    print("✅ All items loaded into database.")

if __name__ == "__main__":
    main()
