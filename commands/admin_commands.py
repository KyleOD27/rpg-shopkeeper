# app/admin_commands.py

import os
import signal
from app.db import execute_db, query_db
from app.config import RuntimeFlags  # <-- Use shared config flags

def handle_admin_command(admin_input):
    parts = admin_input.strip().split()

    if len(parts) < 2:
        return "Invalid admin command."

    command = parts[1]

    if command == "shutdown":
        execute_db("""
            INSERT INTO system_logs (action, details)
            VALUES (?, ?)
        """, ("SHUTDOWN", "Safe shutdown initiated by admin."))

        print("[ADMIN] Safe shutdown initiated.")
        os.kill(os.getpid(), signal.SIGINT)
        return "🛑 System shutdown initiated."

    elif command == "status":
        return (
            "✅ System running. Debug mode is ON."
            if RuntimeFlags.DEBUG_MODE else
            "✅ System running. Debug mode is OFF."
        )

    elif command == "log":
        logs = query_db("SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT 10")
        if not logs:
            return "[ADMIN] No logs found."
        return "\n".join([
            f"{log['timestamp']} - {log['action']}: {log['details']}" for log in logs
        ])

    elif command == "restart":
        execute_db("INSERT INTO system_logs (action, details) VALUES (?, ?)", ("RESTART", "Admin restart requested."))
        return "🔁 Restart requested (stub). You must restart the app manually or via process manager."

    elif command == "clear_cache":
        # Add cache clearing logic here if applicable
        return "🧹 Cache cleared (stub)."

    elif command == "debug_on":
        RuntimeFlags.DEBUG_MODE = True
        return "🐞 Debug mode ENABLED."

    elif command == "debug_off":
        RuntimeFlags.DEBUG_MODE = False
        return "🐞 Debug mode DISABLED."


    elif command == "reset_state":

        execute_db("""

            UPDATE character_sessions

            SET current_state = NULL,

                pending_action = NULL,

                pending_item = NULL,

                updated_at = CURRENT_TIMESTAMP

        """)

        return "🔄 All character session states have been reset."

    return (
        "Unknown admin command. Available commands:\n"
        "- admin shutdown\n"
        "- admin status\n"
        "- admin log\n"
        "- admin restart\n"
        "- admin clear_cache\n"
        "- admin debug_on / debug_off\n"
        "- admin reset_state"
    )
