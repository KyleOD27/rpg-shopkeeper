# app/shop_handlers/sell_handler.py

from app.interpreter import find_item_in_input
from app.models.items import get_item_by_name
from app.models.parties import update_party_gold
from app.models.ledger import record_transaction
from app.conversation import ConversationState, PlayerIntent


class SellHandler:
    def __init__(self, convo, agent, party_id, character_id, player_name, party_data):
        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.character_id = character_id
        self.player_name = player_name
        self.party_data = party_data

    def get_dict_item(self, item_reference):
        name = str(item_reference)
        return dict(get_item_by_name(name) or {})

    def process_sell_item_flow(self, player_input):
        item_name, _ = find_item_in_input(player_input)

        if not item_name:
            self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
            return self.agent.shopkeeper_sell_enquire_item()

        self.convo.set_pending_item(item_name)
        self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)

        item = self.get_dict_item(item_name)
        offer_price = round(item.get("base_price", 0) * 0.6)
        return self.agent.shopkeeper_sell_offer_prompt(item, offer_price)

    def handle_confirm_sale(self, _):
        item_name = self.convo.pending_item
        item = self.get_dict_item(item_name)

        if not item:
            return self.agent.say("Something went wrong — I can't find that item.")

        return self.finalise_sale()

    def handle_cancel_sale(self, _):
        item_name = self.convo.pending_item
        item = self.get_dict_item(item_name)

        self.convo.reset_state()
        self.convo.set_pending_item(None)

        return self.agent.shopkeeper_sell_cancel_prompt(item)

    def finalise_sale(self):
        item_name = self.convo.pending_item
        item = self.get_dict_item(item_name)

        if not item:
            return self.agent.say("Something went wrong — I can't find that item.")

        offer_price = round(item.get("base_price", 0) * 0.6)
        name = item.get("name") or item.get("title") or item_name

        self.party_data["party_gold"] += offer_price
        update_party_gold(self.party_id, self.party_data["party_gold"])

        record_transaction(
            party_id=self.party_id,
            character_id=self.character_id,
            item_name=name,
            amount=offer_price,
            action="SELL",
            balance_after=self.party_data["party_gold"],
            details="Sold item"
        )

        self.convo.reset_state()
        self.convo.set_pending_item(None)

        return self.agent.shopkeeper_sell_success_prompt(item, offer_price)
