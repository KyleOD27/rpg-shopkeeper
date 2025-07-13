from __future__ import annotations

from typing import Callable, Dict, Tuple, Any
from app.interpreter import interpret_input, normalize_input, find_item_in_input
from app.models.parties import get_party_balance_cp
from app.models.visits import touch_visit
from app.shop_handlers.buy_handler import BuyHandler
from app.shop_handlers.sell_handler import SellHandler
from app.shop_handlers.deposit_handler import DepositHandler
from app.shop_handlers.withdraw_handler import WithdrawHandler
from app.shop_handlers.generic_chat_handler import GenericChatHandler
from app.shop_handlers.inspect_handler import InspectHandler
from app.shop_handlers.view_handler import ViewHandler
from commands.dm_commands import handle_dm_command
from commands.admin_commands import handle_admin_command
from app.conversation import ConversationState, PlayerIntent
from app.utils.debug import HandlerDebugMixin
from app.keywords import CONFIRMATION_WORDS, CANCELLATION_WORDS
from app.shop_handlers.stash_handler import StashHandler

import json
from json import JSONDecodeError


CATEGORY_MAPPING = {    PlayerIntent.VIEW_ARMOUR_CATEGORY: ('armour_category', 'Armor'),
                        PlayerIntent.VIEW_WEAPON_CATEGORY: ('weapon_category', 'Weapon'),
                        PlayerIntent.VIEW_GEAR_CATEGORY: ('gear_category', 'Adventuring Gear'),
                        PlayerIntent.VIEW_TOOL_CATEGORY: ('tool_category', 'Tools'),
                        PlayerIntent.VIEW_TREASURE_CATEGORY: ('current_section', 'treasure'),
                        PlayerIntent.VIEW_EQUIPMENT_CATEGORY: ('current_section', 'equipment')}


