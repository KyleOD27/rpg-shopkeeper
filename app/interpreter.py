import re
import os
import json
import logging
from difflib import get_close_matches
from typing import Optional, Dict, Tuple, Any
from dotenv import load_dotenv
from openai import OpenAI
from app.conversation import PlayerIntent, Conversation, ConversationState

from app.models.items import (
    get_all_items,
    get_all_equipment_categories,
    get_weapon_categories,
    get_gear_categories,
    get_armour_categories,
    get_tool_categories)

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
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def normalize_input(text: str, convo=None) ->str:
    """Lowercase, remove punctuation, collapse spaces."""
    norm = re.sub('[^a-z0-9\\s]', '', text.lower()).strip()
    norm = re.sub('\\s+', ' ', norm)
    if convo is not None:
        convo.normalized_input = norm
    return norm


def sanitize(text: str) ->str:
    """Lowercase, remove punctuation, drop STOP_WORDS."""
    txt = re.sub('[^a-z0-9\\s]', ' ', text.lower())
    tokens = [t for t in txt.split() if t not in STOP_WORDS]
    return ' '.join(tokens)


def preprocess(player_input: str) ->str:
    """Collapse spaces, strip INTENT_PREFIXES, then sanitize."""
    t = re.sub('\\s+', ' ', player_input.strip().lower())
    for p in sorted(INTENT_PREFIXES, key=len, reverse=True):
        if t.startswith(p + ' '):
            t = t[len(p) + 1:]
            break
    return sanitize(t)


PREFERRED_ORDER: list[PlayerIntent] = [PlayerIntent.DEPOSIT_GOLD,
    PlayerIntent.WITHDRAW_GOLD, PlayerIntent.CHECK_BALANCE, PlayerIntent.
    VIEW_ACCOUNT, PlayerIntent.VIEW_PROFILE, PlayerIntent.VIEW_LEDGER,
    PlayerIntent.INSPECT_ITEM, PlayerIntent.VIEW_ITEMS,
    PlayerIntent.VIEW_WEAPON_SUBCATEGORY, PlayerIntent.VIEW_ARMOUR_SUBCATEGORY,
    PlayerIntent.VIEW_GEAR_SUBCATEGORY,  PlayerIntent.VIEW_TOOL_SUBCATEGORY,
    PlayerIntent.VIEW_EQUIPMENT_CATEGORY, PlayerIntent.VIEW_WEAPON_CATEGORY,
    PlayerIntent.VIEW_ARMOUR_CATEGORY, PlayerIntent.VIEW_GEAR_CATEGORY,
    PlayerIntent.VIEW_TOOL_CATEGORY, PlayerIntent.SHOW_GRATITUDE,
    PlayerIntent.GREETING, PlayerIntent.NEXT, PlayerIntent.PREVIOUS,
    PlayerIntent.BUY_ITEM, PlayerIntent.SELL_ITEM]


def _pref_index(intent: PlayerIntent) ->int:
    """Return the intent’s position in the preference list (lower = better)."""
    try:
        return PREFERRED_ORDER.index(intent)
    except ValueError:
        return len(PREFERRED_ORDER)


def rank_intent_kw(user_input: str) ->tuple[PlayerIntent, float]:
    """
    Score each intent by counting how many of its keywords appear in the
    normalized input.  If two intents get the same score, break the tie with
    `PREFERRED_ORDER` so we always pick the most specific / important intent
    deterministically.
    """
    raw = normalize_input(user_input)
    logger.debug(f'[RANKER] raw normalized: {raw!r}')
    scores: dict[PlayerIntent, int] = {intent: sum(1 for kw in kws if kw in
        raw) for intent, kws in INTENT_KEYWORDS.items()}
    best_intent: PlayerIntent = max(scores, key=lambda i: (scores[i], -
        _pref_index(i)))
    total_keywords = max(len(INTENT_KEYWORDS.get(best_intent, ())), 1)
    confidence = scores[best_intent] / total_keywords
    logger.debug(
        f'[RANKER] scores={scores}, best={best_intent}, conf={confidence:.2f}')
    return best_intent, confidence


