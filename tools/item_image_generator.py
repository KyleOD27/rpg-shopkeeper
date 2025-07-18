import os
import time
import requests
import openai
import re
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from app.db import get_connection

# === CONFIG ===
FILTER_KEYWORD = ""  # All items!
IMAGE_OUT_DIR = "images/items"
IMAGE_SIZE = "1024x1024"
DELAY_BETWEEN_CALLS = 1.5
VISUAL_CACHE = "visual_desc_cache.csv"

# === ENV ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Missing OPENAI_API_KEY env variable!")
client = openai.OpenAI()

Path(IMAGE_OUT_DIR).mkdir(parents=True, exist_ok=True)

with get_connection() as conn:
    rows = conn.execute("""
        SELECT item_name, normalised_item_name, desc, rarity,
               gear_category, tool_category, treasure_category, equipment_category
        FROM items
        WHERE LOWER(item_name) LIKE ?
        ORDER BY item_id
    """, (f"%{FILTER_KEYWORD.lower()}%",)).fetchall()
    df = pd.DataFrame([dict(r) for r in rows])

def extract_key_visuals(desc):
    if not desc:
        return ""
    desc_lc = desc.lower()
    color_words = ["red", "blue", "green", "gold", "silver", "black", "white", "purple", "yellow", "orange", "pink", "grey", "brown", "copper", "bronze"]
    material_words = ["glass", "metal", "wood", "crystal", "leather", "stone", "bone", "cloth", "paper", "gem", "diamond", "emerald", "ruby", "sapphire", "iron", "steel", "bronze"]
    shape_words = ["vial", "sword", "wand", "ring", "potion", "scroll", "necklace", "amulet", "gem", "pouch", "orb", "bottle", "blade", "staff", "bow", "arrow", "hammer", "shield"]
    found = []
    for word in color_words + material_words + shape_words:
        if word in desc_lc and word not in found:
            found.append(word)
    numbers = re.findall(r'\b(one|two|three|four|five|six|seven|eight|nine|ten|pair|set of)\b', desc_lc)
    found.extend(numbers)
    special = []
    for phrase in ["cork stopper", "swirling", "glowing", "etched", "jeweled", "with a chain", "with runes", "studded", "spiked"]:
        if phrase in desc_lc:
            special.append(phrase)
    found.extend(special)
    return ", ".join(found)

def generate_ai_visual_desc(item_name):
    prompt = (
        f"Describe the physical appearance of a '{item_name}' as a Dungeons & Dragons magic item. "
        "One sentence only. Focus only on what an artist should draw—no abilities or story."
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4o" if you have access
        messages=[{"role": "user", "content": prompt}],
        max_tokens=48,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def fetch_visual_description(item_name, desc, cache):
    # Try cache first
    if item_name in cache:
        return cache[item_name]
    visual = extract_key_visuals(desc) if desc else ""
    if visual and len(visual.split()) >= 2:
        cache[item_name] = visual
        return visual
    # Otherwise, ask GPT and cache
    gpt_desc = generate_ai_visual_desc(item_name)
    cache[item_name] = gpt_desc
    return gpt_desc

rarity_colors = {
    "common": "light grey",
    "uncommon": "green",
    "rare": "blue",
    "very rare": "purple",
    "legendary": "gold",
    "artifact": "red",
}

# Load or initialize cache
if os.path.exists(VISUAL_CACHE):
    visual_desc_cache = pd.read_csv(VISUAL_CACHE).set_index("item_name")["visual_desc"].to_dict()
else:
    visual_desc_cache = {}

# Main loop, row by row
for i, row in df.iterrows():
    name = row["item_name"]
    norm_name = row["normalised_item_name"]
    desc = row["desc"] or ""
    rarity = (row["rarity"] or "common").strip().lower()
    category = (
        row["gear_category"] or row["tool_category"] or
        row["treasure_category"] or row["equipment_category"] or "item"
    )
    bg_color = rarity_colors.get(rarity, "grey")

    visual_detail = fetch_visual_description(name, desc, visual_desc_cache)
    prompt = (
        f"A {name}, a {category.lower()}, centered on a plain solid {bg_color} background. "
        "Pixel art, manga-inspired style. Only the item is shown, centered. Full image should fit well within frame."
    )
    if visual_detail:
        prompt += f" Features: {visual_detail}."

    filename = norm_name.replace(" ", "_").lower() + ".png"
    out_path = Path(IMAGE_OUT_DIR) / filename

    if out_path.exists():
        print(f"[✔] Skipping {name} (already exists)")
        continue

    print(f"[{i+1}/{len(df)}] Generating: {name}")

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=IMAGE_SIZE,
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        image_data = requests.get(image_url).content

        with open(out_path, "wb") as f:
            f.write(image_data)
        print(f"[✔] Saved to {out_path}")
    except Exception as e:
        print(f"[✖] Failed for {name}: {e}")

    # Save cache every 5 items to avoid data loss
    if i % 5 == 0:
        pd.DataFrame(
            [{"item_name": k, "visual_desc": v} for k, v in visual_desc_cache.items()]
        ).to_csv(VISUAL_CACHE, index=False)

    time.sleep(DELAY_BETWEEN_CALLS)

# Save cache at end too
pd.DataFrame(
    [{"item_name": k, "visual_desc": v} for k, v in visual_desc_cache.items()]
).to_csv(VISUAL_CACHE, index=False)
