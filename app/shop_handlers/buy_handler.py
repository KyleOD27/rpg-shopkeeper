# app/shop_handlers/buy_handler.py

from app.interpreter import find_item_in_input
from app.models.items import get_item_by_name
from app.models.parties import update_party_gold
from app.models.ledger import record_transaction
from app.conversation import ConversationState, PlayerIntent


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

    def handle_confirm_purchase(self, _):
        item_name = self.convo.pending_item
        item = self.get_dict_item(item_name)

        if not item:
            return self.agent.say("Something went wrong — I can't find that item in stock.")

        return self.finalise_purchase()

    def handle_cancel_purchase(self, _):
        item_name = self.convo.pending_item
        item = self.get_dict_item(item_name)

        self.convo.reset_state()
        self.convo.set_pending_item(None)

        return self.agent.shopkeeper_buy_cancel_prompt(item)

    def finalise_purchase(self):
        item_name = self.convo.pending_item
        item = self.get_dict_item(item_name)

        if not item:
            return self.agent.say("Something went wrong — I can't find that item in stock.")

        cost = item.get("base_price", 0)
        name = item.get("name") or item.get("title") or item_name

        if self.party_data["party_gold"] < cost:
            return self.agent.shopkeeper_buy_failure_prompt(item, "Not enough gold.", self.party_data["party_gold"])

        self.party_data["party_gold"] -= cost
        update_party_gold(self.party_id, self.party_data["party_gold"])

        record_transaction(
            party_id=self.party_id,
            character_id=self.player_id,  # ✅ player_id is actually character_id now
            item_name=item["item_name"],
            amount=-item["base_price"],
            action="BUY",
            balance_after=self.party_data["party_gold"],
            details="Purchased item"
        )

        self.convo.reset_state()
        self.convo.set_pending_item(None)

        return self.agent.shopkeeper_buy_success_prompt(item, "Purchase complete!")
