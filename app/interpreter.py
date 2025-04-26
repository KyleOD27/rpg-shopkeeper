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
    PlayerIntent.BUY_ITEM: ["buy", "purchase", "get", "acquire"],
    PlayerIntent.SELL_ITEM: ["sell", "offload", "trade in"],
    PlayerIntent.DEPOSIT_GOLD: ["deposit", "store gold", "stash"],
    PlayerIntent.WITHDRAW_GOLD: ["withdraw", "take gold", "collect"],
    PlayerIntent.CHECK_BALANCE: ["balance", "gold amount", "how much gold", "check funds"],
    PlayerIntent.VIEW_LEDGER: ["ledger", "transactions", "history"],
    PlayerIntent.HAGGLE: ["haggle", "negotiate", "bargain", "deal", "cheaper", "discount"],
    PlayerIntent.SHOW_GRATITUDE: ["thanks", "thankyou", "grateful", "ty"],
    PlayerIntent.GREETING: ["hello", "hi", "greetings", "hallo", "hey", "what up"],
    PlayerIntent.NEXT: ["next", "more", "show more", "continue", "keep going"],
    PlayerIntent.PREVIOUS: ["previous", "back", "go back", "last page"],
}

CONFIRMATION_WORDS = ["yes", "yeah", "yep", "aye", "sure", "of course", "deal", "done", "absolutely", "ok", "okay", "fine"]
CANCELLATION_WORDS = ["no", "nah", "never", "cancel", "forget it", "stop", "not now", "no deal"]
GRATITUDE_KEYWORDS = ["thanks", "thank", "thank you", "merci", "danke", "ta", "ty", "cheers"]
SMALL_TALK_KEYWORDS = ["goodbye", "farewell"]

# --- UTILITY FUNCTIONS ---

def normalize_input(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return re.sub(r'\s+', ' ', text)

def get_category_match(player_input: str):
    lowered = normalize_input(player_input)
    categories = {
        "equipment_category": get_all_equipment_categories(),
        "weapon_category": get_weapon_categories(),
        "gear_category": get_gear_categories(),
        "armour_category": get_armour_categories(),
        "tool_category": get_tool_categories(),
    }
    for category_type, names in categories.items():
        norm_names = [normalize_input(n) for n in names]
        if lowered in norm_names:
            idx = norm_names.index(lowered)
            return category_type, names[idx]
        match = get_close_matches(lowered, norm_names, n=1, cutoff=0.8)
        if match:
            idx = norm_names.index(match[0])
            return category_type, names[idx]
    return None, None

def find_item_in_input(player_input: str, convo=None):
    lowered = normalize_input(player_input)

    # 1️⃣ Check if player input matches a known CATEGORY first
    from app.models.items import (
        get_all_equipment_categories,
        get_weapon_categories,
        get_gear_categories,
        get_armour_categories,
        get_tool_categories
    )

    categories = (
        get_all_equipment_categories() +
        get_weapon_categories() +
        get_gear_categories() +
        get_armour_categories() +
        get_tool_categories()
    )

    category_names = [normalize_input(c) for c in categories]

    for cat in category_names:
        if cat in lowered or lowered in cat:
            # 🛡️ It's a category request! Not an item!
            return None, cat  # No item, but category detected

    # 2️⃣ If no category matched, check item names normally
    items = get_all_items()
    item_names = [item["item_name"] for item in items]

    # Exact match inside input
    for name in item_names:
        if normalize_input(name) in lowered:
            return name, None

    # Fuzzy match
    matches = get_close_matches(lowered, [normalize_input(i) for i in item_names], n=1, cutoff=0.7)
    if matches:
        matched = matches[0]
        for item in item_names:
            if normalize_input(item) == matched:
                return item, None

    # Fallback to pending item if it exists
    if convo and convo.pending_item:
        return convo.pending_item, None

    return None, None


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

    # --- Category match first (View Items flow) ---
    category_type, category_value = get_category_match(player_input)
    if category_type:
        metadata[category_type] = category_value
        return {"intent": PlayerIntent.VIEW_ITEMS, "metadata": metadata}

    # --- Confirmation / Cancellation handling ---
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

    # --- Keyword intent detection ---
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

    # --- Last fallback: try to match item automatically ---
    item_name, _ = find_item_in_input(player_input, convo)
    if item_name:
        metadata["item"] = item_name
        return {"intent": PlayerIntent.BUY_ITEM, "metadata": metadata}

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
