# app/db.py – runtime DB helper (persistent outside PyInstaller temp dir)
# -----------------------------------------------------------------------------
# * Distinguishes read‑only resources (bundled with the .exe) from the writable
#   user directory where data/shopkeeper.db must live.
# * Copies the seeded rpg-shopkeeper.db to that persistent location on first
#   launch, so the file survives after the _MEIXXXX temp folder is gone.
# * Behaviour in development / tests is unchanged (both roots are project dir).
# -----------------------------------------------------------------------------

from __future__ import annotations

import os
import shutil
import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path
from typing import Iterable, Any

# ──────────────────── Root helpers ──────────────────────────

def _resource_root() -> Path:
    """Read‑only files that PyInstaller bundles (schema.sql, seeded DB, etc.)."""
    if getattr(sys, "_MEIPASS", None):  # frozen bundle
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[1]  # repo checkout


def _user_root() -> Path:
    """Writable root that persists between runs."""
    if getattr(sys, "_MEIPASS", None):
        # directory that contains the .exe – stays after temp dir is gone
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


RESOURCE_ROOT = _resource_root()  # read‑only
ROOT = _user_root()              # writable / dev root

# ───────────────────── Paths ───────────────────────────────
SCHEMA_PATH = RESOURCE_ROOT / "database" / "schema.sql"
SEEDED_DB = RESOURCE_ROOT / "rpg-shopkeeper.db"        # bundled with build

DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "shopkeeper.db"                   # runtime file
SETUP_PKG = "setup.setup_all"                          # only used in dev

# ───────────────────── Guards ──────────────────────────────
_BOOTSTRAPPED = False  # run schema patch once

# ─────────────────── Schema loader ─────────────────────────

def _load_schema() -> str:
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    fixed: list[str] = []
    for line in text.splitlines():
        if line.strip().upper().startswith("CREATE TABLE ") and "IF NOT EXISTS" not in line.upper():
            line = line.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
        fixed.append(line)
    return "\n".join(fixed)

# ─────────────────── DB provisioning ───────────────────────

def _build_seed_db(no_srd: bool = False) -> None:
    """Run setup/setup_all.py --reset (dev only)."""
    print("⚒️  Building seeded database …")
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}"
    args = [sys.executable, "-m", SETUP_PKG, "--reset"]
    if no_srd or env.get("SHOP_NO_SRD") == "1":
        args.append("--no-srd")
    subprocess.run(args, cwd=str(ROOT), env=env, check=True)


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_local_db(no_srd: bool = False) -> None:
    """Create data/shopkeeper.db by copying the bundled seeded DB."""
    _ensure_data_dir()

    if DB_PATH.exists():
        return  # already there

    if not SEEDED_DB.exists():  # dev environment where build not run yet
        _build_seed_db(no_srd=no_srd)

    shutil.copy2(SEEDED_DB, DB_PATH)
    print("🗂  Copied seeded DB into data/")

# ─────────────────── Schema bootstrap ─────────────────────

def _bootstrap() -> None:
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return

    with sqlite3.connect(DB_PATH) as conn:
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='users'"
        ).fetchone()
        if not exists:
            conn.executescript(_load_schema())
            conn.commit()
    _BOOTSTRAPPED = True

# ─────────────────── Connection factory ───────────────────

def _get_connection() -> sqlite3.Connection:
    _ensure_local_db()
    _bootstrap()
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

get_connection = _get_connection  # backward compatibility

# ───────────────────── Public helpers ─────────────────────

def query_db(sql: str, args: Iterable[Any] = (), one: bool = False):
    with closing(_get_connection()) as conn:
        cur = conn.execute(sql, args)
        rows = cur.fetchall()
        return rows[0] if one and rows else rows


def execute_db(sql: str, args: Iterable[Any] = ()) -> int:
    with closing(_get_connection()) as conn:
        cur = conn.execute(sql, args)
        conn.commit()
        return cur.lastrowid


def execute(sql: str, args: Iterable[Any] = ()) -> int:
    with closing(_get_connection()) as conn:
        cur = conn.execute(sql, args)
        conn.commit()
        return cur.rowcount

# ───────── Domain‑specific helpers (unchanged) ────────────
# … (rest of file unchanged)

# ─────────────── Domain‑specific helpers (unchanged) ───────────────

def get_convo_state(character_id: str):
    row = query_db(
        "SELECT current_state, pending_action, pending_item, updated_at "
        "FROM character_sessions WHERE character_id = ?", (character_id,), True
    )
    return dict(row) if row else None