def get_category_match(player_input: str):
    lowered = normalize_input(player_input)
    categories = {'equipment_category': get_all_equipment_categories(),
        'weapon_category': get_weapon_categories(), 'gear_category':
        get_gear_categories(), 'armour_category': get_armour_categories(),
        'tool_category': get_tool_categories()}
    for field, names in categories.items():
        normed = [normalize_input(n) for n in names]
        if lowered in normed:
            return field, names[normed.index(lowered)]
        close = get_close_matches(lowered, normed, n=1, cutoff=0.8)
        if close:
            return field, names[normed.index(close[0])]
    return None, None


def get_subcategory_match(section: str, player_input: str):
    """
    Return the *exact DB spelling* of a sub-category that best matches the
    player’s phrase, giving priority to more specific names.

    Match order:
      1. exact equality after normalisation
      2. containment, longest names first  (so "artisans tools" wins over "tools")
      3. fuzzy nearest-neighbour fallback
    """
    lowered = normalize_input(player_input)
    if section == 'armor':
        cats = get_armour_categories()
    elif section == 'weapon':
        cats = get_weapon_categories()
    elif section == 'gear':
        cats = get_gear_categories()
    elif section == 'tool':
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


# top of item_match.py  (or a nearby utils module)
INTENT_LEADERS = {
    *INTENT_KEYWORDS[PlayerIntent.BUY_ITEM],
    *INTENT_KEYWORDS[PlayerIntent.SELL_ITEM],
    *INTENT_KEYWORDS[PlayerIntent.INSPECT_ITEM],
}

def strip_leading_intent(text: str) -> str:
    """
    Remove ONE leading intent keyword + punctuation/spaces.
    'buy crossbow, light' -> 'crossbow, light'
    'inspect  wand'       -> 'wand'
    """
    t = text.lstrip()
    for kw in INTENT_LEADERS:
        if t.lower().startswith(kw):
            return t[len(kw):].lstrip(" ,;:")
    return text

def find_item_in_input(player_input: str, convo=None):
    """
    Return (matches, detected_category)

    Match order
    ───────────
      1. Numeric ID
      2. Category name
      3. Exact full-name substring        (unchanged, but direction flipped)
      4. Token-subset relaxed match       (NEW: handles plurals & punctuation)
      5. Fuzzy by token                   (unchanged)
      6. Fallback to convo.pending_item
    """
    # ── 0. Pre-clean ──────────────────────────────────────────────────────
    raw = preprocess(player_input)
    for p in (
        'could you', 'would you', 'can you', 'i want to', "i'd like to",
        'please', 'good sir', 'thank you', 'thanks', 'would it cost',
        'what does it do', "i'm looking to"
    ):
        raw = raw.replace(p, '')
    raw = raw.strip()

    # --- NEW: pre-cleaned variant with intent verb removed -------------
    search_raw = strip_leading_intent(raw)
    norm_raw = normalize_input(raw).replace(',', '')  # original
    norm_search = normalize_input(search_raw).replace(',', '')  # NEW
    # -------------------------------------------------------------------

    if norm_raw in SHOP_ACTION_WORDS or (
            len(norm_raw) < 4 and not norm_raw.isdigit()
    ):
        logger.debug('[ITEM MATCH] skipped: stop-word or too short')
        return None, None

    words = raw.split()
    words_search = search_raw.split()  # NEW
    items = [dict(json.loads(r) if isinstance(r, str) else r)
             for r in get_all_items()]

    # ── 1. Numeric ID ────────────────────────────────────────────────────
    digit = next((w for w in words if w.isdigit()), None)
    if digit:
        matches = [i for i in items if str(i.get('item_id')) == digit]
        if matches:
            logger.debug(f'[ITEM MATCH] by ID {digit}: {matches}')
            return matches, None

    # ── 2. Exact substring but user ⊂ item  (direction flipped) ──────────
    name_map = {normalize_input(i['normalised_item_name']).replace(',', ''): i for i in items}
    for norm, itm in name_map.items():
        if norm_raw in norm:
            logger.debug(f"[ITEM MATCH] exact-substring: {itm['normalised_item_name']}")
            return [itm], None

    # 3. TOKEN-SUBSET (use search tokens)
    search_tokens = {w.rstrip('s') for w in norm_search.split()}
    for norm, itm in name_map.items():
        item_tokens = {w.rstrip('s') for w in norm.split()}
        if search_tokens and search_tokens.issubset(item_tokens):
            logger.debug(f"[ITEM MATCH] token-subset: {itm['item_name']}")
            return [itm], None

    # ── 4. Category match (unchanged) ────────────────────────────────────
    all_cats = (
        get_all_equipment_categories()
        + get_weapon_categories()
        + get_gear_categories()
        + get_armour_categories()
        + get_tool_categories()
    )
    cat_map = {normalize_input(c): c for c in all_cats}
    for norm, orig in cat_map.items():
        if norm in norm_raw:
            logger.debug(f'[ITEM MATCH] category full: {orig}')
            return None, orig



    # 5. FUZZY by token (use words_search)
    matches = []
    for w in words_search:
        close = get_close_matches(normalize_input(w), name_map.keys(), n=3, cutoff=0.55)
        for nm in close:
            itm = name_map[nm]
            if itm not in matches:
                matches.append(itm)
                logger.debug(f"[ITEM MATCH] fuzzy: {itm['item_name']}")
    if matches:
        return matches, None

    if matches:
        return matches, None

    # ── 6. Fallback to convo.pending_item ────────────────────────────────
    if convo and convo.get_pending_item():
        pend = convo.get_pending_item()
        if isinstance(pend, dict):
            return [pend], None
        if isinstance(pend, list):
            return pend, None
        if isinstance(pend, str):
            return [{'item_name': pend}], None

    logger.debug('[ITEM MATCH] no matches')
    return None, None


