from typing import Callable, Dict, Tuple, Any
from app.interpreter import interpret_input, normalize_input, find_item_in_input
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

CATEGORY_MAPPING = {
    PlayerIntent.VIEW_ARMOUR_CATEGORY:    ("armour_category",    "Armor"),
    PlayerIntent.VIEW_WEAPON_CATEGORY:    ("weapon_category",    "Weapon"),
    PlayerIntent.VIEW_GEAR_CATEGORY:      ("gear_category",      "Adventuring Gear"),
    PlayerIntent.VIEW_TOOL_CATEGORY:      ("tool_category",      "Tools"),
    PlayerIntent.VIEW_EQUIPMENT_CATEGORY: ("current_section",    "equipment"),
}

class ConversationService:
    def __init__(self, convo, agent, party_id, player_id, player_name, party_data):
        self.convo = convo
        self.agent = agent
        self.party_id = party_id
        self.player_id = player_id

        self.party_data = dict(party_data)
        self.party_data["player_name"] = player_name
        self.party_data["visit_count"] = self.party_data.get("visit_count", 1)

        # Handlers
        self.buy_handler      = BuyHandler(convo, agent, party_id, player_id, player_name, self.party_data)
        self.sell_handler     = SellHandler(convo, agent, party_id, player_id, player_name, self.party_data)
        self.deposit_handler  = DepositHandler(convo, agent, party_id, player_id, player_name, self.party_data)
        self.withdraw_handler = WithdrawHandler(convo, agent, party_id, player_id, player_name, self.party_data)
        self.generic_handler  = GenericChatHandler(agent, self.party_data, convo, party_id)
        self.inspect_handler  = InspectHandler(agent, self.party_data, convo, party_id)
        self.view_handler     = ViewHandler(convo, agent, self.buy_handler)

        self.intent_router = self._build_router()


    # ─── helper to handle yes/no when awaiting confirmation ────────
    def _handle_confirmation_flow(self, wrapped_input):
        pending = self.convo.pending_action

        # both straight BUY_ITEM *and* BUY_CONFIRM go to the same finaliser
        if pending in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_CONFIRM}:
            return self.buy_handler.handle_confirm_purchase(wrapped_input)

        if pending in {PlayerIntent.SELL_ITEM, PlayerIntent.SELL_CONFIRM}:
            return self.sell_handler.handle_sell_confirm(wrapped_input)

        return self.generic_handler.handle_confirm(wrapped_input)

    # ─── helper to reset on cancellation ───────────────────────────
    def _handle_cancellation_flow(self, wrapped_input):
        self.convo.set_pending_item(None)
        self.convo.set_pending_action(None)
        self.convo.set_discount(None)
        self.convo.reset_state()
        self.convo.set_state(ConversationState.AWAITING_ACTION)
        self.convo.save_state()
        return self.generic_handler.handle_cancel(wrapped_input)


    # ─── list/multi → detail handler used by both buy & inspect ────
    def _list_or_detail(self, intent, wrapped_input):
        raw = wrapped_input["text"]
        matches, detected_category = find_item_in_input(raw, self.convo)

        # 1️⃣ single match
        if matches and len(matches) == 1:
            item = matches[0]

            if intent == PlayerIntent.BUY_ITEM:
                # set up the pending buy flow
                self.convo.set_pending_item(item)
                self.convo.set_pending_action(PlayerIntent.BUY_ITEM)
                self.convo.set_state(ConversationState.AWAITING_CONFIRMATION)
                self.convo.save_state()
                return self.agent.shopkeeper_buy_confirm_prompt(
                    item,
                    self.party_data.get("party_gold", 0)
                )

            # INSPECT flow: get the emoji‐rich list of lines
            lines = self.inspect_handler.handle_inspect_item({
                "text": raw,
                "intent": intent,
                "item": item["item_name"]
            })
            # render them via your new helper
            return self.agent.shopkeeper_inspect_item_prompt(lines)

        # 2️⃣ multiple
        if matches and len(matches) > 1:
            self.convo.set_pending_item(matches)
            self.convo.set_pending_action(intent)
            self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
            self.convo.save_state()
            return self.agent.shopkeeper_list_matching_items(matches)

        # 3️⃣ category fallback for BUY
        if intent == PlayerIntent.BUY_ITEM and detected_category:
            self.convo.set_state(ConversationState.VIEWING_CATEGORIES)
            return self.agent.shopkeeper_show_items_by_category({"equipment_category": detected_category})

        # 4️⃣ final BUY fallback
        if intent == PlayerIntent.BUY_ITEM:
            return self.agent.shopkeeper_view_items_prompt()

        # 5️⃣ inspect fallback
        return "❓ I couldn’t find anything called that. Try ‘inspect longsword’ or give me a number."


    # ─── main entrypoint ─────────────────────────────────────────
    def handle(self, player_input: str):
        import json
        text = player_input.strip()
        low  = text.lower()

        # ─── 1. DM / admin ────────────────────────────────────────
        if low.startswith("dm "):
            return handle_dm_command(self.party_id, self.player_id, player_input, party_data=self.party_data)
        if low.startswith("admin "):
            resp = handle_admin_command(player_input)
            if "reset" in low:
                self.convo.reset_state()
                self.convo.set_pending_item(None)
                self.convo.set_discount(None)
                self.convo.save_state()
            return resp

        # ─── 2. Record raw & normalized ──────────────────────────
        self.convo.set_input(player_input)
        normalized = normalize_input(player_input) if isinstance(player_input, str) else "N/A"
        self.convo.normalized_input = normalized
        self.convo.debug(f"[HANDLE] raw={player_input!r}, normalized={normalized!r}")

        # ─── 3. Numeric ID selection ─────────────────────────────
        if text.isdigit() and self.convo.state == ConversationState.AWAITING_ITEM_SELECTION:
            pending = self.convo.pending_action
            self.convo.debug(f"[HANDLE] numeric select → intent={pending}, id={text}")
            return self._list_or_detail(pending, {
                "text": text,
                "intent": pending,
                "item": None
            })

        # ─── 4. SHORT-CIRCUIT “yes/no” on pending confirmation ────
        if self.convo.state == ConversationState.AWAITING_CONFIRMATION:
            if low in {"yes", "y", "sure", "ok", "okay","deal"}:
                pending = self.convo.pending_action
                if pending in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_CONFIRM}:
                    return self.buy_handler.handle_confirm_purchase({"text": text})
                if pending == PlayerIntent.SELL_ITEM:
                    return self.sell_handler.handle_sell_confirm({"text": text})
            if low in {"no", "n", "cancel", "never mind"}:
                return self._handle_cancellation_flow({"text": text})

        # ─── 5. interpret & route normally ───────────────────────
        intent_data = interpret_input(player_input, self.convo)
        intent      = intent_data.get("intent")
        metadata    = intent_data.get("metadata", {}) or {}
        item        = metadata.get("item")
        self.convo.set_intent(intent)
        self.convo.debug(f"[HANDLE] intent={intent}, metadata={metadata}")

        # map category intents
        if intent in CATEGORY_MAPPING:
            field, val = CATEGORY_MAPPING[intent]
            metadata[field] = val

        wrapped = {"text": player_input, "intent": intent, "item": item, **metadata}
        if item is not None:
            if isinstance(item, str):
                try:
                    item = json.loads(item)
                except json.JSONDecodeError:
                    pass
            wrapped["item"] = item
            self.convo.set_pending_item(item)
            self.convo.set_pending_action(intent)

        handler = (
            self.intent_router.get((self.convo.state, intent))
            or self._route_intent(intent)
        )
        self.convo.debug(
            f"[HANDLE] routing → state={self.convo.state}, "
            f"intent={intent}, handler={handler.__name__}"
        )
        return handler(wrapped)


    # ─── build the state/intent → handler map ───────────────────
    def _build_router(self) -> Dict[Tuple[ConversationState, PlayerIntent], Callable]:
        router: Dict[Tuple[ConversationState, PlayerIntent], Callable] = {}

        # INTRODUCTION
        intro_intents = [
            PlayerIntent.GREETING, PlayerIntent.VIEW_ITEMS,
            PlayerIntent.VIEW_EQUIPMENT_CATEGORY, PlayerIntent.VIEW_WEAPON_CATEGORY,
            PlayerIntent.VIEW_GEAR_CATEGORY, PlayerIntent.VIEW_ARMOUR_CATEGORY,
            PlayerIntent.VIEW_TOOL_CATEGORY, PlayerIntent.VIEW_MOUNT_CATEGORY,
            PlayerIntent.DEPOSIT_GOLD, PlayerIntent.WITHDRAW_GOLD,
            PlayerIntent.CHECK_BALANCE, PlayerIntent.VIEW_LEDGER
        ]
        for i in intro_intents:
            router[(ConversationState.INTRODUCTION, i)] = self._route_intent(i)
        router[(ConversationState.INTRODUCTION, PlayerIntent.UNKNOWN)] = \
            self.generic_handler.handle_fallback

        # AWAITING_ACTION
        action_intents = [
            PlayerIntent.GREETING, PlayerIntent.VIEW_ITEMS,
            PlayerIntent.VIEW_EQUIPMENT_CATEGORY, PlayerIntent.VIEW_WEAPON_CATEGORY,
            PlayerIntent.VIEW_GEAR_CATEGORY, PlayerIntent.VIEW_ARMOUR_CATEGORY,
            PlayerIntent.VIEW_TOOL_CATEGORY, PlayerIntent.VIEW_MOUNT_CATEGORY,
            PlayerIntent.BUY_ITEM, PlayerIntent.BUY_NEEDS_ITEM,
            PlayerIntent.SELL_ITEM, PlayerIntent.SELL_NEEDS_ITEM,
            PlayerIntent.DEPOSIT_GOLD, PlayerIntent.WITHDRAW_GOLD,
            PlayerIntent.CHECK_BALANCE, PlayerIntent.VIEW_LEDGER,
            PlayerIntent.INSPECT_ITEM
        ]
        for i in action_intents:
            router[(ConversationState.AWAITING_ACTION, i)] = self._route_intent(i)
        router[(ConversationState.AWAITING_ACTION, PlayerIntent.UNKNOWN)] = \
            self.generic_handler.handle_fallback

        # AWAITING_ITEM_SELECTION
        router[(ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.BUY_ITEM)] = \
            self.buy_handler.process_item_selection
        router[(ConversationState.AWAITING_ITEM_SELECTION, PlayerIntent.SELL_ITEM)] = \
            self.sell_handler.process_sell_item_flow

        # ─── AWAITING_CONFIRMATION ───────────────────────────────
        # haggle retry
        router[(ConversationState.AWAITING_CONFIRMATION, PlayerIntent.HAGGLE)] = self.buy_handler.handle_haggle

        # “I’d like to buy that” (from haggle-success path)
        router[(ConversationState.AWAITING_CONFIRMATION,
                PlayerIntent.BUY_CONFIRM)] = self.buy_handler.handle_confirm_purchase

        # “Yes” / “Okay” / “Confirm”
        router[(ConversationState.AWAITING_CONFIRMATION, PlayerIntent.CONFIRM)] = self._handle_confirmation_flow

        # in case something downstream still registers as BUY_ITEM
        router[(ConversationState.AWAITING_CONFIRMATION, PlayerIntent.BUY_ITEM)] = self._handle_confirmation_flow

        # sell side
        router[(ConversationState.AWAITING_CONFIRMATION,
                PlayerIntent.SELL_CONFIRM)] = self.sell_handler.handle_sell_confirm

        # cancellations
        for c in (PlayerIntent.CANCEL, PlayerIntent.BUY_CANCEL, PlayerIntent.SELL_CANCEL):
            router[(ConversationState.AWAITING_CONFIRMATION, c)] = self._handle_cancellation_flow

        return router


    # ─── fallback routing for anything not in the router ────────
    def _route_intent(self, intent: PlayerIntent, state=None) -> Callable:
        if intent == PlayerIntent.INSPECT_ITEM:
            return lambda w: self._list_or_detail(PlayerIntent.INSPECT_ITEM, w)
        if intent in {PlayerIntent.BUY_ITEM, PlayerIntent.BUY_NEEDS_ITEM}:
            return lambda w: self._list_or_detail(PlayerIntent.BUY_ITEM, w)
        if intent in {PlayerIntent.SELL_ITEM, PlayerIntent.SELL_NEEDS_ITEM}:
            return self.sell_handler.process_sell_item_flow

        view_intents = {
            PlayerIntent.VIEW_ITEMS, PlayerIntent.VIEW_EQUIPMENT_CATEGORY,
            PlayerIntent.VIEW_WEAPON_CATEGORY, PlayerIntent.VIEW_GEAR_CATEGORY,
            PlayerIntent.VIEW_ARMOUR_CATEGORY, PlayerIntent.VIEW_TOOL_CATEGORY,
            PlayerIntent.VIEW_MOUNT_CATEGORY,
            PlayerIntent.VIEW_ARMOUR_SUBCATEGORY, PlayerIntent.VIEW_WEAPON_SUBCATEGORY,
            PlayerIntent.VIEW_GEAR_SUBCATEGORY, PlayerIntent.VIEW_TOOL_SUBCATEGORY
        }
        if intent in view_intents:
            return self.view_handler.process_view_items_flow
        if intent == PlayerIntent.NEXT:
            return self.generic_handler.handle_next_page
        if intent == PlayerIntent.PREVIOUS:
            return self.generic_handler.handle_previous_page
        if intent == PlayerIntent.GREETING:
            return self.generic_handler.handle_reply_to_greeting
        if intent == PlayerIntent.DEPOSIT_GOLD:
            return self.deposit_handler.process_deposit_gold_flow
        if intent == PlayerIntent.WITHDRAW_GOLD:
            return self.withdraw_handler.process_withdraw_gold_flow
        if intent == PlayerIntent.CHECK_BALANCE:
            return self.generic_handler.handle_check_balance
        if intent == PlayerIntent.VIEW_LEDGER:
            return self.generic_handler.handle_view_ledger

        return self.generic_handler.handle_fallback
