import importlib
from app.db import query_db
from app.conversation import Conversation
from app.conversation_service import ConversationService
from app.models.parties import get_party_by_id
from app.models.visits import get_visit_count, increment_visit_count
from app.models.shops import get_all_shops
from app.config import SHOP_NAME
from app.auth.user_login import get_user_by_phone
from integrations.sms.sms_session_manager import SessionManager

# Create one global manager
session_manager = SessionManager()


# === In-memory session store ===
conversations = {}

def handle_sms_command(sender: str, text: str) -> str:
    try:
        user = get_user_by_phone(sender)
        if not user:
            return "🚫 You’re not registered. Ask the Game Master to set you up! 🧙‍♂️"

        session = session_manager.get_session(sender)

        if session is None:
            # First time user - create everything
            character = query_db(
                "SELECT * FROM characters WHERE user_id = ? ORDER BY character_id ASC LIMIT 1",
                (user["user_id"],), one=True
            )
            if not character:
                return "No character found for your user. Ask the Game Master to help you roll one up."

            party = get_party_by_id(character["party_id"])
            if not party:
                return "Your party wasn’t found. Ask the Game Master to check setup."

            shops = get_all_shops()
            if not shops:
                return "No shops found in the system."

            shop = next((s for s in shops if s["shop_name"].lower() == SHOP_NAME.lower()), shops[0])
            increment_visit_count(party["party_id"], shop["shop_id"])
            visit_count = get_visit_count(party["party_id"], shop["shop_id"])

            # Load agent dynamically
            mod = importlib.import_module(f'app.agents.personalities.{shop["agent_name"].lower()}')
            Agent = getattr(mod, shop["agent_name"])
            agent = Agent()

            # Create conversation
            conversation = Conversation(character["character_id"])

            # Start session
            session_manager.start_session(
                sender,
                conversation,
                agent,
                party,
                character["player_name"],
                character["character_id"]
            )

            session = session_manager.get_session(sender)

        # Existing session
        convo = session["conversation"]
        agent = session["agent"]
        party = session["party"]
        player_name = session["player_name"]
        character_id = session["character_id"]

        service = ConversationService(
            convo=convo,
            agent=agent,
            party_id=party["party_id"],
            player_id=character_id,
            player_name=player_name,
            party_data=party,
        )

        # Check for special commands
        if text.strip().lower() == "reset":
            session_manager.end_session(sender)
            return "🧹 Your session has been reset. Send any message to start again!"

        response = service.handle(text)
        return response or "Hmm… the shopkeeper says nothing. Try again?"

    except Exception as e:
        print(f"[ERROR] in handle_sms_command: {e}")
        return "Something broke while speaking to the shopkeeper. Please tell the Game Master!"

