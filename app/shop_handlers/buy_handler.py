# app/shop_handlers/buy_handler.py
import re

from app.interpreter import find_item_in_input, normalize_input
from app.models.items import get_item_by_name
from app.models.parties import update_party_gold
from app.models.ledger import record_transaction
from app.conversation import ConversationState, PlayerIntent
from app.shop_handlers.haggle_handler import HaggleHandler
import copy

class BuyHandler:
    def __init__(self, convo, agent, party_id, player_id, player_name, party_data):
        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.player_id = player_id
        self.player_name = player_name
        self.party_data = party_data

    def get_dict_item(self, item_reference):
        if isinstance(item_reference, dict):
            return item_reference
        return dict(get_item_by_name(str(item_reference)) or {})

    def process_buy_item_flow(self, player_input):
        raw = player_input.get("text", "") if isinstance(player_input, dict) else player_input
        item_name = player_input.get("item") if isinstance(player_input, dict) else None
        category  = player_input.get("category") if isinstance(player_input, dict) else None

        # clear any previous pending
        self.convo.clear_pending()

        if not item_name and not category:
            matches, detected_category = find_item_in_input(raw, self.convo)

            if matches:
                # single match → confirm immediately
                if len(matches) == 1:
                    item = matches[0]
                    self._stash_and_confirm(item)
                    return self.agent.shopkeeper_buy_confirm_prompt(
                        item,
                        self.party_data["party_gold"],
                        self.convo.discount
                    )

                # multiple → list them
                self.convo.set_pending_item(matches)
                self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)

                # 🆕 store canonical-name → item dict for instant lookup later
                self.convo.name_to_item = {
                    re.sub(r"[^\w\s]", "", m["item_name"].lower()).strip(): m  # canonicalise once
                    for m in matches
                }

                self.convo.save_state()
                return self.agent.shopkeeper_list_matching_items(matches)

            elif detected_category:
                self.convo.set_state(ConversationState.VIEWING_CATEGORIES)
                return self.agent.shopkeeper_show_items_by_category({
                    "equipment_category": detected_category
                })

            else:
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                return self.agent.get_equipment_categories()

        # direct structured lookup
        if item_name:
            item = self.get_dict_item(item_name)
            if item:
                self._stash_and_confirm(item)
                return self.agent.shopkeeper_buy_confirm_prompt(
                    item,
                    self.party_data["party_gold"],
                    self.convo.discount
                )

        # fallback
        self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
        return self.agent.get_equipment_categories()

    def _stash_and_confirm(self, item):
        """Put item into convo and prepare for confirmation."""
        self.convo.set_pending_item(item)
        self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
        self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)

        self.convo.save_state()


    def process_item_selection(self, player_input):
        choice = player_input.get("text", "").strip()

        # 1️⃣ strip an optional leading verb ----------------------------------
        for p in ("buy ", "get ", "select ", "take ", "pick "):
            if choice.lower().startswith(p):
                choice = choice[len(p):].lstrip()
                break
        # --------------------------------------------------------------------

        # what we remembered from the previous “🔎 Here's what I found” list
        pending = self.convo.get_pending_item()

        # 🛠  if the list is gone (e.g. after a reload) just run the usual
        #     name/ID matching logic instead of bailing back to INTRODUCTION
        if not pending:
            matches, detected_category = find_item_in_input(choice, self.convo)

            if matches:
                # single match → confirm immediately
                if len(matches) == 1:
                    item = matches[0]
                    self._stash_and_confirm(item)
                    return self.agent.shopkeeper_buy_confirm_prompt(
                        item,
                        self.party_data["party_gold"],
                        self.convo.discount,
                    )

                # multiple matches → show the list again
                self.convo.set_pending_item(matches)
                self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
                self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
                self.convo.save_state()
                return self.agent.shopkeeper_list_matching_items(matches)

            # nothing matched at all
            return self.agent.shopkeeper_say(
                "I’m not sure which item you mean. Try the full name or its ID number."
            )

        # --------------------------------------------------------------------
        # original logic when we *do* still have the pending list -------------
        norm = normalize_input(choice)
        if isinstance(pending, list):
            item = next(
                (i for i in pending
                 if str(i["item_id"]) == norm
                 or normalize_input(i["item_name"]) == norm),
                None
            )
        else:
            item = pending

        if not item:
            return self.agent.shopkeeper_say(
                "I couldn't find that item in the options. Please say the full name or ID."
            )

        # stash for final purchase + prompt
        self._stash_and_confirm(item)
        return self.agent.shopkeeper_buy_confirm_prompt(
            item,
            self.party_data["party_gold"],
            self.convo.discount,
        )

    def handle_haggle(self, player_input):
        item = self.get_dict_item(self.convo.pending_item)
        if not item or item.get("base_price") is None:
            return self.agent.shopkeeper_generic_say(
                "There's nothing to haggle over just yet."
            )
        if self.convo.state != ConversationState.AWAITING_CONFIRMATION:
            return self.agent.shopkeeper_generic_say(
                "Let’s decide what you’re buying first, then we can haggle!"
            )

        haggle = HaggleHandler(self.agent, self.convo, self.party_data)
        result = haggle.attempt_haggle(item)

        if self.convo.discount is not None:
            # ✅ Haggle success
            self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
            self.convo.set_pending_item(item)
            self.convo.set_pending_action(PlayerIntent.BUY_CONFIRM)
            self.convo.save_state()

            discounted_price = self.convo.discount or item.get("base_price", 0)
            item_name = item["item_name"]
            gold = self.party_data["party_gold"]

            return (
                f"Alright, alright, you twisted my arm.\n"
                f" \n"
                f"How about *{discounted_price}* gp for the *{item_name}*?\n"
                f" \n"
                f"Your balance is *{gold}* gp."
                f" Would you like to proceed with the purchase?"
            )

        # ❌ Haggle failed — re-offer at full price
        self.convo.set_discount(None)
        self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
        self.convo.set_pending_item(item)
        self.convo.set_pending_action(PlayerIntent.BUY_CONFIRM)
        self.convo.save_state()

        full_price = item.get("base_price", 0)
        item_name = item["item_name"]
        gold = self.party_data["party_gold"]

        return (
            f"😅 Nice try, but that price is already a bargain.\n"
            f" \n"
            f"The *{item_name}* still costs *{full_price}* gp.\n"
            f" \n"
            f"Your balance is *{gold}* gp."
            f" Would you like to proceed with the purchase?"
        )

    def handle_confirm_purchase(self, player_input):
        # pull out the one dict we stashed
        pending = self.convo.pending_item
        item = (pending[0] if isinstance(pending, list) and len(pending)==1 else
                pending if isinstance(pending, dict) else
                None)

        if not item or not item.get("item_name"):
            self.convo.debug(f"Purchase failed: no valid item. State={pending}")
            return self.agent.shopkeeper_say(
                "Something went wrong — I can't find that item in stock."
            )

        # finalize & reset state
        response = self.finalise_purchase(item)
        self.convo.reset_state()
        self.convo.set_pending_item(None)
        self.convo.set_discount(None)
        self.convo.set_state(ConversationState.AWAITING_ACTION)
        self.convo.save_state()
        return response

    def handle_cancel_purchase(self, player_input):
        item = self.get_dict_item(self.convo.pending_item)
        self.convo.reset_state()
        self.convo.set_pending_item(None)
        self.convo.set_discount(None)
        self.convo.set_state(ConversationState.AWAITING_ACTION)
        self.convo.save_state()
        return self.agent.shopkeeper_buy_cancel_prompt(item)

    def finalise_purchase(self, item):
        price = self.convo.discount if self.convo.discount is not None else item["base_price"]
        if self.party_data["party_gold"] < price:
            return self.agent.shopkeeper_buy_failure_prompt(
                item, "Not enough gold.", self.party_data["party_gold"]
            )

        # deduct & record
        self.party_data["party_gold"] -= price
        update_party_gold(self.party_id, self.party_data["party_gold"])

        saved = item["base_price"] - price
        note = f" (you saved {saved}g)" if saved>0 else ""
        record_transaction(
            party_id=self.party_id,
            character_id=self.player_id,
            item_name=item["item_name"],
            amount=-price,
            action="BUY",
            balance_after=self.party_data["party_gold"],
            details=f"Purchased item{note}"
        )

        return self.agent.shopkeeper_buy_success_prompt(item, price)

    # alias
    handle_buy_confirm = handle_confirm_purchase
