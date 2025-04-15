# cli.py

from app.models.parties import get_party_by_id
from app.models.shops import get_shop_by_id
from app.models.visits import get_visit_count, increment_visit_count
from app.system_agent import choose_shop_via_gpt, SHOP_NAMES
from app.gpt_agent import set_active_agent
from app.engine import GameEngine
from app.conversation import Conversation
import importlib

from dotenv import load_dotenv
import os
import openai

load_dotenv()  # Load variables from .env into environment
openai.api_key = os.getenv("OPENAI_API_KEY")


# Static Context
party_id = 'group_001'
player_id = 1
player_name = 'Thistle'


def choose_shop():
    print("=== Available Shops ===")
    for name in SHOP_NAMES:
        print(f"- {name}")

    player_input = input("Which shop would you like to visit?: ")

    chosen_shop_name = choose_shop_via_gpt(player_input)
    if not chosen_shop_name:
        print("I couldn't figure out which shop you meant. Try again.")
        return choose_shop()

    shop_id = SHOP_NAMES.index(chosen_shop_name) + 1
    shop = get_shop_by_id(shop_id)

    shop_module = importlib.import_module(f'app.agents.{shop["agent_name"].lower()}')
    agent_class = getattr(shop_module, shop["agent_name"])

    set_active_agent(shop["agent_name"])

    return shop_id, shop['shop_name'], agent_class()


def main():
    shop_id, shop_name, agent = choose_shop()
    increment_visit_count(party_id, shop_id)
    visit_count = get_visit_count(party_id, shop_id)
    party = get_party_by_id(party_id)

    print(f"=== Welcome to {agent.name}'s Shop ===")
    print(f"Party: {party['party_name']}")
    print(f"Gold: {party['party_gold']}\n")

    greeting = agent.generate_greeting(party['party_name'], visit_count, player_name)
    print(greeting)

    # Load / Resume Conversation
    convo = Conversation(player_id)
    game_engine = GameEngine(party_id, player_id, agent)

    while True:
        player_input = input(">> ").strip()

        if player_input.lower() in ['exit', 'quit']:
            print("Leaving the shop...")
            break

        # Show debug state for development
        convo.debug()

        # Pass input to engine
        game_engine.handle_player_input(player_input, player=party, convo=convo)


if __name__ == '__main__':
    main()
