-- Insert Shops
INSERT INTO shops (shop_name, agent_name, location) VALUES
('RPG Shop', 'Shopkeeper', 'RPG'),                          -- shop_id = 1
('Grizzlebeard''s Emporium', 'Grizzlebeard', 'Stonehelm Market'),
('Merlinda''s Curios', 'Merlinda', 'Everspring Forest'),
('Skabfang''s Shack', 'Skabfang', 'Goblin Warrens');

-- Insert Users
INSERT INTO users (phone_number, user_name, subscription_tier) VALUES
('+447971548666', 'Kyle', 'Adventurer'),       -- user_id = 1
('+447851681361', 'Jaz', 'Free'),              -- user_id = 2
('+447940133344', 'Will', 'DM');               -- user_id = 3

-- Insert Party
INSERT INTO parties (party_id, party_name, party_gold, reputation_score) VALUES
('group_001', 'The Cursed Cartographers', 100, 0);

-- Insert Party Owner (Kyle is the DM)
INSERT INTO party_owners (party_id, user_id) VALUES
('group_001', 1);

-- Add Users to Party Membership
INSERT INTO party_membership (party_id, user_id) VALUES
('group_001', 1),  -- Kyle
('group_001', 2),  -- Jaz
('group_001', 3);  -- Will (DM)

-- Insert Characters
INSERT INTO characters (user_id, party_id, player_name, character_name, role) VALUES
(1, 'group_001', 'Kyle', 'Kookyko', 'Wizard'),
(2, 'group_001', 'Jaz', 'JazzySmash', 'Bard'),
(3, 'group_001', 'Will', 'Will of the Meeple', 'Barbarian');

-- Insert Shop Items
INSERT INTO items (item_name, description, base_price, rarity) VALUES
('Healing Potion', 'Restores 2d4+2 HP', 50, 'Common'),
('Iron Dagger', 'Simple but sharp', 5, 'Common'),
('Scroll of Identify', 'Reveals item properties', 80, 'Uncommon'),
('Cloak of Billowing', 'Dramatic wind effect on demand', 100, 'Uncommon'),
('Bag of Holding', 'Stores far more than it should', 500, 'Rare'),
('Mystery Box', 'Who knows what is inside? Might be cursed.', 150, 'Rare');

-- Grant RPG Shop (shop_id = 1) access to all users
INSERT INTO user_shop_access (user_id, shop_id) VALUES
(1, 1),  -- Kyle
(2, 1),  -- Jaz
(3, 1);  -- Will
