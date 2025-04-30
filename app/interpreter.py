# app/interpreter.py

import re
import os
import json
import logging
from difflib import get_close_matches
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

from app.conversation import PlayerIntent
from app.models.items import (
    get_all_items,
    get_all_equipment_categories,
    get_weapon_categories,
    get_gear_categories,
    get_armour_categories,
    get_tool_categories,
)

# ─── Logging setup ───────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# ─── 1. INTENT PROTOTYPES & STOP-WORDS ───────────────────────────────────

# Keywords per intent (for ranking + exact detection)
INTENT_KEYWORDS = {
    PlayerIntent.VIEW_ITEMS: [
        "items","inventory","stock","what do you have","show me",
        "what do you sell","what do you buy","browse"
    ],
    PlayerIntent.VIEW_ARMOUR_CATEGORY: ["armor","armour"],
    PlayerIntent.VIEW_WEAPON_CATEGORY: ["weapon","weapons"],
    PlayerIntent.VIEW_GEAR_CATEGORY: ["gear","adventuring gear","supplies","packs"],
    PlayerIntent.VIEW_TOOL_CATEGORY: ["tool","tools","artisan's tools","kits"],
    PlayerIntent.VIEW_EQUIPMENT_CATEGORY: ["equipment","mounts","vehicles","travelling gear"],

    PlayerIntent.VIEW_ARMOUR_SUBCATEGORY: ["light","medium","heavy"],
    PlayerIntent.VIEW_WEAPON_SUBCATEGORY: ["simple","martial"],
    PlayerIntent.VIEW_GEAR_SUBCATEGORY: ["backpack","rope","tinderbox","torch"],
    PlayerIntent.VIEW_TOOL_SUBCATEGORY: ["artisan","disguise","forgery","thieves","musical"],

    PlayerIntent.BUY_ITEM: ["buy","purchase","get","acquire","grab","want"],
    PlayerIntent.SELL_ITEM: ["sell","offload","trade in"],

    PlayerIntent.DEPOSIT_GOLD: ["deposit","store gold","stash"],
    PlayerIntent.WITHDRAW_GOLD: ["withdraw","take gold","collect"],

    PlayerIntent.CHECK_BALANCE: ["balance","gold amount","how much gold","check funds"],
    PlayerIntent.VIEW_LEDGER: ["ledger","transactions","history"],
    PlayerIntent.HAGGLE: ["haggle","negotiate","bargain","deal","cheaper","discount"],

    PlayerIntent.SHOW_GRATITUDE: ["thanks","thankyou","grateful","ty"],
    PlayerIntent.GREETING: ["hello","hi","greetings","hallo","hey","what up"],

    PlayerIntent.NEXT: ["next","more","show more","continue","keep going"],
    PlayerIntent.PREVIOUS: ["previous","back","go back","last page"],

    PlayerIntent.INSPECT_ITEM: [
        "inspect","details","tell me about","what does it do",
        "info","information","what is","explain","describe","how much","see more"
    ],
}

# Words to strip when sanitizing
STOP_WORDS = {
    "a","an","the","and","or","but","of","for","to","in","on","at",
    "please","good","sir","maam","hey","hi","how","much","might","be",
    "is","are","was","were","i","you","do","does"
}

# Phrases to strip as polite prefixes
INTENT_PREFIXES = [
    "i want to buy","i want to purchase","can i buy",
    "how much is","how much would","tell me about",
    "what does","what is","show me",
]

CONFIRMATION_WORDS = ["yes","yeah","yep","sure","ok","okay","aye"]
CANCELLATION_WORDS = ["no","nah","cancel","stop","never","forget"]
GRATITUDE_KEYWORDS = ["thanks","thank you","ty","cheers"]
GOODBYE_KEYWORDS = ["bye","farewell","later","see you"]

INTENT_CONF_THRESHOLD = 0.10


# ─── 2. NORMALIZATION & SANITIZATION ────────────────────────────────────

def normalize_input(text: str, convo=None) -> str:
    """Lowercase, remove punctuation, collapse spaces."""
    norm = re.sub(r'[^a-z0-9\s]', '', text.lower()).strip()
    norm = re.sub(r'\s+', ' ', norm)
    if convo is not None:
        convo.normalized_input = norm
    return norm

def sanitize(text: str) -> str:
    """Lowercase, remove punctuation, drop STOP_WORDS."""
    txt = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
    tokens = [t for t in txt.split() if t not in STOP_WORDS]
    return ' '.join(tokens)

def preprocess(player_input: str) -> str:
    """Collapse spaces, strip INTENT_PREFIXES, then sanitize."""
    t = re.sub(r'\s+', ' ', player_input.strip().lower())
    for p in sorted(INTENT_PREFIXES, key=len, reverse=True):
        if t.startswith(p + " "):
            t = t[len(p)+1:]
            break
    return sanitize(t)


