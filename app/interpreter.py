# app/interpreter.py

import re
import os
import json
from difflib import get_close_matches
from dotenv import load_dotenv
from openai import OpenAI
from app.conversation import PlayerIntent, ConversationState
from app.models.items import get_all_items, get_all_equipment_categories

# === INTENT KEYWORDS ===
INTENT_KEYWORDS = {
    PlayerIntent.VIEW_ITEMS: ["items", "inventory", "stock", "what do you have", "show me", "what do you sell", "what do you buy", "what else"],
    PlayerIntent.BUY_ITEM: ["buy", "purchase", "get", "acquire"],
    PlayerIntent.SELL_ITEM: ["sell", "offload", "trade in"],
    PlayerIntent.DEPOSIT_GOLD: ["deposit", "store gold", "stash"],
    PlayerIntent.WITHDRAW_GOLD: ["withdraw", "take gold", "collect"],
    PlayerIntent.CHECK_BALANCE: ["balance", "gold amount", "how much gold", "check funds"],
    PlayerIntent.VIEW_LEDGER: ["ledger", "transactions", "history"],
    PlayerIntent.HAGGLE: ["haggle", "negotiate", "bargain", "deal", "cheaper", "too much", "discount"],
    PlayerIntent.SHOW_GRATITUDE: ["thanks", "thankyou", "grateful", "ty"],
    PlayerIntent.GREETING: ["hello", "hi", "greetings", "hallo", "hey", "what up"],
    PlayerIntent.NEXT: ["next", "more", "show more", "continue", "keep going"],
    PlayerIntent.PREVIOUS: ["previous", "back", "go back", "last page"],


}

SMALL_TALK_KEYWORDS = ["goodbye", "farewell"]
CONFIRMATION_WORDS = ["yes", "yeah", "yep", "aye", "sure", "of course", "deal", "done", "absolutely", "ok", "okay", "fine"]
CANCELLATION_WORDS = ["no", "nah", "never", "cancel", "forget it", "stop", "not now", "no deal"]
GRATITUDE_KEYWORDS = ["thanks", "thank", "thank you", "merci", "danke", "ta", "ty", "cheers", "farewell"]

def normalize_input(text: str):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)        # remove punctuation
    text = re.sub(r'\s+', ' ', text)               # collapse extra spaces
    return text

def normalize_input(text: str):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)        # remove punctuation
    text = re.sub(r'\s+', ' ', text)               # collapse extra spaces
    return text

def find_item_in_input(player_input, convo=None):
    items = get_all_items()
    item_names = [item['item_name'] for item in items]
    input_lower = normalize_input(player_input)

    print(f"[DEBUG] Normalized Input: '{input_lower}'")

    # Guard: if it's an exact equipment category, don’t match it as an item
    category = get_equipment_category_from_input(player_input)
    if category and normalize_input(player_input) == normalize_input(category):
        return None, None

    # 1. Full phrase match
    for name in item_names:
        norm_name = normalize_input(name)
        print(f"[DEBUG] Comparing item: '{norm_name}'")
        if norm_name in input_lower:
            print(f"[DEBUG] Item matched by full phrase: '{name}'")
            return name, None

    # 2. Substring match
    exact_matches = [item for item in item_names if normalize_input(item) in input_lower]
    if len(exact_matches) == 1:
        print(f"[DEBUG] Item matched by substring: '{exact_matches[0]}'")
        return exact_matches[0], None
    elif len(exact_matches) > 1:
        print(f"[DEBUG] Multiple substring matches found: {exact_matches}")
        return None, exact_matches

    # 3. Fuzzy match
    matches = get_close_matches(input_lower, [normalize_input(i) for i in item_names], n=1, cutoff=0.7)
    if matches:
        matched = matches[0]
        for item in item_names:
            if normalize_input(item) == matched:
                print(f"[DEBUG] Item matched by fuzzy match: '{item}'")
                return item, None

    # 4. Fallback to pending item
    if convo and convo.pending_item:
        print(f"[DEBUG] Using pending item: {convo.pending_item}")
        return convo.pending_item, None

    print("[DEBUG] No item matched.")
    return None, None





