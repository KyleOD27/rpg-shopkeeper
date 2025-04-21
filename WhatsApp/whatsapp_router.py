import importlib
from app.conversation import Conversation
from app.conversation_service import ConversationService
from app.models.characters import get_character_by_id, get_character_id_by_player_name
from app.models.parties import get_party_by_id
from app.models.visits import get_visit_count, increment_visit_count
from app.models.shops import get_all_shops
from config import SHOP_NAME, AUTO_LOGIN_NAME

# In-memory cache of sessions
conversations = {}

# Hardcoded sender mapping — you can extend this or load from config/db
sender_to_player_id = {
    "whatsapp:+447971548666": AUTO_LOGIN_NAME,
}

def handle_whatsapp_command(sender: str, text: str) -> str:
    try:
        if sender not in sender_to_player_id:
            return "You’re not registered. Ask the Game Master to set you up! 🧙‍♂️"

        player_name = sender_to_player_id[sender]
        print(f"[DEBUG] Mapped sender to player: {player_name}")

        player_id = get_character_id_by_player_name(player_name)
        print(f"[DEBUG] Player ID: {player_id}")
        if not player_id:
            return "Character not found. Please ask the Game Master to check your setup."

        player = get_character_by_id(player_id)
        print(f"[DEBUG] Player: {player}")
        if not player:
            return "Player details missing. Please contact the Game Master."

        party = get_character_by_id(player["party_id"])
        print(f"[DEBUG] Party: {party}")
        if not party:
            return "Party not found. Please contact the Game Master."

        all_shops = get_all_shops()
        print(f"[DEBUG] All shops: {all_shops}")
        if not all_shops:
            return "No shops found in the system."

        if SHOP_NAME:
            matching = [s for s in all_shops if s["shop_name"].lower() == SHOP_NAME.lower()]
            shop = matching[0] if matching else all_shops[0]
        else:
            shop = all_shops[0]
        print(f"[DEBUG] Selected shop: {shop}")

        visit_count = get_visit_count(party["party_id"], shop["shop_id"])
        increment_visit_count(party["party_id"], shop["shop_id"])
        print(f"[DEBUG] Visit count: {visit_count}")

        mod = importlib.import_module(f'app.agents.personalities.{shop["agent_name"].lower()}')
        print(f"[DEBUG] Imported module for: {shop['agent_name']}")
        Agent = getattr(mod, shop["agent_name"])
        agent = Agent()

        if sender not in conversations:
            conversations[sender] = Conversation(player_id)

        convo = conversations[sender]
        service = ConversationService(
            convo=convo,
            agent=agent,
            party_id=party["party_id"],
            player_id=player_id,
            player_name=player["player_name"],
            party_data=party,
        )

        response = service.handle(text)
        print(f"[DEBUG] Agent response: {response}")
        return response or "Hmm… no response from the shopkeeper. Try again?"
    except Exception as e:
        print(f"[ERROR] in handle_whatsapp_command: {e}")
        return "Something broke when talking to the shopkeeper. Please tell the Game Master!"
