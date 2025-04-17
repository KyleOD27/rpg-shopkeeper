# cli.py

import importlib
import os
import openai
from dotenv import load_dotenv

from app.models.parties import get_party_by_id
from app.models.players import get_player_by_id
from app.models.visits import get_visit_count, increment_visit_count
from app.models.shops import get_all_shops, get_shop_names
from app.system_agent import choose_shop_via_gpt
from app.conversation import Conversation
from app.conversation_service import ConversationService
from config import DEBUG_MODE, SHOP_NAME, DEFAULT_PLAYER_NAME

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Static Context
party_id = 'group_001'
player_id = 1
player = get_player_by_id(player_id)
player_name = DEFAULT_PLAYER_NAME

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