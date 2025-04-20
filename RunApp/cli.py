# cli.py

import importlib
import os
import openai
from dotenv import load_dotenv

from app.models.parties import get_party_by_id, get_all_parties, add_new_party
from app.models.players import (
    get_player_id_by_name,
    get_player_by_id,
    get_player_name_by_id,
    validate_login_credentials,
    add_player_to_party
)
from app.models.visits import get_visit_count, increment_visit_count
from app.models.shops import get_all_shops, get_shop_names
from app.system_agent import choose_shop_via_gpt
from app.conversation import Conversation
from app.conversation_service import ConversationService
from config import DEBUG_MODE, SHOP_NAME, AUTO_LOGIN_NAME, AUTO_LOGIN_PIN

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


def login():
    print("=== Welcome to RPG Shopkeeper ===")

    # Config override path
    if AUTO_LOGIN_NAME and AUTO_LOGIN_PIN:
        print("[DEBUG] Attempting auto-login via config...")
        result = validate_login_credentials(AUTO_LOGIN_NAME, AUTO_LOGIN_PIN)
        print(f"[DEBUG] Validating login: name='{AUTO_LOGIN_NAME}', passcode='{AUTO_LOGIN_PIN}' => result: {result}")

        if isinstance(result, int):
            print(f"[INFO] Auto-login successful as '{AUTO_LOGIN_NAME}'\n")
            return result
        else:
            print("[WARN] Auto-login failed, falling back to manual login.\n")

    # Manual login + registration loop
    for _ in range(3):
        entered_id = input("User ID: ").strip()
        entered_pin = input("PIN: ").strip()
        print(f"[DEBUG] Entered ID: '{entered_id}', PIN: '{entered_pin}'")

        result = validate_login_credentials(entered_id, entered_pin)
        print(f"[DEBUG] Validating login: name='{entered_id}', passcode='{entered_pin}' => result: {result}")

        if isinstance(result, int):
            print("Login successful!\n")
            return result

        print("User not found or incorrect PIN.")
        choice = input("Would you like to register as a new player? (yes/no): ").strip().lower()
        if choice in ["yes", "y"]:
            print("1. Join Existing Party")
            print("2. Register New Party")
            party_choice = input("Choose an option (1/2): ").strip()

            if party_choice == "1":
                parties = get_all_parties()
                print("\nAvailable Parties:")
                for i, party in enumerate(parties, 1):
                    print(f"{i}. {party['party_name']} (ID: {party['party_id']})")
                selection = int(input("Choose a party by number: ").strip()) - 1
                selected_party = parties[selection]
                party_id = selected_party["party_id"]

            elif party_choice == "2":
                party_id = register_new_party()
                if not party_id:
                    continue
            else:
                print("Invalid option. Try again.")
                continue

            character_name = input("Enter your character name: ").strip()
            role = input("Choose a role (e.g. Wizard, Rogue): ").strip()
            add_player_to_party(party_id, entered_id, character_name, role, entered_pin)
            player_id_row = get_player_id_by_name(entered_id)
            if isinstance(player_id_row, int):
                print(f"[INFO] New player '{entered_id}' added successfully!")
                return player_id_row
            else:
                print("[ERROR] Failed to retrieve new player ID.\n")

        print("Try again...\n")

    print("Too many failed attempts. Exiting.")
    return None



def choose_shop():
    shop_list = get_all_shops()

    if SHOP_NAME:
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
    player_id = login()
    if not player_id:
        return

    player = get_player_by_id(player_id)
    player_row = get_player_name_by_id(player_id)
    player_name = player_row["player_name"] if player_row else "Adventurer"
    party_id = player["party_id"]

    result = choose_shop()
    if result is None:
        print("[FATAL] Failed to load shop. Exiting.")
        return

    shop_id, shop_name, agent = result
    increment_visit_count(party_id, shop_id)
    visit_count = get_visit_count(party_id, shop_id)
    party = get_party_by_id(party_id)

    print(f"=== Welcome to {agent.name}'s Shop ===")
    print(f"Party: {party['party_name']}")
    print(f"Gold: {party['party_gold']}\n")

    greeting = agent.shopkeeper_greeting(party["party_name"], visit_count, player_name)
    print(greeting)

    convo = Conversation(player_id)
    service = ConversationService(convo, agent, party_id, player_id, player_name, party)

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