def detect_buy_intent(player_input: str, convo=None):
    items, _ = find_item_in_input(player_input, convo)
    return (PlayerIntent.BUY_ITEM, items) if items else (PlayerIntent.
        BUY_NEEDS_ITEM, None)



def detect_sell_intent(player_input: str, convo=None):
    items, _ = find_item_in_input(player_input, convo)
    return (PlayerIntent.SELL_ITEM, items) if items else (PlayerIntent.
        SELL_NEEDS_ITEM, None)


def detect_deposit_intent(player_input: str, convo=None):
    m = re.search('\\b\\d+\\b', normalize_input(player_input))
    return (PlayerIntent.DEPOSIT_GOLD, int(m.group())) if m else (PlayerIntent
        .DEPOSIT_NEEDS_AMOUNT, None)


def detect_withdraw_intent(player_input: str, convo=None):
    m = re.search('\\b\\d+\\b', normalize_input(player_input))
    return (PlayerIntent.WITHDRAW_GOLD, int(m.group())) if m else (PlayerIntent
        .WITHDRAW_NEEDS_AMOUNT, None)


# ────────────────────────────────────────────────────────────────────────────
#  Tables for intent → (metadata-field, helper-args)
# ────────────────────────────────────────────────────────────────────────────
CATEGORY_INTENTS: Dict[PlayerIntent, str] = {
    PlayerIntent.VIEW_ARMOUR_CATEGORY:   "equipment_category",
    PlayerIntent.VIEW_WEAPON_CATEGORY:   "equipment_category",
    PlayerIntent.VIEW_GEAR_CATEGORY:     "equipment_category",
    PlayerIntent.VIEW_TOOL_CATEGORY:     "equipment_category",
    PlayerIntent.VIEW_EQUIPMENT_CATEGORY:"equipment_category",
}

SUBCATEGORY_INTENTS: Dict[PlayerIntent, Tuple[str, str]] = {
    PlayerIntent.VIEW_WEAPON_SUBCATEGORY: ("category_range",  "weapon"),
    PlayerIntent.VIEW_GEAR_SUBCATEGORY:   ("gear_category",   "gear"),
    PlayerIntent.VIEW_ARMOUR_SUBCATEGORY: ("armour_category", "armor"),
    PlayerIntent.VIEW_TOOL_SUBCATEGORY:   ("tool_category",   "tool"),
}

