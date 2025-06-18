from app.db import query_db, execute_db


def get_party_by_id(party_id):
    sql = 'SELECT * FROM parties WHERE party_id = ?'
    return query_db(sql, (party_id,), one=True)

def update_reputation(party_id, change):
    party = get_party_by_id(party_id)
    if not party:
        raise ValueError('Party not found')
    current_rep = party['reputation_score']
    new_rep = current_rep + change
    new_rep = max(-5, min(new_rep, 5))
    sql = 'UPDATE parties SET reputation_score = ? WHERE party_id = ?'
    execute_db(sql, (new_rep, party_id))


def create_party(party_id, party_name, starting_balance_cp=1000):
    sql = """
        INSERT INTO parties (party_id, party_name, party_balance_cp, reputation_score)
        VALUES (?, ?, ?, 0)
    """
    execute_db(sql, (party_id, party_name, starting_balance_cp))


def add_player_to_party(party_id, player_name, character_name, role, passcode):
    sql = """
        INSERT INTO players (party_id, player_name, character_name, role, passcode)
        VALUES (?, ?, ?, ?, ?)
    """
    try:
        execute_db(sql, (party_id, player_name, character_name, role, passcode)
            )
        print(f"[DEBUG] Player '{player_name}' added to party '{party_id}'.")
        return True
    except Exception as e:
        print(f'[ERROR] Failed to add player to party: {e}')
        return False


def get_party_by_id(party_id: str):
    return query_db('SELECT * FROM parties WHERE party_id = ?', (party_id,),
        one=True)

def update_party_balance_cp(party_id: str, new_party_balance_cp: int):
    execute_db('UPDATE parties SET  party_balance_cp = ? WHERE party_id = ?', (
        new_party_balance_cp, party_id))


def get_all_parties():
    sql = 'SELECT party_id, party_name FROM parties'
    return query_db(sql)


def generate_next_party_id():
    result = query_db('SELECT COUNT(*) as count FROM parties', one=True)
    next_id = result['count'] + 1
    return f'group_{str(next_id).zfill(3)}'


def add_new_party(party_name):
    party_id = generate_next_party_id()
    try:
        sql = """
            INSERT INTO parties (party_id, party_name,  party_balance_cp, reputation_score)
            VALUES (?, ?, 100, 0)
        """
        execute_db(sql, (party_id, party_name))
        print(f"[INFO] Party '{party_name}' created with ID '{party_id}'")
        return party_id
    except Exception as e:
        print(f'[ERROR] Failed to add party: {e}')
        return None


def get_party_balance_cp(party_id: int) ->int:
    return query_db('SELECT party_balance_cp FROM parties WHERE party_id = ?', (
        party_id,), one=True)[0]
