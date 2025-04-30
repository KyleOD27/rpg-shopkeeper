# app/handlers/inspect_handler.py

from app.conversation import PlayerIntent, ConversationState
from app.db import get_connection, get_item_details

class InspectHandler:
    def __init__(self, agent, party_data, convo, party_id):
        self.agent      = agent
        self.party_data = party_data
        self.convo      = convo
        self.party_id   = party_id

    def handle_inspect_item(self, wrapped_input):
        import json, sqlite3
        from app.conversation import PlayerIntent, ConversationState
        from app.db import get_connection, get_item_details

        # ─── DEBUG ─────────────────────────────────────────────────────────────
        self.convo.debug(f"[INSPECT] wrapped_input={wrapped_input!r}")
        self.convo.debug(f"[INSPECT] pending_item(before)={self.convo.get_pending_item()!r}")
        # ────────────────────────────────────────────────────────────────────────

        item_data = wrapped_input.get("item")

        # 🛠 If the item came in as a JSON string, parse it
        if isinstance(item_data, str):
            try:
                item_data = json.loads(item_data)
                self.convo.debug(f"[INSPECT] parsed JSON item_data={item_data!r}")
            except json.JSONDecodeError:
                self.convo.debug(f"[INSPECT] item_data not JSON")

        # 🧠 Fallback to any pending_item
        if not item_data:
            item_data = self.convo.get_pending_item()
            self.convo.debug(f"[INSPECT] using pending_item now={item_data!r}")

        # 🧠 If it's a list, ask the user to pick one
        if isinstance(item_data, list):
            self.convo.debug(f"[INSPECT] multiple candidates, listing them")
            self.convo.set_pending_item(item_data)
            self.convo.set_pending_action(PlayerIntent.INSPECT_ITEM)
            self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
            self.convo.save_state()
            return self.agent.shopkeeper_list_matching_items(item_data)

        # 🧠 Extract the item_name
        if isinstance(item_data, dict):
            item_name = item_data.get("item_name")
        else:
            item_name = item_data  # assume string
        self.convo.debug(f"[INSPECT] resolved item_name={item_name!r}")

        if not item_name or not isinstance(item_name, str):
            return "❓ I couldn’t tell which item you meant. Try saying 'inspect longsword' or give me a number."

        # ✅ Fetch the details row from the DB
        conn = get_connection()
        row = get_item_details(conn, item_name)

        # ─── Convert sqlite3.Row to dict ───────────────────────────────────────
        if isinstance(row, sqlite3.Row):
            row = dict(row)
            self.convo.debug(f"[INSPECT] DB row data={row!r}")
            # store it in pending_item so you can reference it later if needed
            self.convo.set_pending_item(row)

        if not row:
            return f"❓ I couldn’t find an item named '{item_name}'."

        # ─── Unpack by key ────────────────────────────────────────────────────
        name = row["item_name"]
        equip_cat = row.get("equipment_category")
        gear_cat = row.get("gear_category")
        weapon_cat = row.get("weapon_category")
        wpn_range = row.get("weapon_range")
        cat_range = row.get("category_range")
        dmg_dice = row.get("damage_dice")
        dmg_type = row.get("damage_type")
        r_normal = row.get("range_normal")
        r_long = row.get("range_long")
        price = row.get("base_price")
        unit = row.get("price_unit")
        weight = row.get("weight")
        desc = row.get("desc")

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

        # ─── TEARDOWN: clear out inspect state ────────────────────────────────
        self.convo.set_pending_item(None)
        self.convo.set_pending_action(None)
        self.convo.set_state(ConversationState.INTRODUCTION)
        self.convo.save_state()
        # ────────────────────────────────────────────────────────────────────────

        return "\n".join(parts)

