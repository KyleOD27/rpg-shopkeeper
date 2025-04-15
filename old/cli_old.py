# cli.py

from app.shop import buy_item, sell_item, haggle, deposit_gold, withdraw_gold
from app.models.items import get_all_items
from app.models.parties import get_party_by_id
from app.models.ledger import get_last_transactions
from app.models.shops import get_all_shops, get_shop_by_id
from app.models.visits import get_visit_count, increment_visit_count
from app.gpt_agent import set_active_agent, generate_agent_reply
from app.system_agent import choose_shop_via_gpt, SHOP_NAMES
from app.conversation import ConversationManager, PlayerIntent, ConversationState

import importlib

party_id = 'group_001'
player_id = 1  # Thistle
player_name = 'Thistle'

convo = ConversationManager()
convo.pending_item = None  # Ensure this exists for item handling

def choose_shop():
    print("=== Available Shops ===")
    for name in SHOP_NAMES:
        print(f"- {name}")

    player_input = input("Which shop would you like to visit?: ")

    chosen_shop_name = choose_shop_via_gpt(player_input)

    if not chosen_shop_name:
        print("I couldn't figure out which shop you meant. Try again.")
        return choose_shop()

    shop = get_shop_by_id(SHOP_NAMES.index(chosen_shop_name) + 1)

    agent_module = importlib.import_module(f'app.agents.{shop["agent_name"].lower()}')
    agent_class = getattr(agent_module, shop["agent_name"])

    set_active_agent(shop["agent_name"])

    return shop, agent_class()

def list_items():
    items = get_all_items()
    print("\n=== Shop Items ===")
    for item in items:
        print(f"{item['item_name']} - {item['base_price']} gold - {item['rarity']}")
    print()

def print_help():
    print("""
Available Commands:
- items
- buy <item name>
- sell <item name> <value>
- deposit <amount>
- withdraw <amount>
- check balance
- ledger
- exit
    """)

def main():
    shop, agent = choose_shop()

    shop_id = SHOP_NAMES.index(shop['shop_name']) + 1
    increment_visit_count(party_id, shop_id)

    party = get_party_by_id(party_id)
    visit_count = get_visit_count(party_id, shop_id)

    print(f"=== Welcome to {agent.name}'s Shop ===")
    print(f"Party: {party['party_name']}")
    print(f"Gold: {party['party_gold']}")

    greeting = agent.generate_greeting(party['party_name'], visit_count, player_name)
    print(greeting)

    unknown_counter = 0

    def agent_says(message):
        print(agent.reply(message))

    while True:
        player_input = input(">> ").strip().lower()

        if player_input in ['exit', 'quit']:
            agent_says("Off with ye then!")
            break

        intent = convo.handle_input(player_input)

        if intent == PlayerIntent.BUY_ITEM:
            if convo.pending_item:
                response = buy_item(party_id, player_id, convo.pending_item)
                agent_says(response["message"])
                print(f"[-{response['amount']} Gold] [+1 {convo.pending_item}]")
                convo.state = ConversationState.AWAITING_ACTION
                convo.pending_intent = None
                convo.pending_item = None
                continue

        if intent == PlayerIntent.VIEW_ITEMS:
            unknown_counter = 0
            list_items()
            continue

        if intent == PlayerIntent.CHECK_BALANCE:
            unknown_counter = 0
            party = get_party_by_id(party_id)
            agent_says(f"Your party has {party['party_gold']} gold.")
            continue

        if intent == PlayerIntent.VIEW_LEDGER:
            unknown_counter = 0
            transactions = get_last_transactions(party_id)
            if not transactions:
                agent_says("Hah! No transactions yet.")
                continue

            print("\n=== Recent Transactions ===")
            for t in transactions:
                print(f"{t['timestamp']} | {t['action']} | {t['item_name'] or ''} | {t['amount']} gold | Balance After: {t['balance_after']} | {t['details']}")
            print()
            continue

        if intent == PlayerIntent.UNKNOWN:
            unknown_counter += 1
            if unknown_counter >= 2:
                print_help()
                agent_says("Lost are ye? Here's what ye can ask for.")
            else:
                agent_says(generate_agent_reply(player_input)["data"])
            continue

        unknown_counter = 0
        result = generate_agent_reply(player_input)

        if result["type"] == "text":
            agent_says(result["data"])

        elif result["type"] == "command":
            command = result["data"]

            action = command.get("action")
            item = command.get("item")
            amount = command.get("amount")

            if action == "buy":
                convo.pending_item = item
                response = buy_item(party_id, player_id, item)
                agent_says(response["message"])
                print(f"[Transaction Complete: -{response['cost']} Gold | +1 {item}]")

            elif action == "sell":
                response = sell_item(party_id, player_id, item, amount)
                agent_says(response["message"])

            elif action == "deposit":
                response = deposit_gold(party_id, player_id, amount)
                agent_says(response["message"])

            elif action == "withdraw":
                response = withdraw_gold(party_id, player_id, amount)
                agent_says(response["message"])

            elif action == "check_balance":
                party = get_party_by_id(party_id)
                agent_says(f"Your party has {party['party_gold']} gold.")

            elif action == "ledger":
                transactions = get_last_transactions(party_id)
                if not transactions:
                    agent_says("Hah! No transactions yet.")
                    continue

                print("\n=== Recent Transactions ===")
                for t in transactions:
                    print(f"{t['timestamp']} | {t['action']} | {t['item_name'] or ''} | {t['amount']} gold | Balance After: {t['balance_after']} | {t['details']}")
                print()

            else:
                agent_says("Eh? I don't understand what you're after.")

if __name__ == '__main__':
    main()