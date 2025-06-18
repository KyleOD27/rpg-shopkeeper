# app/interpreter.py – banking intent & confirmation fix
# -----------------------------------------------------------------------------
# Detects “deposit …” / “withdraw …” *even while a confirmation prompt is open*.
# We do that by handling banking keywords inside `_confirmation_overrides` *before*
# the numeric‑ID → INSPECT fallback. Everything else remains as in the previous
# version you reviewed.
# -----------------------------------------------------------------------------

from __future__ import annotations

import json
import logging
import os
import re
from difflib import get_close_matches
from typing import Any, Dict, Tuple

from dotenv import load_dotenv
from openai import OpenAI

from app.conversation import Conversation, ConversationState, PlayerIntent
from app.models.items import (
    get_all_equipment_categories,
    get_all_items,
    get_armour_categories,
    get_gear_categories,
    get_tool_categories,
    get_weapon_categories,
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

# ─── Normalisation helpers ──────────────────────────────────────────────

def normalize_input(text: str, convo: Conversation | None = None) -> str:
    norm = re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()
    norm = re.sub(r"\s+", " ", norm)
    if convo is not None:
        convo.normalized_input = norm
    return norm


def sanitize(text: str) -> str:
    txt = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    tokens = [t for t in txt.split() if t not in STOP_WORDS]
    return " ".join(tokens)


def preprocess(player_input: str) -> str:
    t = re.sub(r"\s+", " ", player_input.strip().lower())
    for p in sorted(INTENT_PREFIXES, key=len, reverse=True):
        if t.startswith(p + " "):
            t = t[len(p) + 1 :]
            break
    return sanitize(t)

# ─── Ranker helpers ─────────────────────────────────────────────────────

PREFERRED_ORDER: list[PlayerIntent] = [
    PlayerIntent.DEPOSIT_BALANCE,
    PlayerIntent.WITHDRAW_BALANCE,
    PlayerIntent.CHECK_BALANCE,
    PlayerIntent.VIEW_LEDGER,
    PlayerIntent.BUY_ITEM,
    PlayerIntent.SELL_ITEM,
    PlayerIntent.INSPECT_ITEM,
    PlayerIntent.VIEW_WEAPON_SUBCATEGORY,
    PlayerIntent.VIEW_ARMOUR_SUBCATEGORY,
    PlayerIntent.VIEW_GEAR_SUBCATEGORY,
    PlayerIntent.VIEW_TOOL_SUBCATEGORY,
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


def _pref_index(intent: PlayerIntent) -> int:
    try:
        return PREFERRED_ORDER.index(intent)
    except ValueError:
        return len(PREFERRED_ORDER)


def rank_intent_kw(user_input: str,
                   convo: Conversation | None = None   # ← new argument
                   ) -> tuple[PlayerIntent, float]:
    raw = normalize_input(user_input)
    scores = {
        intent: sum(1 for kw in kws if kw in raw)
        for intent, kws in INTENT_KEYWORDS.items()
    }
    best_intent = max(scores, key=lambda i: (scores[i], -_pref_index(i)))
    confidence  = scores[best_intent] / max(len(INTENT_KEYWORDS[best_intent]), 1)

    # Log to the CSV if a Conversation was supplied, else fall back to console.
    if convo is not None:
        convo.debug(f"[RANK] {best_intent.name} {confidence:.2f} {scores}")
    else:
        logger.debug(
            "[rank_intent_kw] %r → %s %.2f %s",
            user_input, best_intent.name, confidence, scores,
        )

    return best_intent, confidence

# ─── Category helpers (unchanged) ───────────────────────────────────────

def get_category_match(player_input: str):
    lowered = normalize_input(player_input)
    cats = {
        "equipment_category": get_all_equipment_categories(),
        "weapon_category": get_weapon_categories(),
        "gear_category": get_gear_categories(),
        "armour_category": get_armour_categories(),
        "tool_category": get_tool_categories(),
    }
    for field, names in cats.items():
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
    if lowered in norm_map:
        return norm_map[lowered]
    for norm in sorted(norm_map.keys(), key=len, reverse=True):
        if norm in lowered:
            return norm_map[norm]
    close = get_close_matches(lowered, norm_map.keys(), n=1, cutoff=0.7)
    return norm_map.get(close[0]) if close else None

# ─── Item matcher (trimmed) ─────────────────────────────────────────────

def find_item_in_input(
    player_input: str,
    convo=None,
    *,
    fuzzy_cutoff: float = 0.75,   # ← caller can loosen/tighten match here
    max_suggestions: int = 3      #   …and control list length if desired
):
    """
    Return ([matched_items], None) or (None, None).

    • Skips any token in EXCEPTION_WORDS so UI words ('next', 'back', …)
      can’t become false item hits.
    • `fuzzy_cutoff` lets callers decide how "loose" the fuzzy search is.
      – strict flows: 0.75-0.85
      – suggestion lists: 0.5-0.6
    """

    raw      = preprocess(player_input)
    norm_raw = normalize_input(raw)

    # ── quick exits ────────────────────────────────────────────────
    if (
        norm_raw in EXCEPTION_WORDS
        or norm_raw in SHOP_ACTION_WORDS
        or (len(norm_raw) < 4 and not norm_raw.isdigit())
    ):
        return None, None

    words  = raw.split()
    items  = [dict(json.loads(r) if isinstance(r, str) else r)
              for r in get_all_items()]

    # ── numeric ID match ───────────────────────────────────────────
    if digit := next((w for w in words if w.isdigit()), None):
        matches = [i for i in items if str(i.get("item_id")) == digit]
        if matches:
            return matches, None

    # ── exact / fuzzy name match ───────────────────────────────────
    name_map = {normalize_input(i["item_name"]): i for i in items}

    # exact substring first
    for norm, itm in name_map.items():
        if norm in norm_raw:
            return [itm], None

    # fuzzy – skip exception tokens
    matches: list[dict] = []
    for w in words:
        lw = w.lower()
        if lw in EXCEPTION_WORDS:
            continue
        for nm in get_close_matches(
            normalize_input(w),
            name_map.keys(),
            n=max_suggestions,
            cutoff=fuzzy_cutoff
        ):
            itm = name_map[nm]
            if itm not in matches:
                matches.append(itm)

    return (matches or None), None
# ─── Banking helpers ────────────────────────────────────────────────────

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
    """Special‑case parsing while waiting for yes/no."""
    if not (convo and convo.state == ConversationState.AWAITING_CONFIRMATION):
        return None

    # Banking keywords should *break us out* of confirmation mode ------------
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.DEPOSIT_BALANCE]):
        intent, amt = detect_deposit_intent(player_input)
        return {"intent": intent, "metadata": {"amount": amt}}
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.WITHDRAW_BALANCE]):
        intent, amt = detect_withdraw_intent(player_input)
        return {"intent": intent, "metadata": {"amount": amt}}

    # bare number → inspect that item ----------------------------------------
    if re.search(r"\b\d+\b", lowered):
        return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": {}}

    # explicit "inspect …"
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.INSPECT_ITEM]):
        return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": {}}

    return None