# ────────────────────────────────────────────────────────────────────────────
def interpret_input(player_input: str, convo: Conversation | None = None) -> Dict[str, Any]:
    """
    Returns {"intent": PlayerIntent, "metadata": dict}
    """
    lowered = normalize_input(player_input)
    logger.debug("[INTERPRETER] raw=%r  lowered=%r", player_input, lowered)

    # 0️⃣ STATE-BASED OVERRIDES ────────────────────────────────────────────
    early = _confirmation_overrides(player_input, lowered, convo)
    if early:
        return early

    # 1️⃣ >>> UNIVERSAL  item-first short-circuit  <<< ----------------------------
    items, _ = find_item_in_input(player_input, convo)
    if items:                                          # we found at least one item
        # decide which intent matches the user’s verb
        if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.INSPECT_ITEM]):
            intent = PlayerIntent.INSPECT_ITEM
        elif any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.SELL_ITEM]):
            intent = PlayerIntent.SELL_ITEM
        elif any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.BUY_ITEM]):
            intent = PlayerIntent.BUY_ITEM
        else:
            # no explicit verb – default to BUY_ITEM (or pick another default)
            intent = PlayerIntent.BUY_ITEM

        logger.debug("[INTERPRETER] concrete item wins → %s", intent)
        return {"intent": intent, "metadata": {"item": items}}
    # 1️⃣ <<< end item-first block <<< --------------------------------------------

    # 2️⃣ KEYWORD RANKER ───────────────────────────────────────────────────
    intent_r, conf = rank_intent_kw(player_input)
    logger.debug("[INTERPRETER] ranker → %s (conf=%.2f)", intent_r, conf)

    if conf >= INTENT_CONF_THRESHOLD:
        result = _handle_ranked_intent(intent_r, player_input, lowered, convo)
        if result:
            return result

    # 2️⃣ LONG-TAIL FALLBACK PARSER ────────────────────────────────────────
    return _fallback_parse(player_input, lowered, convo)


# ────────────────────────────────────────────────────────────────────────────
#                                HELPERS
# ────────────────────────────────────────────────────────────────────────────
def _confirmation_overrides(player_input: str, lowered: str, convo: Conversation | None):
    """Special cases while the convo waits for a yes/no but the user types something else."""
    if not (convo and convo.state == ConversationState.AWAITING_CONFIRMATION):
        return None

    # number → inspect N
    if m := re.search(r"\b(\d+)\b", lowered):
        items, _ = find_item_in_input(player_input, convo)
        if items:
            meta = {"item": items if len(items) > 1 else items[0]["item_name"]}
            logger.debug("[INTERPRETER] confirm numeric → INSPECT_ITEM")
            return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": meta}

    # explicit "inspect"
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.INSPECT_ITEM]):
        items, _ = find_item_in_input(player_input, convo)
        if items:
            meta = {"item": items if len(items) > 1 else items[0]["item_name"]}
            logger.debug("[INTERPRETER] confirm keyword → INSPECT_ITEM")
            return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": meta}

    return None


