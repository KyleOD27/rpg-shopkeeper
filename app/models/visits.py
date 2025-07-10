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

def get_visit_count(shop_id, party_id=None, user_id=None, character_id=None):
    row = query_db(
        """
        SELECT visit_count FROM shop_visits
        WHERE shop_id = ?
          AND (party_id IS ?)
          AND (user_id IS ?)
          AND (character_id IS ?)
        """,
        (shop_id, party_id, user_id, character_id),
        one=True,
    )
    return _val(row, "visit_count", 0, 0) if row else 0

def touch_visit(shop_id, character_id, user_id, party_id):
    now = datetime.now(timezone.utc).replace(microsecond=0)
    row = query_db(
        """
        SELECT visit_count, last_activity_utc FROM shop_visits
        WHERE shop_id = ? AND character_id = ?
        """,
        (shop_id, character_id),
        one=True,
    )

    if not row:
        execute_db(
            """
            INSERT INTO shop_visits
                (shop_id, character_id, user_id, party_id, visit_count, last_activity_utc)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (shop_id, character_id, user_id, party_id, now.isoformat(" ")),
        )
        return 1

    visit_count = _val(row, "visit_count", 0, 0)
    last_activity_str = _val(row, "last_activity_utc", 1, None)
    last_activity = datetime.fromisoformat(last_activity_str).astimezone(timezone.utc) if last_activity_str else datetime.min.replace(tzinfo=timezone.utc)
    if now - last_activity > _VISIT_TIMEOUT:
        visit_count += 1

    execute_db(
        """
        UPDATE shop_visits
           SET visit_count = ?,
               last_activity_utc = ?,
               user_id = ?,
               party_id = ?
         WHERE shop_id = ? AND character_id = ?
        """,
        (visit_count, now.isoformat(" "), user_id, party_id, shop_id, character_id),
    )
    return visit_count