# ─── 3. LOCAL INTENT RANKER ─────────────────────────────────────────────

def rank_intent_kw(user_input: str):
    """
    Score each intent by counting how many of its keywords appear in the normalized input.
    """
    raw = normalize_input(user_input)
    logger.debug(f"[RANKER] raw normalized: {raw!r}")
    scores = {}
    for intent, kws in INTENT_KEYWORDS.items():
        scores[intent] = sum(1 for kw in kws if kw in raw)
    best = max(scores, key=scores.get)
    best_score = scores[best]
    total = max(len(INTENT_KEYWORDS[best]), 1)
    conf = best_score / total
    logger.debug(f"[RANKER] scores={scores}, best={best}, conf={conf:.2f}")
    return best, conf


# ─── 4. CATEGORY MATCHERS ────────────────────────────────────────────────

def get_category_match(player_input: str):
    lowered = normalize_input(player_input)
    categories = {
        "equipment_category": get_all_equipment_categories(),
        "weapon_category":    get_weapon_categories(),
        "gear_category":      get_gear_categories(),
        "armour_category":    get_armour_categories(),
        "tool_category":      get_tool_categories(),
    }
    for field, names in categories.items():
        normed = [normalize_input(n) for n in names]
        if lowered in normed:
            return field, names[normed.index(lowered)]
        close = get_close_matches(lowered, normed, n=1, cutoff=0.8)
        if close:
            return field, names[normed.index(close[0])]
    return None, None

def get_subcategory_match(section: str, player_input: str):
    lowered = normalize_input(player_input)
    if section == "armor":
        cats = get_armour_categories()
    elif section == "weapon":
        cats = get_weapon_categories()
    elif section == "gear":
        cats = get_gear_categories()
    elif section == "tool":
        cats = get_tool_categories()
    else:
        return None
    norm_map = {normalize_input(c): c for c in cats}
    for norm, orig in norm_map.items():
        if norm in lowered:
            return orig
    close = get_close_matches(lowered, norm_map.keys(), n=1, cutoff=0.75)
    return norm_map.get(close[0]) if close else None


# ─── 5. ITEM MATCHER ─────────────────────────────────────────────────────

def find_item_in_input(player_input: str, convo=None):
    """
    1) Strip polite prefixes from a temp copy
    2) Numeric ID
    3) Category name
    4) Full item-name
    5) Fuzzy by token
    6) Fallback to convo.pending_item
    """
    raw = normalize_input(player_input)
    # strip polite prefixes only for matching
    for p in [
        "could you","would you","can you","i want to","i'd like to",
        "please","hey","good sir","thank you","thanks",
        "would it cost","what does it do","i'm looking to"
    ]:
        raw = raw.replace(p, "")
    raw = raw.strip()
    words = raw.split()

    # load items
    items = []
    for rec in get_all_items():
        try:
            obj = json.loads(rec) if isinstance(rec, str) else rec
            items.append(dict(obj))
        except:
            continue

    # 1️⃣ by ID
    digit = next((w for w in words if w.isdigit()), None)
    if digit:
        matches = [i for i in items if str(i.get("item_id")) == digit]
        if matches:
            logger.debug(f"[ITEM MATCH] by ID {digit}: {matches}")
            return matches, None

    # 2️⃣ by category
    all_cats = (
        get_all_equipment_categories() +
        get_weapon_categories() +
        get_gear_categories() +
        get_armour_categories() +
        get_tool_categories()
    )
    cat_map = {normalize_input(c): c for c in all_cats}
    for norm, orig in cat_map.items():
        if norm in raw:
            logger.debug(f"[ITEM MATCH] category full: {orig}")
            return None, orig
    for w in words:
        close = get_close_matches(w, cat_map.keys(), n=1, cutoff=0.7)
        if close:
            logger.debug(f"[ITEM MATCH] category fuzzy: {cat_map[close[0]]}")
            return None, cat_map[close[0]]

    # 3️⃣ full name
    name_map = {normalize_input(i["item_name"]): i for i in items}
    for norm, itm in name_map.items():
        if norm in raw:
            logger.debug(f"[ITEM MATCH] full name: {itm['item_name']}")
            return [itm], None

    # 4️⃣ fuzzy tokens
    matches = []
    for w in words:
        close = get_close_matches(w, name_map.keys(), n=3, cutoff=0.6)
        for nm in close:
            itm = name_map[nm]
            if itm not in matches:
                matches.append(itm)
                logger.debug(f"[ITEM MATCH] fuzzy: {itm['item_name']}")
    if matches:
        return matches, None

    # 5️⃣ fallback to pending
    if convo and convo.get_pending_item():
        pend = convo.get_pending_item()
        if isinstance(pend, dict):
            return [pend], None
        if isinstance(pend, list):
            return pend, None
        if isinstance(pend, str):
            return [{"item_name": pend}], None

    logger.debug("[ITEM MATCH] no matches")
    return None, None


