# app/auth/user_login.py

from app.db import query_db, execute_db
from app.models.parties import get_all_parties, add_new_party
import re

def strip_prefix(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("+44"):
        return phone[3:]
    elif phone.startswith("44"):
        return phone[2:]
    elif phone.startswith("0"):
        return phone[1:]
    return phone

def normalise_for_storage(phone):
    return f"+44{strip_prefix(phone)}"

def get_user_by_phone(input_phone):
    stripped_input = strip_prefix(input_phone)
    sql = "SELECT * FROM users"
    all_users = query_db(sql)

    for user in all_users:
        stored = strip_prefix(user["phone_number"])
        if stripped_input == stored:
            return user
    return None

def register_user(phone, user_name):
    stored_phone = normalise_for_storage(phone)
    execute_db("INSERT INTO users (phone_number, user_name) VALUES (?, ?)", (stored_phone, user_name))
    return get_user_by_phone(phone)

def create_character_for_user(phone, user_id, party_id, player_name, character_name, role):
    execute_db(
        '''
        INSERT INTO characters (user_id, party_id, player_name, character_name, role)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (user_id, party_id, player_name, character_name, role)
    )
    print(f"[INFO] New character '{player_name}' added successfully!")
