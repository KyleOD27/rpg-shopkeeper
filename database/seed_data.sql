-- Insert Shop Items
INSERT INTO items (item_name, description, base_price, rarity) VALUES
('Healing Potion', 'Restores 2d4+2 HP', 50, 'Common'),
('Iron Dagger', 'Simple but sharp', 5, 'Common'),
('Scroll of Identify', 'Reveals item properties', 80, 'Uncommon'),
('Cloak of Billowing', 'Dramatic wind effect on demand', 100, 'Uncommon'),
('Bag of Holding', 'Stores far more than it should', 500, 'Rare'),
('Mystery Box', 'Who knows what is inside? Might be cursed.', 150, 'Rare');

-- Insert Test Party
INSERT INTO parties (party_id, party_name, party_gold, reputation_score) VALUES
('group_001', 'The Cursed Cartographers', 100, 0);

-- Insert Test Players
INSERT INTO players (party_id, player_name, character_name, role, passcode) VALUES
('group_001', 'Alice', 'Thistle', 'Rogue', '1234'),
('group_001', 'Bob', 'Magnus', 'Wizard', '5678'),
('group_001', 'Charlie', 'Garruk', 'Barbarian','9012');

-- Insert Shops
INSERT INTO shops (shop_name, agent_name, location) VALUES
('RPG Shop', 'Shopkeeper', 'RPG'),
('Grizzlebeard''s Emporium', 'Grizzlebeard', 'Stonehelm Market'),
('Merlinda''s Curios', 'Merlinda', 'Everspring Forest'),
('Skabfang''s Shack', 'Skabfang', 'Goblin Warrens');
