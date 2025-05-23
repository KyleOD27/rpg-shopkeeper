-- USERS TABLE
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT UNIQUE NOT NULL,
    user_name TEXT,
    subscription_tier TEXT CHECK(subscription_tier IN ('Free', 'Adventurer', 'DM', 'Guild', 'ADMIN')) DEFAULT 'Free',
    lifetime_access BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PARTIES TABLE
CREATE TABLE parties (
    party_id TEXT PRIMARY KEY,
    party_name TEXT,
    party_gold INTEGER DEFAULT 100,
    reputation_score INTEGER DEFAULT 0
);

-- PARTY OWNERS
CREATE TABLE party_owners (
    party_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(party_id) REFERENCES parties(party_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

-- PARTY MEMBERSHIP
CREATE TABLE party_membership (
    party_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (party_id, user_id),
    FOREIGN KEY(party_id) REFERENCES parties(party_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

-- CHARACTERS TABLE
CREATE TABLE characters (
    character_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    party_id TEXT NOT NULL,
    player_name TEXT NOT NULL,
    character_name TEXT,
    role TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(party_id) REFERENCES parties(party_id),
    UNIQUE(party_id, player_name)
);

DROP TABLE IF EXISTS items;

CREATE TABLE items (
    item_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    srd_index      TEXT UNIQUE,
    item_name      TEXT NOT NULL,

    -- categories
    equipment_category TEXT,     -- “Armor”, “Weapon”, …
    armour_category    TEXT,     -- “Light”, “Medium”, “Heavy”, “Shield”
    weapon_category    TEXT,
    gear_category      TEXT,
    tool_category      TEXT,

    -- weapon stats
    weapon_range   TEXT,
    category_range TEXT,
    damage_dice    TEXT,
    damage_type    TEXT,
    range_normal   INTEGER,
    range_long     INTEGER,

    -- armour stats (★ NEW ★)
    base_ac               INTEGER,
    dex_bonus             BOOLEAN,  -- 0/1   (True if any Dex mod is allowed)
    max_dex_bonus         INTEGER,  -- NULL or 2
    str_minimum           INTEGER,  -- NULL if none
    stealth_disadvantage  BOOLEAN,  -- 0/1

    -- misc
    base_price     INTEGER DEFAULT 0,
    price_unit     TEXT    DEFAULT 'gp',
    weight         REAL,
    desc           TEXT,
    rarity         TEXT
        CHECK(rarity IN ('Common', 'Uncommon','Rare','Very Rare','Legendary'))
        DEFAULT 'Common'
);



-- TRANSACTION LEDGER
CREATE TABLE transaction_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    party_id TEXT NOT NULL,
    character_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action TEXT NOT NULL CHECK(action IN ('BUY', 'SELL', 'HAGGLE', 'ADJUST', 'DEPOSIT', 'WITHDRAW')),
    item_name TEXT,
    amount INTEGER,
    balance_after INTEGER,
    details TEXT,
    FOREIGN KEY(party_id) REFERENCES parties(party_id),
    FOREIGN KEY(character_id) REFERENCES characters(character_id)
);

-- REPUTATION EVENTS
CREATE TABLE reputation_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    party_id TEXT NOT NULL,
    event_description TEXT,
    change INTEGER,
    event_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(party_id) REFERENCES parties(party_id)
);

-- SHOPS TABLE
CREATE TABLE shops (
    shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_name TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    location TEXT
);

-- SHOP VISITS
CREATE TABLE shop_visits (
    party_id TEXT NOT NULL,
    shop_id INTEGER NOT NULL,
    visit_count INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (party_id, shop_id),
    FOREIGN KEY(party_id) REFERENCES parties(party_id),
    FOREIGN KEY(shop_id) REFERENCES shops(shop_id)
);

-- CHARACTER SESSION STATE
CREATE TABLE character_sessions (
    character_id INTEGER PRIMARY KEY,
    current_state TEXT,
    pending_action TEXT,
    pending_item TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(character_id) REFERENCES characters(character_id)
);

-- SESSION STATE LOG
CREATE TABLE session_state_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    state TEXT NOT NULL,
    pending_action TEXT,
    pending_item TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(character_id) REFERENCES characters(character_id)
);

-- USER SHOP ACCESS TABLE
CREATE TABLE user_shop_access (
    user_id INTEGER NOT NULL,
    shop_id INTEGER NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, shop_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(shop_id) REFERENCES shops(shop_id)
);

CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action TEXT,
    details TEXT
);

CREATE TABLE audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   DATETIME  DEFAULT CURRENT_TIMESTAMP,
    entity_type TEXT      NOT NULL,
    entity_id   TEXT      NOT NULL,
    field       TEXT      NOT NULL,
    old_value   TEXT,
    new_value   TEXT,
    changed_by  INTEGER,
    FOREIGN KEY(changed_by) REFERENCES users(user_id)
);
