# app/shop_handlers/buy_handler.py

from app.interpreter import find_item_in_input
from app.models.items import get_item_by_name
from app.models.parties import update_party_gold
from app.models.ledger import record_transaction
from app.conversation import ConversationState, PlayerIntent
from app.shop_handlers.haggle_handler import HaggleHandler

class BuyHandler:
    def __init__(self, convo, agent, party_id, player_id, player_name, party_data):
        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.player_id = player_id
        self.player_name = player_name
        self.party_data = party_data

    def get_dict_item(self, item_reference):
        name = str(item_reference)
        return dict(get_item_by_name(name) or {})

    def process_buy_item_flow(self, player_input):
        raw_input = player_input.get("text", "") if isinstance(player_input, dict) else player_input
        item_name = player_input.get("item") if isinstance(player_input, dict) else None
        category = player_input.get("category") if isinstance(player_input, dict) else None

        if not item_name and not category:
            item_name, category = find_item_in_input(raw_input, self.convo)

        if category and not item_name:
            self.convo.set_state(ConversationState.VIEWING_CATEGORIES)
            return self.agent.shopkeeper_show_items_by_category({"equipment_category": category})

        if not item_name:
            if self.convo.state == ConversationState.AWAITING_ACTION:
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                return self.agent.shopkeeper_buy_enquire_item()
            return self.agent.shopkeeper_clarify_item_prompt()

        # ✅ Set pending item, pending action, and state
        self.convo.set_pending_item(item_name)
        self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
        self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
        self.convo.save_state()

        item = self.get_dict_item(item_name)
        return self.agent.shopkeeper_buy_confirm_prompt(item, self.party_data.get("party_gold", 0))

    def handle_haggle(self, player_input):
        item_name = self.convo.pending_item
        item = self.get_dict_item(item_name)

        if not item or item.get("base_price") is None:
            return self.agent.say("There's nothing to haggle over just yet.")

        if self.convo.state != ConversationState.AWAITING_CONFIRMATION:
            return self.agent.say("Let’s decide what you’re buying first, then we can haggle!")

        haggle = HaggleHandler(self.agent, self.convo, self.party_data)
        return haggle.attempt_haggle(item)

    def handle_confirm_purchase(self, player_input):
        item_name = self.convo.pending_item
        item = self.get_dict_item(item_name)

        if not item:
            return self.agent.say("Something went wrong — I can't find that item in stock.")

        response = self.finalise_purchase()

        # ✅ Reset conversation after purchase
        self.convo.set_state(ConversationState.AWAITING_ACTION)
        self.convo.save_state()

        return response

    def handle_cancel_purchase(self, player_input):
        item_name = self.convo.pending_item
        item = self.get_dict_item(item_name)

        self.convo.reset_state()
        self.convo.set_pending_item(None)
        self.convo.set_discount(None)

        self.convo.set_state(ConversationState.AWAITING_ACTION)
        self.convo.save_state()

        return self.agent.shopkeeper_buy_cancel_prompt(item)

    def finalise_purchase(self):
        item_name = self.convo.pending_item
        item = self.get_dict_item(item_name)

        if not item:
            return self.agent.say("Something went wrong — I can't find that item in stock.")

        discount_price = self.convo.discount
        base_price = item.get("base_price", 0)
        cost = discount_price if discount_price is not None else base_price
        name = item.get("name") or item.get("title") or item_name

        if self.party_data["party_gold"] < cost:
            return self.agent.shopkeeper_buy_failure_prompt(item, "Not enough gold.", self.party_data["party_gold"])

        # Deduct gold
        self.party_data["party_gold"] -= cost
        update_party_gold(self.party_id, self.party_data["party_gold"])

        # Record transaction
        discount_note = (
            f" (you saved {base_price - cost}g — discounted from {base_price}g)"
            if discount_price is not None else ""
        )

        record_transaction(
            party_id=self.party_id,
            character_id=self.player_id,
            item_name=item["item_name"],
            amount=-cost,
            action="BUY",
            balance_after=self.party_data["party_gold"],
            details=f"Purchased item{discount_note}"
        )

        # ✅ Reset conversation state after transaction
        self.convo.reset_state()
        self.convo.set_pending_item(None)
        self.convo.set_discount(None)
        self.convo.set_state(ConversationState.AWAITING_ACTION)
        self.convo.save_state()

        return self.agent.shopkeeper_buy_success_prompt(item, cost)

    def handle_buy_confirm(self, player_input):
        return self.handle_confirm_purchase(player_input)
