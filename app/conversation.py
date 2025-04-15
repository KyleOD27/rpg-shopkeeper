# app/conversation.py

from enum import Enum, auto
from app.db import get_convo_state, update_convo_state, log_convo_state

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
    BUY_NEEDS_ITEM = auto()  # edge case: user said "buy" but gave no item

class ConversationState(Enum):
    INTRODUCTION = "INTRODUCTION"
    AWAITING_ITEM_SELECTION = "AWAITING_ITEM_SELECTION"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"

class Conversation:
    def __init__(self, player_id):
        self.player_id = player_id
        self.state = ConversationState.INTRODUCTION
        self.pending_action = None
        self.pending_item = None

        saved = get_convo_state(self.player_id)
        if saved:
            self.state = ConversationState(saved["current_state"])
            self.pending_action = saved["pending_action"]
            self.pending_item = saved["pending_item"]
        else:
            self.save_state()

    def set_state(self, new_state: ConversationState):
        self.state = new_state
        self.save_state()

    def set_intent(self, intent: PlayerIntent):
        self.pending_action = intent.name
        self.save_state()

    def set_pending_item(self, item):
        if item is None:
            self.pending_item = None
        else:
            self.pending_item = item['item_name']
        self.save_state()

    def reset_state(self):
        self.state = ConversationState.INTRODUCTION
        self.pending_action = None
        self.pending_item = None
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

    def debug(self):
        print(f"[DEBUG] State: {self.state.name} | Action: {self.pending_action} | Item: {self.pending_item}")
