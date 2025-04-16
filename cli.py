# cli.py

from app.models.parties import get_party_by_id
from app.models.shops import get_shop_by_id
from app.models.visits import get_visit_count, increment_visit_count
from app.system_agent import choose_shop_via_gpt, SHOP_NAMES
from app.gpt_agent import set_active_agent
from app.engine import GameEngine
from app.conversation import Conversation
from app.conversation_service import ConversationService
import importlib
from config import DEBUG_MODE, FORCE_SHOP_NAME

from dotenv import load_dotenv
import os
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Static Context
party_id = 'group_001'
player_id = 1
player_name = 'Thistle'


def choose_shop():
    if DEBUG_MODE and FORCE_SHOP_NAME:
        shop_name = FORCE_SHOP_NAME
        print(f"[DEBUG] Auto-loading shop: {shop_name}")
    else:
        print("=== Available Shops ===")
        for name in SHOP_NAMES:
            print(f"- {name}")
        player_input = input("Which shop would you like to visit?: ")
        shop_name = choose_shop_via_gpt(player_input)

        if not shop_name:
            print("I couldn't figure out which shop you meant. Try again.")
            return choose_shop()

    if shop_name not in SHOP_NAMES:
        print(f"[ERROR] Shop '{shop_name}' not found in known list.")
        return None

    shop_id = SHOP_NAMES.index(shop_name) + 1
    shop = get_shop_by_id(shop_id)

    shop_module = importlib.import_module(f'app.agents.{shop["agent_name"].lower()}')
    agent_class = getattr(shop_module, shop["agent_name"])

    set_active_agent(shop["agent_name"])

    return shop_id, shop["shop_name"], agent_class()


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

    greeting = agent.generate_greeting(party["party_name"], visit_count, player_name)
    print(greeting)

    # Single shared conversation and service object
    convo = Conversation(player_id)
    service = ConversationService(convo, agent, party_id, player_id)

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
