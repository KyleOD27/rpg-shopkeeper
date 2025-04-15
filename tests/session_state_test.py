# tests/full_state_log_test.py

import sqlite3
from app.db import BASE_DIR

DB_PATH = BASE_DIR / 'grizzlebeard.db'

def print_full_state_log():
    print("=== CURRENT PLAYER SESSION STATE ===\n")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT player_id, current_state, pending_action, pending_item, updated_at
            FROM player_sessions
            ORDER BY updated_at ASC
            '''
        )

        rows = cursor.fetchall()

        if not rows:
            print("No active player sessions found.")
            return

        for row in rows:
            player_id, state, action, item, timestamp = row
            print(f"[{timestamp}] Player: {player_id} → State: {state} | Action: {action or '-'} | Item: {item or '-'}")
#


        print("\n=== END OF SESSION STATE ===")

if __name__ == "__main__":
    print_full_state_log()
