import sqlite3
from app.db import BASE_DIR
DB_PATH = BASE_DIR / 'grizzlebeard.db'


def print_latest_states():
    print('=== Latest State per Player ===\n')
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT player_id, current_state, pending_action, pending_item, updated_at
               FROM player_sessions
               ORDER BY updated_at DESC"""
            )
        rows = cursor.fetchall()
        for row in rows:
            print(
                f"[{row[4]}] {row[0]} → {row[1]} | Action: {row[2] or '-'} | Item: {row[3] or '-'}"
                )
        print('-' * 40)


def print_state_history():
    print('\n=== Full State History ===\n')
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT player_id, state, pending_action, pending_item, timestamp
               FROM session_state_log
               ORDER BY timestamp ASC"""
            )
        rows = cursor.fetchall()
        for row in rows:
            print(
                f"[{row[4]}] {row[0]} → {row[1]} | Action: {row[2] or '-'} | Item: {row[3] or '-'}"
                )
        print('-' * 40)


if __name__ == '__main__':
    print_latest_states()
    print_state_history()
