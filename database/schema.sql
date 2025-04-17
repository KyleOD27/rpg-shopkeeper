-- Parties Table
CREATE TABLE parties (
    party_id TEXT PRIMARY KEY,              -- Unique ID (e.g. WhatsApp Group ID)
    party_name TEXT,                        -- Optional Party Name
    party_gold INTEGER DEFAULT 100,         -- Shared Party Gold
    reputation_score INTEGER DEFAULT 0      -- Reputation Score (-5 to +5)
);

-- Players Table
CREATE TABLE players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    party_id TEXT NOT NULL,                 -- Foreign Key to parties
    player_name TEXT NOT NULL,              -- Player's Name (real or character)
    character_name TEXT,                    -- Optional Character Name
    role TEXT,                              -- Optional Role (Wizard, Rogue etc.)
    passcode TEXT,                           -- Used for Login
    UNIQUE(party_id, player_name),          -- Prevent duplicates within a party
    FOREIGN KEY(party_id) REFERENCES parties(party_id)
);

-- Items Table (Shop Inventory)
CREATE TABLE items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,                -- Item Name
    description TEXT,                       -- Item Description
    base_price INTEGER NOT NULL,            -- Base Price in Gold
    rarity TEXT CHECK(rarity IN ('Common', 'Uncommon', 'Rare', 'Very Rare', 'Legendary'))
);

-- Transaction Ledger Table (History of Buys/Sells)
CREATE TABLE transaction_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    party_id TEXT NOT NULL,                 -- Party who transacted
    player_id INTEGER,                      -- Player involved (if applicable)
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action TEXT NOT NULL CHECK(action IN ('BUY', 'SELL', 'HAGGLE', 'ADJUST', 'DEPOSIT', 'WITHDRAW')),
    item_name TEXT,                         -- Item bought or sold
    amount INTEGER,                         -- Gold gained (+) or lost (-)
    balance_after INTEGER,                  -- Party Gold after transaction
    details TEXT,                           -- Notes / Flavour / Insult
    FOREIGN KEY(party_id) REFERENCES parties(party_id),
    FOREIGN KEY(player_id) REFERENCES players(player_id)
);

-- Reputation Events Table (Track Changes)
CREATE TABLE reputation_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    party_id TEXT NOT NULL,
    event_description TEXT,                 -- What happened
    change INTEGER,                         -- Reputation Change (+/-)
    event_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(party_id) REFERENCES parties(party_id)
);

CREATE TABLE IF NOT EXISTS shops (
    shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_name TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    location TEXT
);

CREATE TABLE IF NOT EXISTS shop_visits (
    party_id TEXT NOT NULL,
    shop_id INTEGER NOT NULL,
    visit_count INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (party_id, shop_id)
);

CREATE TABLE player_sessions (
    player_id TEXT PRIMARY KEY,
    current_state TEXT,
    pending_action TEXT,
    pending_item TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS session_state_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id TEXT NOT NULL,
    state TEXT NOT NULL,
    pending_action TEXT,
    pending_item TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
