class SessionManager:

    def __init__(self):
        # simple in-memory store for sessions
        self.sessions = {}

    def start_session(
        self,
        sender,
        conversation,
        agent,
        party,
        player_name,
        character_id,
        character_name,
        visit_count=None,
        shop_id=None
    ):
        self.sessions[sender] = {
            'conversation': conversation,
            'agent': agent,
            'party': party,
            'player_name': player_name,
            'character_id': character_id,
            'character_name': character_name,
            'visit_count': visit_count,
            'shop_id': shop_id
        }

    def get_session(self, sender):
        return self.sessions.get(sender)

    def end_session(self, sender):
        self.sessions.pop(sender, None)
