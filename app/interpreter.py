# app/interpreter.py

import re
import os
import json
from difflib import get_close_matches
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from app.conversation import PlayerIntent
from app.models.items import get_all_items, get_all_equipment_categories, get_weapon_categories, get_gear_categories, get_armour_categories, get_tool_categories

# --- INTENT KEYWORDS ---
INTENT_KEYWORDS = {
    PlayerIntent.VIEW_ITEMS: ["items", "inventory", "stock", "what do you have", "show me", "what do you sell", "what do you buy", "what else"],

    # 🛡️ Main categories
    PlayerIntent.VIEW_ARMOUR_CATEGORY: ["armor", "armour"],
    PlayerIntent.VIEW_WEAPON_CATEGORY: ["weapon", "weapons"],
    PlayerIntent.VIEW_GEAR_CATEGORY: ["gear", "adventuring gear", "supplies", "packs"],
    PlayerIntent.VIEW_TOOL_CATEGORY: ["tools", "tool", "kits", "artisan's tools"],
    PlayerIntent.VIEW_EQUIPMENT_CATEGORY: ["equipment", "mounts", "vehicles", "travelling gear"],

    # 🛡️ Subcategories
    PlayerIntent.VIEW_ARMOUR_SUBCATEGORY: ["light", "medium", "heavy", "shield"],
    PlayerIntent.VIEW_WEAPON_SUBCATEGORY: ["simple", "martial", "bow", "crossbow", "dagger", "axe", "sword"],
    PlayerIntent.VIEW_GEAR_SUBCATEGORY: ["backpack", "rope", "tinderbox", "torch"],
    PlayerIntent.VIEW_TOOL_SUBCATEGORY: ["artisan", "disguise", "forgery", "thieves", "musical"],

    # 🛒 Trading
    PlayerIntent.BUY_ITEM: ["buy", "purchase", "get", "acquire"],
    PlayerIntent.SELL_ITEM: ["sell", "offload", "trade in"],

    # 💰 Money management
    PlayerIntent.DEPOSIT_GOLD: ["deposit", "store gold", "stash"],
    PlayerIntent.WITHDRAW_GOLD: ["withdraw", "take gold", "collect"],

    # 📖 Utility
    PlayerIntent.CHECK_BALANCE: ["balance", "gold amount", "how much gold", "check funds"],
    PlayerIntent.VIEW_LEDGER: ["ledger", "transactions", "history"],
    PlayerIntent.HAGGLE: ["haggle", "negotiate", "bargain", "deal", "cheaper", "discount"],

    # 🎩 Small talk
    PlayerIntent.SHOW_GRATITUDE: ["thanks", "thankyou", "grateful", "ty"],
    PlayerIntent.GREETING: ["hello", "hi", "greetings", "hallo", "hey", "what up"],

    # 📖 Navigation
    PlayerIntent.NEXT: ["next", "more", "show more", "continue", "keep going"],
    PlayerIntent.PREVIOUS: ["previous", "back", "go back", "last page"],
}



CONFIRMATION_WORDS = ["yes", "yeah", "yep", "aye", "sure", "of course", "deal", "done", "absolutely", "ok", "okay", "fine"]
CANCELLATION_WORDS = ["no", "nah", "never", "cancel", "forget it", "stop", "not now", "no deal"]
GRATITUDE_KEYWORDS = ["thanks", "thank", "thank you", "merci", "danke", "ta", "ty", "cheers"]
SMALL_TALK_KEYWORDS = ["goodbye", "farewell"]

# --- UTILITY FUNCTIONS ---

def normalize_input(text: str, convo=None) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    normalized = re.sub(r'\s+', ' ', text)

    if convo is not None:
        convo.normalized_input = normalized

    return normalized

from difflib import get_close_matches


def get_category_match(player_input: str):
    lowered = normalize_input(player_input)

    # --- Dynamically load your real categories ---
    categories = {
        "equipment_category": get_all_equipment_categories(),
        "weapon_category": get_weapon_categories(),
        "gear_category": get_gear_categories(),
        "armour_category": get_armour_categories(),
        "tool_category": get_tool_categories(),
    }

    # --- Try exact match (after normalization) ---
    for category_type, names in categories.items():
        norm_names = [normalize_input(n) for n in names]
        if lowered in norm_names:
            idx = norm_names.index(lowered)
            return category_type, names[idx]

    # --- Try close match (typo tolerance) ---
    for category_type, names in categories.items():
        norm_names = [normalize_input(n) for n in names]
        match = get_close_matches(lowered, norm_names, n=1, cutoff=0.75)
        if match:
            idx = norm_names.index(match[0])
            return category_type, names[idx]

    return None, None

