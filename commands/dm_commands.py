# app/dm_commands.py

from app.models.parties import get_party_by_id, get_all_parties, add_new_party, update_party_gold
from app.models.characters import get_user_by_phone, add_character_to_party, get_all_owned_characters
from app.auth.user_login import register_user, create_character_for_user
from app.db import execute_db, query_db

# ✅ Handle in-game DM commands like "dm add_gold 50"
def handle_dm_command(party_id, player_id, player_input, party_data=None):
    parts = player_input.split()

    if len(parts) < 2:
        return "Invalid DM command."

    command = parts[1]

    if command == "add_gold":
        if len(parts) != 3:
            return "Usage: dm add_gold <amount>"
        try:
            amount = int(parts[2])
        except ValueError:
            return "Amount must be a number."

        party = get_party_by_id(party_id)
        if not party:
            return "Party not found."

        new_gold = party['party_gold'] + amount
        update_party_gold(party_id, new_gold)

        if party_data is not None:
            party_data["party_gold"] = new_gold

        execute_db("""
            INSERT INTO transaction_ledger (party_id, character_id, action, amount, balance_after, details)
            VALUES (?, ?, 'ADJUST', ?, ?, ?)
        """, (party_id, player_id, amount, new_gold, f"DM granted {amount} gold"))

        return f"[DM] Added {amount} gold. Party gold is now {new_gold}."

    elif command == "new_party":
        name = " ".join(parts[2:])
        if not name:
            return "Usage: dm new_party <party name>"
        new_id = add_new_party(name)  # ✅ Correct function call here
        return f"[DM] New party '{name}' created with ID '{new_id}'" if new_id else "❌ Failed to create party."

    elif command == "new_user":
        if len(parts) < 4:
            return "Usage: dm new_user <+44...> <user name>"
        phone = parts[2]
        name = " ".join(parts[3:])
        user = register_user(phone, name)
        return f"[DM] User '{name}' created." if user else "❌ Failed to register user."

    elif command == "new_char":
        if len(parts) < 6:
            return "Usage: dm new_char <+44...> <party_id> <player name> <char name> <role>"
        phone = parts[2]
        party_id = parts[3]
        player_name = parts[4]
        char_name = parts[5]
        role = " ".join(parts[6:]) if len(parts) > 6 else "Adventurer"
        user = get_user_by_phone(phone)
        if not user:
            return "❌ User not found."
        create_character_for_user(phone, user["user_id"], party_id, player_name, char_name, role)
        return f"[DM] Character '{char_name}' created for {player_name}."

    elif command == "rename_user":
        if len(parts) < 4:
            return "Usage: dm rename_user <+44...> <new name>"
        phone = parts[2]
        new_name = " ".join(parts[3:])
        user = get_user_by_phone(phone)
        if not user:
            return "❌ User not found."
        execute_db("UPDATE users SET user_name = ? WHERE user_id = ?", (new_name, user["user_id"]))
        return f"[DM] User name updated to {new_name}."

    elif command == "rename_party":
        if len(parts) < 4:
            return "Usage: dm rename_party <party_id> <new name>"
        party_id = parts[2]
        new_name = " ".join(parts[3:])
        execute_db("UPDATE parties SET party_name = ? WHERE party_id = ?", (new_name, party_id))
        return f"[DM] Party name updated to '{new_name}'."

    elif command == "rename_char":
        if len(parts) < 5:
            return "Usage: dm rename_char <character_id> <new name> <new role>"
        character_id = int(parts[2])
        new_name = parts[3]
        new_role = " ".join(parts[4:])
        execute_db(
            "UPDATE characters SET character_name = ?, role = ? WHERE character_id = ?",
            (new_name, new_role, character_id)
        )
        return f"[DM] Character {character_id} updated to '{new_name}' the {new_role}'."

    # New commands to see all users and characters
    elif command == "see_users":
        users = query_db("SELECT * FROM users")
        if not users:
            return "No users found."
        user_list = "\n".join([f"{user['user_name']} ({user['phone_number']})" for user in users])
        return f"[DM] Users:\n{user_list}"

    elif command == "see_chars":
        characters = query_db("SELECT * FROM characters")
        if not characters:
            return "No characters found."
        char_list = "\n".join([f"{char['character_name']} ({char['role']}) - Player: {char['player_name']}" for char in characters])
        return f"[DM] Characters:\n{char_list}"

    # Return available commands if the command is not recognized
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
        "- dm see_chars"
    )