def update_convo_state(
    character_id: str,
    state: str,
    action: str | None = None,
    item: str | None = None,
):
    execute_db(
        """INSERT INTO character_sessions (character_id, current_state,
                                           pending_action, pending_item)
              VALUES (?, ?, ?, ?)
         ON CONFLICT(character_id) DO UPDATE SET
             current_state   = excluded.current_state,
             pending_action  = excluded.pending_action,
             pending_item    = excluded.pending_item,
             updated_at      = CURRENT_TIMESTAMP""",
        (character_id, state, action, item),
    )


def log_convo_state(
    character_id,
    state,
    action,
    item,
    user_input=None,
    player_intent=None,
):
    with open(DATA_DIR / "session_log.txt", "a", encoding="utf-8") as f:
        f.write(
            f"CharacterID={character_id} | State={state} | Action={action} "
            f"| Item={item} | Input='{user_input}' | Intent={player_intent}\n"
        )


def get_item_details(conn, item_name: str):
    return conn.execute(
        """SELECT item_name, equipment_category, gear_category, weapon_category,
                 weapon_range, category_range, damage_dice, damage_type,
                 range_normal, range_long, base_price, price_unit,
                 weight, desc
            FROM items
           WHERE LOWER(item_name) = LOWER(?)
           LIMIT 1""",
        (item_name,),
    ).fetchone()

def get_account_profile(character_id: int) -> dict:
    with _get_connection() as conn:
        cur = conn.cursor()

        # ─── account row ─────────────────────────────
        cur.execute(
            """SELECT u.user_id, u.user_name, u.phone_number, u.subscription_tier
                 FROM users u
                 JOIN characters c ON c.user_id = u.user_id
                WHERE c.character_id = ?""",
            (character_id,),
        )
        user = cur.fetchone()
        if not user:
            raise ValueError(f"character_id {character_id} not found")

        # ─── all chars that belong to *this user* ───
        cur.execute(
            """SELECT c.character_id, c.player_name, c.character_name, c.role,
                      p.party_id,  p.party_name
                 FROM characters c
                 JOIN parties     p ON p.party_id = c.party_id
                WHERE c.user_id = ?
             ORDER BY c.character_id""",
            (user["user_id"],),
        )
        chars = [dict(r) for r in cur.fetchall()]

        # Pick the first char’s party as the “active” header
        active_party_id   = chars[0]["party_id"]  if chars else None
        active_party_name = chars[0]["party_name"] if chars else None

        owner_name  = get_party_owner_name(active_party_id) if active_party_id else None
        member_list = get_party_member_names(active_party_id) if active_party_id else []

    return (
        dict(user)
        | {
            "player_name": chars[0]["player_name"] if chars else None,
            "party_name":  active_party_name,
            "party_owner_name": owner_name,
            "party_members": member_list,          #  🆕  <<<<<<<<
            "characters": chars,
        }
    )


# ───────── Party owner helper ──────────────────────────────
def get_party_owner_name(party_id: str) -> str | None:
    row = query_db(
        """SELECT COALESCE(c.player_name, u.user_name) AS owner_name
             FROM party_owners  po
             JOIN users        u  ON u.user_id = po.user_id
        LEFT JOIN characters    c  ON c.user_id = u.user_id
                                      AND c.party_id = po.party_id
            WHERE po.party_id = ?
            LIMIT 1""",
        (party_id,),
        one=True,
    )
    return row["owner_name"] if row else None

# ───────── Party-member helper ─────────────────────────────
def get_party_member_names(party_id: str) -> list[str]:
    """
    Return the display names of everyone who belongs to `party_id`
    (character-player name if they have one in this party, otherwise account user_name).
    """
    rows = query_db(
        """
        SELECT DISTINCT
               COALESCE(c.player_name, u.user_name)  AS member_name
          FROM party_membership pm
          JOIN users            u  ON u.user_id = pm.user_id
     LEFT JOIN characters        c  ON c.user_id  = u.user_id
                                    AND c.party_id = pm.party_id
         WHERE pm.party_id = ?
         ORDER BY member_name
        """,
        (party_id,),
    )
    return [r["member_name"] for r in rows]



# ───────────────────── CLI utility (dev) ───────────────────
if __name__ == "__main__":
    print("Ensuring schema …")
    _ensure_local_db()
    _bootstrap()
    print(f"✅ SQLite DB ready at {DB_PATH}")
