# commands/admin_commands.py
"""
Admin command handling module.

Exports
-------
- AdminCommandHandler : class
- handle_admin_command : legacy function wrapper
"""

from __future__ import annotations

import os
import signal
import time
from typing import Any

from app.db import execute_db, query_db
from app.config import RuntimeFlags
from app.models.characters import get_user_by_phone

# ─────────────────────────── constants ────────────────────────────
APP_START_TS = time.time()  # for uptime in _status()


class AdminCommandHandler:
    """Dispatcher for every `admin …` console command (DM-style layout)."""

    # DMs may not assign Admin, but Admins may assign all tiers.
    VALID_TIERS: set[str] = {"Free", "Adventurer", "DM", "Guild", "Admin"}

    # ───────────────────────── constructor ──────────────────────────
    def __init__(self) -> None:
        self._commands: dict[str, callable] = {
            # system maintenance
            "shutdown": self._shutdown,
            "status": self._status,
            "log": self._log,
            "restart": self._restart,
            "clear_cache": self._clear_cache,
            "debug_on": self._debug_on,
            "debug_off": self._debug_off,
            "reset_state": self._reset_state,
            # user management
            "upgrade_user": self._upgrade_user,
        }

    # ───────────────────── public entry-point ───────────────────────
    def handle(self, admin_input: str, admin_user_id: int | None = None) -> str:
        """
        Only callers whose **subscription_tier** is ADMIN may run `admin …`.
        """
        # ── PERMISSION GATE ──────────────────────────────────────────
        row = query_db(
            "SELECT subscription_tier FROM users WHERE user_id = ?",
            (admin_user_id,),
            one=True,
        )
        if (
            not row
            or row["subscription_tier"].lower() != "admin"
        ):
            return "⛔  Only ADMIN-tier accounts may issue Admin commands."

        # ── dispatch logic (matches dm_commands style) ──────────────
        parts = admin_input.strip().split()
        if len(parts) < 2 or parts[0].lower() != "admin":
            return "Invalid admin command."

        cmd = parts[1].lower()
        fn = self._commands.get(cmd)
        if not fn:
            return self._help()

        try:
            return fn(parts[2:], admin_user_id)
        except Exception as exc:  # pragma: no cover
            return f"❌ An unexpected error occurred: {exc}"

    # ───────────────────────── helpers ──────────────────────────────
    @staticmethod
    def _audit(
        entity_type: str,
        entity_id: int | str,
        field: str,
        old: Any,
        new: Any,
        changed_by: int | None,
    ) -> None:
        execute_db(
            """
            INSERT INTO audit_log
                  (entity_type, entity_id, field, old_value, new_value, changed_by)
            VALUES (?,           ?,         ?,     ?,         ?,         ?)
            """,
            (entity_type, entity_id, field, str(old), str(new), changed_by),
        )

    # ─────────────────── admin sub-commands ─────────────────────────
    # (DM-style: each returns a string that goes back to the CLI)

    def _shutdown(self, _args, admin_id) -> str:
        execute_db(
            """
            INSERT INTO system_logs (action, details)
            VALUES ('SHUTDOWN', 'Safe shutdown initiated by admin.')
            """
        )
        self._audit("system", 0, "shutdown", None, "initiated", admin_id)
        print("[ADMIN] Safe shutdown initiated.")
        os.kill(os.getpid(), signal.SIGINT)
        return "🛑 System shutdown initiated."

    def _status(self, _args, _admin_id) -> str:
        minutes = int((time.time() - APP_START_TS) // 60)
        up_for = f"{minutes} min" if minutes else "less than a minute"
        dbg = "ON" if RuntimeFlags.DEBUG_MODE else "OFF"
        return f"✅ System running for {up_for}. Debug mode is {dbg}."

    def _log(self, _args, _admin_id) -> str:
        rows = query_db(
            "SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT 10"
        )
        if not rows:
            return "[ADMIN] No logs found."
        return "\n".join(
            f"{r['timestamp']} • {r['action']}: {r['details']}" for r in rows
        )

    def _restart(self, _args, admin_id) -> str:
        execute_db(
            "INSERT INTO system_logs (action, details) "
            "VALUES ('RESTART', 'Admin restart requested.')"
        )
        self._audit("system", 0, "restart", None, "requested", admin_id)
        return (
            "🔁 Restart requested (stub). Restart the process via your manager."
        )

    def _clear_cache(self, _args, admin_id) -> str:
        # real cache clear would go here
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
        """
        admin upgrade_user <phone | player-name> <tier>
        """
        if len(args) < 2:
            return "Usage: admin upgrade_user <phone|player name> <tier>"

        *identifier_parts, tier_raw = args
        identifier = " ".join(identifier_parts)

        # tier validation
        tier_key = tier_raw.lower()
        if tier_key not in {t.lower() for t in self.VALID_TIERS}:
            allowed = ", ".join(sorted(self.VALID_TIERS))
            return f"Tier must be one of: {allowed}."

        # canonical form
        tier = (
            "Admin" if tier_key == "admin"
            else "DM" if tier_key == "dm"
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
                WHERE LOWER(c.player_name)=LOWER(?)
                LIMIT 1
                """,
                (identifier,),
                one=True,
            )
        if not user:
            return "❌ User not found."

        # apply & audit
        old_tier = user["subscription_tier"]
        execute_db(
            "UPDATE users SET subscription_tier = ? WHERE user_id = ?",
            (tier, user["user_id"]),
        )
        self._audit(
            "user",
            user["user_id"],
            "subscription_tier",
            old_tier,
            tier,
            admin_id,
        )
        return f"[ADMIN] User '{user['user_name']}' upgraded to {tier} tier."

    # ─────────────────────────── help ───────────────────────────────
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


# ─────────────────── legacy wrapper (like dm_commands) ─────────────
_handler = AdminCommandHandler()


def handle_admin_command(admin_input: str, admin_user_id: int | None = None) -> str:
    """Functional API retained so old imports keep working."""
    return _handler.handle(admin_input, admin_user_id)


__all__ = ["AdminCommandHandler", "handle_admin_command"]
