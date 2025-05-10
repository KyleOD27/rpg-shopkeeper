class SessionManager:

    def __init__(self):
        self.debug('→ Entering __init__')
        self.sessions = {}
        self.debug('← Exiting __init__')

    def start_session(self, sender, conversation, agent, party, player_name,
        character_id, visit_count=None, shop_id=None):
        self.debug('→ Entering start_session')
        self.sessions[sender] = {'conversation': conversation, 'agent':
            agent, 'party': party, 'player_name': player_name,
            'character_id': character_id, 'visit_count': visit_count,
            'shop_id': shop_id}
        self.debug('← Exiting start_session')

    def get_session(self, sender):
        self.debug('→ Entering get_session')
        self.debug('← Exiting get_session')
        return self.sessions.get(sender)

    def end_session(self, sender):
        self.debug('→ Entering end_session')
        self.sessions.pop(sender, None)
        self.debug('← Exiting end_session')
