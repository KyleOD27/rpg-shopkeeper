# integrations/whatsapp/whatsapp_router.py
import importlib
from app.db import query_db
from app.conversation import Conversation
from app.conversation_service import ConversationService
from app.auth.user_login import get_user_by_phone
from app.models.parties import get_party_by_id
from app.models.visits import increment_visit_count, get_visit_count
from app.models.shops import get_all_shops
from app.config import SHOP_NAME
from integrations.sms.sms_session_manager import SessionManager  # reused

session_manager = SessionManager()


def _load_agent(shop_row):
    mod = importlib.import_module(
        f"app.agents.personalities.{shop_row['agent_name'].lower()}"
    )
    Agent = getattr(mod, shop_row["agent_name"])
    return Agent()


def handle_whatsapp_command(sender: str, text: str) -> str:
    """
    Main entrypoint for every incoming WhatsApp message.
    `sender` arrives like 'whatsapp:+4479…', so we strip the prefix
    before looking up the user.
    """
    try:
        phone_e164 = sender.replace("whatsapp:", "")
        user = get_user_by_phone(phone_e164)
        if not user:
            return "🚫 You’re not registered. Ask the Game Master to set you up!"

        # ─── Session lookup / bootstrap ────────────────────────────
        session = session_manager.get_session(sender)

        if session is None:
            # character, party, shop rows
            character = query_db(
                "SELECT * FROM characters WHERE user_id = ? ORDER BY character_id ASC LIMIT 1",
                (user["user_id"],),
                one=True
            )
            if not character:
                return "No character found. Ask the Game Master to roll one up for you."

            party = get_party_by_id(character["party_id"])
            if not party:
                return "Your party wasn’t found. Tell the Game Master."

            all_shops = get_all_shops()
            if not all_shops:
                return "No shops exist in the system right now."

            shop = next(
                (s for s in all_shops if s["shop_name"].lower() == SHOP_NAME.lower()),
                all_shops[0]
            )

            # bump visit counter once per new session
            increment_visit_count(party["party_id"], shop["shop_id"])
            visit_count = get_visit_count(party["party_id"], shop["shop_id"])

            # build agent + conversation
            agent        = _load_agent(shop)
            conversation = Conversation(character["character_id"])

            # session create (now passes visit_count & shop_id)
            session_manager.start_session(
                sender,
                conversation,
                agent,
                party,
                character["player_name"],
                character["character_id"],
                visit_count,
                shop["shop_id"]
            )
            session = session_manager.get_session(sender)

        # ─── Unpack session ────────────────────────────────────────
        convo         = session["conversation"]
        agent         = session["agent"]
        party         = session["party"]
        player_name   = session["player_name"]
        character_id  = session["character_id"]
        visit_count   = session["visit_count"]       # guaranteed by start_session

        # ─── “reset” shortcut ─────────────────────────────────────
        if text.strip().lower() == "reset":
            session_manager.end_session(sender)
            return "🧹 Your session has been reset. Send any message to start again!"

        # ─── Delegate to ConversationService ─────────────────────
        service = ConversationService(
            convo       = convo,
            agent       = agent,
            party_id    = party["party_id"],
            player_id   = character_id,
            player_name = player_name,
            party_data  = party,
            visit_count = visit_count
        )

        response = service.handle(text)
        return response or "Hmm… the shopkeeper says nothing. Try again?"

    except Exception as exc:
        print(f"[ERROR][handle_whatsapp_command] {exc}")
        return "Something broke while speaking to the shopkeeper. Please tell the Game Master!"
