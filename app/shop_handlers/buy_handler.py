# app/shop_handlers/buy_handler.py

from app.interpreter import find_item_in_input, normalize_input
from app.models.items import get_item_by_name, get_all_items
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
        # If the reference is already an item (dictionary), return it directly
        if isinstance(item_reference, dict):
            return item_reference

        # Otherwise, if it's just a name (string), get the item from the DB or item list
        name = str(item_reference)
        return dict(get_item_by_name(name) or {})

    def process_buy_item_flow(self, player_input):
        raw_input = player_input.get("text", "") if isinstance(player_input, dict) else player_input
        item_name = player_input.get("item") if isinstance(player_input, dict) else None
        category = player_input.get("category") if isinstance(player_input, dict) else None

        # 🧹 Always clear pending actions
        self.convo.clear_pending()

        # 📚 No direct item or category given — Search from text input
        if not item_name and not category:
            item_matches, detected_category = find_item_in_input(raw_input, self.convo)

            if item_matches:
                # ✅ 1 Match = go straight to confirmation
                if len(item_matches) == 1:
                    item = item_matches[0]
                    self.convo.set_pending_item(item)
                    self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
                    self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
                    self.convo.save_state()
                    return self.agent.shopkeeper_buy_confirm_prompt(item, self.party_data.get("party_gold", 0))

                # 🔥 Multiple matches = ask user to pick
                self.convo.set_pending_item(item_matches)
                self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                self.convo.save_state()
                return self.agent.shopkeeper_list_matching_items(item_matches)

            elif detected_category:
                # 📂 No item, but detected a category
                self.convo.set_state(ConversationState.VIEWING_CATEGORIES)
                return self.agent.shopkeeper_show_items_by_category({"equipment_category": detected_category})

            else:
                # 🤷 No matches at all — show main categories
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                return self.agent.get_equipment_categories()

        # 📦 Direct item lookup (e.g. from structured input)
        if item_name:
            item = self.get_dict_item(item_name)
            if item:
                self.convo.set_pending_item(item)
                self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
                self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
                self.convo.save_state()
                return self.agent.shopkeeper_buy_confirm_prompt(item, self.party_data.get("party_gold", 0))

        # 🛑 Should never get here, fallback if missing
        self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
        return self.agent.get_equipment_categories()

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
        # Ensure that pending_item contains the correct information
        item = self.convo.get_pending_item()  # This should return a dictionary with item details

        if not item:
            return self.agent.shopkeeper_say("Something went wrong — I can't find that item in stock. (handle_confirm)")

        # Log the full item to debug if needed
        self.convo.debug(f"Item details: {item}")

        # If item is a dictionary, you can access item_name or item_id for the purchase process
        item_name = item.get("item_name")  # or item.get("item_id") if needed
        if not item_name:
            return self.agent.shopkeeper_say("Item name not found in pending item. (handle_confirm)")

        # Finalize purchase
        response = self.finalise_purchase()

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
        item = self.convo.get_pending_item()  # This should now be a full item dictionary

        if not item:
            return self.agent.say("Something went wrong — I can't find that item in stock.")

        discount_price = self.convo.discount
        base_price = item.get("base_price", 0)
        cost = discount_price if discount_price is not None else base_price
        name = item.get("item_name") or item.get("title") or "Unknown Item"

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

        self.convo.reset_state()
        self.convo.set_pending_item(None)
        self.convo.set_discount(None)
        self.convo.set_state(ConversationState.AWAITING_ACTION)
        self.convo.save_state()

        return self.agent.shopkeeper_buy_success_prompt(item, cost)

    def handle_buy_confirm(self, player_input):
        return self.handle_confirm_purchase(player_input)

    def process_item_selection(self, player_input):
        selection = player_input.get("text", "").strip()
        pending_items = self.convo.get_pending_item()

        if not pending_items:
            self.convo.reset_state()
            self.convo.set_pending_item(None)
            return self.agent.shopkeeper_fallback_prompt()

        if isinstance(pending_items, list):  # Ensure it's a list of items
            selected_item = next(
                (item for item in pending_items if
                 str(item.get("item_id")) == selection or normalize_input(item["item_name"]) == selection),
                None
            )
        else:
            selected_item = pending_items  # Directly use the single item if not a list

        if not selected_item:
            return self.agent.shopkeeper_say(
                "I couldn't find that item in the options. Please say the full item name or ID."
            )

        # ✅ Found the selected item clearly!
        self.convo.set_pending_item(selected_item)  # Make sure it's the correct full item object
        self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
        self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
        self.convo.save_state()

        return self.agent.shopkeeper_buy_confirm_prompt(
            selected_item, self.party_data.get("party_gold", 0)
        )