def detect_buy_intent(player_input: str, convo=None):
    item_name, _ = find_item_in_input(player_input, convo)
    if not item_name:
        print(f"[DEBUG] BUY_NEEDS_ITEM: No item identified from input '{player_input}'")
        return PlayerIntent.BUY_NEEDS_ITEM, None
    return PlayerIntent.BUY_ITEM, item_name

def detect_sell_intent(player_input: str):
    item_name, _ = find_item_in_input(player_input)
    if not item_name:
        print(f"[DEBUG] SELL_NEEDS_ITEM: No item identified from input '{player_input}'")
        return PlayerIntent.SELL_NEEDS_ITEM, None
    return PlayerIntent.SELL_ITEM, item_name

def detect_haggle_intent(player_input: str, convo=None):
    input_lower = normalize_input(player_input)

    if convo and convo.pending_item:
        print(f"[DEBUG] Using pending item '{convo.pending_item}' for haggling.")
        return PlayerIntent.HAGGLE, convo.pending_item

    item_name, _ = find_item_in_input(player_input)
    if not item_name:
        print(f"[DEBUG] HAGGLE_NEEDS_ITEM: No item identified from input '{player_input}'")
        return PlayerIntent.HAGGLE, None

    return PlayerIntent.HAGGLE, item_name



def detect_deposit_intent(player_input: str):
    lowered = normalize_input(player_input)
    match = re.search(r'\b\d+\b', lowered)
    if match:
        amount = int(match.group())
        return PlayerIntent.DEPOSIT_GOLD, amount
    print(f"[DEBUG] DEPOSIT_NEEDS_AMOUNT: No amount found in input '{player_input}'")
    return PlayerIntent.DEPOSIT_NEEDS_AMOUNT, None

def detect_withdraw_intent(player_input: str):
    lowered = normalize_input(player_input)
    match = re.search(r'\b\d+\b', lowered)
    if match:
        amount = int(match.group())
        return PlayerIntent.WITHDRAW_GOLD, amount
    print(f"[DEBUG] WITHDRAW_NEEDS_AMOUNT: No amount found in input '{player_input}'")
    return PlayerIntent.WITHDRAW_NEEDS_AMOUNT, None


def get_equipment_category_from_input(player_input: str):
    from app.models.items import get_all_equipment_categories
    from difflib import get_close_matches

    input_lower = normalize_input(player_input)
    input_words = input_lower.split()

    categories = get_all_equipment_categories()
    category_names = [c.lower() for c in categories]

    # 1. Exact match
    for cat in category_names:
        if cat in input_lower:
            return cat.title()

    # 2. Partial word match
    for cat in category_names:
        cat_tokens = cat.split()
        if any(word in input_words for word in cat_tokens):
            return cat.title()

    # 3. Fuzzy match
    close = get_close_matches(input_lower, category_names, n=1, cutoff=0.6)
    if close:
        return close[0].title()

    return None



