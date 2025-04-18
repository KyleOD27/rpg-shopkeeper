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
sender_to_player_id = {
    "whatsapp:+447971548666": AUTO_LOGIN_NAME,  # Replace with your sandbox number
}

def handle_whatsapp_command(sender: str, text: str) -> str:
    if sender not in sender_to_player_id:
        return "You’re not registered. Ask the Game Master to set you up! 🧙‍♂️"

    player_name = sender_to_player_id[sender]
    player_id = get_player_id_by_name(player_name)

    if not player_id:
        return "Character not found. Please ask the Game Master to check your setup."

    player = get_player_by_id(player_id)
    if not player:
        return "Player details missing. Please contact the Game Master."

    party = get_party_by_id(player["party_id"])
    if not party:
        return "Party not found. Please contact the Game Master."

    # 🛍️ Get the shop
    all_shops = get_all_shops()
    if SHOP_NAME:
        matching = [s for s in all_shops if s["shop_name"].lower() == SHOP_NAME.lower()]
        shop = matching[0] if matching else all_shops[0]
    else:
        shop = all_shops[0]

    # 🧾 Log visits
    visit_count = get_visit_count(party["party_id"], shop["shop_id"])
    increment_visit_count(party["party_id"], shop["shop_id"])

    # 🧙 Load shopkeeper
    mod = importlib.import_module(f'app.agents.personalities.{shop["agent_name"].lower()}')
    Agent = getattr(mod, shop["agent_name"])
    agent = Agent()

    # 💬 Maintain session
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

    return service.handle(text)

