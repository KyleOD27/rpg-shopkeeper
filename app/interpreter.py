# app/interpreter.py – enhanced for plural/synonym and n-gram matching

from __future__ import annotations

import json
import logging
import os
import re
from difflib import get_close_matches
from typing import Any, Dict, Tuple

import inflect
p = inflect.engine()

from dotenv import load_dotenv
from openai import OpenAI

from app.conversation import Conversation, ConversationState, PlayerIntent
from app.models.items import (
    get_all_equipment_categories,
    get_all_items,
    get_armour_categories,
    get_gear_categories,
    get_tool_categories,
    get_weapon_categories, get_treasure_categories,
)
from app.keywords import (
    INTENT_KEYWORDS,
    STOP_WORDS,
    SHOP_ACTION_WORDS,
    INTENT_PREFIXES,
    CONFIRMATION_WORDS,
    CANCELLATION_WORDS,
    GRATITUDE_KEYWORDS,
    GOODBYE_KEYWORDS,
    INTENT_CONF_THRESHOLD,
    EXCEPTION_WORDS
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Optionally add category or item aliases here (e.g. "heals" -> "Potion")
CATEGORY_ALIASES = {
    "potions": "potion",
    "heals": "potion",
    "scrolls": "scroll",
    # Extend as needed!
}

# ─── Normalisation helpers ──────────────────────────────────────────────

def singularize(word):
    return p.singular_noun(word) or word

def normalize_input(text: str, convo: Conversation | None = None) -> str:
    norm = re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()
    norm = re.sub(r"\s+", " ", norm)
    # Singularize each word, strip stopwords
    norm = " ".join(singularize(w) for w in norm.split() if w not in STOP_WORDS)
    # Apply category alias (only for single-word queries)
    if norm in CATEGORY_ALIASES:
        norm = CATEGORY_ALIASES[norm]
    if convo is not None:
        convo.normalized_input = norm
    return norm

def sanitize(text: str) -> str:
    txt = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    tokens = [singularize(t) for t in txt.split() if t not in STOP_WORDS]
    # Apply alias at token level if needed
    tokens = [CATEGORY_ALIASES.get(tok, tok) for tok in tokens]
    return " ".join(tokens)

def preprocess(player_input: str) -> str:
    t = re.sub(r"\s+", " ", player_input.strip().lower())
    for pfx in sorted(INTENT_PREFIXES, key=len, reverse=True):
        if t.startswith(pfx + " "):
            t = t[len(pfx) + 1:]
            break
    return sanitize(t)

# ─── Ranker helpers ─────────────────────────────────────────────────────

PREFERRED_ORDER: list[PlayerIntent] = [
    PlayerIntent.DEPOSIT_BALANCE,
    PlayerIntent.WITHDRAW_BALANCE,
    PlayerIntent.CHECK_BALANCE,
    PlayerIntent.VIEW_LEDGER,
    PlayerIntent.STASH_ADD,
    PlayerIntent.STASH_REMOVE,
    PlayerIntent.BUY_ITEM,
    PlayerIntent.SELL_ITEM,
    PlayerIntent.INSPECT_ITEM,
    PlayerIntent.VIEW_WEAPON_SUBCATEGORY,
    PlayerIntent.VIEW_ARMOUR_SUBCATEGORY,
    PlayerIntent.VIEW_GEAR_SUBCATEGORY,
    PlayerIntent.VIEW_TOOL_SUBCATEGORY,
    PlayerIntent.VIEW_TREASURE_SUBCATEGORY,
    PlayerIntent.VIEW_ITEMS,
    PlayerIntent.VIEW_EQUIPMENT_CATEGORY,
    PlayerIntent.VIEW_WEAPON_CATEGORY,
    PlayerIntent.VIEW_ARMOUR_CATEGORY,
    PlayerIntent.VIEW_GEAR_CATEGORY,
    PlayerIntent.VIEW_TOOL_CATEGORY,
    PlayerIntent.SHOW_GRATITUDE,
    PlayerIntent.GREETING,
    PlayerIntent.NEXT,
    PlayerIntent.PREVIOUS,
]

# Build a normalized copy of the intent keywords for matching
NORMALIZED_INTENT_KEYWORDS = {
    intent: [normalize_input(kw) for kw in kws]
    for intent, kws in INTENT_KEYWORDS.items()
}

def _pref_index(intent: PlayerIntent) -> int:
    try:
        return PREFERRED_ORDER.index(intent)
    except ValueError:
        return len(PREFERRED_ORDER)

def rank_intent_kw(user_input: str, convo: Conversation | None = None) -> tuple[PlayerIntent, float]:
    raw = normalize_input(user_input)
    scores = {
        intent: sum(1 for kw in NORMALIZED_INTENT_KEYWORDS[intent] if kw in raw)
        for intent in NORMALIZED_INTENT_KEYWORDS
    }
    best_intent = max(scores, key=lambda i: (scores[i], -_pref_index(i)))
    confidence = scores[best_intent] / max(len(NORMALIZED_INTENT_KEYWORDS[best_intent]), 1)

    if convo is not None:
        convo.debug(f"[RANK] {best_intent.name} {confidence:.2f} {scores}")
    else:
        logger.debug(
            "[rank_intent_kw] %r → %s %.2f %s",
            user_input, best_intent.name, confidence, scores,
        )
    return best_intent, confidence


# ─── Category helpers (improved) ───────────────────────────────────────

def get_category_match(player_input: str):
    lowered = normalize_input(player_input)
    # Alias correction
    if lowered in CATEGORY_ALIASES:
        lowered = CATEGORY_ALIASES[lowered]
    cats = {
        "equipment_category": get_all_equipment_categories(),
        "weapon_category": get_weapon_categories(),
        "gear_category": get_gear_categories(),
        "armour_category": get_armour_categories(),
        "tool_category": get_tool_categories(),
        "treasure_category": get_treasure_categories()
    }
    # Try n-gram match first
    for field, names in cats.items():
        normed = [normalize_input(n) for n in names]
        # Exact or alias match
        if lowered in normed:
            return field, names[normed.index(lowered)]
        # Try close match with fuzzy
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
    elif section == "treasure":
        cats = get_treasure_categories()
    else:
        return None
    norm_map = {normalize_input(c): c for c in cats}
    # Direct or alias match
    if lowered in norm_map:
        return norm_map[lowered]
    for norm in sorted(norm_map.keys(), key=len, reverse=True):
        if norm in lowered:
            return norm_map[norm]
    close = get_close_matches(lowered, norm_map.keys(), n=1, cutoff=0.7)
    return norm_map.get(close[0]) if close else None

# ─── Item matcher (improved for n-grams) ─────────────────────────────

from difflib import SequenceMatcher, get_close_matches

def tokenize(text):
    # Lowercase, remove punctuation, singularize, strip stopwords
    words = [singularize(w) for w in re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()]
    return set(w for w in words if w and w not in STOP_WORDS)

def find_item_in_input(
    player_input: str,
    convo=None,
    *,
    fuzzy_cutoff: float = 0.75,
    max_suggestions: int = 3
):
    raw = preprocess(player_input)
    norm_raw = normalize_input(raw)
    if (
        norm_raw in EXCEPTION_WORDS
        or norm_raw in SHOP_ACTION_WORDS
        or (len(norm_raw) < 4 and not norm_raw.isdigit())
    ):
        return None, None

    words = norm_raw.split()
    items = [dict(json.loads(r) if isinstance(r, str) else r) for r in get_all_items()]
    name_map = {normalize_input(i["item_name"]): i for i in items}
    input_tokens = tokenize(player_input)

    # 1. N-gram exact
    for n in range(len(words), 0, -1):
        for i in range(len(words) - n + 1):
            ngram = " ".join(words[i:i + n])
            if ngram in name_map:
                return [name_map[ngram]], None

    # 2. Numeric ID
    digit = next((w for w in words if w.isdigit()), None)
    if digit:
        matches = [i for i in items if str(i.get("item_id")) == digit]
        if matches:
            return matches, None

    # 3. Improved Fuzzy/Token Overlap
    scored = []
    for item in items:
        item_name = item["item_name"]
        item_tokens = tokenize(item_name)
        # Token overlap score (proportion of query tokens found in item)
        overlap = len(input_tokens & item_tokens) / max(1, len(input_tokens))
        # SequenceMatcher ratio for fallback
        seq_score = SequenceMatcher(None, norm_raw, normalize_input(item_name)).ratio()
        # Composite: prioritize overlap, then seq_score as tiebreaker
        score = (overlap, seq_score)
        if overlap > 0 or seq_score > fuzzy_cutoff:
            scored.append((score, item))
    # Sort by overlap, then sequence match
    scored.sort(key=lambda t: t[0], reverse=True)
    matches = [item for (_, item) in scored[:max_suggestions]]
    if matches:
        return matches, None

    return None, None

def _num_in(text: str) -> int | None:
    m = re.search(r"\b(\d+)\b", normalize_input(text))
    return int(m.group()) if m else None

def detect_deposit_intent(text: str):
    amt = _num_in(text)
    return (
        PlayerIntent.DEPOSIT_BALANCE if amt is not None else PlayerIntent.DEPOSIT_NEEDS_AMOUNT,
        amt,
    )

def detect_withdraw_intent(text: str):
    amt = _num_in(text)
    return (
        PlayerIntent.WITHDRAW_BALANCE if amt is not None else PlayerIntent.WITHDRAW_NEEDS_AMOUNT,
        amt,
    )


# ─── Confirmation‑state overrides ───────────────────────────────────────

def _confirmation_overrides(player_input: str, lowered: str, convo: Conversation | None):
    if not (convo and convo.state == ConversationState.AWAITING_CONFIRMATION):
        return None
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.DEPOSIT_BALANCE]):
        intent, amt = detect_deposit_intent(player_input)
        return {"intent": intent, "metadata": {"amount": amt}}
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.WITHDRAW_BALANCE]):
        intent, amt = detect_withdraw_intent(player_input)
        return {"intent": intent, "metadata": {"amount": amt}}
    if re.search(r"\b\d+\b", lowered):
        return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": {}}
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.INSPECT_ITEM]):
        return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": {}}
    return None

