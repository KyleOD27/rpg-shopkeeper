import sqlite3
from contextlib import closing
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env for config
load_dotenv()

# Dynamically locate the project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Absolute path to your DB file
DB_PATH = BASE_DIR / 'rpg-shopkeeper.db'


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 🛠️ <-- ADD THIS
    return conn


def query_db(query, args=(), one=False):
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        cur.execute(query, args)
        conn.commit()
        return cur.lastrowid


def get_convo_state(character_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT current_state, pending_action, pending_item, updated_at
            FROM character_sessions
            WHERE character_id = ?
            ''',
            (character_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "current_state": row[0],
                "pending_action": row[1],
                "pending_item": row[2],
                "updated_at": row[3],
            }
        return None


def update_convo_state(character_id, state, action=None, item=None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            '''
            INSERT INTO character_sessions (character_id, current_state, pending_action, pending_item)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(character_id) DO UPDATE SET
              current_state=excluded.current_state,
              pending_action=excluded.pending_action,
              pending_item=excluded.pending_item,
              updated_at=CURRENT_TIMESTAMP
            ''',
            (character_id, state, action, item)
        )


def log_convo_state(character_id, state, action, item, user_input=None, player_intent=None):
    with open("session_log.txt", "a") as log:
        log.write(
            f"CharacterID={character_id} | State={state} | Action={action} | Item={item} | "
            f"Input='{user_input}' | Intent={player_intent}\n"
        )


def create_tables():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS character_sessions (
                character_id TEXT PRIMARY KEY,
                current_state TEXT,
                pending_action TEXT,
                pending_item TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS session_state_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                state TEXT NOT NULL,
                pending_action TEXT,
                pending_item TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Tables ensured: character_sessions, session_state_log")


def upsert_character_session(character_id, state, pending_action=None, pending_item=None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO character_sessions (character_id, current_state, pending_action, pending_item)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(character_id) DO UPDATE SET
                current_state = excluded.current_state,
                pending_action = excluded.pending_action,
                pending_item = excluded.pending_item,
                updated_at = CURRENT_TIMESTAMP
        ''', (character_id, state, pending_action, pending_item))
        conn.commit()

def get_item_details(conn, item_name: str):
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_name, equipment_category, gear_category, weapon_category,
                   weapon_range, category_range, damage_dice, damage_type,
                   range_normal, range_long, base_price, price_unit, weight, desc
            FROM items
            WHERE LOWER(item_name) = LOWER(?)
            LIMIT 1
        """, (item_name,))
        return cursor.fetchone()

# ─── Account / character profile helper ────────────────────────────────
def get_account_profile(character_id: int) -> dict:
    """
    Given the *current* character_id (the one in this chat session),
    return:
      user_name, phone_number, subscription_tier
      characters -> list[{character_id, player_name, character_name, role,
                          party_id, party_name}]
    """
    with get_connection() as conn:
        cur = conn.cursor()

        # 1.  Who is the user that owns this character?
        cur.execute(
            """SELECT u.user_id, u.user_name, u.phone_number, u.subscription_tier
                 FROM users u
                 JOIN characters c ON c.user_id = u.user_id
                WHERE c.character_id = ?""",
            (character_id,))
        user = cur.fetchone()
        if not user:
            raise ValueError(f"character_id {character_id} not found")

        # 2.  Pull *all* characters that user owns (join parties for names)
        cur.execute(
            """SELECT c.character_id, c.player_name, c.character_name, c.role,
                      p.party_id, p.party_name
                 FROM characters   c
                 JOIN parties      p ON p.party_id = c.party_id
                WHERE c.user_id = ?
                ORDER BY c.character_id""",
            (user["user_id"],))
        chars = [dict(r) for r in cur.fetchall()]

    return {
        "user_name":        user["user_name"] or "Unnamed",
        "phone_number":     user["phone_number"],
        "subscription_tier": user["subscription_tier"],
        "characters":       chars,
    }



if __name__ == "__main__":
    create_tables()
