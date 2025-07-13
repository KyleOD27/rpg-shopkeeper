from app.models.characters import add_character_to_party
from app.db import execute_db, query_db

def get_user_by_id(user_id):
    sql = 'SELECT * FROM users WHERE user_id = ?'
    return query_db(sql, (user_id,), one=True)

def get_user_party(user_id):
    row = query_db(
        "SELECT party_id FROM party_membership WHERE user_id = ? LIMIT 1",
        (user_id,),
        one=True
    )
    return row["party_id"] if row else None

class UserCommandHandler:
    def __init__(self):
        self._commands = {
            "new_char": self._new_char,
            "delete_char": self._delete_char,
            "switch_char": self._switch_char,
        }
        # Alias mapping (add as many as you like)
        self._aliases = {
            # NEW CHARACTER
            "new char": "new_char",
            "new character": "new_char",
            "add char": "new_char",
            "add character": "new_char",
            "create char": "new_char",
            "create character": "new_char",
            # DELETE CHARACTER
            "delete char": "delete_char",
            "delete character": "delete_char",
            "remove char": "delete_char",
            "remove character": "delete_char",
            "del char": "delete_char",
            # SWITCH CHARACTER / LOGOUT
            "switch": "switch_char",
            "switch char": "switch_char",
            "switch character": "switch_char",
            "switch user": "switch_char",
            "logout": "switch_char",
            "log out": "switch_char",
            "logoff": "switch_char",
        }

    def handle(self, user_id: int, user_input: str) -> str:
        parts = user_input.strip().split()
        if len(parts) < 2 or parts[0].lower() != "user":
            return "Invalid user command."
        # Try two-word commands (e.g., new char)
        cmd = " ".join(parts[1:3]).lower()
        fn = self._commands.get(cmd)
        if not fn:
            # Fallback to single word
            cmd = parts[1].lower()
            fn = self._commands.get(cmd)
        if not fn:
            # Try aliases (two-word, then one-word)
            alias = " ".join(parts[1:3]).lower()
            canonical = self._aliases.get(alias)
            if not canonical:
                alias = parts[1].lower()
                canonical = self._aliases.get(alias)
            fn = self._commands.get(canonical) if canonical else None
            # Adjust argument offset for alias match
            if canonical:
                # Split the canonical (e.g. new_char) to know offset
                alias_len = len(alias.split())
                try:
                    args = parts[1+alias_len:]
                except Exception:
                    args = parts[2:]
            else:
                args = parts[2:]
        else:
            # Fallback if found as command
            args = parts[len(cmd.split())+1:]
        if not fn:
            return self._help()
        import traceback
        try:
            return fn(user_id, args)
        except Exception as exc:
            tb = traceback.format_exc()
            exc_type = type(exc).__name__
            return f"❌ {exc_type}: {exc}\n\nTraceback:\n{tb}"

    def _new_char(self, user_id, args):
        if len(args) < 1:
            return "Usage: user new_char <char_name> <role>"
        char_name = args[0]
        role = " ".join(args[1:]) if len(args) > 1 else "Adventurer"
        user = get_user_by_id(user_id)
        if not user:
            return "❌ User not found."
        phone = user['phone_number']
        player_name = user['user_name']
        party_id = get_user_party(user_id)
        if not party_id:
            return "❌ You are not a member of any party. Please join a party before creating a character."
        char_id = add_character_to_party(phone, party_id, player_name, char_name, role)
        if char_id:
            return f"[USER] Character '{char_name}' created in party '{party_id}' with role '{role}'."
        else:
            return f"[USER] Character '{char_name}' already exists in your party."

    def _delete_char(self, user_id, args):
        if not args:
            return "Usage: user delete_char <character_id|char_name>"
        identifier = " ".join(args).strip()
        char = None
        if identifier.isdigit():
            char = query_db("SELECT * FROM characters WHERE character_id=? AND user_id=?",
                            (int(identifier), user_id), one=True)
        if not char:
            char = query_db("SELECT * FROM characters WHERE (LOWER(character_name)=LOWER(?) OR LOWER(player_name)=LOWER(?)) AND user_id=? LIMIT 1",
                            (identifier.lower(), identifier.lower(), user_id), one=True)
        if not char:
            return "❌ Character not found or you do not own this character."
        cid = char["character_id"]
        name = char["character_name"] or char["player_name"]
        execute_db("UPDATE characters SET deleted=1 WHERE character_id=?", (cid,))
        return f"[USER] Character '{name}' marked as deleted."

    def _switch_char(self, user_id, args):
        if not args:
            chars = query_db(
                "SELECT character_id, character_name, role, party_id FROM characters WHERE user_id=? AND deleted=0",
                (user_id,))
            if not chars:
                return "You have no active characters to switch to."
            return {"switch_char_choices": chars}
        identifier = " ".join(args).strip()
        char = None
        if identifier.isdigit():
            char = query_db(
                "SELECT * FROM characters WHERE character_id=? AND user_id=? AND deleted=0",
                (int(identifier), user_id), one=True)
        if not char:
            char = query_db(
                "SELECT * FROM characters WHERE LOWER(character_name)=LOWER(?) AND user_id=? AND deleted=0 LIMIT 1",
                (identifier.lower(), user_id), one=True)
        if not char:
            return "❌ Character not found or you do not own this character."
        execute_db(
            "UPDATE users SET active_character_id = ? WHERE user_id = ?",
            (char["character_id"], user_id)
        )
        return f"[USER] You are now playing as '{char['character_name']}'!"

    @staticmethod
    def _help():
        return (
            "Unknown user command. Available commands:\n"
            "- user new_char <char_name> <role>\n"
            "- user delete_char <character_id|char_name>\n"
            "- user switch_char <character_id|character_name>\n"
            "You can also use natural commands like 'user add char', 'user switch', 'user logout', etc."
        )

_handler = UserCommandHandler()

def handle_user_command(user_id: int, user_input: str) -> str:
    return _handler.handle(user_id, user_input)
