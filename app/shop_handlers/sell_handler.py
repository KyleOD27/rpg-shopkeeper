from app.interpreter import find_item_in_input
from app.models.items import get_item_by_name
from app.models.parties import update_party_gold
from app.models.ledger import record_transaction
from app.conversation import ConversationState


class SellHandler:
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

    def process_sell_item_flow(self, player_input):
        item_name, _ = find_item_in_input(player_input)
        item = self.get_dict_item(item_name)

        if not item:
            return "I can't buy that, sorry. Doesn’t look familiar."

        # Save item and set next state
        self.convo.set_pending_item(item_name)
        self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)

        offer_price = item.get("sell_price") or round(item.get("base_price", 0) * 0.5)
        return self.agent.shopkeeper_sell_offer_prompt(item_name, offer_price)

    def handle_confirm_sale(self, _):
        item_name = self.convo.pending_item
        item = self.get_dict_item(item_name)

        if not item:
            return "Something went wrong — I can't find that item."

        offer_price = item.get("sell_price") or round(item.get("base_price", 0) * 0.5)

        # 💰 Increase party gold
        self.party_data["party_gold"] += offer_price
        update_party_gold(self.party_id, self.party_data["party_gold"])

        # 🧾 Record the transaction
        record_transaction(
            party_id=self.party_id,
            player_id=self.player_id,
            item_name=item_name,
            amount=offer_price,
            action="SELL",
            balance_after=self.party_data["party_gold"],
            details=f"{self.player_name} sold an item"
        )

        # 🧹 Clean up state
        self.convo.reset_state()
        self.convo.set_pending_item(None)

        return self.agent.shopkeeper_sell_success_prompt(item_name, offer_price)

    def handle_cancel_sale(self, _):
        item_name = self.convo.pending_item
        self.convo.reset_state()
        self.convo.set_pending_item(None)
        return self.agent.shopkeeper_sell_cancel_prompt(item_name)
