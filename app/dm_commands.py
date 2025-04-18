# app/dm_commands.py

from app.models.parties import get_party_by_id, update_party_gold
from app.db import execute_db


def handle_dm_command(party_id, player_id, player_input):
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

        execute_db("""
            INSERT INTO transaction_ledger (party_id, player_id, action, amount, balance_after, details)
            VALUES (?, ?, 'ADJUST', ?, ?, ?)
        """, (party_id, player_id, amount, new_gold, f"DM granted {amount} gold"))

        return f"[DM] Added {amount} gold. Party gold is now {new_gold}."

    return "Unknown DM command."