def _handle_ranked_intent(
    intent_r: PlayerIntent,
    raw: str,
    lowered: str,
    convo: Conversation | None,
):
    """Fast-path for high-confidence matches from ranker."""
    meta: Dict[str, Any] = {}

    # BUY / SELL ───────────────────────────────────────────────────────────
    if intent_r is PlayerIntent.BUY_ITEM:
        # ① FIRST: try to identify a concrete item name
        intent, items = detect_buy_intent(raw, convo)
        meta["item"] = items

        # ② If no item matched, fall back to category / sub-category parsing
        if not items:
            field, val = get_category_match(raw)
            if field:
                meta[field] = val
                meta["current_section"] = val.lower()

        return {"intent": intent, "metadata": meta}

    if intent_r is PlayerIntent.SELL_ITEM:
        intent, items = detect_sell_intent(raw, convo)
        meta["item"] = items
        return {"intent": intent, "metadata": meta}

        # INSPECT ──────────────────────────────────────────────────────────────
    if intent_r is PlayerIntent.INSPECT_ITEM:
        items, _ = find_item_in_input(raw, convo)
        if items:
            meta["item"] = items if len(items) > 1 else items[0]
        return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": meta}

    # CATEGORY VIEW ────────────────────────────────────────────────────────
    if intent_r in CATEGORY_INTENTS:
        field = CATEGORY_INTENTS[intent_r]
        meta[field] = get_category_match(raw)[1]
        return {"intent": intent_r, "metadata": meta}

    # SUB-CATEGORY VIEW ────────────────────────────────────────────────────
    if intent_r in SUBCATEGORY_INTENTS:
        field, group = SUBCATEGORY_INTENTS[intent_r]
        sub = get_subcategory_match(group, raw)
        if sub:
            meta[field] = sub.lower()
        return {"intent": intent_r, "metadata": meta}



    # SIMPLE INTENTS WITH NO EXTRA DATA ────────────────────────────────────
    if intent_r in {PlayerIntent.VIEW_PROFILE, PlayerIntent.VIEW_ACCOUNT}:
        return {"intent": intent_r, "metadata": {}}

    # Default: let fallback handle it (may still match CONFIRM/GREET etc.)
    return None


def _fallback_parse(player_input: str, lowered: str, convo: Conversation | None):
    """Slower keyword checks for low-confidence inputs."""
    words = lowered.split()

    # BUY intent by verb only
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.BUY_ITEM]):
        intent, items = detect_buy_intent(player_input, convo)
        meta = {"item": items} if items else {}
        return {"intent": intent, "metadata": meta}

    # category (plain "weapon", "armor", …)
    field, val = get_category_match(player_input)
    if field:
        view_intent = getattr(PlayerIntent, f"VIEW_{field.upper()}", PlayerIntent.VIEW_ITEMS)
        return {"intent": view_intent, "metadata": {field: val}}

    # generic keywords
    if any(w in words for w in CONFIRMATION_WORDS):
        return {"intent": PlayerIntent.CONFIRM, "metadata": {}}
    if any(w in words for w in CANCELLATION_WORDS):
        return {"intent": PlayerIntent.CANCEL, "metadata": {}}
    if any(w in words for w in GRATITUDE_KEYWORDS):
        return {"intent": PlayerIntent.SHOW_GRATITUDE, "metadata": {}}
    if any(w in words for w in GOODBYE_KEYWORDS):
        return {"intent": PlayerIntent.GOODBYE, "metadata": {}}

    # inspect keyword
    if any(kw in lowered for kw in INTENT_KEYWORDS[PlayerIntent.INSPECT_ITEM]):
        items, _ = find_item_in_input(player_input, convo)
        if items:
            meta = {"item": items if len(items) > 1 else items[0]["item_name"]}
            return {"intent": PlayerIntent.INSPECT_ITEM, "metadata": meta}

    # raw item mention → implicit buy
    items, _ = find_item_in_input(player_input, convo)
    if items:
        return {"intent": PlayerIntent.BUY_ITEM, "metadata": {"item": items}}

    # nothing matched
    logger.debug("[INTERPRETER] → UNKNOWN")
    return {"intent": PlayerIntent.UNKNOWN, "metadata": {}}



load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def check_confirmation_via_gpt(user_input: str, convo=None):
    try:
        resp = client.chat.completions.create(model='gpt-3.5-turbo',
            messages=[{'role': 'system', 'content':
            'Classify CONFIRM/CANCEL/UNKNOWN. Return JSON.'}, {'role':
            'user', 'content': f'"{user_input}"'}], temperature=0,
            max_tokens=30)
        j = json.loads(resp.choices[0].message.content)
        if j.get('intent') == 'CONFIRM':
            return PlayerIntent.CONFIRM
        if j.get('intent') == 'CANCEL':
            return PlayerIntent.CANCEL
    except Exception as e:
        logger.debug(f'[GPT CONFIRM] error {e}')
    return PlayerIntent.UNKNOWN


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
