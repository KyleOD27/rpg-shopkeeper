# app/interpreter.py

from app.conversation import PlayerIntent
from app.models.items import get_all_items
from difflib import get_close_matches
import re

INTENT_KEYWORDS = {
    PlayerIntent.VIEW_ITEMS: ["items", "inventory", "stock", "what do you have", "show me"],
    PlayerIntent.BUY_ITEM: ["buy", "purchase", "get", "acquire"],
    PlayerIntent.SELL_ITEM: ["sell", "offload", "trade in"],
    PlayerIntent.DEPOSIT_GOLD: ["deposit", "store gold", "stash"],
    PlayerIntent.WITHDRAW_GOLD: ["withdraw", "take gold", "collect"],
    PlayerIntent.CHECK_BALANCE: ["balance", "gold amount", "how much gold", "check funds"],
    PlayerIntent.VIEW_LEDGER: ["ledger", "transactions", "history"],
    PlayerIntent.HAGGLE: ["haggle", "negotiate", "bargain", "deal"],
}

SMALL_TALK_KEYWORDS = ["thanks", "thank", "hello", "hi", "greetings", "bye", "goodbye", "cheers", "farewell"]

CONFIRMATION_WORDS = ["yes", "yeah", "yep", "aye", "sure", "of course", "deal", "done", "absolutely", "ok", "okay"]

CANCELLATION_WORDS = ["no", "nah", "never", "cancel", "forget it", "stop", "not now"]

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
        return next(item for item in item_names if item.lower() == matched), None

    return None, None

def interpret_input(player_input: str):
    lowered = normalize_input(player_input)
    words = lowered.split()

    # 1. ACTION MATCHING FIRST (prioritised)
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            if intent == PlayerIntent.BUY_ITEM:
                item_name = find_item_in_input(player_input)
                if not item_name:
                    return {"intent": PlayerIntent.BUY_NEEDS_ITEM, "item": None}
                return {"intent": PlayerIntent.BUY_ITEM, "item": item_name}
            return {"intent": intent}

    # 2. THEN CONFIRMATION
    if any(word in words for word in CONFIRMATION_WORDS):
        return {"intent": PlayerIntent.CONFIRM}

    # 3. THEN CANCELLATION
    if any(word in words for word in CANCELLATION_WORDS):
        return {"intent": PlayerIntent.CANCEL}

    # 4. THEN SMALL TALK (lowest priority)
    if any(word in words for word in SMALL_TALK_KEYWORDS):
        return {"intent": PlayerIntent.SMALL_TALK}

    # 5. Default
    return {"intent": PlayerIntent.UNKNOWN}