# ─── Interpreter entry point ────────────────────────────────────────────

# ─── Interpreter entry point ────────────────────────────────────────────

def interpret_input(player_input, convo=None):
    lowered = normalize_input(player_input)

    # 0️⃣ confirmation overrides -----------------------------------------
    early = _confirmation_overrides(player_input, lowered, convo)
    if early:
        return early

    # 1️⃣ early banking detection ---------------------------------------
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.DEPOSIT_BALANCE]):
        intent, amt = detect_deposit_intent(player_input)
        return {"intent": intent, "metadata": {"amount": amt}}
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.WITHDRAW_BALANCE]):
        intent, amt = detect_withdraw_intent(player_input)
        return {"intent": intent, "metadata": {"amount": amt}}

    # 2️⃣ item-first (strict cutoff) ------------------------------------
    items, _ = find_item_in_input(player_input, convo)   # cutoff 0.75
    if items:
        if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.INSPECT_ITEM]):
            return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": {"item": items}}
        if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.SELL_ITEM]):
            return {"intent": PlayerIntent.SELL_ITEM, "metadata": {"item": items}}
        return {"intent": PlayerIntent.BUY_ITEM,  "metadata": {"item": items}}

    # 3️⃣ keyword ranker -------------------------------------------------
    intent_r, conf = rank_intent_kw(player_input, convo)
    if (conf >= INTENT_CONF_THRESHOLD and
            intent_r not in (PlayerIntent.DEPOSIT_BALANCE, PlayerIntent.WITHDRAW_BALANCE)):
        return {"intent": intent_r, "metadata": {}}

    # 4️⃣ polite words ---------------------------------------------------
    words = lowered.split()
    if any(w in words for w in GRATITUDE_KEYWORDS):
        return {"intent": PlayerIntent.SHOW_GRATITUDE, "metadata": {}}
    if any(w in words for w in GOODBYE_KEYWORDS):
        return {"intent": PlayerIntent.GOODBYE, "metadata": {}}

    # 5️⃣ last-chance: maybe it's an item name (loose cutoff) ------------
    loose_items, _ = find_item_in_input(player_input, convo,
                                        fuzzy_cutoff=0.55)   # looser
    if loose_items:
        return {"intent": PlayerIntent.INSPECT_ITEM,
                "metadata": {"item": loose_items}}

    # fallback -----------------------------------------------------------
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
