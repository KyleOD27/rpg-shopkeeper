from app.db import query_db, execute_db


def get_user_by_phone(phone_number):
    sql = 'SELECT * FROM users WHERE phone_number = ?'
    return query_db(sql, (phone_number,), one=True)


def get_all_characters_in_party(party_id):
    sql = 'SELECT * FROM characters WHERE party_id = ?'
    return query_db(sql, (party_id,))


def get_character_by_id(character_id):
    sql = 'SELECT * FROM characters WHERE character_id = ?'
    return query_db(sql, (character_id,), one=True)


def get_character_name_by_id(character_id):
    sql = 'SELECT character_name FROM characters WHERE character_id = ?'
    row = query_db(sql, (character_id,), one=True)
    return row['character_name'] if row else None


def get_character_id_by_player_name(player_name):
    sql = 'SELECT character_id FROM characters WHERE player_name = ?'
    row = query_db(sql, (player_name,), one=True)
    return row['character_id'] if row else None


def add_character_to_party(phone_number, party_id, player_name,
    character_name=None, role=None):
    user = get_user_by_phone(phone_number)
    if not user:
        print(f'[INFO] No user found with phone {phone_number}. Creating one.')
        execute_db('INSERT INTO users (phone_number, user_name) VALUES (?, ?)',
            (phone_number, player_name))
        user = get_user_by_phone(phone_number)
    user_id = user['user_id']
    # Duplicate check is now by character_name + party_id, not player_name
    sql_check = (
        'SELECT character_id FROM characters WHERE LOWER(character_name) = ? AND party_id = ?'
    )
    existing = query_db(sql_check, (character_name.lower(), party_id), one=True)
    if existing:
        print(f"[INFO] Character '{character_name}' already exists in this party.")
        return None
    sql_insert = """
        INSERT INTO characters (user_id, party_id, player_name, character_name, role)
        VALUES (?, ?, ?, ?, ?)
    """
    execute_db(sql_insert, (user_id, party_id, player_name, character_name, role))
    print(f"[INFO] New character '{character_name}' added successfully!")
    new_character = query_db(
        'SELECT character_id FROM characters WHERE LOWER(character_name) = ? AND party_id = ?',
        (character_name.lower(), party_id), one=True)
    return new_character['character_id'] if new_character else None



def get_user_by_phone(phone_number):
    sql = 'SELECT * FROM users WHERE phone_number = ?'
    return query_db(sql, (phone_number,), one=True)


from app.db import query_db


def get_all_owned_characters(dm_id):
    """
    Retrieve all characters belonging to the DM's parties.
    """
    sql_parties = 'SELECT party_id FROM parties WHERE dm_id = ?'
    party_ids = query_db(sql_parties, (dm_id,))
    if not party_ids:
        return []
    sql_characters = (
        """
        SELECT * FROM characters WHERE party_id IN ({})
    """
        .format(','.join(str(p['party_id']) for p in party_ids)))
    return query_db(sql_characters)