class ConversationService(HandlerDebugMixin):
    def __init__(self,
                 convo,
                 agent,
                 party_id,
                 player_id,
                 player_name,
                 character_id,
                 character_name,
                 party_data,
                 visit_count):
        # wire up debug proxy
        self.conversation = convo
        self.debug('→ Entering __init__')
        # also keep the old reference if you use it elsewhere
        self.convo = convo

        # assign core identifiers
        self.agent = agent
        self.party_id = party_id
        self.player_id = player_id
        self.character_id = character_id
        self.character_name = character_name

        # build party_data context
        self.party_data = dict(party_data)
        self.party_data['player_name'] = player_name
        self.party_data['character_id'] = character_id
        self.party_data['character_name'] = character_name
        self.party_data['visit_count'] = visit_count

        # initialize handlers with updated context
        self.buy_handler = BuyHandler(
            convo,
            agent,
            party_id,
            player_id,
            player_name,
            self.party_data
        )
        self.sell_handler = SellHandler(
            convo,
            agent,
            party_id,
            player_id,
            player_name,
            self.party_data
        )
        self.deposit_handler = DepositHandler(
            convo,
            agent,
            party_id,
            player_id,
            player_name,
            self.party_data
        )
        self.withdraw_handler = WithdrawHandler(
            convo,
            agent,
            party_id,
            player_id,
            player_name,
            self.party_data
        )
        self.generic_handler = GenericChatHandler(
            agent,
            self.party_data,
            convo,
            party_id,
            player_id
        )
        self.inspect_handler = InspectHandler(
            agent,
            self.party_data,
            convo,
            party_id
        )
        self.view_handler = ViewHandler(
            convo,
            agent,
            self.buy_handler
        )

        self.stash_handler = StashHandler(
            agent, self.party_data, convo, party_id, character_id
        )

        # build intent router
        self.intent_router = self._build_router()
        self.debug('← Exiting __init__')



    def _handle_confirmation_flow(self, wrapped_input):
        self.debug('→ Entering _handle_confirmation_flow')
        intent = wrapped_input.get('intent')
        if intent == PlayerIntent.BUY_ITEM:
            return self._list_or_detail(PlayerIntent.BUY_ITEM, wrapped_input)
        if intent == PlayerIntent.SELL_ITEM:
            return self._list_or_detail(PlayerIntent.SELL_ITEM, wrapped_input)
        pending = self.convo.pending_action
        if pending in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_CONFIRM}:
            return self.buy_handler.handle_confirm_purchase(wrapped_input)
        if pending in {PlayerIntent.SELL_ITEM, PlayerIntent.SELL_CONFIRM}:
            return self.sell_handler.handle_confirm_sale(wrapped_input)
        if pending == PlayerIntent.STASH_REMOVE:
            return self.stash_handler.handle_confirm_stash_remove(wrapped_input)
        if pending == PlayerIntent.STASH_ADD:
            return self.stash_handler.handle_confirm_stash_add(wrapped_input)

        self.debug('← Exiting _handle_confirmation_flow')
        return self.generic_handler.handle_confirm(wrapped_input)

    def _handle_cancellation_flow(self, wrapped_input):
        self.debug('→ Entering _handle_cancellation_flow')
        self.convo.set_pending_item(None)
        self.convo.set_pending_action(None)
        self.convo.set_discount(None)
        self.convo.reset_state()
        self.convo.set_state(ConversationState.AWAITING_ACTION)
        self.convo.save_state()
        self.debug('← Exiting _handle_cancellation_flow')
        return self.generic_handler.handle_cancel(wrapped_input)

    def _list_or_detail(self, intent: PlayerIntent, wrapped_input: dict):
        """
        Decide whether the user wants to see an item *list* or a single *detail*.

        ── Logic ────────────────────────────────────────────────────────────────
        1. Exact match (one item)   → confirm-buy / inspect flow.
        2. Multiple matches         → let user pick a number.
        3. Recognised sub-category  → jump straight to item-list screen.
        4. Plain “buy …” with no clue → show “What are you after?” prompt.
        5. Fallback                 → couldn’t find that text.
        """
        self.debug('→ Entering _list_or_detail')

        raw = wrapped_input['text']

        # use a looser fuzzy search for INSPECT flows so words like 'sword'
        # return several hits; default remains strict for buy/sell.
        cutoff = 0.55 if intent in (PlayerIntent.INSPECT_ITEM, PlayerIntent.UNKNOWN ) else 0.75
        matches, detected_category = find_item_in_input(
            raw,
            self.convo,
            fuzzy_cutoff=cutoff
        )

        # ── 1. single exact match ──────────────────────────────────────────────
        if matches and len(matches) == 1:
            item = matches[0]

            # BUY flow → confirmation prompt
            if intent == PlayerIntent.BUY_ITEM:
                self.convo.set_pending_item(item)
                self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
                self.convo.set_pending_confirm_item(item['item_name'])
                self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
                self.convo.save_state()
                return self.agent.shopkeeper_buy_confirm_prompt(
                    item,
                    self.party_data.get('party_balance_cp', 0),
                )

            # INSPECT / SELL path
            lines = self.inspect_handler.handle_inspect_item({
                'text': raw,
                'intent': intent,
                'item': item['item_name'],
            })
            return self.agent.shopkeeper_inspect_item_prompt(lines)

        # ── 3. recognised sub-category (e.g. “standard gear”) ────────────────
        if (
                intent in (PlayerIntent.BUY_ITEM, PlayerIntent.BUY_NEEDS_ITEM)
                and detected_category
        ):
            self.convo.set_state(ConversationState.VIEWING_ITEMS)
            self.convo.save_state()
            return self.agent.shopkeeper_show_items_by_category({
                'gear_category': detected_category
            })

        # ── 2. multiple fuzzy matches ──────────────────────────────────────────
        if matches and len(matches) > 1:
            self.convo.set_pending_item(matches)
            self.convo.set_pending_action(intent)
            self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
            self.convo.save_state()
            return self.agent.shopkeeper_list_matching_items(matches)

        # ── 4. user just typed “buy” with no clue ──────────────────────────────
        if intent == PlayerIntent.BUY_ITEM:
            return self.agent.shopkeeper_view_items_prompt()

        # ── 5. fallback ────────────────────────────────────────────────────────
        self.debug('← Exiting _list_or_detail')
        return (
            '❓ I couldn’t find anything called that. '
            'Try “inspect longsword” or “inspect 42”.'
        )

    def handle(self, player_input: str):
        self.debug('→ Entering handle')

        text = player_input.strip()
        low = text.lower()

        # refresh party balance every turn
        self.party_data['party_balance_cp'] = get_party_balance_cp(self.party_id)

        # out-of-band commands
        if low.startswith('dm '):
            return handle_dm_command(
                self.party_id, self.player_id, player_input,
                party_data=self.party_data
            )

        if low.startswith('admin '):
            resp = handle_admin_command(self.player_id, player_input)
            if 'reset' in low:
                self.convo.reset_state()
                self.convo.set_pending_item(None)
                self.convo.set_discount(None)
                self.convo.save_state()
            return resp

        # --- SPECIAL CASE: Awaiting item selection for stash add/remove ---
        if self.convo.state == ConversationState.AWAITING_STASH_ITEM_SELECTION:
            return self.stash_handler.process_stash_item_selection({'text': text})
        if self.convo.state == ConversationState.AWAITING_TAKE_ITEM_SELECTION:
            return self.stash_handler.process_stash_remove_item_selection({'text': text})

        # store raw + normalised input on the convo
        self.convo.set_input(player_input)
        normalised = normalize_input(player_input) if isinstance(player_input, str) else 'N/A'
        self.convo.normalized_input = normalised
        self.convo.debug(f'[HANDLE] raw={player_input!r}, normalised={normalised!r}')

        # SPECIAL CASES: Awaiting deposit/withdraw amount (numeric or not)
        if self.convo.state == ConversationState.AWAITING_DEPOSIT_AMOUNT:
            return self.deposit_handler.process_deposit_balance_cp_flow({'text': text})

        if self.convo.state == ConversationState.AWAITING_WITHDRAW_AMOUNT:
            return self.withdraw_handler.process_withdraw_balance_cp_flow({'text': text})

        # ── numeric selection while browsing ───────
        if (
            low.isdigit()
            and self.convo.state in {
                ConversationState.AWAITING_ITEM_SELECTION,
                ConversationState.VIEWING_ITEMS,
            }
        ):

            idx = int(low)
            if idx <= 0:
                return self.agent.shopkeeper_generic_say('Choose a positive number!')

            pending = self.convo.pending_action
            if pending == PlayerIntent.VIEW_CHARACTER:
                chars = self.convo.pending_item or []
                char_idx = idx - 1
                if 0 <= char_idx < len(chars):
                    self.convo.reset_state()
                    return self.generic_handler.handle_view_character(chars[char_idx])
                return self.agent.shopkeeper_generic_say('That number isn’t in the list—try again!')

            self.convo.debug(f'[HANDLE] numeric select → intent={pending}, id={idx}')
            return self._list_or_detail(
                pending,
                {'text': text, 'intent': pending, 'item': None},
            )

        # ── confirmation / cancellation flow ───────
        if self.convo.state == ConversationState.AWAITING_CONFIRMATION:
            if low in CONFIRMATION_WORDS:
                pending = self.convo.pending_action
                if pending in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_CONFIRM}:
                    return self.buy_handler.handle_confirm_purchase({'text': text})
                if pending == PlayerIntent.SELL_ITEM:
                    return self.sell_handler.handle_confirm_sale({'text': text})
                if pending == PlayerIntent.STASH_ADD:
                    return self.stash_handler.handle_confirm_stash_add({'text': text})
                if pending == PlayerIntent.STASH_REMOVE:
                    return self.stash_handler.handle_confirm_stash_remove({'text': text})
            if low in CANCELLATION_WORDS:
                return self._handle_cancellation_flow({'text': text})

        # ── primary NLU pass ───────────────────────
        intent_data = interpret_input(player_input, self.convo)
        intent    = intent_data.get('intent')
        metadata  = intent_data.get('metadata', {}) or {}

        # pop item out of metadata so we don't double-store
        item = metadata.pop('item', None)

        self.convo.set_intent(intent)
        self.convo.debug(f'[HANDLE] intent={intent}, metadata={metadata}')

        # map category-intents to metadata helpers
        if intent in CATEGORY_MAPPING:
            field, val = CATEGORY_MAPPING[intent]
            metadata[field] = val

        self.convo.metadata.update(metadata)

        # final payload for handler
        wrapped: dict = {'text': player_input, 'intent': intent, **metadata}

        if item is not None:
            if isinstance(item, str):
                # handle JSON-encoded item blobs from the interpreter
                try:
                    item = json.loads(item)
                except JSONDecodeError:
                    self.debug(f'[HANDLE] bad JSON in item: {item!r}')
                    item = None
            wrapped['item'] = item
            self.convo.set_pending_item(item)
            self.convo.set_pending_action(intent)

        # ── route to the correct handler ───────────
        handler = (
            self.intent_router.get((self.convo.state, intent))
            or self._route_intent(intent)
        )

        self.convo.debug(
            f'[HANDLE] routing → state={self.convo.state}, intent={intent}, '
            f'handler={handler.__name__}'
        )
        self.debug('← Exiting handle')
        return handler(wrapped)



    def _build_router(self) -> Dict[Tuple[ConversationState, PlayerIntent], Callable]:
        self.debug('→ Entering _build_router')
        router: Dict[Tuple[ConversationState, PlayerIntent], Callable] = {}

        # ---------- 1. intro screen ----------
        intro_intents = [
            PlayerIntent.GREETING,
            PlayerIntent.SHOW_GRATITUDE,
            PlayerIntent.VIEW_ITEMS,
            PlayerIntent.VIEW_EQUIPMENT_CATEGORY,
            PlayerIntent.VIEW_WEAPON_CATEGORY,
            PlayerIntent.VIEW_GEAR_CATEGORY,
            PlayerIntent.VIEW_ARMOUR_CATEGORY,
            PlayerIntent.VIEW_TOOL_CATEGORY,
            PlayerIntent.VIEW_TREASURE_CATEGORY,
            PlayerIntent.VIEW_MOUNT_CATEGORY,
            PlayerIntent.DEPOSIT_BALANCE,
            PlayerIntent.WITHDRAW_BALANCE,
            PlayerIntent.CHECK_BALANCE,
            PlayerIntent.VIEW_LEDGER,
            PlayerIntent.VIEW_PROFILE,
            PlayerIntent.VIEW_PARTY_PROFILE,
            PlayerIntent.VIEW_ARMOUR_SUBCATEGORY,
            PlayerIntent.VIEW_WEAPON_SUBCATEGORY,
            PlayerIntent.VIEW_GEAR_SUBCATEGORY,
            PlayerIntent.VIEW_TOOL_SUBCATEGORY,
            PlayerIntent.VIEW_TREASURE_SUBCATEGORY,
            PlayerIntent.DEPOSIT_BALANCE, PlayerIntent.DEPOSIT_NEEDS_AMOUNT,
            PlayerIntent.WITHDRAW_BALANCE, PlayerIntent.WITHDRAW_NEEDS_AMOUNT,
        ]
        for i in intro_intents:
            router[ConversationState.INTRODUCTION, i] = self._route_intent(i)
        router[ConversationState.INTRODUCTION, PlayerIntent.UNKNOWN] = (
            self.generic_handler.handle_fallback
        )

        # ---------- 2. awaiting-action screen ----------
        action_intents = [
            PlayerIntent.GREETING,
            PlayerIntent.SHOW_GRATITUDE,
            PlayerIntent.VIEW_ITEMS,
            PlayerIntent.VIEW_EQUIPMENT_CATEGORY,
            PlayerIntent.VIEW_WEAPON_CATEGORY,
            PlayerIntent.VIEW_GEAR_CATEGORY,
            PlayerIntent.VIEW_ARMOUR_CATEGORY,
            PlayerIntent.VIEW_TOOL_CATEGORY,
            PlayerIntent.VIEW_TREASURE_CATEGORY,
            PlayerIntent.VIEW_MOUNT_CATEGORY,
            PlayerIntent.BUY_ITEM,
            PlayerIntent.BUY_NEEDS_ITEM,
            PlayerIntent.SELL_ITEM,
            PlayerIntent.SELL_NEEDS_ITEM,
            PlayerIntent.DEPOSIT_BALANCE, PlayerIntent.DEPOSIT_NEEDS_AMOUNT,
            PlayerIntent.WITHDRAW_BALANCE, PlayerIntent.WITHDRAW_NEEDS_AMOUNT,
            PlayerIntent.CHECK_BALANCE,
            PlayerIntent.VIEW_LEDGER,
            PlayerIntent.INSPECT_ITEM,
            PlayerIntent.VIEW_PROFILE,
            PlayerIntent.VIEW_PARTY_PROFILE,
            PlayerIntent.VIEW_ARMOUR_SUBCATEGORY,
            PlayerIntent.VIEW_WEAPON_SUBCATEGORY,
            PlayerIntent.VIEW_GEAR_SUBCATEGORY,
            PlayerIntent.VIEW_TOOL_SUBCATEGORY,
            PlayerIntent.VIEW_TREASURE_SUBCATEGORY,
        ]
        for i in action_intents:
            router[ConversationState.AWAITING_ACTION, i] = self._route_intent(i)
        router[ConversationState.AWAITING_ACTION, PlayerIntent.UNKNOWN] = (
            self.generic_handler.handle_fallback
        )

        # ---------- 3. the rest of the routers stay exactly the same ----------
        # (AWAITING_ITEM_SELECTION, AWAITING_CONFIRMATION, gratitude loop, …)

        self.debug('← Exiting _build_router')
        return router

    def _route_intent(self, intent: PlayerIntent, state=None) -> Callable:
        self.debug('→ Entering _route_intent')

        # ---------- 1. BUY / SELL / INSPECT branches ----------
        if intent == PlayerIntent.INSPECT_ITEM:
            return lambda w: self._list_or_detail(PlayerIntent.INSPECT_ITEM, w)
        if intent in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_NEEDS_ITEM}:
            return lambda w: self._list_or_detail(PlayerIntent.BUY_ITEM, w)
        if intent in {PlayerIntent.SELL_ITEM, PlayerIntent.SELL_NEEDS_ITEM}:
            return self.sell_handler.process_sell_item_flow

        # ---------- 2. TOP-LEVEL INTENT ROUTING: always do this BEFORE stash/unstash state checks! ----------
        if intent == PlayerIntent.VIEW_LEDGER:
            return self.generic_handler.handle_view_ledger
        if intent == PlayerIntent.CHECK_BALANCE:
            return self.generic_handler.handle_check_balance
        if intent == PlayerIntent.VIEW_PROFILE:
            return self.generic_handler.handle_view_profile
        if intent == PlayerIntent.VIEW_PARTY_PROFILE:
            return self.generic_handler.handle_view_party_profile
        if intent == PlayerIntent.NEXT:
            return self.generic_handler.handle_next_page
        if intent == PlayerIntent.PREVIOUS:
            return self.generic_handler.handle_previous_page
        if intent == PlayerIntent.GREETING:
            return self.generic_handler.handle_reply_to_greeting
        if intent in {PlayerIntent.DEPOSIT_BALANCE, PlayerIntent.DEPOSIT_NEEDS_AMOUNT}:
            return self.deposit_handler.process_deposit_balance_cp_flow
        if intent in {PlayerIntent.WITHDRAW_BALANCE, PlayerIntent.WITHDRAW_NEEDS_AMOUNT}:
            return self.withdraw_handler.process_withdraw_balance_cp_flow
        if intent == PlayerIntent.HAGGLE:
            return self.buy_handler.handle_haggle
        if intent == PlayerIntent.SHOW_GRATITUDE:
            return self.generic_handler.handle_accept_thanks
        if intent == PlayerIntent.UNDO:
            return self.generic_handler.handle_undo_last_transaction

        # ---------- 3. Stash/Unstash stateful routing (do this AFTER the intent-based top-level checks) ----------

        # 1. Add handler for viewing stash (intent only)
        if intent == PlayerIntent.VIEW_STASH:
            return self.stash_handler.handle_view_stash

        # 2. Stash add flow: Use state, NOT intent or pending_action!
        if self.convo.state == ConversationState.AWAITING_STASH_ITEM_SELECTION:
            return self.stash_handler.process_stash_item_selection
        if self.convo.state == ConversationState.AWAITING_CONFIRMATION and self.convo.pending_action == PlayerIntent.STASH_ADD:
            return self.stash_handler.handle_confirm_stash_add
        if intent == PlayerIntent.STASH_ADD:
            return self.stash_handler.process_stash_add_flow

        # 3. Stash remove flow: Use state, NOT intent or pending_action!
        if self.convo.state == ConversationState.AWAITING_TAKE_ITEM_SELECTION:
            return self.stash_handler.process_stash_remove_item_selection
        if self.convo.state == ConversationState.AWAITING_CONFIRMATION and self.convo.pending_action == PlayerIntent.STASH_REMOVE:
            return self.stash_handler.handle_confirm_stash_remove
        if intent == PlayerIntent.STASH_REMOVE:
            return self.stash_handler.process_stash_remove_flow

        # ---------- 4. view-intents ----------
        view_category_intents = {
            PlayerIntent.VIEW_ITEMS,
            PlayerIntent.VIEW_EQUIPMENT_CATEGORY,
            PlayerIntent.VIEW_WEAPON_CATEGORY,
            PlayerIntent.VIEW_GEAR_CATEGORY,
            PlayerIntent.VIEW_ARMOUR_CATEGORY,
            PlayerIntent.VIEW_TOOL_CATEGORY,
            PlayerIntent.VIEW_MOUNT_CATEGORY,
            PlayerIntent.VIEW_TREASURE_CATEGORY,
        }
        view_subcategory_intents = {
            PlayerIntent.VIEW_ARMOUR_SUBCATEGORY,
            PlayerIntent.VIEW_WEAPON_SUBCATEGORY,
            PlayerIntent.VIEW_GEAR_SUBCATEGORY,
            PlayerIntent.VIEW_TOOL_SUBCATEGORY,
            PlayerIntent.VIEW_TREASURE_SUBCATEGORY,
        }  # defined at top

        if intent in view_subcategory_intents:
            def _subcat(wrapped):
                self.convo.set_state(ConversationState.VIEWING_ITEMS)
                self.convo.save_state()
                return self.view_handler.process_view_items_flow(wrapped)

            return _subcat

        if intent in view_category_intents:
            def _cat(wrapped):
                self.convo.set_state(ConversationState.VIEWING_CATEGORIES)
                self.convo.save_state()
                return self.view_handler.process_view_items_flow(wrapped)

            return _cat

        self.debug('← Exiting _route_intent')
        return self.generic_handler.handle_fallback


