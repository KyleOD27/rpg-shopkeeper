"""DM command handling module.

Exports:
    - DMCommandHandler : class
    - handle_dm_command : legacy function wrapper

The free function `handle_dm_command` delegates to a singleton instance of
`DMCommandHandler`, so existing code that does::

    from commands.dm_commands import handle_dm_command

continues to work unchanged after the refactor.

If you're integrating into a fresh component you should prefer::

    from commands.dm_commands import DMCommandHandler
    handler = DMCommandHandler()
    handler.handle(...)
"""

from __future__ import annotations

from typing import Any

from app.models.parties import get_party_by_id, add_new_party, update_party_gold
from app.models.characters import get_user_by_phone
from app.auth.user_login import register_user, create_character_for_user
from app.db import execute_db, query_db


class DMCommandHandler:
    """Class-based handler for every “dm …” Dungeon-Master command."""

    # ─────────────────────────── constants ────────────────────────────
    VALID_TIERS: set[str] = {"Free", "Adventurer", "DM", "Guild"}

    # ────────────────────────── constructor ───────────────────────────
    def __init__(self) -> None:
        # keyword  →  bound method
        self._commands: dict[str, callable] = {
            "add_gold": self._add_gold,
            "new_party": self._new_party,
            "new_user": self._new_user,
            "new_char": self._new_char,
            "rename_user": self._rename_user,
            "rename_party": self._rename_party,
            "rename_char": self._rename_char,
            "see_users": self._see_users,
            "see_chars": self._see_chars,
            # NEW
            "upgrade_user": self._upgrade_user,
        }

    # ───────────────────── public entry-point ────────────────────────
    def handle(
        self,
        party_id: int,
        player_id: int,
        player_input: str,
        party_data: dict | None = None,
    ) -> str:
        parts = player_input.split()
        if len(parts) < 2 or parts[0].lower() != "dm":
            return "Invalid DM command."

        cmd = parts[1].lower()
        fn = self._commands.get(cmd)
        if not fn:
            return self._help()

        try:
            return fn(party_id, player_id, parts[2:], party_data)
        except Exception as exc:  # pragma: no cover
            return f"❌ An unexpected error occurred: {exc}"


    # ───────────────────────── helpers ────────────────────────────
    @staticmethod
    def _audit(
        entity_type: str,
        entity_id: int | str,
        field: str,
        old: Any,
        new: Any,
        changed_by: int | None,
    ) -> None:
        """Write a row to audit_log."""
        execute_db(
            """
            INSERT INTO audit_log
              (entity_type, entity_id, field, old_value, new_value, changed_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (entity_type, entity_id, field, str(old), str(new), changed_by),
        )

    # -- DM sub‑commands ---------------------------------------------------------

    def _add_gold(self, party_id, player_id, args, party_data):
        if len(args) != 1:
            return "Usage: dm add_gold <amount>"
        try:
            amount = int(args[0])
        except ValueError:
            return "Amount must be a number."

        party = get_party_by_id(party_id)
        if not party:
            return "Party not found."

        new_gold = party["party_gold"] + amount
        update_party_gold(party_id, new_gold)

        if party_data is not None:
            party_data["party_gold"] = new_gold

        execute_db(
            """
            INSERT INTO transaction_ledger (party_id, character_id, action, amount, balance_after, details)
            VALUES (?, ?, 'ADJUST', ?, ?, ?)
            """,
            (party_id, player_id, amount, new_gold, f"DM granted {amount} gold"),
        )
        return f"[DM] Added {amount} gold. Party gold is now {new_gold}. "

    def _new_party(self, _party_id, _player_id, args, _party_data):
        if not args:
            return "Usage: dm new_party <party name>"
        name = " ".join(args)
        new_id = add_new_party(name)
        return (
            f"[DM] New party '{name}' created with ID '{new_id}'"
            if new_id
            else "❌ Failed to create party."
        )

    def _new_user(self, _party_id, _player_id, args, _party_data):
        if len(args) < 2:
            return "Usage: dm new_user <+44...> <user name>"
        phone, *name_parts = args
        name = " ".join(name_parts)
        user = register_user(phone, name)
        return f"[DM] User '{name}' created." if user else "❌ Failed to register user."

    def _new_char(self, _party_id, _player_id, args, _party_data):
        if len(args) < 5:
            return "Usage: dm new_char <+44...> <party_id> <player name> <char name> <role>"
        phone, party_id, player_name, char_name, *role_parts = args
        role = " ".join(role_parts) if role_parts else "Adventurer"

        user = get_user_by_phone(phone)
        if not user:
            return "❌ User not found."

        create_character_for_user(phone, user["user_id"], party_id, player_name, char_name, role)
        return f"[DM] Character '{char_name}' created for {player_name}."

    def _rename_user(self, _party_id, dm_user_id, args, _party_data):
        if len(args) < 2:
            return "Usage: dm rename_user <+44...> <new name>"
        phone, *new_name_parts = args
        new_name = " ".join(new_name_parts)
        user = get_user_by_phone(phone)
        if not user:
            return "❌ User not found."

        old_name = user["user_name"]
        execute_db(
            "UPDATE users SET user_name = ? WHERE user_id = ?",
            (new_name, user["user_id"]),
        )
        self._audit("user", user["user_id"], "user_name", old_name, new_name, dm_user_id)
        return f"[DM] User name updated to {new_name}."

    def _rename_party(self, _party_id, dm_user_id, args, _party_data):
        if len(args) < 2:
            return "Usage: dm rename_party <party_id> <new name>"
        party_id, *new_name_parts = args
        new_name = " ".join(new_name_parts)
        old_party = query_db(
            "SELECT party_name FROM parties WHERE party_id = ?",
            (party_id,),
            one=True,
        )
        if not old_party:
            return "❌ Party not found."
        old_name = old_party["party_name"]

        execute_db(
            "UPDATE parties SET party_name = ? WHERE party_id = ?",
            (new_name, party_id),
        )
        self._audit("party", party_id, "party_name", old_name, new_name, dm_user_id)
        return f"[DM] Party name updated to '{new_name}'."

    def _rename_char(self, _party_id, dm_user_id, args, _party_data):
        if len(args) < 3:
            return "Usage: dm rename_char <character_id> <new name> <new role>"
        character_id, new_name, *role_parts = args
        new_role = " ".join(role_parts)

        char = query_db(
            "SELECT character_name, role FROM characters WHERE character_id = ?",
            (character_id,),
            one=True,
        )
        if not char:
            return "❌ Character not found."

        execute_db(
            "UPDATE characters SET character_name = ?, role = ? WHERE character_id = ?",
            (new_name, new_role, int(character_id)),
        )
        # separate audit rows for each field
        self._audit("character", character_id, "character_name",
                    char["character_name"], new_name, dm_user_id)
        self._audit("character", character_id, "role",
                    char["role"], new_role, dm_user_id)
        return f"[DM] Character {character_id} updated to '{new_name}' the {new_role}."

    def _see_users(self, _party_id, _player_id, _args, _party_data):
        users = query_db("SELECT * FROM users")
        if not users:
            return "No users found."
        user_list = "\n".join(f"{u['user_name']} ({u['phone_number']})" for u in users)
        return f"[DM] Users:\n{user_list}"

    def _see_chars(self, _party_id, _player_id, _args, _party_data):
        characters = query_db("SELECT * FROM characters")
        if not characters:
            return "No characters found."
        char_list = "\n".join(
            f"{c['character_name']} ({c['role']}) - Player: {c['player_name']}" for c in characters
        )
        return f"[DM] Characters:\n{char_list}"

        # ──────────────────── 🆕 upgrade_user ────────────────────────────

    # ──────────────────── upgrade_user (with audit) ───────────────────
    def _upgrade_user(self, _party_id, dm_user_id, args, _party_data) -> str:
        """
        dm upgrade_user <phone | player-name> <tier>
        """
        if len(args) < 2:
            return "Usage: dm upgrade_user <phone|player name> <tier>"

        *identifier_parts, tier_raw = args
        identifier = " ".join(identifier_parts)

        # ----- validate tier ---------------------------------------------------
        tier_key = tier_raw.lower()
        if tier_key not in {t.lower() for t in self.VALID_TIERS}:
            allowed = ", ".join(sorted(self.VALID_TIERS))
            return f"Tier must be one of: {allowed}."
        tier = "DM" if tier_key == "dm" else tier_key.capitalize()

        # ----- locate the user -------------------------------------------------
        user = None
        if identifier.lstrip("+").isdigit():  # phone?
            user = get_user_by_phone("+" + identifier.lstrip("+"))

        if not user:  # account name?
            user = query_db(
                "SELECT * FROM users WHERE LOWER(user_name)=LOWER(?) LIMIT 1",
                (identifier,),
                one=True,
            )

        if not user:  # player name?
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

        # ----- apply the upgrade and AUDIT it ---------------------------------
        old_tier = user["subscription_tier"]  # ← NEW
        execute_db(
            "UPDATE users SET subscription_tier = ? WHERE user_id = ?",
            (tier, user["user_id"]),
        )

        # record the change (dm_user_id == caller’s player_id)
        self._audit(  # ← NEW
            "user",
            user["user_id"],
            "subscription_tier",
            old_tier,
            tier,
            dm_user_id,
        )

        return f"[DM] User '{user['user_name']}' upgraded to {tier} tier."

    # -- Helpers ----------------------------------------------------------------

    @staticmethod
    def _help() -> str:
        return (
            "Unknown DM command. Available commands:\n"
            "- dm add_gold <amount>\n"
            "- dm new_party <name>\n"
            "- dm new_user <+44...> <user name>\n"
            "- dm new_char <+44...> <party_id> <player> <char> <role>\n"
            "- dm rename_user <+44...> <new name>\n"
            "- dm rename_party <party_id> <new name>\n"
            "- dm rename_char <character_id> <new name> <new role>\n"
            "- dm see_users\n"
            "- dm see_chars\n"
            "- dm upgrade_user <+44...> <tier>"

        )


# ---------------------------------------------------------------------------
# Back‑compat shim ----------------------------------------------------------
# ---------------------------------------------------------------------------

_handler = DMCommandHandler()


def handle_dm_command(
    party_id: int,
    player_id: int,
    player_input: str,
    party_data: dict | None = None,
) -> str:  # noqa: D401
    """Delegate to a singleton instance of :class:`DMCommandHandler`."""
    return _handler.handle(party_id, player_id, player_input, party_data)


__all__ = ["DMCommandHandler", "handle_dm_command"]
