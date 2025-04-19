import importlib
from app.conversation import Conversation
from app.conversation_service import ConversationService
from app.models.players import get_player_by_id, get_player_id_by_name
from app.models.parties import get_party_by_id
from app.models.visits import get_visit_count, increment_visit_count
from app.models.shops import get_all_shops
from config import SHOP_NAME, AUTO_LOGIN_NAME

# In-memory cache of sessions
conversations = {}

# 🔗 Map SMS sender number to known player name
sender_to_player_id = {
    "+447971548666": AUTO_LOGIN_NAME,  # Replace with your number and config value
}

def handle_sms_command(sender: str, text: str) -> str:
    try:
        if sender not in sender_to_player_id:
            return "You’re not registered. Ask the Game Master to set you up! 🧙‍♂️"

        player_name = sender_to_player_id[sender]
        print(f"[DEBUG] Mapped sender to player: {player_name}")

        player_id = get_player_id_by_name(player_name)
        if not player_id:
            return "Character not found. Please ask the Game Master to check your setup."

        player = get_player_by_id(player_id)
        if not player:
            return "Player details missing. Please contact the Game Master."

        party = get_party_by_id(player["party_id"])
        if not party:
            return "Party not found. Please contact the Game Master."

        all_shops = get_all_shops()
        if not all_shops:
            return "No shops found in the system."

        # Select the correct shop
        shop = next((s for s in all_shops if s["shop_name"].lower() == SHOP_NAME.lower()), all_shops[0])

        visit_count = get_visit_count(party["party_id"], shop["shop_id"])
        increment_visit_count(party["party_id"], shop["shop_id"])
        print(f"[DEBUG] Visit count for {shop['shop_name']}: {visit_count}")

        # Load agent
        mod = importlib.import_module(f'app.agents.personalities.{shop["agent_name"].lower()}')
        Agent = getattr(mod, shop["agent_name"])
        agent = Agent()

        # Retrieve or create session
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
        return response or "Hmm… the shopkeeper says nothing. Try again?"

    except Exception as e:
        print(f"[ERROR] in handle_sms_command: {e}")
        return "Something broke while speaking to the shopkeeper. Please tell the Game Master!"
