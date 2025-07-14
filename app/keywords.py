"""
Keyword & constant tables used by the interpreter layer.

Keeping them here means:
  • the interpreter stays readable;
  • other code (tests, future handlers, etc.) can import them too;
  • you only edit in one place when wording changes.
"""

from __future__ import annotations

from enum import auto

from app.conversation import PlayerIntent

# ──────────────────────────────────────────────
# Core look‑up tables
# ──────────────────────────────────────────────

INTENT_KEYWORDS: dict[PlayerIntent, list[str]] = {
    # ▸ General browsing
    PlayerIntent.VIEW_ITEMS: ["items", "inventory", "stock", "what do you have", "show me",  "what do you sell", "what do you buy", "browse", "see"],

    # ▸ Top‑level equipment categories
    PlayerIntent.VIEW_EQUIPMENT_CATEGORY: ["items", "inventory", "item", "shop"],
    PlayerIntent.VIEW_ARMOUR_CATEGORY:    ["armor", "armour"],
    PlayerIntent.VIEW_WEAPON_CATEGORY:    ["weapon", "weapons"],
    PlayerIntent.VIEW_GEAR_CATEGORY:      ["gear", "adventuring gear", "supplies", "packs"],
    PlayerIntent.VIEW_TOOL_CATEGORY:      ["tool", "tools"],
    PlayerIntent.VIEW_MOUNT_CATEGORY:     ["mounts and vehicles", "mounts", "mount", "vehicle", "vehicles"],
    PlayerIntent.VIEW_TREASURE_CATEGORY:  ["treasure"],

    # ▸ Sub‑categories
    PlayerIntent.VIEW_ARMOUR_SUBCATEGORY: ["light", "medium", "heavy"],
    PlayerIntent.VIEW_WEAPON_SUBCATEGORY: ["martial melee", "martial ranged", "simple melee", "simple ranged"],
    PlayerIntent.VIEW_GEAR_SUBCATEGORY: [ "ammunition", "arcane foci", "druidic foci",  "equipment packs", "holy symbols", "kits", "standard gear", "standard", "potion", "scroll",],
    PlayerIntent.VIEW_TOOL_SUBCATEGORY: ["artisan's tools", "artisans tools", "gaming sets", "musical instrument", "other tools"],
    PlayerIntent.VIEW_TREASURE_SUBCATEGORY: ["wand", "gemstones", "trade bars", "trade goods", "art objects", "ring", "rod", "staff"],

    # ▸ Transactions
    PlayerIntent.BUY_ITEM:  ["buy", "purchase", "get", "acquire", "grab", "want"],
    PlayerIntent.SELL_ITEM: ["sell", "offload"],

    # ▸ Bank actions
    PlayerIntent.DEPOSIT_BALANCE:  ["deposit", "add gold"],
    PlayerIntent.WITHDRAW_BALANCE: ["withdraw", "collect", "take gold", "take copper", "take money", "take platinum", "take electrum" ],
    PlayerIntent.CHECK_BALANCE: ["balance", "amount", "funds"],

    # Stash actions
    PlayerIntent.STASH_ADD: ["stash", "store", "add"],
    PlayerIntent.STASH_REMOVE: ["unstash", "remove", "take", "retrieve"],
    PlayerIntent.VIEW_STASH: ["view", "see stash", "view stash", "party stash"],

    # ▸ Miscellaneous
    PlayerIntent.VIEW_LEDGER:    ["ledger", "transactions", "history"],
    PlayerIntent.HAGGLE:         ["haggle", "negotiate", "bargain", "deal", "cheaper", "discount"],
    PlayerIntent.SHOW_GRATITUDE: ["thanks", "thankyou", "grateful", "ty", "gracias", "merci", "danke"],
    PlayerIntent.GREETING:       ["hello", "greetings", "hallo", "hey", "ey", "hi", "whaddup", "wassup"],
    PlayerIntent.NEXT:           ["next", "more", "show more", "continue", "another"],
    PlayerIntent.PREVIOUS:       ["previous", "back",  "last", "prev", "last"],
    PlayerIntent.UNDO:           ["undo"],
    PlayerIntent.INSPECT_ITEM: ["inspect", "details", "tell", "info", "explain", "describe",],
    PlayerIntent.VIEW_PROFILE: ["profile", "my profile", "see me", "player", "user" ],
    PlayerIntent.VIEW_PARTY_PROFILE: ["party", "party profile", "see party", "party", "group"],
}

# ──────────────────────────────────────────────
# Helper word‑lists
# ──────────────────────────────────────────────

STOP_WORDS: set[str] = {
    "a", "an", "the", "and", "or", "but",
    "of", "for", "to", "in", "on", "at",
}

SHOP_ACTION_WORDS: set[str] = {
    "buy", "sell", "browse", "list", "view",
    "show", "inspect", "deposit", "withdraw", "balance",
}

INTENT_PREFIXES: list[str] = [
    "want to buy", "want to purchase", "can i buy",
    "how much is", "how much would",
    "tell me about", "what does", "what is", "show me", "see"
]

CONFIRMATION_WORDS: list[str] = ["yes", "yeah", "yep", "sure", "ok", "okay", "aye"]
CANCELLATION_WORDS: list[str] = ["no", "nah", "cancel", "stop", "never", "forget", "exit"]
GRATITUDE_KEYWORDS: list[str] = INTENT_KEYWORDS[PlayerIntent.SHOW_GRATITUDE]
GOODBYE_KEYWORDS: list[str]   = ["bye", "farewell", "later", "see you" "goodbye"]

# ──────────────────────────────────────────────
# Exception words
# ──────────────────────────────────────────────
# Words or phrases that must never be considered item names by the fuzzy matcher.
# We collect every helper word **and** every keyword phrase, then expand them into
# lowercase atomic tokens so that both "next" and "what" are excluded.

# 1) Raw phrase collection
_EXCEPTION_PHRASES: set[str] = (
    STOP_WORDS
    | SHOP_ACTION_WORDS
    | {phrase for phrases in INTENT_KEYWORDS.values() for phrase in phrases}
)

# 2) Token‑level, lowercase expansion
EXCEPTION_WORDS: set[str] = {
    token.lower()
    for phrase in _EXCEPTION_PHRASES
    for token in phrase.split()
}

# ──────────────────────────────────────────────
# Misc settings
# ──────────────────────────────────────────────

# Minimum confidence required for the interpreter to accept a fuzzy match
INTENT_CONF_THRESHOLD: float = 0.10

__all__ = [
    "INTENT_KEYWORDS", "STOP_WORDS", "SHOP_ACTION_WORDS", "INTENT_PREFIXES",
    "CONFIRMATION_WORDS", "CANCELLATION_WORDS", "GRATITUDE_KEYWORDS",
    "GOODBYE_KEYWORDS", "INTENT_CONF_THRESHOLD", "EXCEPTION_WORDS",
]