# ─── 6. INTENT DETECTORS ─────────────────────────────────────────────────

def detect_buy_intent(player_input: str, convo=None):
    items, _ = find_item_in_input(player_input, convo)
    return (PlayerIntent.BUY_ITEM, items) if items else (PlayerIntent.BUY_NEEDS_ITEM, None)

def detect_sell_intent(player_input: str, convo=None):
    items, _ = find_item_in_input(player_input, convo)
    return (PlayerIntent.SELL_ITEM, items) if items else (PlayerIntent.SELL_NEEDS_ITEM, None)

def detect_deposit_intent(player_input: str, convo=None):
    m = re.search(r'\b\d+\b', normalize_input(player_input))
    return (PlayerIntent.DEPOSIT_GOLD, int(m.group())) if m else (PlayerIntent.DEPOSIT_NEEDS_AMOUNT, None)

def detect_withdraw_intent(player_input: str, convo=None):
    m = re.search(r'\b\d+\b', normalize_input(player_input))
    return (PlayerIntent.WITHDRAW_GOLD, int(m.group())) if m else (PlayerIntent.WITHDRAW_NEEDS_AMOUNT, None)


# ─── 7. MAIN INTERPRETER ─────────────────────────────────────────────────

from app.conversation import PlayerIntent, ConversationState

import re