# ─── Interpreter entry point (unchanged except for normalization flow) ─

def interpret_input(player_input, convo=None):
    # --- State-aware handling for special input modes ---
    if convo is not None:
        # Deposit amount input
        if convo.state == ConversationState.AWAITING_DEPOSIT_AMOUNT:
            intent, amt = detect_deposit_intent(player_input)
            return {"intent": intent, "metadata": {"amount": amt}}
        # Withdraw amount input
        if convo.state == ConversationState.AWAITING_WITHDRAW_AMOUNT:
            intent, amt = detect_withdraw_intent(player_input)
            return {"intent": intent, "metadata": {"amount": amt}}
        # Stash add selection
        if convo.state == ConversationState.AWAITING_STASH_ITEM_SELECTION:
            items, _ = find_item_in_input(player_input, convo)
            if items:
                return {"intent": PlayerIntent.STASH_ADD, "metadata": {"item": items}}
            return {"intent": PlayerIntent.STASH_ADD, "metadata": {}}
        # Stash remove selection
        if convo.state == ConversationState.AWAITING_UNSTASH_ITEM_SELECTION:
            items, _ = find_item_in_input(player_input, convo)
            if items:
                return {"intent": PlayerIntent.STASH_REMOVE, "metadata": {"item": items}}
            return {"intent": PlayerIntent.STASH_REMOVE, "metadata": {}}
        # If in AWAITING_ITEM_SELECTION but not stash, fall through to buy/sell/inspect logic

    # --- Standard intent detection below (unchanged) ---
    lowered = normalize_input(player_input)
    early = _confirmation_overrides(player_input, lowered, convo)
    if early:
        return early
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.DEPOSIT_BALANCE]):
        intent, amt = detect_deposit_intent(player_input)
        return {"intent": intent, "metadata": {"amount": amt}}
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.WITHDRAW_BALANCE]):
        intent, amt = detect_withdraw_intent(player_input)
        return {"intent": intent, "metadata": {"amount": amt}}

    # ...rest of your normal logic (category browsing, fallback, etc) ...





    # --- VIEW_STASH direct keyword detection (must come before fuzzy!) ---
    view_stash_keywords = INTENT_KEYWORDS[PlayerIntent.VIEW_STASH]
    if any(normalize_input(player_input) == normalize_input(kw) for kw in view_stash_keywords):
        return {"intent": PlayerIntent.VIEW_STASH, "metadata": {}}

    # --- Category detection ---
    # ... (rest unchanged)

    # --- Category detection ---
    CATEGORY_INTENTS = [
        PlayerIntent.VIEW_TOOL_CATEGORY,
        PlayerIntent.VIEW_GEAR_CATEGORY,
        PlayerIntent.VIEW_WEAPON_CATEGORY,
        PlayerIntent.VIEW_ARMOUR_CATEGORY,
        PlayerIntent.VIEW_TREASURE_CATEGORY,
        PlayerIntent.VIEW_EQUIPMENT_CATEGORY,
    ]
    SUBCATEGORY_INTENTS = [
        PlayerIntent.VIEW_TOOL_SUBCATEGORY,
        PlayerIntent.VIEW_GEAR_SUBCATEGORY,
        PlayerIntent.VIEW_WEAPON_SUBCATEGORY,
        PlayerIntent.VIEW_ARMOUR_SUBCATEGORY,
        PlayerIntent.VIEW_TREASURE_SUBCATEGORY,
    ]
    for intent in CATEGORY_INTENTS:
        if lowered in NORMALIZED_INTENT_KEYWORDS[intent]:
            return {"intent": intent, "metadata": {}}
    for intent in SUBCATEGORY_INTENTS:
        if lowered in NORMALIZED_INTENT_KEYWORDS[intent]:
            meta_key = None
            if intent == PlayerIntent.VIEW_TOOL_SUBCATEGORY:
                meta_key = "tool_category"
            elif intent == PlayerIntent.VIEW_GEAR_SUBCATEGORY:
                meta_key = "gear_category"
            elif intent == PlayerIntent.VIEW_WEAPON_SUBCATEGORY:
                meta_key = "weapon_category"
            elif intent == PlayerIntent.VIEW_ARMOUR_SUBCATEGORY:
                meta_key = "armour_category"
            elif intent == PlayerIntent.VIEW_TREASURE_SUBCATEGORY:
                meta_key = "treasure_category"
            if meta_key:
                return {"intent": intent, "metadata": {meta_key: lowered}}

    # --- HAGGLE and other special keyword-based intents ---
    for special_intent in [
        PlayerIntent.HAGGLE,
        PlayerIntent.SHOW_GRATITUDE,
        PlayerIntent.GREETING,
        PlayerIntent.NEXT,
        PlayerIntent.PREVIOUS,
        PlayerIntent.UNDO,
    ]:
        if any(kw in lowered for kw in NORMALIZED_INTENT_KEYWORDS[special_intent]):
            return {"intent": special_intent, "metadata": {}}
    # --- End special intents ---

    # Fuzzy item search as fallback
    items, _ = find_item_in_input(player_input, convo)  # cutoff 0.75
    if items:
        if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.INSPECT_ITEM]):
            return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": {"item": items}}
        if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.SELL_ITEM]):
            return {"intent": PlayerIntent.SELL_ITEM, "metadata": {"item": items}}
        if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.STASH_REMOVE]):
            return {"intent": PlayerIntent.STASH_REMOVE, "metadata": {"item": items}}
        if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.STASH_ADD]):
            return {"intent": PlayerIntent.STASH_ADD, "metadata": {"item": items}}
        return {"intent": PlayerIntent.BUY_ITEM, "metadata": {"item": items}}

    # (rest unchanged...)
    intent_r, conf = rank_intent_kw(player_input, convo)
    if (conf >= INTENT_CONF_THRESHOLD and
            intent_r not in (PlayerIntent.DEPOSIT_BALANCE, PlayerIntent.WITHDRAW_BALANCE)):
        return {"intent": intent_r, "metadata": {}}
    words = lowered.split()
    if any(w in words for w in GRATITUDE_KEYWORDS):
        return {"intent": PlayerIntent.SHOW_GRATITUDE, "metadata": {}}
    if any(w in words for w in GOODBYE_KEYWORDS):
        return {"intent": PlayerIntent.GOODBYE, "metadata": {}}
    loose_items, _ = find_item_in_input(player_input, convo, fuzzy_cutoff=0.55)
    if loose_items:
        return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": {"item": loose_items}}
    return {"intent": PlayerIntent.UNKNOWN, "metadata": {}}


# ─── GPT confirm fallback (unchanged) ───────────────────────────────────

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def check_confirmation_via_gpt(user_input: str):
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Classify CONFIRM/CANCEL/UNKNOWN. Return JSON."},
                {"role": "user", "content": f'"{user_input}"'},
            ],
            temperature=0,
            max_tokens=30,
        )
        j = json.loads(resp.choices[0].message.content)
        if j.get("intent") == "CONFIRM":
            return PlayerIntent.CONFIRM
        if j.get("intent") == "CANCEL":
            return PlayerIntent.CANCEL
    except Exception as e:
        logger.debug("[GPT CONFIRM] %s", e)
    return PlayerIntent.UNKNOWN

# ─── Compatibility helpers (legacy callers) -----------------------------

def get_equipment_category_from_input(text: str):
    return get_category_match(text)[1]

def get_weapon_category_from_input(text: str):
    return get_category_match(text)[1]

def get_gear_category_from_input(text: str):
    return get_category_match(text)[1]

def get_armour_category_from_input(text: str):
    return get_category_match(text)[1]

def get_tool_category_from_input(text: str):
    return get_category_match(text)[1]
