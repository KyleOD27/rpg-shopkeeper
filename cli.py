# cli.py

from app.models.parties import get_party_by_id
from app.models.shops import get_shop_by_id
from app.models.visits import get_visit_count, increment_visit_count
from app.system_agent import choose_shop_via_gpt, SHOP_NAMES
from app.agents.shopkeeper_agent import set_active_agent
from app.conversation import Conversation
from app.conversation_service import ConversationService
import importlib
from config import DEBUG_MODE, FORCE_SHOP_NAME, DEFAULT_SHOP_NAME
from app.agents.shopkeeper_agent import shopkeeper_greeting

from dotenv import load_dotenv
load_dotenv()
import os


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
    shop_name = DEFAULT_SHOP_NAME

    if not shop_name or shop_name not in SHOP_NAMES:
        print(f"[ERROR] Configured shop '{shop_name}' not found in known list.")
        return None

    print(f"[DEBUG] Loading shop from config: {shop_name}")
    shop_id = SHOP_NAMES.index(shop_name) + 1
    shop = get_shop_by_id(shop_id)

    shop_module = importlib.import_module(f'app.agents.personalities.{shop["agent_name"].lower()}')
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

    greeting = shopkeeper_greeting(party["party_name"], visit_count, player_name)
    print(greeting)

    # Single shared conversation and service object
    convo = Conversation(player_id)
    service = ConversationService(convo, agent, party_id, player_id, party)


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