def get_subcategory_match(section: str, player_input: str):
    lowered = normalize_input(player_input)

    if section == "armor":
        categories = get_armour_categories()
    elif section == "weapon":
        categories = get_weapon_categories()
    elif section == "gear":
        categories = get_gear_categories()
    elif section == "tool":
        categories = get_tool_categories()
    else:
        return None  # Not a valid parent section

    normalized_to_original = {normalize_input(c): c for c in categories}

    # New logic: find if any known subcategory is contained inside the input
    for norm_word, original_word in normalized_to_original.items():
        if norm_word in lowered:
            return original_word

    # Fallback to fuzzy match
    match = get_close_matches(lowered, normalized_to_original.keys(), n=1, cutoff=0.75)
    if match:
        return normalized_to_original[match[0]]

    return None


def find_item_in_input(player_input: str, convo=None):
    from app.models.items import (
        get_all_equipment_categories,
        get_weapon_categories,
        get_gear_categories,
        get_armour_categories,
        get_tool_categories,
        get_all_items
    )
    import json

    lowered = normalize_input(player_input)
    original_input = lowered  # Keep original normalized input for full phrase matching

    # Remove buy-related keywords from start
    buy_keywords = ["buy", "purchase", "get", "grab", "obtain", "want", "acquire"]
    for keyword in buy_keywords:
        if lowered.startswith(keyword):
            lowered = lowered[len(keyword):].strip()

    words = lowered.split()
    items_raw = get_all_items()
    items = []

    # Ensure that items are loaded correctly
    for item in items_raw:
        if isinstance(item, str):
            try:
                item = json.loads(item)
            except json.JSONDecodeError:
                continue
        items.append(dict(item))

    # 1️⃣ Check for numeric ID first
    item_id = next((word for word in words if word.isdigit()), None)
    if item_id:
        matches_by_id = [item for item in items if str(item.get("item_id")) == item_id]
        if matches_by_id:
            return matches_by_id, None

    # 2️⃣ CATEGORY match - more flexible matching
    categories = (
            get_all_equipment_categories() +
            get_weapon_categories() +
            get_gear_categories() +
            get_armour_categories() +
            get_tool_categories()
    )

    # Create a mapping of normalized names to original category names
    category_map = {normalize_input(c): c for c in categories}

    # Check for full phrase matches first (e.g., "adventuring gear")
    for norm_cat, original_cat in category_map.items():
        if norm_cat in original_input:  # Check against full normalized input
            print(f"Full category match found: {original_cat}")
            return None, original_cat

    # Then check word by word matches
    for word in words:
        # Find closest category match using fuzzy matching
        closest_matches = get_close_matches(word, category_map.keys(), n=1, cutoff=0.6)
        if closest_matches:
            matched_cat = closest_matches[0]
            print(f"Fuzzy category match found: {category_map[matched_cat]}")
            return None, category_map[matched_cat]

    # 3️⃣ ITEM matches - more flexible matching
    item_name_map = {normalize_input(item["item_name"]): item for item in items}

    # Check for full item name matches first
    for norm_name, item in item_name_map.items():
        if norm_name in original_input:
            print(f"Full item name match found: {item['item_name']}")
            return [item], None

    # Then check word by word with fuzzy matching
    matches_by_name = []
    for word in words:
        # Find closest item name matches
        closest_items = get_close_matches(word, item_name_map.keys(), n=3, cutoff=0.6)
        for matched_name in closest_items:
            if item_name_map[matched_name] not in matches_by_name:
                matches_by_name.append(item_name_map[matched_name])
                print(f"Fuzzy item match found: {item_name_map[matched_name]['item_name']}")

    if matches_by_name:
        return matches_by_name, None

    # 4️⃣ Fallback to pending items in conversation
    if convo and convo.pending_item:
        if isinstance(convo.pending_item, list):
            return convo.pending_item, None
        elif isinstance(convo.pending_item, dict):
            return [convo.pending_item], None
        elif isinstance(convo.pending_item, str):
            return [{"item_name": convo.pending_item}], None

    # If no matches were found, return available categories to help user
    print("No matches found in categories or items.")
    return None, categories  # Return all categories as fallback


def detect_buy_intent(player_input: str, convo=None):
    item_name, _ = find_item_in_input(player_input, convo)
    return (PlayerIntent.BUY_ITEM, item_name) if item_name else (PlayerIntent.BUY_NEEDS_ITEM, None)

