from app.models.ledger import get_last_transactions
from app.interpreter import get_equipment_category_from_input


class GenericChatHandler:
    def __init__(self, agent, party_data, convo, party_id):
        self.agent = agent
        self.party_data = party_data
        self.convo = convo
        self.party_id = party_id

    def handle_reply_to_greeting(self, player_input):
        return self.agent.shopkeeper_greeting(
            party_name=self.party_data["party_name"],
            visit_count=self.party_data["visit_count"],
            player_name=self.party_data["player_name"]
        )

    def handle_fallback(self, player_input):
        return self.agent.shopkeeper_fallback_prompt()

    def handle_view_ledger(self, player_input):
        raw_entries = get_last_transactions(self.party_id)
        entries = [dict(row) for row in raw_entries]
        return self.agent.shopkeeper_show_ledger(entries)

    def handle_accept_thanks(self, player_input):
        return self.agent.shopkeeper_accept_thanks()

    def handle_check_balance(self, player_input):
        current_gold = self.party_data.get("party_gold", 0)
        return self.agent.shopkeeper_check_balance_prompt(current_gold)

    def handle_view_items(self, player_input):
        if isinstance(player_input, dict) and "category" in player_input:
            return self.agent.shopkeeper_show_items_by_category(player_input["category"])

        category = get_equipment_category_from_input(player_input)
        if category:
            self.convo.metadata["current_category"] = category
            self.convo.metadata["current_page"] = 1
            self.convo.save_state()
            return self.agent.shopkeeper_show_items_by_category({"category": category, "page": 1})

        return self.agent.shopkeeper_view_items_prompt()
