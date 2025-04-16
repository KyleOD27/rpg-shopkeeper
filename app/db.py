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
    return sqlite3.connect(DB_PATH)

def query_db(query, args=(), one=False):
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
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

def get_convo_state(player_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT current_state, pending_action, pending_item, updated_at
            FROM player_sessions
            WHERE player_id = ?
            ''',
            (player_id,)
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

def update_convo_state(player_id, state, action=None, item=None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            '''
            INSERT INTO player_sessions (player_id, current_state, pending_action, pending_item)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(player_id) DO UPDATE SET
              current_state=excluded.current_state,
              pending_action=excluded.pending_action,
              pending_item=excluded.pending_item,
              updated_at=CURRENT_TIMESTAMP
            ''',
            (player_id, state, action, item)
        )

def log_convo_state(player_id, state, action, item, user_input=None, player_intent=None):
    with open("session_log.txt", "a") as log:
        log.write(
            f"PlayerID={player_id} | State={state} | Action={action} | Item={item} | "
            f"Input='{user_input}' | Intent={player_intent}\n"
        )


def create_tables():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS player_sessions (
                player_id TEXT PRIMARY KEY,
                current_state TEXT,
                pending_action TEXT,
                pending_item TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS session_state_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                state TEXT NOT NULL,
                pending_action TEXT,
                pending_item TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Tables ensured: player_sessions, session_state_log")


def upsert_player_session(player_id, state, pending_action=None, pending_item=None):
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO player_sessions (player_id, current_state, pending_action, pending_item)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(player_id) DO UPDATE SET
                        current_state = excluded.current_state,
                        pending_action = excluded.pending_action,
                        pending_item = excluded.pending_item,
                        updated_at = CURRENT_TIMESTAMP
                ''', (player_id, state, pending_action, pending_item))

                conn.commit()


if __name__ == "__main__":
    create_tables()


