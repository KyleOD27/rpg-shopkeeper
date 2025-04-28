import pytest
import copy
from app.conversation import ConversationState, PlayerIntent
from app.shop_handlers.buy_handler import BuyHandler
from app.agents.shopkeeper_agent import BaseShopkeeper  # <-- assuming you have a dummy agent to reply (or fake one for tests)

@pytest.fixture
def setup_conversation():
    # Setup fake convo and agent
    class DummyConversation:
        def __init__(self):
            self.character_id = 1
            self.state = ConversationState.AWAITING_ITEM_SELECTION
            self.pending_action = None
            self.pending_item = None
            self.metadata = {}
            self.discount = None
            self.item = None
            self.normalized_input = None

        def set_pending_item(self, item):
            self.pending_item = item

        def set_pending_action(self, action):
            self.pending_action = action

        def set_state(self, state):
            self.state = state

        def save_state(self):
            pass

        def reset_state(self):
            self.state = ConversationState.INTRODUCTION

        # ✅ ADD THIS:
        def debug(self, message):
            # Just a silent pass or print(message) if you want
            pass

    # Dummy agent that just returns static text
    class DummyAgent:
        def shopkeeper_buy_confirm_prompt(self, item, gold):
            return f"Ready to buy {item['item_name']} for {gold}g?"

        def shopkeeper_buy_success_prompt(self, item, cost):
            return f"Success buying {item['item_name']} for {cost}g!"

        def shopkeeper_buy_failure_prompt(self, item, reason, gold):
            return f"Failed to buy {item['item_name']}: {reason}"

        def shopkeeper_fallback_prompt(self):
            return "Fallback"

        def shopkeeper_say(self, message):
            return message

    convo = DummyConversation()
    agent = DummyAgent()
    party_data = {
        "party_gold": 100  # Start with 100 gold
    }
    return convo, agent, party_data

def test_buy_and_confirm_success(setup_conversation):
    convo, agent, party_data = setup_conversation
    handler = BuyHandler(convo, agent, party_id=1, player_id=1, player_name="TestPlayer", party_data=party_data)

    # Simulate item selection
    selected_item = {
        "item_id": 64,
        "item_name": "Club",
        "equipment_category": "Weapon",
        "base_price": 10,
        "price_unit": "gp",
        "weight": 2.0,
        "rarity": "Common"
    }
    convo.item = copy.deepcopy(selected_item)
    convo.set_pending_item(copy.deepcopy(selected_item))
    convo.set_pending_action(PlayerIntent.BUY_ITEM)
    convo.set_state(ConversationState.AWAITING_CONFIRMATION)

    # Simulate saying "yes"
    response = handler.handle_confirm_purchase({"text": "yes"})

    assert "Success buying Club" in response  # Success message
    assert party_data["party_gold"] == 90  # Gold reduced by 10
    assert convo.state == ConversationState.AWAITING_ACTION  # Conversation moved back to normal