def detect_sell_intent(player_input: str):
    item_name, _ = find_item_in_input(player_input)
    return (PlayerIntent.SELL_ITEM, item_name) if item_name else (PlayerIntent.SELL_NEEDS_ITEM, None)

def detect_deposit_intent(player_input: str):
    match = re.search(r'\b\d+\b', normalize_input(player_input))
    return (PlayerIntent.DEPOSIT_GOLD, int(match.group())) if match else (PlayerIntent.DEPOSIT_NEEDS_AMOUNT, None)

def detect_withdraw_intent(player_input: str):
    match = re.search(r'\b\d+\b', normalize_input(player_input))
    return (PlayerIntent.WITHDRAW_GOLD, int(match.group())) if match else (PlayerIntent.WITHDRAW_NEEDS_AMOUNT, None)

# --- MAIN INTERPRETER ---

def interpret_input(player_input: str, convo=None):
    lowered = normalize_input(player_input)
    words = lowered.split()
    metadata = {}

    # 🛡️ --- 1. Check if player is in a section (subcategory matching) ---
    if convo:
        current_section = convo.metadata.get("current_section")
        if current_section:
            matched_subcategory = get_subcategory_match(current_section, player_input)
            if matched_subcategory:
                metadata_key = {
                    "armor": "armour_category",
                    "weapon": "weapon_category",
                    "gear": "gear_category",
                    "tool": "tool_category",
                }.get(current_section)

                intent_mapping = {
                    "armor": PlayerIntent.VIEW_ARMOUR_SUBCATEGORY,
                    "weapon": PlayerIntent.VIEW_WEAPON_SUBCATEGORY,
                    "gear": PlayerIntent.VIEW_GEAR_SUBCATEGORY,
                    "tool": PlayerIntent.VIEW_TOOL_SUBCATEGORY,
                }

                if metadata_key and current_section in intent_mapping:
                    metadata[metadata_key] = matched_subcategory
                    metadata["current_section"] = current_section
                    metadata["current_page"] = 1
                    return {
                        "intent": intent_mapping[current_section],
                        "metadata": metadata
                    }

    # 🛑 --- 2. FORCE override if buying is detected ---
    buy_keywords = INTENT_KEYWORDS.get(PlayerIntent.BUY_ITEM, [])
    if any(keyword in lowered for keyword in buy_keywords):
        detected_intent, item = detect_buy_intent(player_input, convo)
        if item:
            metadata["item"] = item
        return {"intent": detected_intent, "metadata": metadata}

    # 📦 --- 3. Normal category matching ---
    category_type, category_value = get_category_match(player_input)
    if category_type:
        metadata[category_type] = category_value

        # 🛠 SPECIAL PATCH: Weapon inside equipment_category should route to VIEW_WEAPON_CATEGORY
        if category_type == "equipment_category" and category_value.lower() == "weapon":
            return {"intent": PlayerIntent.VIEW_WEAPON_CATEGORY, "metadata": metadata}

        # 🛡 SPECIAL PATCH: Armor inside equipment_category should route to VIEW_ARMOUR_CATEGORY
        if category_type == "equipment_category" and category_value.lower() == "armor":
            return {"intent": PlayerIntent.VIEW_ARMOUR_CATEGORY, "metadata": metadata}

        # 🎒 SPECIAL PATCH: Adventuring Gear inside equipment_category should route to VIEW_GEAR_CATEGORY
        if category_type == "equipment_category" and category_value.lower() == "adventuring gear":
            return {"intent": PlayerIntent.VIEW_GEAR_CATEGORY, "metadata": metadata}

        # 🛠 SPECIAL PATCH: Tools inside equipment_category should route to VIEW_TOOL_CATEGORY
        if category_type == "equipment_category" and category_value.lower() == "tools":
            return {"intent": PlayerIntent.VIEW_TOOL_CATEGORY, "metadata": metadata}

        # 🐎 SPECIAL PATCH: Mounts and Vehicles inside equipment_category
        if category_type == "equipment_category" and category_value.lower() == "mounts and vehicles":
            return {"intent": PlayerIntent.VIEW_MOUNT_CATEGORY, "metadata": metadata}  # Still equipment

        if category_type == "weapon_category":
            return {"intent": PlayerIntent.VIEW_WEAPON_CATEGORY, "metadata": metadata}
        if category_type == "gear_category":
            return {"intent": PlayerIntent.VIEW_GEAR_CATEGORY, "metadata": metadata}
        if category_type == "armour_category":
            return {"intent": PlayerIntent.VIEW_ARMOUR_CATEGORY, "metadata": metadata}
        if category_type == "tool_category":
            return {"intent": PlayerIntent.VIEW_TOOL_CATEGORY, "metadata": metadata}
        return {"intent": PlayerIntent.VIEW_ITEMS, "metadata": metadata}

    # 🔄 --- 4. Confirmation / Cancellation / Small talk ---
    if any(word in words for word in CONFIRMATION_WORDS):
        if convo and convo.player_intent == PlayerIntent.SELL_ITEM:
            return {"intent": PlayerIntent.SELL_CONFIRM}
        if convo and convo.player_intent == PlayerIntent.BUY_ITEM:
            return {"intent": PlayerIntent.BUY_CONFIRM}
        return {"intent": PlayerIntent.CONFIRM}

    if any(word in words for word in CANCELLATION_WORDS):
        if convo and convo.player_intent == PlayerIntent.SELL_ITEM:
            return {"intent": PlayerIntent.SELL_CANCEL}
        if convo and convo.player_intent == PlayerIntent.BUY_ITEM:
            return {"intent": PlayerIntent.BUY_CANCEL}
        return {"intent": PlayerIntent.CANCEL}

    if any(word in words for word in GRATITUDE_KEYWORDS):
        return {"intent": PlayerIntent.SHOW_GRATITUDE}

    if any(word in words for word in SMALL_TALK_KEYWORDS):
        return {"intent": PlayerIntent.SMALL_TALK}

    # 🔑 --- 5. Keyword-based detection ---
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            if intent == PlayerIntent.BUY_ITEM:
                detected_intent, item = detect_buy_intent(player_input, convo)
                if item:
                    metadata["item"] = item
                return {"intent": detected_intent, "metadata": metadata}
            if intent == PlayerIntent.SELL_ITEM:
                detected_intent, item = detect_sell_intent(player_input)
                if item:
                    metadata["item"] = item
                return {"intent": detected_intent, "metadata": metadata}
            if intent == PlayerIntent.DEPOSIT_GOLD:
                detected_intent, amount = detect_deposit_intent(player_input)
                if amount:
                    metadata["amount"] = amount
                return {"intent": detected_intent, "metadata": metadata}
            if intent == PlayerIntent.WITHDRAW_GOLD:
                detected_intent, amount = detect_withdraw_intent(player_input)
                if amount:
                    metadata["amount"] = amount
                return {"intent": detected_intent, "metadata": metadata}
            return {"intent": intent}

    # 🛒 --- 6. LAST fallback: try match to an item directly ---
    item_name, _ = find_item_in_input(player_input, convo)
    if item_name:
        metadata["item"] = item_name
        return {"intent": PlayerIntent.BUY_ITEM, "metadata": metadata}

    # ❓ --- 7. Unknown ---
    return {"intent": PlayerIntent.UNKNOWN}


