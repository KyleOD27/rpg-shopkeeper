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
from config import DEBUG_MODE, SHOP_NAME

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
    if DEBUG_MODE and SHOP_NAME:
        shop_name = SHOP_NAME
        print(f"[DEBUG] Loading shop from config: {shop_name}")
    else:
        shop_names = get_shop_names()
        print("=== Available Shops ===")
        for name in shop_names:
            print(f"- {name}")
        player_input = input("Which shop would you like to visit?: ")
        shop_name = choose_shop_via_gpt(player_input)

    all_shops = get_all_shops()
    shop = next((s for s in all_shops if s["shop_name"] == shop_name), None)

    if not shop:
        print(f"[ERROR] Configured shop '{shop_name}' not found in known list.")
        return None

    shop_module = importlib.import_module(f'app.agents.personalities.{shop["agent_name"].lower()}')
    agent_class = getattr(shop_module, shop["agent_name"])
    agent_instance = agent_class()

    return shop["shop_id"], shop["shop_name"], agent_instance


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
