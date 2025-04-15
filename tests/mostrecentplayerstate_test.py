# test_state_log.py

import sqlite3

from app.db import BASE_DIR

DB_PATH = BASE_DIR / 'grizzlebeard.db'

def print_all_player_states():
    print("=== Player Conversation State Log ===\n")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT player_id, current_state, pending_action, pending_item, updated_at FROM player_sessions")

        rows = cursor.fetchall()

        if not rows:
            print("No player sessions found.")
            return

        for row in rows:
            print(f"Player ID        : {row[0]}")
            print(f"Current State    : {row[1]}")
            print(f"Pending Action   : {row[2] or '-'}")
            print(f"Pending Item     : {row[3] or '-'}")
            print(f"Last Updated     : {row[4]}")
            print("-" * 40)

if __name__ == "__main__":
    print_all_player_states()
