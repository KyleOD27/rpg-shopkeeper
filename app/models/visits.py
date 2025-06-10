from datetime import datetime, timedelta, timezone
import os
from app.db import query_db, execute_db

# ────────────────────────────────────────────────────────────────────────────────
#  Rolling‑window definition of a “visit”
#     • Same party + same shop
#     • A new visit starts only when the player has been silent for ≥ timeout
# ────────────────────────────────────────────────────────────────────────────────

VISIT_TIMEOUT_MINUTES = int(os.environ.get("VISIT_TIMEOUT_MINUTES", 60))
_VISIT_TIMEOUT = timedelta(minutes=VISIT_TIMEOUT_MINUTES)

__all__ = [
    "touch_visit",
    "get_visit_count",
]

# ----------------------------------------------------------------------------
#  Helpers for row‑style agnosticism
# ----------------------------------------------------------------------------

def _val(row, key, pos, default=None):
    """Return a column from *row* regardless of whether `query_db` returned a mapping
    (sqlite3.Row / dict) or a tuple/list. If neither access path works, return
    *default*."""
    # Mapping‑style (sqlite3.Row, dict, etc.)
    try:
        return row[key]
    except Exception:
        pass

    # Tuple/list style
    if isinstance(row, (list, tuple)) and pos < len(row):
        return row[pos]

    return default


# ----------------------------------------------------------------------------
#  Public API
# ----------------------------------------------------------------------------

def get_visit_count(party_id: str, shop_id: int) -> int:
    """Return the cumulative *visit_count* for the party in this shop."""
    row = query_db(
        """
        SELECT visit_count
          FROM shop_visits
         WHERE party_id = ? AND shop_id = ?
        """,
        (party_id, shop_id),
        one=True,
    )
    return _val(row, "visit_count", 0, 0) if row else 0


def touch_visit(party_id: str, shop_id: int) -> int:
    """Ensure the correct visit row exists and refresh its *last_activity_utc*.

    • If there is **no** row yet → create one with ``visit_count = 1``.
    • If the most‑recent activity is **> timeout** ago → increment *visit_count*.
    • Otherwise → just update *last_activity_utc*.

    Returns the current *visit_count* (after any increment).
    """
    now = datetime.now(timezone.utc).replace(microsecond=0)

    row = query_db(
        """
        SELECT visit_count, last_activity_utc
          FROM shop_visits
         WHERE party_id = ? AND shop_id = ?
        """,
        (party_id, shop_id),
        one=True,
    )

    # ── First‑ever visit ───────────────────────────────────────────────────────
    if row is None:
        execute_db(
            """
            INSERT INTO shop_visits (party_id, shop_id, visit_count, last_activity_utc)
            VALUES (?, ?, 1, ?)
            """,
            (party_id, shop_id, now.isoformat(" ")),
        )
        return 1

    # ── Row exists – decide whether it’s a *new* visit ────────────────────────
    visit_count = _val(row, "visit_count", 0, 0)
    last_activity_str = _val(row, "last_activity_utc", 1, None)

    if last_activity_str:
        last_activity = datetime.fromisoformat(last_activity_str).astimezone(timezone.utc)
    else:
        # If the timestamp column was collapsed away, pretend it was ages ago so
        # we force a new visit and re‑populate the timestamp.
        last_activity = datetime.min.replace(tzinfo=timezone.utc)

    if now - last_activity > _VISIT_TIMEOUT:
        # Silent gap ≥ timeout ⇒ new visit
        visit_count += 1

    # Update timestamp (and counter if it increased)
    execute_db(
        """
        UPDATE shop_visits
           SET visit_count       = ?,
               last_activity_utc = ?
         WHERE party_id = ? AND shop_id = ?
        """,
        (visit_count, now.isoformat(" "), party_id, shop_id),
    )
    return visit_count
