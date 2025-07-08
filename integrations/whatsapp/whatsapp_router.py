import importlib
import json
from app.db import query_db, update_convo_state, log_convo_state
from app.conversation import Conversation
from app.conversation_service import ConversationService
from app.models.parties import get_party_by_id, get_all_parties, add_new_party
from app.models.visits import touch_visit  # NEW – rolling 60-min visits
from app.models.shops import get_all_shops
from app.config import SHOP_NAME
from integrations.sharedutils.shared_session_manager import SessionManager
from app.auth.user_login import get_user_by_phone, register_user, create_character_for_user

session_manager = SessionManager()

# Temp state: tracks multi-step setup for registration, party and character creation
user_setup_state: dict[str, dict] = {}


def _load_agent(shop_row, conversation):
    mod = importlib.import_module(
        f"app.agents.personalities.{shop_row['agent_name'].lower()}"
    )
    AgentClass = getattr(mod, shop_row['agent_name'])
    return AgentClass(conversation)


#below contains user setup and login consider refactoring
def handle_whatsapp_command(sender: str, text: str) -> str:
    """Main entrypoint for every incoming WhatsApp message."""
    try:
        phone_e164 = sender.replace('whatsapp:', '')
        user = get_user_by_phone(phone_e164)
        state = user_setup_state.get(phone_e164, {})

        # ── 🔐 Handle unknown users and initial registration ─────────────
        if not user:
            if state.get('stage') == 'awaiting_name':
                new_user = register_user(phone_e164, text.strip())
                user_setup_state.pop(phone_e164, None)
                return f'✅ Welcome, {new_user["user_name"]}! Let\'s set up your character next.'
            else:
                user_setup_state[phone_e164] = {'stage': 'awaiting_name'}
                return "📝 You’re new here! What’s your name?"

        # ── Handle users without a character ─────────────────────────────
        session = session_manager.get_session(sender)
        if session is None:
            character = query_db(
                'SELECT * FROM characters WHERE user_id = ? ORDER BY character_id ASC LIMIT 1',
                (user['user_id'],), one=True
            )
            if not character:
                # If awaiting party choice
                if state.get('stage') == 'awaiting_party_choice':
                    choice = text.strip().lower()
                    parties = get_all_parties()
                    if choice == 'new':
                        user_setup_state[phone_e164] = {'stage': 'awaiting_new_party_name'}
                        return 'A new set of adventurers, excellent! What is the name of your new party?'
                    try:
                        idx = int(choice) - 1
                        selected = parties[idx]
                        state.update({
                            'stage': 'awaiting_character_name',
                            'party_id': selected['party_id']
                        })
                        user_setup_state[phone_e164] = state
                        return 'Great! What would you like to name your character?'
                    except Exception:
                        return 'Invalid choice. Reply with a number from the list or "new" to create a party.'

                # If creating new party
                if state.get('stage') == 'awaiting_new_party_name':
                    name = text.strip()
                    new_id = add_new_party(name)
                    state.update({
                        'stage': 'awaiting_character_name',
                        'party_id': new_id
                    })
                    user_setup_state[phone_e164] = state
                    return 'Ok, noted! Now, what would you like to name your character?'

                # If awaiting character name
                if state.get('stage') == 'awaiting_character_name':
                    char_name = text.strip()
                    party_id = state['party_id']
                    player_name = user['user_name']
                    create_character_for_user(
                        phone_e164,
                        user_id=user['user_id'],
                        party_id=party_id,
                        player_name=player_name,
                        character_name=char_name,
                        role='Adventurer'
                    )
                    party = get_party_by_id(party_id)
                    party_name = party['party_name'] if party else 'your party'
                    user_setup_state.pop(phone_e164, None)
                    return (
                        f'✅ Character "{char_name}" created in party "{party_name}"! '
                        'Send any message to begin shopping.'
                    )

                # Initial prompt to choose or create party
                parties = get_all_parties()
                if not parties:
                    user_setup_state[phone_e164] = {'stage': 'awaiting_new_party_name'}
                    return 'No parties found. Please send a name for your new party.'
                msg = 'Ok, now choose a party by number, or reply "new" to make one:'
                for i, p in enumerate(parties, start=1):
                    msg += f"\n{i}. {p['party_name']}"
                user_setup_state[phone_e164] = {'stage': 'awaiting_party_choice'}
                return msg

            # Character now exists → start session
            party = get_party_by_id(character['party_id'])
            if not party:
                return 'Your party wasn’t found. Tell the Game Master.'
            all_shops = get_all_shops()
            if not all_shops:
                return 'No shops exist in the system right now.'
            shop = next(
                (s for s in all_shops if s['shop_name'].lower() == SHOP_NAME.lower()),
                all_shops[0]
            )
            visit_count = touch_visit(party['party_id'], shop['shop_id'])
            conversation = Conversation(character['character_id'])
            agent = _load_agent(shop, conversation)
            session_manager.start_session(
                sender,
                conversation,
                agent,
                party,
                character['player_name'],
                character['character_id'],
                character['character_name'],
                visit_count,
                shop['shop_id']
            )
            session = session_manager.get_session(sender)

        # ── Existing session logic ─────────────────────────────────────────
        party = session['party']
        visit_count = touch_visit(party['party_id'], session['shop_id'])
        session['visit_count'] = visit_count

        convo = session['conversation']
        agent = session['agent']
        player_name = session['player_name']
        character_id = session['character_id']
        character_name = session['character_name']

        # 2️⃣ Special commands
        if text.strip().lower() == 'reset':
            session_manager.end_session(sender)
            return '🧹 Your session has been reset. Send any message to start again!'

        # 3️⃣ Gameplay flow
        service = ConversationService(
            convo=convo,
            agent=agent,
            party_id=party['party_id'],
            player_id=character_id,
            player_name=player_name,
            party_data=party,
            visit_count=visit_count,
            character_id=character_id,
            character_name=character_name
        )
        response = service.handle(text)

        # Persist into `character_sessions` (serialize enums & lists)
        raw_action = convo.pending_action
        action_val = raw_action.name if hasattr(raw_action, "name") else raw_action
        raw_item = convo.pending_item
        item_val = raw_item.name if hasattr(raw_item, "name") else raw_item
        if isinstance(item_val, (list, dict)):
            item_val = json.dumps(item_val)

        update_convo_state(
            character_id=character_id,
            state=convo.state.name,
            action=action_val,
            item=item_val,
        )

        # And write an audit record into `session_state_log`
        player_intent = (
            service.convo.player_intent.name
            if hasattr(service.convo.player_intent, "name")
            else service.convo.player_intent
        )
        log_convo_state(
            character_id=character_id,
            state=convo.state.name,
            action=action_val,
            item=item_val,
            user_input=text,
            player_intent=player_intent,
        )

        return response or 'Hmm… the shopkeeper says nothing. Try again?'

    except Exception as exc:
        print(f'[ERROR][handle_whatsapp_command] {exc}')
        return (
            'Something broke while speaking to the shopkeeper. '
            'Please tell the Game Master!'
        )
