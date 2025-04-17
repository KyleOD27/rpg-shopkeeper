# app/interpreter.py

import re
import os
import json
from difflib import get_close_matches
from dotenv import load_dotenv
from openai import OpenAI

from app.conversation import PlayerIntent
from app.models.items import get_all_items

# === INTENT KEYWORDS ===
INTENT_KEYWORDS = {
    PlayerIntent.VIEW_ITEMS: ["items", "inventory", "stock", "what do you have", "show me"],
    PlayerIntent.BUY_ITEM: ["buy", "purchase", "get", "acquire"],
    PlayerIntent.SELL_ITEM: ["sell", "offload", "trade in"],
    PlayerIntent.DEPOSIT_GOLD: ["deposit", "store gold", "stash"],
    PlayerIntent.WITHDRAW_GOLD: ["withdraw", "take gold", "collect"],
    PlayerIntent.CHECK_BALANCE: ["balance", "gold amount", "how much gold", "check funds"],
    PlayerIntent.VIEW_LEDGER: ["ledger", "transactions", "history"],
    PlayerIntent.HAGGLE: ["haggle", "negotiate", "bargain", "deal"],
    PlayerIntent.SHOW_GRATITUDE: ["thanks", "thankyou", "grateful", "ty"],
}

SMALL_TALK_KEYWORDS = ["hello", "hi", "greetings", "bye", "goodbye", "farewell"]
CONFIRMATION_WORDS = ["yes", "yeah", "yep", "aye", "sure", "of course", "deal", "done", "absolutely", "ok", "okay", "fine"]
CANCELLATION_WORDS = ["no", "nah", "never", "cancel", "forget it", "stop", "not now", "no deal"]
GRATITUDE_KEYWORDS = ["thanks", "thank", "thank you", "merci", "danke", "ta", "ty", "cheers", "farewell"]

def normalize_input(text: str):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower().strip())


def find_item_in_input(player_input: str):
    items = get_all_items()
    item_names = [item['item_name'] for item in items]
    input_lower = normalize_input(player_input)

    # Direct match
    exact_matches = [item for item in item_names if item.lower() in input_lower]
    if len(exact_matches) == 1:
        return exact_matches[0], None
    elif len(exact_matches) > 1:
        return None, exact_matches

    # Token match
    partial_matches = []
    for item in item_names:
        if any(token in input_lower.split() for token in item.lower().split()):
            partial_matches.append(item)
    if len(partial_matches) == 1:
        return partial_matches[0], None
    elif partial_matches:
        return None, partial_matches

    # Fuzzy match
    matches = get_close_matches(input_lower, [i.lower() for i in item_names], n=1, cutoff=0.6)
    if matches:
        matched = matches[0]
        for item in item_names:
            if item.lower() == matched:
                return item, None

    return None, None


def detect_buy_intent(player_input: str):
    item_name, _ = find_item_in_input(player_input)
    if not item_name:
        print(f"[DEBUG] BUY_NEEDS_ITEM: No item identified from input '{player_input}'")
        return PlayerIntent.BUY_NEEDS_ITEM, None
    return PlayerIntent.BUY_ITEM, item_name


def interpret_input(player_input: str):
    lowered = normalize_input(player_input)
    words = lowered.split()

    # 1. ACTION MATCHING
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            if intent == PlayerIntent.BUY_ITEM:
                intent_type, item = detect_buy_intent(player_input)
                return {"intent": intent_type, "item": item}
            return {"intent": intent}

    # 2. CONFIRMATION
    if any(word in words for word in CONFIRMATION_WORDS):
        return {"intent": PlayerIntent.CONFIRM}

    # 3. ITEM DETECTION without intent keyword
    item_name, _ = find_item_in_input(player_input)
    if item_name:
        return {"intent": PlayerIntent.BUY_ITEM, "item": item_name}

    # 4. CONFIRMATION (move this further down)
    if any(word in words for word in CONFIRMATION_WORDS):
        return {"intent": PlayerIntent.CONFIRM}

    # 4. SMALL TALK
    if any(word in words for word in SMALL_TALK_KEYWORDS):
        return {"intent": PlayerIntent.SMALL_TALK}

    # 5. SMALL TALK
    if any(word in words for word in GRATITUDE_KEYWORDS):
            return {"intent": PlayerIntent.SHOW_GRATITUDE}

    # 5. GPT fallback for confirmation/cancel detection
    gpt_result = check_confirmation_via_gpt(player_input)
    if gpt_result in [PlayerIntent.CONFIRM, PlayerIntent.CANCEL]:
        return {"intent": gpt_result}

    # 6. Unknown
    return {"intent": PlayerIntent.UNKNOWN}


# === GPT FALLBACK CLASSIFIER ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def check_confirmation_via_gpt(user_input: str):
    system_prompt = (
        "You are a classifier that determines whether a user's sentence is a CONFIRMATION, "
        "a CANCELLATION, or UNKNOWN. "
        "Return JSON in this format: { \"intent\": \"CONFIRM\" | \"CANCEL\" | \"UNKNOWN\", \"confidence\": <int 0–100> }."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"\"{user_input}\""}
            ],
            temperature=0.0,
            max_tokens=100,
        )

        result = json.loads(response.choices[0].message.content.strip())

        if result.get("confidence", 0) >= 85:
            if result["intent"] == "CONFIRM":
                return PlayerIntent.CONFIRM
            elif result["intent"] == "CANCEL":
                return PlayerIntent.CANCEL

    except Exception as e:
        print("[GPT CONFIRM CHECK ERROR]", e)

    return PlayerIntent.UNKNOWN
