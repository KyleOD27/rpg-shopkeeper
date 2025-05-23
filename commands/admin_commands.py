# commands/admin_commands.py
"""
Admin command handler (API mirrors dm_commands).

Exports
-------
- AdminCommandHandler : class
- handle_admin_command : functional wrapper
"""

from __future__ import annotations

import os
import signal
import time
from typing import Any

from app.db import execute_db, query_db
from app.config import RuntimeFlags
from app.models.characters import get_user_by_phone

APP_START_TS = time.time()                 # for uptime read-out
VALID_TIERS  = {"Free", "Adventurer", "DM", "Guild", "Admin"}


class AdminCommandHandler:
    """Dispatcher for every `admin …` console command."""

    def __init__(self) -> None:
        self._commands: dict[str, callable] = {
            # maintenance
            "shutdown":    self._shutdown,
            "status":      self._status,
            "log":         self._log,
            "restart":     self._restart,
            "clear_cache": self._clear_cache,
            "debug_on":    self._debug_on,
            "debug_off":   self._debug_off,
            "reset_state": self._reset_state,
            # user management
            "upgrade_user": self._upgrade_user,
        }

    # ───────────────────── public entry-point ──────────────────────
    def handle(self, player_id: int, admin_input: str) -> str:
        """
        Gate, parse and dispatch an **admin** command.

        Call signature matches dm_commands.handle():
            handle_admin_command(player_id, "admin status")
        """
        # ── PERMISSION CHECK ────────────────────────────────────────
        row = query_db(
            "SELECT subscription_tier FROM users WHERE user_id = ?",
            (player_id,),
            one=True,
        )
        if not row or row["subscription_tier"].lower() != "admin":
            return "⛔  Only ADMIN-tier accounts may issue Admin commands."

        # ── dispatch logic (identical pattern to DM) ───────────────
        parts = admin_input.strip().split()
        if len(parts) < 2 or parts[0].lower() != "admin":
            return "Invalid admin command."

        cmd = parts[1].lower()
        fn  = self._commands.get(cmd)
        if not fn:
            return self._help()

        try:
            return fn(parts[2:], player_id)
        except Exception as exc:                     # pragma: no cover
            return f"❌ An unexpected error occurred: {exc}"

    # ───────────────────────── helpers ─────────────────────────────
    @staticmethod
    def _audit(
        entity_type: str,
        entity_id: int | str,
        field: str,
        old: Any,
        new: Any,
        changed_by: int,
    ) -> None:
        execute_db(
            """
            INSERT INTO audit_log
                  (entity_type, entity_id, field, old_value, new_value, changed_by)
            VALUES (?,?,?,?,?,?)
            """,
            (entity_type, entity_id, field, str(old), str(new), changed_by),
        )

    # ─────────────────── admin sub-commands ────────────────────────
    def _shutdown(self, _args, admin_id) -> str:
        execute_db(
            "INSERT INTO system_logs(action,details)"
            "VALUES('SHUTDOWN','Safe shutdown by admin.')"
        )
        self._audit("system", 0, "shutdown", None, "initiated", admin_id)
        os.kill(os.getpid(), signal.SIGINT)
        return "🛑 System shutdown initiated."

    def _status(self, _args, _admin_id) -> str:
        mins = int((time.time() - APP_START_TS) // 60)
        uptime = f"{mins} min" if mins else "less than a minute"
        dbg = "ON" if RuntimeFlags.DEBUG_MODE else "OFF"
        return f"✅ System running for {uptime}. Debug mode is {dbg}."

    def _log(self, _args, _admin_id) -> str:
        rows = query_db("SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT 10")
        return (
            "\n".join(f"{r['timestamp']} • {r['action']}: {r['details']}" for r in rows)
            if rows else "[ADMIN] No logs found."
        )

    def _restart(self, _args, admin_id) -> str:
        execute_db(
            "INSERT INTO system_logs(action,details)"
            "VALUES('RESTART','Admin restart requested.')"
        )
        self._audit("system", 0, "restart", None, "requested", admin_id)
        return "🔁 Restart requested (stub). Restart via your process manager."

    def _clear_cache(self, _args, admin_id) -> str:
        self._audit("system", 0, "clear_cache", None, "performed", admin_id)
        return "🧹 Cache cleared (stub)."

    def _debug_on(self, _args, admin_id) -> str:
        prev = RuntimeFlags.DEBUG_MODE
        RuntimeFlags.DEBUG_MODE = True
        self._audit("system", 0, "debug_mode", prev, True, admin_id)
        return "🐞 Debug mode ENABLED."

    def _debug_off(self, _args, admin_id) -> str:
        prev = RuntimeFlags.DEBUG_MODE
        RuntimeFlags.DEBUG_MODE = False
        self._audit("system", 0, "debug_mode", prev, False, admin_id)
        return "🐞 Debug mode DISABLED."

    def _reset_state(self, _args, admin_id) -> str:
        execute_db(
            """
            UPDATE character_sessions
               SET current_state = NULL,
                   pending_action = NULL,
                   pending_item = NULL,
                   updated_at = CURRENT_TIMESTAMP
            """
        )
        self._audit("system", 0, "reset_state", None, "all_sessions", admin_id)
        return "🔄 All character session states have been reset."

    def _upgrade_user(self, args, admin_id) -> str:
        if len(args) < 2:
            return "Usage: admin upgrade_user <phone|player> <tier>"

        *identifier_parts, tier_raw = args
        identifier = " ".join(identifier_parts)

        tier_key = tier_raw.lower()
        if tier_key not in {t.lower() for t in VALID_TIERS}:
            return f"Tier must be one of: {', '.join(sorted(VALID_TIERS))}."

        tier = (
            "Admin" if tier_key == "admin"
            else "DM"   if tier_key == "dm"
            else tier_key.capitalize()
        )

        # locate user
        user = None
        if identifier.lstrip("+").isdigit():
            user = get_user_by_phone("+" + identifier.lstrip("+"))
        if not user:
            user = query_db(
                "SELECT * FROM users WHERE LOWER(user_name)=LOWER(?) LIMIT 1",
                (identifier,),
                one=True,
            )
        if not user:
            user = query_db(
                """
                SELECT u.* FROM users u
                 JOIN characters c ON c.user_id = u.user_id
                WHERE LOWER(c.player_name)=LOWER(?) LIMIT 1
                """,
                (identifier,),
                one=True,
            )
        if not user:
            return "❌ User not found."

        old_tier = user["subscription_tier"]
        execute_db(
            "UPDATE users SET subscription_tier=? WHERE user_id=?",
            (tier, user["user_id"]),
        )
        self._audit("user", user["user_id"], "subscription_tier",
                     old_tier, tier, admin_id)
        return f"[ADMIN] User '{user['user_name']}' upgraded to {tier} tier."

    # ───────────── help text ─────────────
    @staticmethod
    def _help() -> str:
        return (
            "Unknown admin command. Available commands:\n"
            "- admin shutdown\n"
            "- admin status\n"
            "- admin log\n"
            "- admin restart\n"
            "- admin clear_cache\n"
            "- admin debug_on / debug_off\n"
            "- admin reset_state\n"
            "- admin upgrade_user <phone|player> <tier>"
        )


# ───────────── functional wrapper ─────────────
_handler = AdminCommandHandler()


def handle_admin_command(player_id: int, admin_input: str) -> str:
    """
    Same calling order as dm_commands:
        handle_admin_command(player_id, "admin status")
    """
    return _handler.handle(player_id, admin_input)


__all__ = ["AdminCommandHandler", "handle_admin_command"]
