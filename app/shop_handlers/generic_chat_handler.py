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

    def handle_next_page(self, _input):
        category = self.convo.metadata.get("current_category")
        if not category:
            return self.agent.shopkeeper_generic_say("Next what? I’m not sure what you’re looking at!")

        current_page = self.convo.metadata.get("current_page", 1)
        next_page = current_page + 1

        self.convo.metadata["current_page"] = next_page
        self.convo.save_state()

        return self.agent.shopkeeper_show_items_by_category({
            "category": category,
            "page": next_page
        })

    def handle_previous_page(self, _input):
        category = self.convo.metadata.get("current_category")
        if not category:
            return self.agent.shopkeeper_view_items_prompt()

        current_page = self.convo.metadata.get("current_page", 1)
        new_page = max(current_page - 1, 1)

        self.convo.metadata["current_page"] = new_page
        self.convo.save_state()

        return self.agent.shopkeeper_show_items_by_category({
            "category": category,
            "page": new_page
        })

    def handle_confirm(self, player_input):
        # Generic fallback if no special confirmation handler was active
        return self.agent.shopkeeper_generic_say("Thanks for confirming!")

    def handle_cancel(self, player_input):
        return self.agent.shopkeeper_generic_say("Alright, I’ve cancelled that action.")
