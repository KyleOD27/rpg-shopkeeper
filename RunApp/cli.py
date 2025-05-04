# cli.py

import importlib
import os
import openai
from dotenv import load_dotenv

from app.db import execute_db, query_db
from app.models.parties import get_party_by_id, get_all_parties, add_new_party
from app.models.visits import get_visit_count, increment_visit_count
from app.models.shops import get_all_shops
from app.conversation import Conversation
from app.conversation_service import ConversationService
from app.config import RuntimeFlags, SHOP_NAME
from app.auth.user_login import get_user_by_phone, register_user, create_character_for_user

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def register_new_party():
    print("\n=== New Party Registration ===")
    party_name = input("Enter a name for your new party: ").strip()
    party_id = add_new_party(party_name)
    if party_id:
        return party_id
    else:
        print("[ERROR] Party registration failed.")
        return None


def manual_login_or_register():
    for _ in range(3):
        raw_phone = input("Phone Number (+44...): ").strip()
        user = get_user_by_phone(raw_phone)

        if user:
            print("✅ Login successful!\n")
            return user["user_id"]

        print("🚫 No user found for that phone number.")
        choice = input("Would you like to register as a new user? (yes/no): ").strip().lower()
        if choice not in ["yes", "y"]:
            print("Try again...\n")
            continue

        print("1. Join Existing Party")
        print("2. Register New Party")
        party_choice = input("Choose an option (1/2): ").strip()

        if party_choice == "1":
            parties = get_all_parties()
            print("\nAvailable Parties:")
            for i, party in enumerate(parties, 1):
                print(f"{i}. {party['party_name']} (ID: {party['party_id']})")
            selection = int(input("Choose a party by number: ").strip()) - 1
            party_id = parties[selection]["party_id"]

        elif party_choice == "2":
            party_id = register_new_party()
            if not party_id:
                continue
        else:
            print("Invalid option. Try again.")
            continue

        user_name = input("Enter your name: ").strip()
        character_name = input("Enter your character name: ").strip()
        role = input("Choose a role (e.g. Wizard, Rogue): ").strip()

        user = register_user(raw_phone, user_name)
        execute_db(
            "INSERT INTO party_membership (party_id, user_id) VALUES (?, ?)",
            (party_id, user["user_id"])
        )
        create_character_for_user(raw_phone, user["user_id"], party_id, user_name, character_name, role)

        print(f"[INFO] New user '{user_name}' and character '{character_name}' added successfully!\n")
        return user["user_id"]

    print("Too many failed attempts. Exiting.")
    return None


def choose_character(user_id):
    characters = query_db("SELECT * FROM characters WHERE user_id = ?", (user_id,))
    if not characters:
        print("[ERROR] No characters found for this user.")
        return None

    if len(characters) == 1:
        character = characters[0]
        print(f"[INFO] Auto-selected character: {character['character_name']} ({character['role']})")
    else:
        print("\nAvailable Characters:")
        for i, c in enumerate(characters, 1):
            print(f"{i}. {c['character_name']} the {c['role']} (Player name: {c['player_name']})")
        choice = int(input("Select a character by number: ").strip()) - 1
        character = characters[choice]

    return character


def choose_shop():
    shop_list = get_all_shops()

    if SHOP_NAME:
        if RuntimeFlags.DEBUG_MODE:
            print(f"[DEBUG] Attempting auto-shop entry from config: '{SHOP_NAME}'")
        matching = [shop for shop in shop_list if shop["shop_name"].lower() == SHOP_NAME.lower()]
        if matching:
            selected_shop = matching[0]
            print(f"[INFO] Auto-selected shop: {selected_shop['shop_name']}")
        else:
            print(f"[WARN] Configured shop '{SHOP_NAME}' not found. Falling back to manual selection.\n")
            selected_shop = None
    else:
        selected_shop = None

    if not selected_shop:
        print("=== Available Shops ===")
        for i, shop in enumerate(shop_list, start=1):
            print(f"{i}. {shop['shop_name']}")

        while True:
            try:
                selection = int(input("Choose a shop by number: ").strip())
                if 1 <= selection <= len(shop_list):
                    selected_shop = shop_list[selection - 1]
                    break
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(shop_list)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    shop_module = importlib.import_module(f'app.agents.personalities.{selected_shop["agent_name"].lower()}')
    agent_class = getattr(shop_module, selected_shop["agent_name"])
    agent_instance = agent_class()

    return selected_shop["shop_id"], selected_shop["shop_name"], agent_instance


def main():
    user_id = manual_login_or_register()
    if not user_id:
        return

    character = choose_character(user_id)
    if not character:
        return

    character_id = character["character_id"]
    player_name = character["player_name"]
    party_id = character["party_id"]

    result = choose_shop()
    if result is None:
        print("[FATAL] Failed to load shop. Exiting.")
        return

    shop_id, shop_name, agent = result
    increment_visit_count(party_id, shop_id)
    visit_count = get_visit_count(party_id, shop_id)
    party = get_party_by_id(party_id)

    print(f"\n=== Welcome to {agent.name}'s Shop ===")
    print(f"Party: {party['party_name']}")
    print(f"Gold: {party['party_gold']}\n")

    greeting = agent.shopkeeper_greeting(party["party_name"], visit_count, player_name)
    print(greeting)

    convo = Conversation(character_id)
    service = ConversationService(convo, agent, party_id, character_id, player_name, party, visit_count)

    while True:
        player_input = input(">> ").strip()

        if player_input.lower() in ['exit', 'quit']:
            print("Leaving the shop...")
            break

        response = service.handle(player_input)
        convo.debug("AFTER HANDLE")
        print(response)


if __name__ == '__main__':
    main()
