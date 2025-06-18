-- Insert Shops
INSERT INTO shops (shop_name, agent_name, location) VALUES
('RPG Shop', 'Shopkeeper', 'RPG'),                          -- shop_id = 1
('Grizzlebeard''s Emporium', 'Grizzlebeard', 'Stonehelm Market'),
('Merlinda''s Curios', 'Merlinda', 'Everspring Forest'),
('Skabfang''s Shack', 'Skabfang', 'Goblin Warrens');

-- Insert Users
INSERT INTO users (phone_number, user_name, subscription_tier) VALUES
('+447000', 'Admin', 'ADMIN'),                      -- user_id = 1
('+447971548666', 'Kyle', 'DM'),                    -- user_id = 2
('+447851681361', 'Jaz', 'Adventurer'),             -- user_id = 3
('+447940133344', 'Will', 'Adventurer');            -- user_id = 4

-- Insert Party
INSERT INTO parties (party_id, party_name, party_balance_cp, reputation_score) VALUES
('group_001', 'The Cursed Cartographers', 100, 0);

-- Insert Party Owner (Kyle is the DM)
INSERT INTO party_owners (party_id, user_id) VALUES
('group_001', 1);

-- Add Users to Party Membership
INSERT INTO party_membership (party_id, user_id) VALUES
('group_001', 1),  -- Admin
('group_001', 2),  -- Kyle
('group_001', 3),  -- Jaz
('group_001', 4);  -- Will (DM)

-- Insert Characters
INSERT INTO characters (user_id, party_id, player_name, character_name, role) VALUES
(1, 'group_001', 'Admin', 'Jurgel', 'God'),
(2, 'group_001', 'Kyle', 'Kookyko', 'Wizard'),
(3, 'group_001', 'Jaz', 'JazzySmash', 'Bard'),
(4, 'group_001', 'Will', 'Will of the Meeple', 'Barbarian');

-- Insert Shop Items

-- Grant RPG Shop (shop_id = 1) access to all users
INSERT INTO user_shop_access (user_id, shop_id) VALUES
(1, 1),
(2, 1),
(3, 1),
(4, 1);
