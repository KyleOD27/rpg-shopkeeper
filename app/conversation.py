from enum import Enum, auto
from datetime import datetime, timedelta
from app.db import get_convo_state, update_convo_state, log_convo_state
from app.config import RuntimeFlags


class PlayerIntent(Enum):
    VIEW_TOOL_SUBCATEGORY = auto()
    VIEW_GEAR_SUBCATEGORY = auto()
    VIEW_WEAPON_SUBCATEGORY = auto()
    VIEW_ARMOUR_SUBCATEGORY = auto()
    VIEW_TOOL_CATEGORY = auto()
    VIEW_ARMOUR_CATEGORY = auto()
    VIEW_GEAR_CATEGORY = auto()
    VIEW_WEAPON_CATEGORY = auto()
    VIEW_EQUIPMENT_CATEGORY = auto()
    SHOW_GRATITUDE = auto()
    VIEW_ITEMS = auto()
    BUY_ITEM = auto()
    SELL_ITEM = auto()
    DEPOSIT_GOLD = auto()
    WITHDRAW_GOLD = auto()
    CHECK_BALANCE = auto()
    VIEW_LEDGER = auto()
    CONFIRM = auto()
    CANCEL = auto()
    SMALL_TALK = auto()
    UNKNOWN = auto()
    BUY_NEEDS_ITEM = auto()
    BUY_CONFIRM = auto()
    BUY_CANCEL = auto()
    SELL_CONFIRM = auto()
    SELL_CANCEL = auto()
    SELL_NEEDS_ITEM = auto()
    DEPOSIT_NEEDS_AMOUNT = auto()
    DEPOSIT_CONFIRM = auto()
    WITHDRAW_NEEDS_AMOUNT = auto()
    WITHDRAW_CONFIRM = auto()
    BARTER = auto()
    BARTER_CONFIRM = auto()
    BARTER_CANCEL = auto()
    BARTER_NEEDS_ITEM = auto()
    GREETING = auto()
    HAGGLE = auto()
    HAGGLE_NEEDS_AMOUNT = auto()
    HAGGLE_CONFIRM = auto()
    HAGGLE_CANCEL = auto()
    NEXT = auto()
    PREVIOUS = auto()


class ConversationState(Enum):
    INTRODUCTION = "INTRODUCTION"
    AWAITING_ACTION = "AWAITING_ACTION"
    AWAITING_ITEM_SELECTION = "AWAITING_ITEM_SELECTION"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    VIEWING_CATEGORIES = "VIEWING_CATEGORIES"
    IN_TRANSACTION = "IN_TRANSACTION"


class Conversation:
    def __init__(self, character_id):
        self.character_id = character_id
        self.state = ConversationState.INTRODUCTION
        self.pending_action = None
        self.pending_item = None
        self.latest_input = None
        self.player_intent = None
        self.match_confirmed = False
        self.metadata = {}
        self.normalized_input = None
        saved = get_convo_state(self.character_id)
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

    def set_discount(self, amount):
        self.metadata["discount"] = amount

    @property
    def discount(self):
        return self.metadata.get("discount", None)

    def can_attempt_haggle(self):
        now = datetime.utcnow()
        history = self.metadata.get("haggle_history", {
            "attempts": 0,
            "success": False,
            "last_reset": now.isoformat()
        })

        last_reset = datetime.fromisoformat(history["last_reset"])
        if now - last_reset > timedelta(hours=24):
            history = {
                "attempts": 0,
                "success": False,
                "last_reset": now.isoformat()
            }

        if history["attempts"] >= 3:
            return False, "You've used all 3 haggle attempts for today."

        if history["success"]:
            return False, "No can do, you have already successfully haggled today."

        return True, None

    def record_haggle_attempt(self, success: bool):
        now = datetime.utcnow()
        history = self.metadata.get("haggle_history", {
            "attempts": 0,
            "success": False,
            "last_reset": now.isoformat()
        })

        last_reset = datetime.fromisoformat(history["last_reset"])
        if now - last_reset > timedelta(hours=24):
            history = {
                "attempts": 0,
                "success": False,
                "last_reset": now.isoformat()
            }

        history["attempts"] += 1
        if success:
            history["success"] = True

        self.metadata["haggle_history"] = history
        self.save_state()

    def save_state(self):

        def safe_name(value):
            return value.name if hasattr(value, 'name') else value

        update_convo_state(
            character_id=self.character_id,
            state=safe_name(self.state),
            action=safe_name(self.pending_action),
            item=self.pending_item
        )

        log_convo_state(
            character_id=self.character_id,
            state=self.state.value,
            action=self.pending_action,
            item=self.pending_item
        )

    def debug(self, note=None):
        if not RuntimeFlags.DEBUG_MODE:
            return
        print("[DEBUG] --- Conversation Debug Info ---")
        if note:
            print(f"Note: {note}")
        print(f"Character ID: {self.character_id}")
        print(f"State: {self.state.name}")
        print(f"Action: {self.pending_action}")
        print(f"Item: {self.pending_item or 'None'}")
        print(f"User Input: {self.latest_input if self.latest_input else 'N/A'}")
        print(f"Normalized Input: {self.normalized_input if self.normalized_input else 'N/A'}")  # 👈 Add this line!
        print(f"Player Intent: {self.player_intent.name if self.player_intent else 'N/A'}")
        print(f"Metadata: {self.metadata if self.metadata else '{}'}")
        print("--------------------------------------")

    def set_pending_action(self, action):
        self.pending_action = action
