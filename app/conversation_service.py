# app/conversation_service.py

from app.conversation import ConversationState, PlayerIntent
from app.interpreter import interpret_input, find_item_in_input
from app.models.items import get_item_by_name
from app.models.parties import update_party_gold
from app.models.ledger import record_transaction


class ConversationService:
    def __init__(self, convo, agent, party_id, player_id, party_data):
        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.player_id = player_id
        self.party_data = dict(party_data)
        self.intent_router = self._build_router()

    def say(self, message):
        return message

    # 🔧 Ensures sqlite3.Row becomes a dict
    def get_dict_item(self, item_reference):
        name = str(item_reference)
        return dict(get_item_by_name(name) or {})

    # 🧠 Central handler
    def handle(self, player_input):
        self.convo.set_input(player_input)
        intent_data = interpret_input(player_input)
        intent = intent_data.get("intent")
        item = intent_data.get("item")
        self.convo.set_intent(intent)

        if item:
            self.convo.set_pending_item(item)

        # Handle INTRODUCTION as a special case
        if self.convo.state == ConversationState.INTRODUCTION:
            return self.handle_introduction()

        # Try routing by (state, intent)
        handler = self.intent_router.get((self.convo.state, intent))

        if handler:
            return handler(player_input)
        else:
            return self.handle_fallback()

    # 📍 Routing table setup
    def _build_router(self):
        return {
            # BUY FLOW — with full input handling
            (ConversationState.AWAITING_ACTION, PlayerIntent.BUY_ITEM): self.process_buy_item_flow,
            (ConversationState.AWAITING_ACTION, PlayerIntent.BUY_NEEDS_ITEM): self.process_buy_item_flow,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.BUY_ITEM): self.process_buy_item_flow,
            (ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.BUY_NEEDS_ITEM): self.process_buy_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.CONFIRM): self.handle_confirm_purchase,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.CANCEL): self.handle_cancel_purchase,

            # BUY FLOW — re-try confirmation if item restated
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.BUY_ITEM): self.process_buy_item_flow,
            (ConversationState.AWAITING_CONFIRMATION, PlayerIntent.BUY_NEEDS_ITEM): self.process_buy_item_flow,
        }

    # 🧭 INTRO flow
    def handle_introduction(self):
        intent = self.convo.player_intent
        if intent in {
            PlayerIntent.VIEW_ITEMS,
            PlayerIntent.BUY_ITEM,
            PlayerIntent.SELL_ITEM,
            PlayerIntent.HAGGLE,
            PlayerIntent.CHECK_BALANCE,
            PlayerIntent.VIEW_LEDGER,
            PlayerIntent.DEPOSIT_GOLD,
            PlayerIntent.WITHDRAW_GOLD,
        }:
            self.convo.set_state(ConversationState.AWAITING_ACTION)
            return self.say("Right then, what’re you here for? Buying, selling, or just lookin'?")

        self.convo.debug("Player hasn't engaged properly yet. Staying in INTRODUCTION.")
        return self.say("Speak up, adventurer. I haven't got all day.")

    # 💬 Default backup
    def handle_fallback(self, *_):
        return self.agent.shopkeeper_fallback_prompt()

    # 🧠 Core item-handling logic
    def process_buy_item_flow(self, player_input):
        item_name, _ = find_item_in_input(player_input)

        if not item_name:
            if self.convo.state == ConversationState.AWAITING_ACTION:
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                return self.agent.shopkeeper_buy_enquire_item()
            return self.agent.shopkeeper_clarify_item_prompt()

        self.convo.set_pending_item(item_name)
        self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)

        item = self.get_dict_item(item_name)
        return self.agent.shopkeeper_buy_confirm_prompt(item, self.party_data["party_gold"])

    # ✅ Confirm purchase
    def handle_confirm_purchase(self, _):
        item_name = self.convo.pending_item
        item = self.get_dict_item(item_name)

        if not item:
            return self.say("Something went wrong — I can't find that item in stock.")

        return self.finalise_purchase()

    # ❌ Cancel purchase
    def handle_cancel_purchase(self, _):
        item_name = self.convo.pending_item
        item = self.get_dict_item(item_name)

        self.convo.reset_state()
        self.convo.set_pending_item(None)

        return self.agent.shopkeeper_buy_cancel_prompt(item)

    # 🎉 Finalise the deal
    def finalise_purchase(self):
        item_name = self.convo.pending_item
        item = self.get_dict_item(item_name)

        if not item:
            return self.say("Something went wrong — I can't find that item in stock.")

        cost = item.get("base_price", 0)
        name = item.get("name") or item.get("title") or item_name  # ✅ fallback chain

        if self.party_data["party_gold"] < cost:
            return self.agent.shopkeeper_buy_failure_prompt(item, "Not enough gold.", self.party_data["party_gold"])

        self.party_data["party_gold"] -= cost

        update_party_gold(self.party_id, self.party_data["party_gold"])  # Optional if implemented

        record_transaction(
            party_id=self.party_id,
            player_id=self.player_id,
            item_name=name,
            amount=cost,
            action="BUY"
        )

        self.convo.reset_state()
        self.convo.set_pending_item(None)

        return self.agent.shopkeeper_buy_success_prompt(item, "Purchase complete!")