def interpret_input(player_input: str, convo=None):
    input_text = player_input if isinstance(player_input, str) else player_input.get("input", "")
    lowered = normalize_input(input_text)
    words = lowered.split()

    # ✅ 1. Confirmation
    if any(word in words for word in CONFIRMATION_WORDS):
        if convo and convo.player_intent == PlayerIntent.SELL_ITEM:
            return {"intent": PlayerIntent.SELL_CONFIRM}
        elif convo and convo.player_intent == PlayerIntent.BUY_ITEM:
            return {"intent": PlayerIntent.BUY_CONFIRM}
        elif convo and convo.player_intent == PlayerIntent.HAGGLE:
            return {"intent": PlayerIntent.HAGGLE_CONFIRM}
        return {"intent": PlayerIntent.CONFIRM}

    # ✅ 2. Cancellation
    if any(word in words for word in CANCELLATION_WORDS):
        if convo and convo.player_intent == PlayerIntent.SELL_ITEM:
            return {"intent": PlayerIntent.SELL_CANCEL}
        elif convo and convo.player_intent == PlayerIntent.BUY_ITEM:
            return {"intent": PlayerIntent.BUY_CANCEL}
        elif convo and convo.player_intent == PlayerIntent.HAGGLE:
            return {"intent": PlayerIntent.HAGGLE_CANCEL}
        return {"intent": PlayerIntent.CANCEL}

    # ✅ 3. Gratitude / Small Talk
    if any(word in words for word in GRATITUDE_KEYWORDS):
        return {"intent": PlayerIntent.SHOW_GRATITUDE}
    if any(word in words for word in SMALL_TALK_KEYWORDS):
        return {"intent": PlayerIntent.SMALL_TALK}

    # ✅ 4. Keyword-Based Action Matching
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            if intent == PlayerIntent.BUY_ITEM:
                intent_type, item = detect_buy_intent(player_input, convo)
                return {"intent": intent_type, "item": item}
            elif intent == PlayerIntent.SELL_ITEM:
                intent_type, item = detect_sell_intent(player_input)
                return {"intent": intent_type, "item": item}
            elif intent == PlayerIntent.HAGGLE:
                intent_type, item = detect_haggle_intent(player_input, convo)
                return {"intent": intent_type, "item": item}
            elif intent == PlayerIntent.DEPOSIT_GOLD:
                intent_type, amount = detect_deposit_intent(player_input)
                return {"intent": intent_type, "amount": amount}
            elif intent == PlayerIntent.WITHDRAW_GOLD:
                intent_type, amount = detect_withdraw_intent(player_input)
                return {"intent": intent_type, "amount": amount}
            else:
                return {"intent": intent}

    # ✅ 5. Item Detection without action word
    item_name, _ = find_item_in_input(player_input)
    if item_name:
        return {"intent": PlayerIntent.BUY_ITEM, "item": item_name}

    # ✅ 5.5. Equipment Category Detection (e.g. "armor", "tools")
    category = get_equipment_category_from_input(player_input)
    if category:
        return {"intent": PlayerIntent.VIEW_ITEMS, "category": category}

    # ✅ 6. If awaiting deposit amount and numeric input
    if convo and convo.player_intent == PlayerIntent.DEPOSIT_NEEDS_AMOUNT:
        match = re.search(r'\d+', lowered)
        if match:
            amount = int(match.group())
            return {"intent": PlayerIntent.DEPOSIT_CONFIRM, "amount": amount}

    # ✅ 7. If awaiting withdraw amount and numeric input
    if convo and convo.player_intent == PlayerIntent.WITHDRAW_NEEDS_AMOUNT:
        match = re.search(r'\d+', lowered)
        if match:
            amount = int(match.group())
            return {"intent": PlayerIntent.WITHDRAW_CONFIRM, "amount": amount}

    # ✅ 8. GPT fallback
    gpt_result = check_confirmation_via_gpt(player_input, convo)
    if gpt_result in [
        PlayerIntent.BUY_CONFIRM, PlayerIntent.BUY_CANCEL,
        PlayerIntent.SELL_CONFIRM, PlayerIntent.SELL_CANCEL,
        PlayerIntent.HAGGLE_CONFIRM, PlayerIntent.HAGGLE_CANCEL
    ]:
        return {"intent": gpt_result}

    return {"intent": PlayerIntent.UNKNOWN}



# === GPT FALLBACK CLASSIFIER ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def check_confirmation_via_gpt(user_input: str, convo=None):

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
                if convo and convo.player_intent == PlayerIntent.SELL_ITEM:
                    return PlayerIntent.SELL_CONFIRM
                elif convo and convo.player_intent == PlayerIntent.BUY_ITEM:
                    return PlayerIntent.BUY_CONFIRM
                return PlayerIntent.CONFIRM
            elif result["intent"] == "CANCEL":
                if convo and convo.player_intent == PlayerIntent.SELL_ITEM:
                    return PlayerIntent.SELL_CANCEL
                elif convo and convo.player_intent == PlayerIntent.BUY_ITEM:
                    return PlayerIntent.BUY_CANCEL
                return PlayerIntent.CANCEL


    except Exception as e:
        print("[GPT CONFIRM CHECK ERROR]", e)

    return PlayerIntent.UNKNOWN
