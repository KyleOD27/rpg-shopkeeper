from app.conversation import PlayerIntent, ConversationState
from app.models.ledger import get_last_transactions
from app.interpreter import get_equipment_category_from_input
from app.db import get_item_details, get_connection


class InspectHandler:
    def __init__(self, agent, party_data, convo, party_id):
        self.agent = agent
        self.party_data = party_data
        self.convo = convo
        self.party_id = party_id

    def handle_inspect_item(self, wrapped_input):
        import json
        # ─── DEBUG ─────────────────────────────────────────────────────────────
        self.convo.debug(f"[INSPECT] wrapped_input={wrapped_input!r}")
        self.convo.debug(f"[INSPECT] pending_item(before)={self.convo.get_pending_item()!r}")
        # ────────────────────────────────────────────────────────────────────────

        item_data = wrapped_input.get("item")

        # 🛠 Fix if item was still a stringified list/dict
        if isinstance(item_data, str):
            try:
                item_data = json.loads(item_data)
                self.convo.debug(f"[INSPECT] parsed JSON item_data={item_data!r}")
            except json.JSONDecodeError:
                self.convo.debug(f"[INSPECT] item_data not JSON")

        # 🧠 Fallback: use pending_item if needed
        if not item_data:
            item_data = self.convo.get_pending_item()
            self.convo.debug(f"[INSPECT] using pending_item now={item_data!r}")

        # 🧠 If it's a list, ask the user to pick from it
        if isinstance(item_data, list):
            self.convo.debug(f"[INSPECT] multiple candidates, listing them")
            self.convo.set_pending_item(item_data)
            self.convo.set_pending_action(PlayerIntent.INSPECT_ITEM)
            self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
            self.convo.save_state()
            return self.agent.shopkeeper_list_matching_items(item_data)

        # 🧠 If it's a dict, extract name
        if isinstance(item_data, dict):
            item_name = item_data.get("item_name")
        else:
            item_name = item_data  # already a string
        self.convo.debug(f"[INSPECT] resolved item_name={item_name!r}")

        if not item_name or not isinstance(item_name, str):
            self.convo.debug(f"[INSPECT] bad item_name, bailing")
            return "❓ I couldn’t tell which item you meant. Try saying 'inspect longsword' or give me a number."

        # ✅ Lookup from DB
        from app.db import get_connection
        conn = get_connection()
        row = get_item_details(conn, item_name)
        self.convo.debug(f"[INSPECT] DB row={row!r}")

        if not row:
            return f"❓ I couldn’t find an item named '{item_name}'."

        (
            name, equip_cat, gear_cat, weapon_cat,
            wpn_range, cat_range, dmg_dice, dmg_type,
            r_normal, r_long, price, unit, weight, desc
        ) = row

        parts = [
            f"🧾 **{name}**",
            f"Category: {equip_cat or 'N/A'}",
            f"Type: {weapon_cat or gear_cat or 'N/A'}",
            f"Cost: {price} {unit}",
            f"Weight: {weight or 'Unknown'} lbs",
        ]

        if dmg_dice:
            parts.append(f"Damage: {dmg_dice} {dmg_type or ''}".strip())
        if wpn_range:
            parts.append(f"Weapon Range: {wpn_range}")
        if cat_range:
            parts.append(f"Category Range: {cat_range}")
        if r_normal:
            parts.append(f"Range: {r_normal} ft" + (f" / {r_long} ft" if r_long else ""))

        if desc:
            parts.append(f"\n📜 {desc}")

        return "\n".join(parts)