def interpret_input(player_input: str, convo=None):
    logger.debug(f"[INTERPRETER] raw input: {player_input!r}")
    lowered = normalize_input(player_input)

    # ─── 0a) NUMERIC INSPECT OVERRIDE during confirmation ────────────────────
    from app.conversation import ConversationState
    if convo and convo.state == ConversationState.AWAITING_CONFIRMATION:
        # if they mention an ID, treat it as an inspect request
        m = re.search(r'\b(\d+)\b', lowered)
        if m:
            items, _ = find_item_in_input(player_input, convo)
            if items:
                meta = {}
                meta["item"] = items if len(items) > 1 else items[0]["item_name"]
                logger.debug(f"[INTERPRETER] confirm-flow numeric-inspect override → INSPECT_ITEM, items={items!r}")
                return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": meta}

    # ─── 0b) INFO/DETAILS on PENDING item ────────────────────────────────────
    if convo and convo.state == ConversationState.AWAITING_CONFIRMATION:
        if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.INSPECT_ITEM]):
            # falls back to convo.get_pending_item() inside find_item_in_input
            items, _ = find_item_in_input(player_input, convo)
            if items:
                meta = {}
                meta["item"] = items if len(items) > 1 else items[0]["item_name"]
                logger.debug(f"[INTERPRETER] confirm-flow keyword-inspect override → INSPECT_ITEM, items={items!r}")
                return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": meta}

    # ─── 1) local ranker ─────────────────────────────────────────────────────
    intent_r, conf = rank_intent_kw(player_input)
    logger.debug(f"[INTERPRETER] ranker -> {intent_r} (conf={conf:.2f})")
    if conf >= INTENT_CONF_THRESHOLD:
        meta = {}
        if intent_r == PlayerIntent.BUY_ITEM:
            intent, items = detect_buy_intent(player_input, convo)
            meta["item"] = items
            return {"intent": intent, "metadata": meta}
        if intent_r == PlayerIntent.SELL_ITEM:
            intent, items = detect_sell_intent(player_input, convo)
            meta["item"] = items
            return {"intent": intent, "metadata": meta}
        if intent_r in {
            PlayerIntent.VIEW_ITEMS,
            PlayerIntent.VIEW_ARMOUR_CATEGORY,
            PlayerIntent.VIEW_WEAPON_CATEGORY,
            PlayerIntent.VIEW_GEAR_CATEGORY,
            PlayerIntent.VIEW_TOOL_CATEGORY,
            PlayerIntent.VIEW_EQUIPMENT_CATEGORY,
        }:
            field, val = get_category_match(player_input)
            if field:
                meta[field] = val
            return {"intent": intent_r, "metadata": meta}
        if intent_r == PlayerIntent.INSPECT_ITEM:
            items, _ = find_item_in_input(player_input, convo)
            if items:
                # always send the dict(s), never a plain name
                meta["item"] = items if len(items) > 1 else items[0]
            return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": meta}

        # CONFIRM/CANCEL/etc
        return {"intent": intent_r, "metadata": {}}

    # ─── 2a) FALLBACK BUY OVERRIDE ────────────────────────────────────────────
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.BUY_ITEM]):
        intent, items = detect_buy_intent(player_input, convo)
        meta = {}
        if items:
            meta["item"] = items
        logger.debug(f"[INTERPRETER] fallback BUY override → {intent}, items={items!r}")
        return {"intent": intent, "metadata": meta}

    # ─── 2b) CATEGORY ───────────────────────────────────────────────────────
    field, val = get_category_match(player_input)
    if field:
        intent_name = f"VIEW_{field.upper()}"
        intent = getattr(PlayerIntent, intent_name, PlayerIntent.VIEW_ITEMS)
        return {"intent": intent, "metadata": {field: val}}

    # ─── 2c) CONFIRM/CANCEL/THANKS/GOODBYE ─────────────────────────────────
    words = lowered.split()
    if any(w in words for w in CONFIRMATION_WORDS):
        return {"intent": PlayerIntent.CONFIRM, "metadata": {}}
    if any(w in words for w in CANCELLATION_WORDS):
        return {"intent": PlayerIntent.CANCEL, "metadata": {}}
    if any(w in words for w in GRATITUDE_KEYWORDS):
        return {"intent": PlayerIntent.SHOW_GRATITUDE, "metadata": {}}
    if any(w in words for w in GOODBYE_KEYWORDS):
        return {"intent": PlayerIntent.GOODBYE, "metadata": {}}

    # ─── 2d) INSPECT OVERRIDE (general) ────────────────────────────────────
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.INSPECT_ITEM]):
        items, _ = find_item_in_input(player_input, convo)
        meta = {}
        if items:
            meta["item"] = items if len(items) > 1 else items[0]["item_name"]
        return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": meta}

    # ─── 2e) FINAL FALLBACK TO BUY ──────────────────────────────────────────
    items, _ = find_item_in_input(player_input, convo)
    if items:
        return {"intent": PlayerIntent.BUY_ITEM, "metadata": {"item": items}}

    # ─── 3) GIVE UP ─────────────────────────────────────────────────────────
    logger.debug("[INTERPRETER] → UNKNOWN")
    return {"intent": PlayerIntent.UNKNOWN, "metadata": {}}


    # 4) BUY override if any buy-keyword anywhere
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.BUY_ITEM]):
        intent, items = detect_buy_intent(player_input, convo)
        meta = {"item": items} if items else {}
        logger.debug(f"[INTERPRETER] fallback BUY override → {intent}, items={items!r}")
        return {"intent": intent, "metadata": meta}

    # 5) Category browsing fallback
    field, val = get_category_match(player_input)
    if field:
        intent = getattr(PlayerIntent, f"VIEW_{field.upper()}", PlayerIntent.VIEW_ITEMS)
        return {"intent": intent, "metadata": {field: val}}

    # 6) Gratitude/goodbye
    if any(w in lowered.split() for w in GRATITUDE_KEYWORDS):
        return {"intent": PlayerIntent.SHOW_GRATITUDE, "metadata": {}}
    if any(w in lowered.split() for w in GOODBYE_KEYWORDS):
        return {"intent": PlayerIntent.GOODBYE, "metadata": {}}

    # 7) Inspect-keyword fallback
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.INSPECT_ITEM]):
        items, _ = find_item_in_input(player_input, convo)
        if items:
            meta = {"item": items if len(items) > 1 else items[0]["item_name"]}
            return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": meta}

    # 8) Final fallback → BUY if it looks like an item mention
    items, _ = find_item_in_input(player_input, convo)
    if items:
        return {"intent": PlayerIntent.BUY_ITEM, "metadata": {"item": items}}

    # 9) Give up
    logger.debug("[INTERPRETER] → UNKNOWN")
    return {"intent": PlayerIntent.UNKNOWN, "metadata": {}}



# ─── 8. GPT CONFIRM FALLBACK (unchanged) ────────────────────────────────

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def check_confirmation_via_gpt(user_input: str, convo=None):
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system","content":"Classify CONFIRM/CANCEL/UNKNOWN. Return JSON."},
                {"role":"user","content":f"\"{user_input}\""}
            ],
            temperature=0, max_tokens=30
        )
        j = json.loads(resp.choices[0].message.content)
        if j.get("intent") == "CONFIRM": return PlayerIntent.CONFIRM
        if j.get("intent") == "CANCEL":  return PlayerIntent.CANCEL
    except Exception as e:
        logger.debug(f"[GPT CONFIRM] error {e}")
    return PlayerIntent.UNKNOWN


# ─── 9. COMPATIBILITY HELPERS ────────────────────────────────────────────

def get_equipment_category_from_input(text: str): return get_category_match(text)[1]
def get_weapon_category_from_input(text: str):    return get_category_match(text)[1]
def get_gear_category_from_input(text: str):      return get_category_match(text)[1]
def get_armour_category_from_input(text: str):    return get_category_match(text)[1]
def get_tool_category_from_input(text: str):      return get_category_match(text)[1]
