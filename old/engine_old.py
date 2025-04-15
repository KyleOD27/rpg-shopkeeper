from app.models.items import get_all_items
from app.models.parties import get_party_by_id
from app.models.ledger import get_last_transactions
from app.shop import buy_item, sell_item, deposit_gold, withdraw_gold, haggle
from app.conversation import ConversationManager, ConversationState, PlayerIntent
from app.interpreter import interpret_input, find_item_in_input
from app.gpt_agent import generate_agent_reply

convo = ConversationManager()


class GameEngine:
    def __init__(self, party_id, player_id, agent):
        self.party_id = party_id
        self.player_id = player_id
        self.agent = agent

    def handle_player_input(self, player_input: str):
        # DM Commands
        if convo.is_dm_command(player_input):
            self.handle_dm_command(player_input)
            return

        # Handle Confirmation
        if convo.state == ConversationState.AWAITING_CONFIRMATION:
            interpretation = interpret_input(player_input)
            if interpretation["intent"] == "CONFIRM":
                self.execute_pending_action()
                convo.reset_state()
                return
            elif interpretation["intent"] == "CANCEL":
                self.agent_says("Transaction cancelled.")
                convo.reset_state()
                return
            else:
                self.agent_says("Hmm? Just a simple yes or no will do.")
                return

        # Detect Intent
        intent = convo.handle_input(player_input)
        if intent is None:
            return  # DM command already handled

        if intent == PlayerIntent.VIEW_ITEMS:
            self.list_items()
        elif intent == PlayerIntent.CHECK_BALANCE:
            party = get_party_by_id(self.party_id)
            self.agent_says(f"Your party has {party['party_gold']} gold.")
        elif intent == PlayerIntent.VIEW_LEDGER:
            self.print_ledger()

        elif intent == PlayerIntent.BUY_ITEM:
            item_name, suggestions = find_item_in_input(player_input)
            if suggestions:
                suggestion_text = "\n".join(f"- {item}" for item in suggestions)
                self.agent_says(f"Did you mean one of these?\n{suggestion_text}\nType the item name you'd like to buy.")
                return
            elif item_name:
                convo.pending_action = 'buy'
                convo.pending_item = item_name
                item_price = next(item['base_price'] for item in get_all_items() if item['item_name'].lower() == item_name.lower())
                self.agent_says(f"Ah, {item_name}? That'll be {item_price} gold. Deal or no deal?")
                convo.state = ConversationState.AWAITING_CONFIRMATION
            else:
                self.agent_says("I can't tell what you're trying to buy. Try using the full item name.")

        else:
            # Fallback to GPT
            result = generate_agent_reply(player_input)
            if result["type"] == "text":
                self.agent_says(result["data"])

    def execute_pending_action(self):
        if convo.pending_action == 'buy':
            response = buy_item(self.party_id, self.player_id, convo.pending_item)
            self.agent_says(response["message"])
            if response.get("success"):
                cost = response.get("cost", 0)
                party = get_party_by_id(self.party_id)
                print(f"[-{cost} Gold] [+1 {convo.pending_item}] Party Gold: {party['party_gold']}")

    def list_items(self):
        items = get_all_items()
        print("\n=== Shop Items ===")
        for item in items:
            print(f"{item['item_name']} - {item['base_price']} gold - {item['rarity']}")
        print()

    def print_ledger(self):
        transactions = get_last_transactions(self.party_id)
        if not transactions:
            self.agent_says("Hah! No transactions yet.")
            return

        print("\n=== Recent Transactions ===")
        for t in transactions:
            print(f"{t['timestamp']} | {t['action']} | {t['item_name'] or ''} | {t['amount']} gold | Balance After: {t['balance_after']} | {t['details']}")
        print()

    def handle_dm_command(self, command):
        if command.lower().startswith("dm add_gold"):
            try:
                _, _, amount_str = command.strip().split()
                amount = int(amount_str)
                party = get_party_by_id(self.party_id)
                new_gold = party['party_gold'] + amount
                from app.models.parties import update_party_gold
                update_party_gold(self.party_id, new_gold)
                self.agent_says(f"Ah, fresh gold in your pockets, eh? Party gold is now {new_gold}.")
            except Exception as e:
                self.agent_says(f"DM command failed: {str(e)}")

    def agent_says(self, message):
        print(self.agent.reply(message))
