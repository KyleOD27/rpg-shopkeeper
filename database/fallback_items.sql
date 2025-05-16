-- database/fallback_items.sql
-- -----------------------------------------------------------------
-- Minimal local seed so tests pass even when the SRD HTTP fetch fails
-- or the --no-srd flag is used.  Feel free to extend this list with
-- additional gear, weapons, armour, etc.
-- -----------------------------------------------------------------

INSERT INTO items (
    srd_index,
    item_name,
    equipment_category,
    gear_category,
    base_price,
    price_unit,
    weight,
    desc,
    rarity
) VALUES
    -- A reliable healing consumable every party recognises
    ('potion-of-healing',
     'Potion of Healing',
     'Adventuring Gear',
     'Potion',
     50,
     'gp',
     0.5,
     'A crimson liquid that glimmers when agitated; restores 2d4+2 HP.',
     'Common'),

    -- Cheap source of fire and illumination
    ('torch',
     'Torch',
     'Adventuring Gear',
     'Standard Gear',
     0.01,
     'gp',
     1.0,
     'Wooden torch that burns for 1 hour, shedding bright light in a 20‑foot radius.',
     'Common'),

    -- A ubiquitous simple weapon
    ('dagger',
     'Dagger',
     'Weapon',
     NULL,
     2,
     'gp',
     1.0,
     'Simple melee weapon (finesse, light, thrown 20/60).',
     'Common');
