import json
import sqlite3
from app.conversation import PlayerIntent, ConversationState
from app.db import get_connection, get_item_details
from app.utils.debug import HandlerDebugMixin


class InspectHandler(HandlerDebugMixin):

    def __init__(self, agent, party_data, convo, party_id):
        # wire up debug proxy before any debug() calls
        self.conversation = convo
        self.debug('→ Entering __init__')
        self.agent = agent
        self.party_data = party_data
        self.convo = convo
        self.party_id = party_id

        self.debug('← Exiting __init__')


    def handle_inspect_item(self, wrapped_input):
        self.debug('→ Entering handle_inspect_item')
        self.convo.debug(f'[INSPECT] wrapped_input={wrapped_input!r}')
        self.convo.debug(
            f'[INSPECT] pending_item(before)={self.convo.get_pending_item()!r}'
            )
        item_data = wrapped_input.get('item')
        if isinstance(item_data, str):
            try:
                item_data = json.loads(item_data)
                self.convo.debug(
                    f'[INSPECT] parsed JSON item_data={item_data!r}')
            except json.JSONDecodeError:
                self.convo.debug(f'[INSPECT] item_data not JSON')
        if not item_data:
            item_data = self.convo.get_pending_item()
            self.convo.debug(f'[INSPECT] using pending_item now={item_data!r}')
        if isinstance(item_data, list):
            self.convo.debug(f'[INSPECT] multiple candidates, listing them')
            self.convo.set_pending_item(item_data)
            self.convo.set_pending_action(PlayerIntent.INSPECT_ITEM)
            self.convo.set_state(ConversationState.AWAITING_ITEM_SELECTION)
            self.convo.save_state()
            return self.agent.shopkeeper_list_matching_items(item_data)
        if isinstance(item_data, dict):
            item_name = item_data.get('item_name')
        else:
            item_name = item_data
        self.convo.debug(f'[INSPECT] resolved item_name={item_name!r}')
        if not item_name or not isinstance(item_name, str):
            return [
                "❓ I couldn’t tell which item you meant. Try saying 'inspect longsword' or give me a number."
                ]
        conn = get_connection()
        row = get_item_details(conn, item_name)
        if isinstance(row, sqlite3.Row):
            row = dict(row)
            self.convo.debug(f'[INSPECT] DB row data={row!r}')
            self.convo.set_pending_item(row)
        if not row:
            return [f"❓ I couldn’t find an item named '{item_name}'."]
        name = row['item_name']
        equip_cat = row.get('equipment_category')
        gear_cat = row.get('gear_category')
        weapon_cat = row.get('weapon_category')
        wpn_range = row.get('weapon_range')
        dmg_dice = row.get('damage_dice')
        dmg_type = row.get('damage_type')
        r_normal = row.get('range_normal')
        r_long = row.get('range_long')
        price = row.get('base_price')
        unit = row.get('price_unit')
        weight = row.get('weight')
        desc = row.get('desc')
        EMOJI = {'name': '🧾', 'category': '🏷️', 'type': '⚙️', 'cost': '💰',
            'weight': '⚖️', 'damage': '⚔️', 'weapon_range': '🎯', 'range':
            '📏', 'desc': '📜'}
        lines = [f"{EMOJI['name']} Item Name: {name}",
            f"{EMOJI['category']} Category: {equip_cat or 'N/A'}",
            f"{EMOJI['type']} Type: {weapon_cat or gear_cat or 'N/A'}",
            f"{EMOJI['cost']} Cost: {price} {unit}",
            f"{EMOJI['weight']} Weight: {weight or 'Unknown'} lbs", f' ']
        if dmg_dice:
            lines.append(
                f"{EMOJI['damage']} Damage: {dmg_dice} {dmg_type or ''}".
                strip())
        if wpn_range:
            lines.append(f"{EMOJI['weapon_range']} Weapon Range: {wpn_range}")
        if r_normal:
            span = f'{r_normal} ft' + (f' / {r_long} ft' if r_long else '')
            lines.append(f"{EMOJI['range']} Range: {span}")
        if desc:
            lines.append(f"{EMOJI['desc']} {desc}")
        self.convo.set_pending_item(None)
        self.convo.set_pending_action(None)
        self.convo.set_state(ConversationState.INTRODUCTION)
        self.convo.save_state()
        self.debug('← Exiting handle_inspect_item')
        return lines
