# app/session_manager.py
class SessionManager:
    def __init__(self):
        self.sessions = {}

    # accept *optional* extra keyword args so old & new calls both succeed
    def start_session(
        self,
        sender,
        conversation,
        agent,
        party,
        player_name,
        character_id,
        visit_count=None,   # ⇦ new, default None
        shop_id=None        # ⇦ new, default None
    ):
        self.sessions[sender] = {
            "conversation": conversation,
            "agent":        agent,
            "party":        party,
            "player_name":  player_name,
            "character_id": character_id,
            "visit_count":  visit_count,
            "shop_id":      shop_id
        }

    def get_session(self, sender):
        return self.sessions.get(sender)

    def end_session(self, sender):
        self.sessions.pop(sender, None)
