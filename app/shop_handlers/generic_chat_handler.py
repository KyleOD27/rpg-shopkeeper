from collections import ChainMap

from app.conversation import PlayerIntent, ConversationState
from app.models.ledger import get_last_transactions
from app.models.items import get_items_by_weapon_range
from app.interpreter import get_equipment_category_from_input
from app.db import get_item_details, get_connection, get_account_profile


class GenericChatHandler:
    def __init__(self, agent, party_data, convo, party_id, player_id):
        self.agent = agent
        self.party_data = party_data
        self.convo = convo
        self.party_id = party_id
        self.player_id = player_id

    def handle_reply_to_greeting(self, player_input):
        return self.agent.shopkeeper_greeting(
            party_name=self.party_data["party_name"],
            visit_count=self.party_data["visit_count"],
            player_name=self.party_data["player_name"]
        )

    def handle_fallback(self, player_input):
        return self.agent.shopkeeper_fallback_prompt()

    def handle_view_ledger(self, player_input):
        # 1) Fetch & normalise rows
        raw_entries = get_last_transactions(self.party_id)
        entries = [dict(row) for row in raw_entries]

        # 2) Cache ledger + paging info for follow-up “next / previous”
        self.convo.metadata.update({
            "current_section": "ledger",  # tells the pager we’re in Ledger view
            "current_page": 1,  # start at page 1
            "ledger_entries": entries,  # keep the list for later pages
        })
        self.convo.save_state()

        # 3) Render page 1
        return self.agent.shopkeeper_show_ledger(entries, page=1)

    def handle_accept_thanks(self, player_input):
        return self.agent.shopkeeper_accept_thanks()

    def handle_check_balance(self, player_input):
        current_gold = self.party_data.get("party_gold", 0)
        return self.agent.shopkeeper_check_balance_prompt(current_gold)


    # ─────────────────────────────────────────────────────────────
    def handle_next_page(self, _input):
        section = self.convo.metadata.get("current_section", "equipment")
        current_page = self.convo.metadata.get("current_page", 1)
        next_page = current_page + 1

        # ── Ledger paging ────────────────────────────────────────
        if section == "ledger":
            ledger_entries = self.convo.metadata.get("ledger_entries", [])
            self.convo.metadata["current_page"] = next_page
            self.convo.save_state()
            return self.agent.shopkeeper_show_ledger(ledger_entries, page=next_page)

        # ── Existing logic (mounts / items) ─────────────────────
        self.convo.metadata["current_page"] = next_page
        self.convo.save_state()

        if section == "mount":
            return self.agent.shopkeeper_show_items_by_mount_category({"page": next_page})

        category = (
                self.convo.metadata.get("current_category_range")
                or self.convo.metadata.get("current_weapon_category")
                or self.convo.metadata.get("current_armour_category")
                or self.convo.metadata.get("current_gear_category")
                or self.convo.metadata.get("current_tool_category")
        )
        if not category:
            return self.agent.shopkeeper_generic_say("Next what? I’m not sure what you’re looking at!")

        if section == "weapon":
            if self.convo.metadata.get("current_category_range"):
                return self.agent.shopkeeper_show_items_by_weapon_range(
                    {"category_range": category, "page": next_page}
                )
            return self.agent.shopkeeper_show_items_by_weapon_category(
                {"weapon_category": category, "page": next_page}
            )
        elif section == "armor":
            return self.agent.shopkeeper_show_items_by_armour_category(
                {"armour_category": category, "page": next_page}
            )
        elif section == "gear":
            return self.agent.shopkeeper_show_items_by_gear_category(
                {"gear_category": category, "page": next_page}
            )
        elif section == "tool":
            return self.agent.shopkeeper_show_items_by_tool_category(
                {"tool_category": category, "page": next_page}
            )

        return self.agent.shopkeeper_generic_say("Next what? I’m not sure what you’re looking at!")

    # ─────────────────────────────────────────────────────────────
    def handle_previous_page(self, _input):
        section = self.convo.metadata.get("current_section", "equipment")
        current_page = self.convo.metadata.get("current_page", 1)
        prev_page = max(current_page - 1, 1)

        # ── Ledger paging ────────────────────────────────────────
        if section == "ledger":
            ledger_entries = self.convo.metadata.get("ledger_entries", [])
            self.convo.metadata["current_page"] = prev_page
            self.convo.save_state()
            return self.agent.shopkeeper_show_ledger(ledger_entries, page=prev_page)

        # ── Existing logic (mounts / items) ─────────────────────
        self.convo.metadata["current_page"] = prev_page
        self.convo.save_state()

        if section == "mount":
            return self.agent.shopkeeper_show_items_by_mount_category({"page": prev_page})

        category = (
                self.convo.metadata.get("current_category_range")
                or self.convo.metadata.get("current_weapon_category")
                or self.convo.metadata.get("current_armour_category")
                or self.convo.metadata.get("current_gear_category")
                or self.convo.metadata.get("current_tool_category")
        )
        if not category:
            return self.agent.shopkeeper_generic_say("Previous what? I’m not sure what you’re looking at!")

        if section == "weapon":
            if self.convo.metadata.get("current_category_range"):
                return self.agent.shopkeeper_show_items_by_weapon_range(
                    {"category_range": category, "page": prev_page}
                )
            return self.agent.shopkeeper_show_items_by_weapon_category(
                {"weapon_category": category, "page": prev_page}
            )
        elif section == "armor":
            return self.agent.shopkeeper_show_items_by_armour_category(
                {"armour_category": category, "page": prev_page}
            )
        elif section == "gear":
            return self.agent.shopkeeper_show_items_by_gear_category(
                {"gear_category": category, "page": prev_page}
            )
        elif section == "tool":
            return self.agent.shopkeeper_show_items_by_tool_category(
                {"tool_category": category, "page": prev_page}
            )

        return self.agent.shopkeeper_generic_say("Previous what? I’m not sure what you’re looking at!")

    def handle_confirm(self, player_input):
        # Generic fallback if no special confirmation handler was active
        return self.agent.shopkeeper_generic_say("Thanks for confirming!")

    def handle_cancel(self, player_input):
        return self.agent.shopkeeper_generic_say("Alright, I’ve cancelled that action.")

    def handle_farewell(self, player_input):
        return self.agent.shopkeeper_farewell()

    # ---------------------------------------------------------------------
    # 📄  View profile / account / character – now all one prompt
    # ---------------------------------------------------------------------

    def handle_view_profile(self, player_input=None):
        """
        Show the full profile (account + current party data).

        • Pull the account row.
        • Merge it with the party-session snapshot.
        • Stash the characters list so the user can still choose “1 / 2 / 3…”.
        """

        acct = get_account_profile(self.player_id)  # DB call
        full_profile = dict(ChainMap(self.party_data, acct))  # acct wins if keys collide

        # keep the numeric-selection workflow alive
        self.convo.set_pending_item(full_profile.get("characters", []))
        self.convo.set_pending_action(PlayerIntent.VIEW_CHARACTER)
        self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
        self.convo.save_state()

        return self.agent.shopkeeper_show_profile(full_profile)

    def handle_view_character(self, char_dict):
        """
        After the player replies “1”, “2”, … send the selected character
        _through the same_ profile prompt. The unified viewer is robust
        enough to print either a bare character dict or the merged account.
        """
        return self.agent.shopkeeper_show_profile(char_dict)

    # …and delete these now-obsolete entry points:
    #     • handle_view_account
    #     • (old) handle_view_profile that only showed party_data
    # ---------------------------------------------------------------------


