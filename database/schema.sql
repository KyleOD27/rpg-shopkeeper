-- USERS TABLE
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT UNIQUE NOT NULL,
    user_name TEXT,
    subscription_tier TEXT CHECK(subscription_tier IN ('Free', 'Adventurer', 'DM', 'Guild', 'ADMIN')) DEFAULT 'Free',
    lifetime_access BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active_character_id INTEGER,
    FOREIGN KEY(active_character_id) REFERENCES characters(character_id)
);


-- PARTIES TABLE
CREATE TABLE parties (
    party_id TEXT PRIMARY KEY,
    party_name TEXT,
    party_balance_cp INTEGER DEFAULT 100,
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
    deleted BOOLEAN DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(party_id) REFERENCES parties(party_id),
    UNIQUE(party_id, player_name, character_name)
);

DROP TABLE IF EXISTS items;

CREATE TABLE items (
    item_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    srd_index      TEXT UNIQUE,
    item_source    TEXT NOT NULL
    CHECK (item_source IN ('SRD','DM-GUIDE-2024','HOMEBREW'))
        DEFAULT 'Common',
    item_name      TEXT NOT NULL,

    -- categories
    equipment_category TEXT,
    armour_category    TEXT,
    weapon_category    TEXT,
    gear_category      TEXT,
    tool_category      TEXT,
    treasure_category  TEXT,

    -- weapon stats
    weapon_range   TEXT,
    category_range TEXT,
    damage_dice    TEXT,
    damage_type    TEXT,
    range_normal   INTEGER,
    range_long     INTEGER,

    -- armour stats
    base_ac               INTEGER,
    dex_bonus             BOOLEAN,          -- 0/1
    max_dex_bonus         INTEGER,
    str_minimum           INTEGER,
    stealth_disadvantage  BOOLEAN,          -- 0/1

    -- misc
    base_price     INTEGER DEFAULT 0,
    base_price_cp  INTEGER DEFAULT 0,
    price_unit     TEXT    DEFAULT 'gp',    -- cp | sp | ep | gp | pp
    weight         REAL,
    desc           TEXT,
    rarity         TEXT
        CHECK (rarity IN ('Common','Uncommon','Rare','Very Rare','Legendary', 'Artifact'))
        DEFAULT 'Common',

    -- magic enhancements
    magic_bonus    INTEGER DEFAULT 0
        CHECK (magic_bonus BETWEEN 0 AND 3),
    is_magical     BOOLEAN DEFAULT 0,

    -- ↳ FOREIGN KEY folded in
    CONSTRAINT fk_items_unit
        FOREIGN KEY (price_unit) REFERENCES currencies(unit)
);

-- Currency mapping
CREATE TABLE currencies (
    unit        TEXT PRIMARY KEY                -- cp | sp | ep | gp | pp
        CHECK (unit IN ('cp','sp','ep','gp','pp')),
    value_in_cp INTEGER NOT NULL                -- how many copper pieces one coin is worth
);

INSERT INTO currencies (unit, value_in_cp) VALUES
    ('cp',   1),      -- copper
    ('sp',  10),      -- silver  = 10 cp
    ('ep',  50),      -- electrum = 5 sp  = 50 cp
    ('gp', 100),      -- gold     = 10 sp = 100 cp
    ('pp',1000);      -- platinum = 10 gp = 1 000 cp

CREATE TABLE transaction_ledger (
    id            INTEGER  PRIMARY KEY AUTOINCREMENT,
    party_id      TEXT     NOT NULL,
    character_id  INTEGER,
    timestamp     DATETIME DEFAULT CURRENT_TIMESTAMP,

    action        TEXT     NOT NULL
                 CHECK (action IN ('BUY','SELL','HAGGLE','ADJUST',
                                   'DEPOSIT','WITHDRAW', 'UNDO', 'STASH_ADD', 'STASH_REMOVE')),
    item_name     TEXT,
    amount        INTEGER,
    currency      TEXT     DEFAULT 'gp',      -- cp | sp | ep | gp | pp
    balance_after INTEGER,
    details       TEXT,

    -- foreign keys
    CONSTRAINT fk_ledger_party
        FOREIGN KEY (party_id)     REFERENCES parties(party_id),
    CONSTRAINT fk_ledger_character
        FOREIGN KEY (character_id) REFERENCES characters(character_id),
    CONSTRAINT fk_ledger_unit
        FOREIGN KEY (currency)     REFERENCES currencies(unit)
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
    shop_id INTEGER NOT NULL,
    party_id TEXT,
    user_id INTEGER,
    character_id INTEGER,
    visit_count INTEGER NOT NULL DEFAULT 1,
    last_activity_utc DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (shop_id, party_id, user_id, character_id),
    FOREIGN KEY(party_id) REFERENCES parties(party_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(character_id) REFERENCES characters(character_id),
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

-- HAGGLE ATTEMPTS
CREATE TABLE haggle_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER,
    item_name TEXT NOT NULL,
    die_roll INTEGER NOT NULL,
    result TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_character
        FOREIGN KEY (character_id) REFERENCES characters(character_id)
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

CREATE TABLE party_stash (
    stash_id INTEGER PRIMARY KEY AUTOINCREMENT,
    party_id TEXT NOT NULL,
    character_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(party_id) REFERENCES parties(party_id),
    FOREIGN KEY(character_id) REFERENCES characters(character_id),
    FOREIGN KEY(item_id) REFERENCES items(item_id)
);
