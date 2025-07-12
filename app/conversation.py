import csv
import os
from enum import Enum, auto
from datetime import datetime, timedelta, timezone
from app.db import get_convo_state, update_convo_state, log_convo_state
from app.config import RuntimeFlags
import json
from app.utils.debug import HandlerDebugMixin

class PlayerIntent(Enum):
    VIEW_ACCOUNT = auto()
    VIEW_CHARACTER = auto()
    VIEW_PROFILE = auto()
    VIEW_MOUNT_CATEGORY = auto()
    VIEW_MOUNT_SUBCATEGORY = auto()
    VIEW_TOOL_SUBCATEGORY = auto()
    VIEW_GEAR_SUBCATEGORY = auto()
    VIEW_WEAPON_SUBCATEGORY = auto()
    VIEW_ARMOUR_SUBCATEGORY = auto()
    VIEW_TREASURE_SUBCATEGORY = auto()
    VIEW_TOOL_CATEGORY = auto()
    VIEW_ARMOUR_CATEGORY = auto()
    VIEW_GEAR_CATEGORY = auto()
    VIEW_WEAPON_CATEGORY = auto()
    VIEW_TREASURE_CATEGORY = auto()
    VIEW_EQUIPMENT_CATEGORY = auto()
    SHOW_GRATITUDE = auto()
    VIEW_ITEMS = auto()
    BUY_ITEM = auto()
    SELL_ITEM = auto()
    DEPOSIT_BALANCE = auto()
    WITHDRAW_BALANCE = auto()
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
    GOODBYE = auto()
    INSPECT_ITEM = auto()
    UNDO = auto()
    STASH_ADD = auto()
    STASH_REMOVE = auto()
    VIEW_STASH = auto()


class ConversationState(Enum):
    INTRODUCTION            = 'INTRODUCTION'
    AWAITING_ACTION         = 'AWAITING_ACTION'
    AWAITING_ITEM_SELECTION = 'AWAITING_ITEM_SELECTION'
    AWAITING_CONFIRMATION   = 'AWAITING_CONFIRMATION'
    VIEWING_CATEGORIES      = 'VIEWING_CATEGORIES'
    VIEWING_ITEMS           = 'VIEWING_ITEMS'
    IN_TRANSACTION          = 'IN_TRANSACTION'
    AWAITING_DEPOSIT_AMOUNT = 'AWAITING_DEPOSIT_AMOUNT'
    AWAITING_WITHDRAW_AMOUNT = 'AWAITING_WITHDRAW_AMOUNT'
    AWAITING_STASH_ITEM_SELECTION = 'AWAITING_STASH_ITEM_SELECTION'
    AWAITING_UNSTASH_ITEM_SELECTION = 'AWAITING_UNSTASH_ITEM_SELECTION'


