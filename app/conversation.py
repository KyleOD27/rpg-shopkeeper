# app/conversation.py

from enum import Enum, auto
from app.db import get_convo_state, update_convo_state, log_convo_state
from config import DEBUG_MODE


class PlayerIntent(Enum):
    VIEW_ITEMS = auto()
    BUY_ITEM = auto()
    SELL_ITEM = auto()
    DEPOSIT_GOLD = auto()
    WITHDRAW_GOLD = auto()
    CHECK_BALANCE = auto()
    VIEW_LEDGER = auto()
    HAGGLE = auto()
    CONFIRM = auto()
    CANCEL = auto()
    SMALL_TALK = auto()
    UNKNOWN = auto()
    BUY_NEEDS_ITEM = auto()  # “Buy” with no item mentioned


class ConversationState(Enum):
    INTRODUCTION = "INTRODUCTION"
    AWAITING_ACTION = "AWAITING_ACTION"
    AWAITING_ITEM_SELECTION = "AWAITING_ITEM_SELECTION"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    IN_TRANSACTION = "IN_TRANSACTION"


class Conversation:
    def __init__(self, player_id):
        self.player_id = player_id
        self.state = ConversationState.INTRODUCTION
        self.pending_action = None
        self.pending_item = None
        self.latest_input = None
        self.player_intent = None
        self.match_confirmed = False  # Used for confirmation flow

        saved = get_convo_state(self.player_id)
        if saved:
            self.state = ConversationState(saved["current_state"])
            self.pending_action = saved["pending_action"]
            self.pending_item = saved["pending_item"] if saved["pending_item"] else None
        else:
            self.save_state()

    def set_state(self, new_state: ConversationState):
        self.state = new_state
        self.save_state()

    def set_intent(self, intent: PlayerIntent):
        self.player_intent = intent
        self.pending_action = intent.name
        self.save_state()

    def set_pending_item(self, item):
        if isinstance(item, str):
            self.pending_item = item
        elif isinstance(item, dict):
            self.pending_item = item.get("item_name")
        elif item is None:
            self.pending_item = None
        else:
            self.pending_item = str(item)
        self.save_state()

    def set_input(self, input_str: str):
        self.latest_input = input_str

    def clear_intent(self):
        self.player_intent = None
        self.pending_action = None

    def reset_state(self):
        self.state = ConversationState.INTRODUCTION
        self.pending_action = None
        self.player_intent = None
        self.latest_input = None
        self.match_confirmed = False
        self.save_state()

    def save_state(self):
        update_convo_state(
            player_id=self.player_id,
            state=self.state.value,
            action=self.pending_action,
            item=self.pending_item
        )
        log_convo_state(
            player_id=self.player_id,
            state=self.state.value,
            action=self.pending_action,
            item=self.pending_item
        )

    def debug(self, note=None):
        if not DEBUG_MODE:
            return
        print("[DEBUG] --- Conversation Debug Info ---")
        if note:
            print(f"Note: {note}")
        print(f"Player ID: {self.player_id}")
        print(f"State: {self.state.name}")
        print(f"Action: {self.pending_action}")
        print(f"Item: {self.pending_item or 'None'}")
        print(f"User Input: {self.latest_input if self.latest_input else 'N/A'}")
        print(f"Player Intent: {self.player_intent.name if self.player_intent else 'N/A'}")
        print("--------------------------------------")