# --- OPTIONAL: GPT confirmation fallback ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def check_confirmation_via_gpt(user_input: str, convo=None):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a classifier. Is this CONFIRM, CANCEL or UNKNOWN? Return JSON."},
                {"role": "user", "content": f"\"{user_input}\""}
            ],
            temperature=0,
            max_tokens=50,
        )
        result = json.loads(response.choices[0].message.content.strip())
        if result.get("confidence", 0) >= 85:
            if result["intent"] == "CONFIRM":
                return PlayerIntent.CONFIRM
            if result["intent"] == "CANCEL":
                return PlayerIntent.CANCEL
    except Exception as e:
        print("[GPT CONFIRM CHECK ERROR]", e)
    return PlayerIntent.UNKNOWN

# Restore these tiny helpers for compatibility!

def get_equipment_category_from_input(player_input: str):
    category_type, category_value = get_category_match(player_input)
    if category_type == "equipment_category":
        return category_value
    return None

def get_weapon_category_from_input(player_input: str):
    category_type, category_value = get_category_match(player_input)
    if category_type == "weapon_category":
        return category_value
    return None

def get_gear_category_from_input(player_input: str):
    category_type, category_value = get_category_match(player_input)
    if category_type == "gear_category":
        return category_value
    return None

def get_armour_category_from_input(player_input: str):
    category_type, category_value = get_category_match(player_input)
    if category_type == "armour_category":
        return category_value
    return None

def get_tool_category_from_input(player_input: str):
    category_type, category_value = get_category_match(player_input)
    if category_type == "tool_category":
        return category_value
    return None