class Conversation(HandlerDebugMixin):
    LOG_FILE = 'debug_log.csv'

    def __init__(self, character_id):
        # 1) Ensure CSV exists with a named header row
        if not os.path.exists(self.LOG_FILE):
            with open(self.LOG_FILE, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp (UTC)',
                    'Debug Note',
                    'Character ID',
                    'Conversation State',
                    'Pending Action',
                    'Pending Item',
                    'User Input',
                    'Normalized Input',
                    'Player Intent',
                    'Metadata'
                ])

        # 2) Now initialize your attributes
        self.character_id = character_id
        self.state = ConversationState.INTRODUCTION
        self.pending_action = None
        self.pending_item = None
        self.latest_input = None
        self.player_intent = None
        self.match_confirmed = False
        self.metadata = {}
        self.normalized_input = None
        self.item = None

        # 3) And now it’s safe to log entry/exit
        self.debug('→ Entering __init__')
        saved = get_convo_state(self.character_id)
        if saved:
            self.state = ConversationState(saved['current_state'])
            self.pending_action = saved['pending_action']
            self.pending_item = saved['pending_item'] or None
        else:
            self.save_state()
        self.debug('← Exiting __init__')


    def set_state(self, new_state: ConversationState):
        self.debug('→ Entering set_state')
        self.state = new_state
        self.save_state()
        self.debug('← Exiting set_state')

    def set_intent(self, intent: PlayerIntent):
        self.debug('→ Entering set_intent')
        self.player_intent = intent
        self.pending_action = intent.name
        self.save_state()
        self.debug('← Exiting set_intent')

    def set_pending_item(self, item):
        self.debug('→ Entering set_pending_item')
        import json
        if isinstance(item, str):
            try:
                parsed = json.loads(item)
                self.pending_item = parsed
            except json.JSONDecodeError:
                self.pending_item = item
        elif isinstance(item, dict):
            self.pending_item = item
        elif isinstance(item, list):
            self.pending_item = item
        elif item is None:
            self.pending_item = None
        else:
            raise ValueError(f'Unsupported pending_item type: {type(item)}')
        self.save_state()
        self.debug('← Exiting set_pending_item')

    def set_input(self, input_str: str):
        self.debug('→ Entering set_input')
        self.latest_input = input_str
        self.debug('← Exiting set_input')

    def clear_intent(self):
        self.debug('→ Entering clear_intent')
        self.player_intent = None
        self.pending_action = None
        self.debug('← Exiting clear_intent')

    def reset_state(self):
        self.debug('→ Entering reset_state')
        self.state = ConversationState.INTRODUCTION
        self.pending_action = None
        self.player_intent = None
        self.latest_input = None
        self.match_confirmed = False
        self.save_state()
        self.debug('← Exiting reset_state')

    def set_discount(self, amount):
        self.debug('→ Entering set_discount')
        self.metadata['discount'] = amount
        self.debug('← Exiting set_discount')

    @property
    def discount(self):
        self.debug('→ Entering discount')
        self.debug('← Exiting discount')
        return self.metadata.get('discount', None)

    def can_attempt_haggle(self):
        self.debug('→ Entering can_attempt_haggle')
        now = datetime.now(timezone.utc)
        history = self.metadata.get('haggle_history', {'attempts': 0,
            'success': False, 'last_reset': now.isoformat()})
        last_reset = datetime.fromisoformat(history['last_reset'])
        if now - last_reset > timedelta(hours=24):
            history = {'attempts': 0, 'success': False, 'last_reset': now.
                isoformat()}
        if history['attempts'] >= 3:
            return False, "You've used all 3 haggle attempts for today."
        if history['success']:
            return (False,
                'No can do, you have already successfully haggled today.')
        self.debug('← Exiting can_attempt_haggle')
        return True, None

    def record_haggle_attempt(self, success: bool):
        self.debug('→ Entering record_haggle_attempt')
        now = datetime.now(timezone.utc)
        history = self.metadata.get('haggle_history', {'attempts': 0,
            'success': False, 'last_reset': now.isoformat()})
        last_reset = datetime.fromisoformat(history['last_reset'])
        if now - last_reset > timedelta(hours=24):
            history = {'attempts': 0, 'success': False, 'last_reset': now.
                isoformat()}
        history['attempts'] += 1
        if success:
            history['success'] = True
        self.metadata['haggle_history'] = history
        self.save_state()
        self.debug('← Exiting record_haggle_attempt')
    import json
    import json

    def save_state(self):
        self.debug('→ Entering save_state')

        def safe_name(value):
            return value.name if hasattr(value, 'name') else value
        item_to_save = self.pending_item
        if isinstance(item_to_save, (dict, list)):
            item_to_save = json.dumps(item_to_save)
        update_convo_state(character_id=self.character_id, state=safe_name(
            self.state), action=safe_name(self.pending_action), item=
            item_to_save)
        log_convo_state(character_id=self.character_id, state=self.state.
            value, action=self.pending_action, item=item_to_save)
        self.debug('← Exiting save_state')

    def debug(self, note=None):
        """Print detailed conversation state and append a row to debug_log.csv."""
        if not RuntimeFlags.DEBUG_MODE:
            return

        # --- console output ---
        print('[DEBUG] --- Conversation Debug Info ---')
        if note:
            print(f'Note: {note}')
        state_obj = getattr(self, 'state', None)
        state_name = state_obj.name if state_obj else 'N/A'
        print(f'Character ID: {getattr(self, "character_id", "N/A")}')
        print(f'State: {state_name}')
        print(f'Action: {getattr(self, "pending_action", "N/A")}')
        print(f"Item: {getattr(self, 'pending_item', None) or 'None'}")
        print(f"User Input: {getattr(self, 'latest_input', None) or 'N/A'}")
        print(f"Normalized Input: {getattr(self, 'normalized_input', None) or 'N/A'}")
        pi = getattr(self, 'player_intent', None)
        print(f"Player Intent: {pi.name if pi else 'N/A'}")
        md = getattr(self, 'metadata', {}) or {}
        print(f"Metadata: {md}")
        print('--------------------------------------')

        # --- CSV output ---
        row = [
            datetime.now(timezone.utc).isoformat(),
            note or '',
            getattr(self, 'character_id', ''),
            state_name,
            getattr(self, 'pending_action', ''),
            json.dumps(self.pending_item) if self.pending_item is not None else '',
            getattr(self, 'latest_input', '') or '',  # ← user_input in row
            getattr(self, 'normalized_input', '') or '',
            pi.name if pi else '',
            json.dumps(md),
        ]
        with open(self.LOG_FILE, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def set_pending_action(self, action):
        self.debug('→ Entering set_pending_action')
        self.pending_action = action
        self.debug('← Exiting set_pending_action')

    def get_pending_item(self):
        self.debug('→ Entering get_pending_item')
        pending_item = self.metadata.get('pending_item')
        if isinstance(pending_item, str):
            import json
            pending_item = json.loads(pending_item)
        if isinstance(pending_item, list):
            if len(pending_item) == 1:
                pending_item = pending_item[0]
            else:
                pass
        self.debug('← Exiting get_pending_item')
        return pending_item

    def clear_pending(self):
        self.debug('→ Entering clear_pending')
        self.metadata['pending_item'] = None
        self.metadata['pending_action'] = None
        self.metadata['matching_items'] = []
        self.save_state()
        self.debug('← Exiting clear_pending')

    def set_pending_confirm_item(self, item_name: str):
        self.debug('→ Entering set_pending_confirm_item')
        self.pending_confirm_item = item_name
        self.debug('← Exiting set_pending_confirm_item')

    def get_pending_confirm_item(self) ->(str | None):
        self.debug('→ Entering get_pending_confirm_item')
        self.debug('← Exiting get_pending_confirm_item')
        return getattr(self, 'pending_confirm_item', None)
