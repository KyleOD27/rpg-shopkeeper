# Armor seed rows with armour_category included
from typing import Optional

#--WEARABLES-START----------------------------------------
ARMOR_ROWS: list[tuple[str, str, int, str, int, bool, int, int, bool, int, str, int, bool, str, str]] = [
    ('leather-armor-plus-one', 'Leather Armor +1', 4000, 'gp', 11, True, 0, 0, False, 10, 'You have a +1 bonus to AC while wearing this armor.', 1, True, 'Rare', 'Light'),
    ('padded-armor-plus-one', 'Padded Armor +1', 4000, 'gp', 11, True, 0, 0, True, 8, 'You have a +1 bonus to AC while wearing this armor.', 1, True, 'Rare', 'Light'),
    ('shield-plus-one', 'Shield +1', 4000, 'gp', 2, False, 0, 0, False, 6, 'You have a +1 bonus to AC while wearing this armor.', 1, True, 'Rare', 'Shield'),
    ('studded-leather-armor-plus-one', 'Studded Leather Armor +1', 4000, 'gp', 12, True, 0, 0, True, 13, 'You have a +1 bonus to AC while wearing this armor.', 1, True, 'Rare', 'Medium'),
    ('leather-armor-plus-two', 'Leather Armor +2', 40000, 'gp', 11, True, 0, 0, False, 10, 'You have a +2 bonus to AC while wearing this armor.', 2, True, 'Very Rare', 'Light'),
    ('padded-armor-plus-two', 'Padded Armor +2', 40000, 'gp', 11, True, 0, 0, True, 8, 'You have a +2 bonus to AC while wearing this armor.', 2, True, 'Very Rare', 'Light'),
    ('shield-plus-two', 'Shield +2', 40000, 'gp', 2, False, 0, 0, False, 6, 'You have a +2 bonus to AC while wearing this armor.', 2, True, 'Very Rare', 'Shield'),
    ('studded-leather-armor-plus-two', 'Studded Leather Armor +2', 40000, 'gp', 12, True, 0, 0, False, 13, 'You have a +2 bonus to AC while wearing this armor.', 2, True, 'Very Rare', 'Medium'),
    ('leather-armor-plus-three', 'Leather Armor +3', 200000, 'gp', 11, True, 0, 0, False, 10, 'You have a +3 bonus to AC while wearing this armor.', 3, True, 'Legendary', 'Light'),
    ('padded-armor-plus-three', 'Padded Armor +3', 200000, 'gp', 11, True, 0, 0, True, 8, 'You have a +3 bonus to AC while wearing this armor.', 3, True, 'Legendary', 'Light'),
    ('shield-plus-three', 'Shield +3', 200000, 'gp', 2, False, 0, 0, False, 6, 'You have a +3 bonus to AC while wearing this armor.', 3, True, 'Legendary', 'Shield'),
    ('studded-leather-armor-plus-three', 'Studded Leather Armor +3', 200000, 'gp', 12, True, 0, 0, False, 13, 'You have a +3 bonus to AC while wearing this armor.', 3, True, 'Legendary', 'Medium'),
    ('breastplate-plus-one', 'Breastplate +1', 4000, 'gp', 14, True, 2, 0, False, 20, 'You have a +1 bonus to AC while wearing this armor.', 1, True, 'Rare', 'Medium'),
    ('chain-mail-plus-one', 'Chain Mail +1', 4000, 'gp', 16, False, 0, 13, True, 55, 'You have a +1 bonus to AC while wearing this armor.', 1, True, 'Rare', 'Heavy'),
    ('chain-shirt-plus-one', 'Chain Shirt +1', 4000, 'gp', 13, True, 2, 0, False, 20, 'You have a +1 bonus to AC while wearing this armor.', 1, True, 'Rare', 'Medium'),
    ('half-plate-armor-plus-one', 'Half Plate Armor +1', 4000, 'gp', 15, True, 2, 0, True, 40, 'You have a +1 bonus to AC while wearing this armor.', 1, True, 'Rare', 'Medium'),
    ('hide-armor-plus-one', 'Hide Armor +1', 4000, 'gp', 12, True, 2, 0, False, 12, 'You have a +1 bonus to AC while wearing this armor.', 1, True, 'Rare', 'Medium'),
    ('plate-armor-plus-one', 'Plate Armor +1', 4000, 'gp', 18, False, 0, 15, True, 65, 'You have a +1 bonus to AC while wearing this armor.', 1, True, 'Rare', 'Heavy'),
    ('ring-mail-plus-one', 'Ring Mail +1', 4000, 'gp', 14, False, 0, 0, True, 40, 'You have a +1 bonus to AC while wearing this armor.', 1, True, 'Rare', 'Heavy'),
    ('scale-mail-plus-one', 'Scale Mail +1', 4000, 'gp', 14, True, 2, 0, True, 45, 'You have a +1 bonus to AC while wearing this armor.', 1, True, 'Rare', 'Medium'),
    ('splint-armor-plus-one', 'Splint Armor +1', 4000, 'gp', 17, False, 0, 15, True, 60, 'You have a +1 bonus to AC while wearing this armor.', 1, True, 'Rare', 'Heavy'),
    ('breastplate-plus-two', 'Breastplate +2', 40000, 'gp', 14, True, 2, 0, False, 20, 'You have a +2 bonus to AC while wearing this armor.', 2, True, 'Very Rare', 'Medium'),
    ('chain-mail-plus-two', 'Chain Mail +2', 40000, 'gp', 16, False, 0, 13, True, 55, 'You have a +2 bonus to AC while wearing this armor.', 2, True, 'Very Rare', 'Heavy'),
    ('chain-shirt-plus-two', 'Chain Shirt +2', 40000, 'gp', 13, True, 2, 0, False, 20, 'You have a +2 bonus to AC while wearing this armor.', 2, True, 'Very Rare', 'Medium'),
    ('half-plate-armor-plus-two', 'Half Plate Armor +2', 40000, 'gp', 15, True, 2, 0, True, 40, 'You have a +2 bonus to AC while wearing this armor.', 2, True, 'Very Rare', 'Medium'),
    ('hide-armor-plus-two', 'Hide Armor +2', 40000, 'gp', 12, True, 2, 0, False, 12, 'You have a +2 bonus to AC while wearing this armor.', 2, True, 'Very Rare', 'Medium'),
    ('plate-armor-plus-two', 'Plate Armor +2', 40000, 'gp', 18, False, 0, 15, True, 65, 'You have a +2 bonus to AC while wearing this armor.', 2, True, 'Very Rare', 'Heavy'),
    ('ring-mail-plus-two', 'Ring Mail +2', 40000, 'gp', 14, False, 0, 0, True, 40, 'You have a +2 bonus to AC while wearing this armor.', 2, True, 'Very Rare', 'Heavy'),
    ('scale-mail-plus-two', 'Scale Mail +2', 40000, 'gp', 14, True, 2, 0, True, 45, 'You have a +2 bonus to AC while wearing this armor.', 2, True, 'Very Rare', 'Medium'),
    ('splint-armor-plus-two', 'Splint Armor +2', 40000, 'gp', 17, False, 0, 15, True, 60, 'You have a +2 bonus to AC while wearing this armor.', 2, True, 'Very Rare', 'Heavy'),
    ('breastplate-plus-three', 'Breastplate +3', 200000, 'gp', 14, True, 2, 0, False, 20, 'You have a +3 bonus to AC while wearing this armor.', 3, True, 'Legendary', 'Medium'),
    ('chain-mail-plus-three', 'Chain Mail +3', 200000, 'gp', 16, False, 0, 13, True, 55, 'You have a +3 bonus to AC while wearing this armor.', 3, True, 'Legendary', 'Heavy'),
    ('chain-shirt-plus-three', 'Chain Shirt +3', 200000, 'gp', 13, True, 2, 0, False, 20, 'You have a +3 bonus to AC while wearing this armor.', 3, True, 'Legendary', 'Medium'),
    ('half-plate-armor-plus-three', 'Half Plate Armor +3', 200000, 'gp', 15, True, 2, 0, True, 40, 'You have a +3 bonus to AC while wearing this armor.', 3, True, 'Legendary', 'Medium'),
    ('hide-armor-plus-three', 'Hide Armor +3', 200000, 'gp', 12, True, 2, 0, False, 12, 'You have a +3 bonus to AC while wearing this armor.', 3, True, 'Legendary', 'Medium'),
    ('plate-armor-plus-three', 'Plate Armor +3', 200000, 'gp', 18, False, 0, 15, True, 65, 'You have a +3 bonus to AC while wearing this armor.', 3, True, 'Legendary', 'Heavy'),
    ('ring-mail-plus-three', 'Ring Mail +3', 200000, 'gp', 14, False, 0, 0, True, 40, 'You have a +3 bonus to AC while wearing this armor.', 3, True, 'Legendary', 'Heavy'),
    ('scale-mail-plus-three', 'Scale Mail +3', 200000, 'gp', 14, True, 2, 0, True, 45, 'You have a +3 bonus to AC while wearing this armor.', 3, True, 'Legendary', 'Medium'),
    ('splint-armor-plus-three', 'Splint Armor +3', 200000, 'gp', 17, False, 0, 15, True, 60, 'You have a +3 bonus to AC while wearing this armor.', 3, True, 'Legendary', 'Heavy'),
    ('adamantine-breastplate', 'Adamantine Breastplate', 400, 'gp', 14, True, 2, 0, False, 20, 'This suit of armor is reinforced with adamantine, one of the hardest substances in existence. While you’re wearing it, any\xa0Critical Hit\xa0against you becomes a normal hit.', 0, True, 'Uncommon', 'Medium'),
    ('adamantine-chain-mail', 'Adamantine Chain Mail', 400, 'gp', 16, False, 0, 13, True, 55, 'This suit of armor is reinforced with adamantine, one of the hardest substances in existence. While you’re wearing it, any\xa0Critical Hit\xa0against you becomes a normal hit.', 0, True, 'Uncommon', 'Heavy'),
    ('adamantine-chain-shirt', 'Adamantine Chain Shirt', 400, 'gp', 13, True, 2, 0, False, 20, 'This suit of armor is reinforced with adamantine, one of the hardest substances in existence. While you’re wearing it, any\xa0Critical Hit\xa0against you becomes a normal hit.', 0, True, 'Uncommon', 'Medium'),
    ('adamantine-half-plate-armor', 'Adamantine Half Plate Armor', 400, 'gp', 15, True, 2, 0, True, 40, 'This suit of armor is reinforced with adamantine, one of the hardest substances in existence. While you’re wearing it, any\xa0Critical Hit\xa0against you becomes a normal hit.', 0, True, 'Uncommon', 'Medium'),
    ('adamantine-plate-armor', 'Adamantine Plate Armor', 400, 'gp', 18, False, 0, 15, True, 65, 'This suit of armor is reinforced with adamantine, one of the hardest substances in existence. While you’re wearing it, any\xa0Critical Hit\xa0against you becomes a normal hit.', 0, True, 'Uncommon', 'Heavy'),
    ('adamantine-ring-mail', 'Adamantine Ring Mail', 400, 'gp', 14, False, 0, 0, True, 40, 'This suit of armor is reinforced with adamantine, one of the hardest substances in existence. While you’re wearing it, any\xa0Critical Hit\xa0against you becomes a normal hit.', 0, True, 'Uncommon', 'Heavy'),
    ('adamantine-scale-mail', 'Adamantine Scale Mail', 400, 'gp', 14, True, 2, 0, True, 45, 'This suit of armor is reinforced with adamantine, one of the hardest substances in existence. While you’re wearing it, any\xa0Critical Hit\xa0against you becomes a normal hit.', 0, True, 'Uncommon', 'Medium'),
    ('adamantine-splint-armor', 'Adamantine Splint Armor', 400, 'gp', 17, False, 0, 15, True, 60, 'This suit of armor is reinforced with adamantine, one of the hardest substances in existence. While you’re wearing it, any\xa0Critical Hit\xa0against you becomes a normal hit.', 0, True, 'Uncommon', 'Heavy'),
]
WEAPON_ROWS: list[tuple[str, str, int, str, str, str, str, str, int, int, float, str, int, bool, str, str]] = [

    ('battleaxe-plus-one', 'Battleaxe +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d8', 'slashing', 0, 0, 4,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Axe'),
    ('battleaxe-plus-two', 'Battleaxe +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d8', 'slashing', 0, 0, 4,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Axe'),
    ('battleaxe-plus-three', 'Battleaxe +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d8', 'slashing', 0, 0, 4,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Axe'),
    ('blowgun-plus-one', 'Blowgun +1', 4000, 'gp', 'Ranged', 'Martial Ranged', '1', 'piercing', 25, 100, 1,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Blowgun'),
    ('blowgun-plus-two', 'Blowgun +2', 40000, 'gp', 'Ranged', 'Martial Ranged', '1', 'piercing', 25, 100, 1,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Blowgun'),
    ('blowgun-plus-three', 'Blowgun +3', 200000, 'gp', 'Ranged', 'Martial Ranged', '1', 'piercing', 25, 100, 1,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Blowgun'),
    ('club-plus-one', 'Club +1', 4000, 'gp', 'Melee', 'Simple Melee', '1d4', 'bludgeoning', 0, 0, 2,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Bludgeon'),
    ('club-plus-two', 'Club +2', 40000, 'gp', 'Melee', 'Simple Melee', '1d4', 'bludgeoning', 0, 0, 2,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Bludgeon'),
    ('club-plus-three', 'Club +3', 200000, 'gp', 'Melee', 'Simple Melee', '1d4', 'bludgeoning', 0, 0, 2,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Bludgeon'),

    ('crossbow-hand-plus-one', 'Crossbow, hand +1', 4000, 'gp', 'Ranged', 'Martial Ranged', '1d6', 'piercing', 30, 120,
     3, 'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Bow'),
    ('crossbow-hand-plus-two', 'Crossbow, hand +2', 40000, 'gp', 'Ranged', 'Martial Ranged', '1d6', 'piercing', 30, 120,
     3, 'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Bow'),
    ('crossbow-hand-plus-three', 'Crossbow, hand +3', 200000, 'gp', 'Ranged', 'Martial Ranged', '1d6', 'piercing', 30,
     120, 3, 'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary',
     'Bow'),
    ('crossbow-heavy-plus-one', 'Crossbow, heavy +1', 4000, 'gp', 'Ranged', 'Martial Ranged', '1d10', 'piercing', 100,
     400, 18, 'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Bow'),
    ('crossbow-heavy-plus-two', 'Crossbow, heavy +2', 40000, 'gp', 'Ranged', 'Martial Ranged', '1d10', 'piercing', 100,
     400, 18, 'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare',
     'Bow'),
    ('crossbow-heavy-plus-three', 'Crossbow, heavy +3', 200000, 'gp', 'Ranged', 'Martial Ranged', '1d10', 'piercing',
     100, 400, 18, 'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary',
     'Bow'),
    ('crossbow-light-plus-one', 'Crossbow, light +1', 4000, 'gp', 'Ranged', 'Simple Ranged', '1d8', 'piercing', 80, 320,
     5, 'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Bow'),
    ('crossbow-light-plus-two', 'Crossbow, light +2', 40000, 'gp', 'Ranged', 'Simple Ranged', '1d8', 'piercing', 80,
     320, 5, 'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare',
     'Bow'),
    ('crossbow-light-plus-three', 'Crossbow, light +3', 200000, 'gp', 'Ranged', 'Simple Ranged', '1d8', 'piercing', 80,
     320, 5, 'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary',
     'Bow'),
    ('dagger-plus-one', 'Dagger +1', 4000, 'gp', 'Melee', 'Simple Melee', '1d4', 'piercing', 20, 60, 1,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Dagger'),
    ('dagger-plus-two', 'Dagger +2', 40000, 'gp', 'Melee', 'Simple Melee', '1d4', 'piercing', 20, 60, 1,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Dagger'),
    ('dagger-plus-three', 'Dagger +3', 200000, 'gp', 'Melee', 'Simple Melee', '1d4', 'piercing', 20, 60, 1,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Dagger'),

    ('dart-plus-one', 'Dart +1', 4000, 'gp', 'Ranged', 'Simple Ranged', '1d4', 'piercing', 20, 60, 0.25,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Thrown'),
    ('dart-plus-two', 'Dart +2', 40000, 'gp', 'Ranged', 'Simple Ranged', '1d4', 'piercing', 20, 60, 0.25,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Thrown'),
    ('dart-plus-three', 'Dart +3', 200000, 'gp', 'Ranged', 'Simple Ranged', '1d4', 'piercing', 20, 60, 0.25,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Thrown'),
    ('flail-plus-one', 'Flail +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d8', 'bludgeoning', 0, 0, 2,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Bludgeon'),
    ('flail-plus-two', 'Flail +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d8', 'bludgeoning', 0, 0, 2,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Bludgeon'),
    ('flail-plus-three', 'Flail +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d8', 'bludgeoning', 0, 0, 2,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Bludgeon'),
    ('glaive-plus-one', 'Glaive +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d10', 'slashing', 0, 0, 6,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Polearm'),
    ('glaive-plus-two', 'Glaive +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d10', 'slashing', 0, 0, 6,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Polearm'),
    ('glaive-plus-three', 'Glaive +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d10', 'slashing', 0, 0, 6,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Polearm'),
    ('greataxe-plus-one', 'Greataxe +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d12', 'slashing', 0, 0, 7,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Axe'),
    ('greataxe-plus-two', 'Greataxe +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d12', 'slashing', 0, 0, 7,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Axe'),
    ('greataxe-plus-three', 'Greataxe +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d12', 'slashing', 0, 0, 7,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Axe'),
    ('greatclub-plus-one', 'Greatclub +1', 4000, 'gp', 'Melee', 'Simple Melee', '1d8', 'bludgeoning', 0, 0, 10,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Bludgeon'),

    ('greatclub-plus-two', 'Greatclub +2', 40000, 'gp', 'Melee', 'Simple Melee', '1d8', 'bludgeoning', 0, 0, 10,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Bludgeon'),
    ('greatclub-plus-three', 'Greatclub +3', 200000, 'gp', 'Melee', 'Simple Melee', '1d8', 'bludgeoning', 0, 0, 10,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Bludgeon'),
    ('greatsword-plus-one', 'Greatsword +1', 4000, 'gp', 'Melee', 'Martial Melee', '2d6', 'slashing', 0, 0, 6,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Unknown'),
    ('greatsword-plus-two', 'Greatsword +2', 40000, 'gp', 'Melee', 'Martial Melee', '2d6', 'slashing', 0, 0, 6,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Unknown'),
    ('greatsword-plus-three', 'Greatsword +3', 200000, 'gp', 'Melee', 'Martial Melee', '2d6', 'slashing', 0, 0, 6,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Unknown'),
    ('halberd-plus-one', 'Halberd +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d10', 'slashing', 0, 0, 6,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Polearm'),
    ('halberd-plus-two', 'Halberd +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d10', 'slashing', 0, 0, 6,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Polearm'),
    ('halberd-plus-three', 'Halberd +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d10', 'slashing', 0, 0, 6,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Polearm'),
    ('handaxe-plus-one', 'Handaxe +1', 4000, 'gp', 'Melee', 'Simple Melee', '1d6', 'slashing', 20, 60, 2,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Axe'),
    ('handaxe-plus-two', 'Handaxe +2', 40000, 'gp', 'Melee', 'Simple Melee', '1d6', 'slashing', 20, 60, 2,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Axe'),
    ('handaxe-plus-three', 'Handaxe +3', 200000, 'gp', 'Melee', 'Simple Melee', '1d6', 'slashing', 20, 60, 2,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Axe'),
    ('javelin-plus-one', 'Javelin +1', 4000, 'gp', 'Melee', 'Simple Melee', '1d6', 'piercing', 30, 120, 2,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Spear'),
    ('javelin-plus-two', 'Javelin +2', 40000, 'gp', 'Melee', 'Simple Melee', '1d6', 'piercing', 30, 120, 2,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Spear'),
    ('javelin-plus-three', 'Javelin +3', 200000, 'gp', 'Melee', 'Simple Melee', '1d6', 'piercing', 30, 120, 2,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Spear'),

    ('lance-plus-one', 'Lance +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d12', 'piercing', 0, 0, 6,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Polearm'),
    ('lance-plus-two', 'Lance +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d12', 'piercing', 0, 0, 6,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Polearm'),
    ('lance-plus-three', 'Lance +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d12', 'piercing', 0, 0, 6,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Polearm'),
    ('light-hammer-plus-one', 'Light hammer +1', 4000, 'gp', 'Melee', 'Simple Melee', '1d4', 'bludgeoning', 20, 60, 2,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Hammer'),
    ('light-hammer-plus-two', 'Light hammer +2', 40000, 'gp', 'Melee', 'Simple Melee', '1d4', 'bludgeoning', 20, 60, 2,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Hammer'),
    ('light-hammer-plus-three', 'Light hammer +3', 200000, 'gp', 'Melee', 'Simple Melee', '1d4', 'bludgeoning', 20, 60,
     2, 'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Hammer'),
    ('longbow-plus-one', 'Longbow +1', 4000, 'gp', 'Ranged', 'Martial Ranged', '1d8', 'piercing', 150, 600, 2,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Bow'),
    ('longbow-plus-two', 'Longbow +2', 40000, 'gp', 'Ranged', 'Martial Ranged', '1d8', 'piercing', 150, 600, 2,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Bow'),
    ('longbow-plus-three', 'Longbow +3', 200000, 'gp', 'Ranged', 'Martial Ranged', '1d8', 'piercing', 150, 600, 2,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Bow'),
    ('longsword-plus-one', 'Longsword +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d8', 'slashing', 0, 0, 3,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Sword'),
    ('longsword-plus-two', 'Longsword +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d8', 'slashing', 0, 0, 3,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Sword'),
    ('longsword-plus-three', 'Longsword +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d8', 'slashing', 0, 0, 3,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Sword'),
    ('mace-plus-one', 'Mace +1', 4000, 'gp', 'Melee', 'Simple Melee', '1d6', 'bludgeoning', 0, 0, 4,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Bludgeon'),
    ('mace-plus-two', 'Mace +2', 40000, 'gp', 'Melee', 'Simple Melee', '1d6', 'bludgeoning', 0, 0, 4,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Bludgeon'),
    ('mace-plus-three', 'Mace +3', 200000, 'gp', 'Melee', 'Simple Melee', '1d6', 'bludgeoning', 0, 0, 4,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Bludgeon'),
    ('maul-plus-one', 'Maul +1', 4000, 'gp', 'Melee', 'Martial Melee', '2d6', 'bludgeoning', 0, 0, 10,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Bludgeon'),
    ('maul-plus-two', 'Maul +2', 40000, 'gp', 'Melee', 'Martial Melee', '2d6', 'bludgeoning', 0, 0, 10,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Bludgeon'),
    ('maul-plus-three', 'Maul +3', 200000, 'gp', 'Melee', 'Martial Melee', '2d6', 'bludgeoning', 0, 0, 10,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Bludgeon'),

    ('morningstar-plus-one', 'Morningstar +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d8', 'piercing', 0, 0, 4,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Spiked'),
    ('morningstar-plus-two', 'Morningstar +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d8', 'piercing', 0, 0, 4,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Spiked'),
    ('morningstar-plus-three', 'Morningstar +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d8', 'piercing', 0, 0, 4,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Spiked'),
    ('net-plus-one', 'Net +1', 4000, 'gp', 'Ranged', 'Martial Ranged', '–', '–', 5, 15, 3,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Net'),
    ('net-plus-two', 'Net +2', 40000, 'gp', 'Ranged', 'Martial Ranged', '–', '–', 5, 15, 3,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Net'),
    ('net-plus-three', 'Net +3', 200000, 'gp', 'Ranged', 'Martial Ranged', '–', '–', 5, 15, 3,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Net'),
    ('pike-plus-one', 'Pike +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d10', 'piercing', 0, 0, 18,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Polearm'),
    ('pike-plus-two', 'Pike +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d10', 'piercing', 0, 0, 18,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Polearm'),
    ('pike-plus-three', 'Pike +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d10', 'piercing', 0, 0, 18,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Polearm'),
    ('quarterstaff-plus-one', 'Quarterstaff +1', 4000, 'gp', 'Melee', 'Simple Melee', '1d6', 'bludgeoning', 0, 0, 4,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Staff'),
    ('quarterstaff-plus-two', 'Quarterstaff +2', 40000, 'gp', 'Melee', 'Simple Melee', '1d6', 'bludgeoning', 0, 0, 4,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Staff'),
    ('quarterstaff-plus-three', 'Quarterstaff +3', 200000, 'gp', 'Melee', 'Simple Melee', '1d6', 'bludgeoning', 0, 0, 4,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Staff'),
    ('rapier-plus-one', 'Rapier +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d8', 'piercing', 0, 0, 2,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Sword'),
    ('rapier-plus-two', 'Rapier +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d8', 'piercing', 0, 0, 2,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Sword'),
    ('rapier-plus-three', 'Rapier +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d8', 'piercing', 0, 0, 2,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Sword'),
    ('scimitar-plus-one', 'Scimitar +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d6', 'slashing', 0, 0, 3,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Sword'),
    ('scimitar-plus-two', 'Scimitar +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d6', 'slashing', 0, 0, 3,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Sword'),
    ('scimitar-plus-three', 'Scimitar +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d6', 'slashing', 0, 0, 3,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Sword'),
    ('shortbow-plus-one', 'Shortbow +1', 4000, 'gp', 'Ranged', 'Simple Ranged', '1d6', 'piercing', 80, 320, 2,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Bow'),
    ('shortbow-plus-two', 'Shortbow +2', 40000, 'gp', 'Ranged', 'Simple Ranged', '1d6', 'piercing', 80, 320, 2,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Bow'),
    ('shortbow-plus-three', 'Shortbow +3', 200000, 'gp', 'Ranged', 'Simple Ranged', '1d6', 'piercing', 80, 320, 2,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Bow'),
    ('shortsword-plus-one', 'Shortsword +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d6', 'piercing', 0, 0, 2,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Sword'),
    ('shortsword-plus-two', 'Shortsword +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d6', 'piercing', 0, 0, 2,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Sword'),
    ('shortsword-plus-three', 'Shortsword +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d6', 'piercing', 0, 0, 2,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Sword'),

    ('sickle-plus-one', 'Sickle +1', 4000, 'gp', 'Melee', 'Simple Melee', '1d4', 'slashing', 0, 0, 2,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Axe'),
    ('sickle-plus-two', 'Sickle +2', 40000, 'gp', 'Melee', 'Simple Melee', '1d4', 'slashing', 0, 0, 2,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Axe'),
    ('sickle-plus-three', 'Sickle +3', 200000, 'gp', 'Melee', 'Simple Melee', '1d4', 'slashing', 0, 0, 2,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Axe'),
    ('sling-plus-one', 'Sling +1', 4000, 'gp', 'Ranged', 'Simple Ranged', '1d4', 'bludgeoning', 30, 120, 0,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Thrown'),
    ('sling-plus-two', 'Sling +2', 40000, 'gp', 'Ranged', 'Simple Ranged', '1d4', 'bludgeoning', 30, 120, 0,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Thrown'),
    ('sling-plus-three', 'Sling +3', 200000, 'gp', 'Ranged', 'Simple Ranged', '1d4', 'bludgeoning', 30, 120, 0,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Thrown'),
    ('spear-plus-one', 'Spear +1', 4000, 'gp', 'Melee', 'Simple Melee', '1d6', 'piercing', 20, 60, 3,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Spear'),
    ('spear-plus-two', 'Spear +2', 40000, 'gp', 'Melee', 'Simple Melee', '1d6', 'piercing', 20, 60, 3,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Spear'),
    ('spear-plus-three', 'Spear +3', 200000, 'gp', 'Melee', 'Simple Melee', '1d6', 'piercing', 20, 60, 3,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Spear'),
    ('trident-plus-one', 'Trident +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d6', 'piercing', 20, 60, 4,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Spear'),
    ('trident-plus-two', 'Trident +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d6', 'piercing', 20, 60, 4,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Spear'),
    ('trident-plus-three', 'Trident +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d6', 'piercing', 20, 60, 4,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Spear'),
    ('war-pick-plus-one', 'War pick +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d8', 'piercing', 0, 0, 2,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Pick'),
    ('war-pick-plus-two', 'War pick +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d8', 'piercing', 0, 0, 2,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Pick'),
    ('war-pick-plus-three', 'War pick +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d8', 'piercing', 0, 0, 2,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Pick'),
    ('warhammer-plus-one', 'Warhammer +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d8', 'bludgeoning', 0, 0, 2,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Hammer'),
    ('warhammer-plus-two', 'Warhammer +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d8', 'bludgeoning', 0, 0, 2,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Hammer'),
    ('warhammer-plus-three', 'Warhammer +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d8', 'bludgeoning', 0, 0, 2,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Hammer'),
    ('whip-plus-one', 'Whip +1', 4000, 'gp', 'Melee', 'Martial Melee', '1d4', 'slashing', 0, 0, 3,
     'You have a +1 bonus to attack and damage rolls made with this magic weapon.', 1, True, 'Rare', 'Whip'),
    ('whip-plus-two', 'Whip +2', 40000, 'gp', 'Melee', 'Martial Melee', '1d4', 'slashing', 0, 0, 3,
     'You have a +2 bonus to attack and damage rolls made with this magic weapon.', 2, True, 'Very Rare', 'Whip'),
    ('whip-plus-three', 'Whip +3', 200000, 'gp', 'Melee', 'Martial Melee', '1d4', 'slashing', 0, 0, 3,
     'You have a +3 bonus to attack and damage rolls made with this magic weapon.', 3, True, 'Legendary', 'Whip'),

    ('adamantine-battleaxe', 'Adamantine Battleaxe', 500, 'gp', 'Melee', 'Martial Melee', '1d8', 'slashing', 0, 0, 4,
     'This magic weapon’s strikes always count as critical hits.', 0, True, 'Uncommon', 'Axe'),
    ('adamantine-greatsword', 'Adamantine Greatsword', 500, 'gp', 'Melee', 'Martial Melee', '2d6', 'slashing', 0, 0, 6,
     'This magic weapon’s strikes always count as critical hits.', 0, True, 'Uncommon', 'Sword'),
    ('adamantine-longsword', 'Adamantine Longsword', 500, 'gp', 'Melee', 'Martial Melee', '1d8', 'slashing', 0, 0, 3,
     'This magic weapon’s strikes always count as critical hits.', 0, True, 'Uncommon', 'Sword'),
    ('adamantine-maul', 'Adamantine Maul', 500, 'gp', 'Melee', 'Martial Melee', '2d6', 'bludgeoning', 0, 0, 10,
     'This magic weapon’s strikes always count as critical hits.', 0, True, 'Uncommon', 'Hammer'),
    ('adamantine-morningstar', 'Adamantine Morningstar', 500, 'gp', 'Melee', 'Martial Melee', '1d8', 'piercing', 0, 0, 4,
     'This magic weapon’s strikes always count as critical hits.', 0, True, 'Uncommon', 'Spiked'),
    ('adamantine-dagger', 'Adamantine Dagger', 500, 'gp', 'Melee', 'Simple Melee', '1d4', 'piercing', 20, 60, 1,
     'This magic weapon’s strikes always count as critical hits.', 0, True, 'Uncommon', 'Dagger'),
    ('adamantine-glaive', 'Adamantine Glaive', 500, 'gp', 'Melee', 'Martial Melee', '1d10', 'slashing', 0, 0, 6,
     'This magic weapon’s strikes always count as critical hits.', 0, True, 'Uncommon', 'Polearm'),
    ('adamantine-halberd', 'Adamantine Halberd', 500, 'gp', 'Melee', 'Martial Melee', '1d10', 'slashing', 0, 0, 6,
     'This magic weapon’s strikes always count as critical hits.', 0, True, 'Uncommon', 'Polearm'),
    ('adamantine-mace', 'Adamantine Mace', 500, 'gp', 'Melee', 'Simple Melee', '1d6', 'bludgeoning', 0, 0, 4,
     'This magic weapon’s strikes always count as critical hits.', 0, True, 'Uncommon', 'Mace'),
    ('adamantine-war-pick', 'Adamantine War Pick', 500, 'gp', 'Melee', 'Martial Melee', '1d8', 'piercing', 0, 0, 2,
     'This magic weapon’s strikes always count as critical hits.', 0, True, 'Uncommon', 'Pick'),
    ('adamantine-warhammer', 'Adamantine Warhammer', 500, 'gp', 'Melee', 'Martial Melee', '1d8', 'bludgeoning', 0, 0, 2,
     'This magic weapon’s strikes always count as critical hits.', 0, True, 'Uncommon', 'Hammer'),

]

WEARABLE_MAGIC_ITEMS_ROWS: list[tuple[str, str, int, str, float, str, int, bool, str, str, Optional[dict]]] = []
for row in ARMOR_ROWS:
    (srd_index, item_name, base_price, price_unit, base_ac,
     dex_bonus, max_dex_bonus, str_minimum, stealth_disadvantage,
     weight, description, magic_bonus, is_magical, rarity, armour_category) = row

    WEARABLE_MAGIC_ITEMS_ROWS.append((
        srd_index, item_name, base_price, price_unit, weight, description,
        magic_bonus, is_magical, rarity, 'Armor',
        {
            'base_ac': base_ac,
            'dex_bonus': dex_bonus,
            'max_dex_bonus': max_dex_bonus,
            'str_minimum': str_minimum,
            'stealth_disadvantage': stealth_disadvantage,
            'armour_category': armour_category
        }
    ))
for row in WEAPON_ROWS:
    (srd_index, item_name, base_price, price_unit,
     weapon_range, category_range, damage_dice, damage_type,
     range_normal, range_long, weight, description,
     magic_bonus, is_magical, rarity, weapon_category) = row

    WEARABLE_MAGIC_ITEMS_ROWS.append((
        srd_index, item_name, base_price, price_unit, weight, description,
        magic_bonus, is_magical, rarity, 'Weapon',
        {
            'weapon_range': weapon_range,
            'category_range': category_range,
            'damage_dice': damage_dice,
            'damage_type': damage_type,
            'range_normal': range_normal,
            'range_long': range_long,
            'weapon_category': weapon_category
        }
    ))
#--WEARABLES-END----------------------------------------

#--CONSUMABLES-START----------------------------------------
AMMUNITION_ROWS:            list[tuple[str, str, int, str, float, str, int, bool, str, str]] = [
# ammo
('adamantine-arrow', 'Adamantine Arrow', 400, 'gp', 0.05,
 'This arrow is made of adamantine, one of the hardest substances in existence. Whenever it hits an object, the hit is a Critical Hit. This item is consumed on use.',
 0, True, 'Uncommon', 'Ammunition'),

('adamantine-blowgun-needle', 'Adamantine Blowgun Needle', 400, 'gp', 0.01,
 'This blowgun made of adamantine, one of the hardest substances in existence. Whenever it hits an object, the hit is a Critical Hit. This item is consumed on use.',
 0, True, 'Uncommon', 'Ammunition'),

('adamantine-crossbow-bolt', 'Adamantine Crossbow Bolt', 400, 'gp', 0.1,
 'This bolt is tipped with adamantine, one of the hardest substances in existence. Whenever it hits an object, the hit is a Critical Hit. This item is consumed on use.',
 0, True, 'Uncommon', 'Ammunition'),

('adamantine-sling-bullet', 'Adamantine Sling Bullet', 400, 'gp', 0.1,
 'This sling bullet is forged from adamantine, one of the hardest substances in existence. Whenever it hits an object, the hit is a Critical Hit. This item is consumed on use.',
 0, True, 'Uncommon', 'Ammunition'), ]
POTION_ROWS:                list[tuple[str, str, int, str, float, str, int, bool, str, str]] = [

    # potions
    ('elixir-of-health', 'Elixir of Health', 40000, 'gp', 0.1,
     "When you drink this potion, you are cured of all magical contagions. In addition, the following conditions end on you: Blinded, Deafened, Paralyzed and Poisoned. "
     "The clear, red liquid has tiny bubbles of light in it.",
     0, True, 'Rare', 'Potion'),

    ('potion-of-healing', 'Potion of Healing', 100, 'gp', 0.1,
     'The red liquid glimmers when agitated. You regain 2d4+2 Hit Points when you drink this potion. This item is consumed when used.',
     0, True, 'Common', 'Potion'),

    ('greater-potion-of-healing', 'Greater Potion of Healing', 400, 'gp', 0.1,
     'You regain 4d4+4 Hit Points when you drink this potion. The red liquid glimmers when agitated. This item is consumed when used.',
     0, True, 'Uncommon', 'Potion'),

    ('superior-potion-of-healing', 'Superior Potion of Healing', 4000, 'gp', 0.1,
     'You regain 8d4+8 Hit Points when you drink this potion. The red liquid glimmers when agitated. This item is consumed when used.',
     0, True, 'Rare', 'Potion'),

    ('supreme-potion-of-healing', 'Supreme Potion of Healing', 40000, 'gp', 0.1,
     'You regain 10d4+20 Hit Points when you drink this potion. The red liquid glimmers when agitated. This item is consumed when used.',
     0, True, 'Very Rare', 'Potion'),

    ('potion-of-animal-friendship', 'Potion of Animal Friendship', 400, 'gp', 0.1,
     'When you drink this potion, you can cast the level 3 version of the *Animal Friendship* spell (save DC 13). Agitating this potions muddy liquid brings little bits into view; a fish scale, a hummingbird feather, a cat claw or a squirrel hair. This item is consumed when used.',
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-clairvoyance', 'Potion of Animal Friendship', 40000, 'gp', 0.1,
     'When you drink this potion, you gain the effect of the *Clairvoyance* spell (no Concentration required). An eyeball bobs in this potions yellowish liquid but vanishes when the potion is opened. This item is consumed when used.',
     0, True, 'Rare', 'Potion'),

    ('potion-of-climbing', 'Potion of Climbing', 40000, 'gp', 0.1,
     'When you drink this potion, you gain a Climb Speed equal to your Speed for 1 hour. During this time you have Advantage on Strength (Athletics) checks to climb. This potion is separated into brown, silver and gray layers resembling bands of stone Shaking the bottle fails to mix the colours. This item is consumed when used.',
     0, True, 'Rare', 'Potion'),

    ('potion-of-comprehension', 'Potion of Comprehension', 400, 'gp', 0.1,
     "When you drink this potion, you gain the effect of the *Comprehend Languages* spell for 1 hour. This potion's liquid is a clear concoction with bits of salt and soot swirling in it. This item is consumed when used.",
     0, True, 'Common', 'Potion'),

    ('potion-of-diminution', 'Potion of Diminution', 40000, 'gp', 0.1,
     "When you drink this potion, you gain the 'reduce' effect of the *Enlarge/Reduce* spell for 1d4 hours (no Concentration required). The red in the potion's liquid continuously contracts to a tiny bead and then expands to color the clear liquid around it. Shaking the bottle fails interrupt the process.",
     0, True, 'Rare', 'Potion'),

    ('potion-of-growth', 'Potion of Growth', 4000, 'gp', 0.1,
     "When you drink this potion, you gain the 'enlarge' effect of the *Enlarge/Reduce* spell for 1d4 hours (no Concentration required). The red in the potion's liquid continuously expands from a tiny bead and then contracts. Shaking the bottle fails interrupt the process.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-fire-breath', 'Potion of Fire Breath', 4000, 'gp', 0.1,
     "After drinking this potion, you can take a Bonus Action to exhale fire at a target within 30 feet of yourself. The target makes a DC 13 Dexterity saving throw, taking 4d6 Fire damage on a failed save or half as much damage on a successful one. This potion's orange liquid flickers, and smoke fills the top of the container and wafts out whenever it is opened.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-gaseous-form', 'Potion of Gaseous Form', 4000, 'gp', 0.1,
     "When you drink this potion, you gain the effect of the *Gaseous Form* spell for 1 hour (no Concentration required) or until you end the effect as a Bonus Action."
     "This potion's container seems to hold fog that moves and pours like water.",
     0, True, 'Rare', 'Potion'),

    ('potion-of-hill-giant-strength', 'Potion of Hill Giant Strength', 400, 'gp', 0.1,
     "When you drink this potion, your Strength score increases to 21 for 1 hour. This potion has no effect on you if your Strength is equal to or greater than 21."
     "This potion's transparent liquid has floating in it a silver light resembling a giant's finger nail.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-frost-giant-strength', 'Potion of Frost Giant Strength', 400, 'gp', 0.1,
     "When you drink this potion, your Strength score increases to 23 for 1 hour. This potion has no effect on you if your Strength is equal to or greater than 23. "
     "This potion's transparent liquid has floating in it a silver light resembling a giant's finger nail.",
     0, True, 'Rare', 'Potion'),

    ('potion-of-fire-giant-strength', 'Potion of Fire Giant Strength', 4000, 'gp', 0.1,
     "When you drink this potion, your Strength score increases to 25 for 1 hour. This potion has no effect on you if your Strength is equal to or greater than 25. "
     "This potion's transparent liquid has floating in it a silver light resembling a giant's finger nail.",
     0, True, 'Rare', 'Potion'),

    ('potion-of-cloud-giant-strength', 'Potion of Cloud Giant Strength', 400000, 'gp', 0.1,
     "When you drink this potion, your Strength score increases to 27 for 1 hour. This potion has no effect on you if your Strength is equal to or greater than 27. "
     "This potion's transparent liquid has floating in it a silver light resembling a giant's finger nail.",
     0, True, 'Very Rare', 'Potion'),

    ('potion-of-storm-giant-strength', 'Potion of Storm Giant Strength', 200000, 'gp', 0.1,
     "When you drink this potion, your Strength score increases to 29 for 1 hour. This potion has no effect on you if your Strength is equal to or greater than 29. "
     "This potion's transparent liquid has floating in it a silver light resembling a giant's finger nail.",
     0, True, 'Legendary', 'Potion'),

    ('potion-of-greater-invisibility', 'Potion of Greater Invisibility', 40000, 'gp', 0.1,
     "This potion's container looks empty but feels as though it holds liquid."
     "When you drink this potion you have the Invisible condition for 1 hour.",
     0, True, 'Very Rare', 'Potion'),

    ('potion-of-heroism', 'Potion of Heroism', 40000, 'gp', 0.1,
     "When you drink this potion, you gain 10 Temporary Hit Points that last for 1 hour. You are also under the effect of the *Bless* spell for the same duration."
     "This potion's blue liquid bubbles and streams as if boiling.",
     0, True, 'Rare', 'Potion'),

    ('potion-of-invisibility', 'Potion of Invisibility', 4000, 'gp', 0.1,
     "This potion's container looks empty but feels as though it holds liquid."
     "When you drink this potion you have the Invisible condition for 1 hour. The effect ends early if you make an attack roll, deal damage or cast a spell.",
     0, True, 'Rare', 'Potion'),

    ('potion-of-invulnerability', 'Potion of Invulnerability', 4000, 'gp', 0.1,

     "For 1 minute after you drink this potion, you have Resistance to all damage."
     "This potion's syrupy liquid looks like liquified iron.",
     0, True, 'Very Rare', 'Potion'),

    ('potion-of-longevity', 'Potion of Longevity', 40000, 'gp', 0.1,
     "When you drink this potion, your physical age is reduced by 1d6+ 6 years to a minimum of 13 years. Each time you subsequently drink a *Potion of Longevity* there is a 10 percent cumulative chance that you instead age by 1d6 + 6 years. "
     "Suspended in this amber liquid is a tiny heart that, against all reason, is still beating. These ingredients vanish when the potion is opened.",
     0, True, 'Very Rare', 'Potion'),

    ('potion-of-mind-reading', 'Potion of Mind Reading', 40000, 'gp', 0.1,
     "When you drink this potion, you gain the effect of the *Detect Thoughts* spell (save DC13) for 10 minutes (no Concentration required). "
     "This potion's dense, purple liquid has an ovoid cloud of pink floating in it.",
     0, True, 'Rare', 'Potion'),

    ('potion-of-pugilism', 'Potion of Pugilism', 400, 'gp', 0.1,
     "After you drink this potion, each Unarmed Strike you make deals an extra 1d6 Force damage on a hit. This effect lasts 10 minutes. "
     "This potion is a thick green fluid that tastes like spinach.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-acid-resistance', 'Potion of Acid Resistance', 400, 'gp', 0.1,
     "When you drink this potion, you have resistance to acid damage for 1 hour. "
     "The liquid is murky green and bubbles slightly, giving off a sharp, tangy odor.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-cold-resistance', 'Potion of Cold Resistance', 400, 'gp', 0.1,
     "When you drink this potion, you have resistance to cold damage for 1 hour. "
     "The liquid is icy blue and cold to the touch, with frost clinging to the bottle.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-fire-resistance', 'Potion of Fire Resistance', 400, 'gp', 0.1,
     "When you drink this potion, you have resistance to fire damage for 1 hour. "
     "The liquid is a swirling orange and red, warm to the touch and flickering like flame.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-force-resistance', 'Potion of Force Resistance', 400, 'gp', 0.1,
     "When you drink this potion, you have resistance to force damage for 1 hour. "
     "The liquid is deep violet with occasional ripples of invisible pressure moving through it.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-lightning-resistance', 'Potion of Lightning Resistance', 400, 'gp', 0.1,
     "When you drink this potion, you have resistance to lightning damage for 1 hour. "
     "The liquid crackles faintly and glows with streaks of silver and blue.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-necrotic-resistance', 'Potion of Necrotic Resistance', 400, 'gp', 0.1,
     "When you drink this potion, you have resistance to necrotic damage for 1 hour. "
     "The liquid is pitch black with wisps of shadow swirling within.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-poison-resistance', 'Potion of Poison Resistance', 400, 'gp', 0.1,
     "When you drink this potion, you have resistance to poison damage for 1 hour. "
     "The liquid is sickly green with a bitter smell and slow-moving swirls.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-psychic-resistance', 'Potion of Psychic Resistance', 400, 'gp', 0.1,
     "When you drink this potion, you have resistance to psychic damage for 1 hour. "
     "The liquid pulses with shifting colors and seems to hum faintly in your mind.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-radiant-resistance', 'Potion of Radiant Resistance', 400, 'gp', 0.1,
     "When you drink this potion, you have resistance to radiant damage for 1 hour. "
     "The liquid glows with a soft golden light and feels warm and invigorating.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-thunder-resistance', 'Potion of Thunder Resistance', 400, 'gp', 0.1,
     "When you drink this potion, you have resistance to thunder damage for 1 hour. "
     "The liquid rumbles gently and fizzes with deep, resonant vibrations.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-classic-resistance', 'Potion of Resistance (Classic)', 400, 'gp', 0.1,
     "When you drink this potion, you have resistance to a damage type for 1 hour. The DM chooses the type or determines it randomly by rolling on the following table. "
     "The liquid inside shimmers with ever-changing colors, cycling through hues and textures that hint at different elemental forces. It feels warm, cold, heavy, and light all at once.",
     0, True, 'Uncommon', 'Potion'),

    ('potion-of-speed', 'Potion of Speed', 40000, 'gp', 0.1,
     "When you drink this potion, you gain the effect of the *Haste* spell for 1 minute (no Concentration required) without suffering the wave of lethargy that typically occurs when the effect ends."
     "The potion's yello fluid is streaked with black and swirls on its own.",
     0, True, 'Very Rare', 'Potion'),

    ('potion-of-vitality', 'Potion of Vitality', 40000, 'gp', 0.1,
     "When you drink this potion, it removes any Exhaustion levels you have and ends the Poisoned condition on you. For the next 24 hours, you regain the maximum number of Hit Points for any Hit Point Die you spend."
     "The potion's crimson liquid regularly pulses with dull light, calling to mind a heartbeat.",
     0, True, 'Very Rare', 'Potion'),

    ('potion-of-water-breathing', 'Potion of Water Breathing', 4000, 'gp', 0.1,
     "You can breathe underwater for 24 hours after drinking this potion."
     "The potion's cloudy green fluid smells of the sea and has a jellyfish-like bubble floating in it",
     0, True, 'Uncommon', 'Potion'),


]
SCROLL_ROWS:                list[tuple[str, str, int, str, float, str, int, bool, str, str]] = [


    #SCROLLS

    ('spell-scroll-classic', 'Spell Scroll (Classic)', 100, 'gp', 0.0,
    "A Spell Scroll bears the words of a single spell, written in a mystical cipher. If the spell is on your spell list, you can read the scroll and cast its spell without Material components. Otherwise, the scroll is unintelligible. "
    "Casting the spell by reading the scroll uses its normal casting time. Once the spell is cast, the scroll crumbles to dust. If the casting is interrupted, the scroll is not lost.\n"
    "If the spell is a higher level than you can normally cast, you must succeed on a spellcasting ability check (DC 10 + spell level) to cast it. On a failure, the spell fades and the scroll is wasted.\n"
    "The scroll's spell level determines its rarity, save DC, and spell attack bonus. See the following:\n"
    "• Cantrip or 1st level – DC 13, +5 attack (Common)\n"
    "• 2nd level – DC 13, +5 attack (Uncommon)\n"
    "• 3rd level – DC 15, +7 attack (Uncommon)\n"
    "• 4th level – DC 15, +7 attack (Rare)\n"
    "• 5th level – DC 17, +9 attack (Rare)\n"
    "• 6th level – DC 17, +9 attack (Very Rare)\n"
    "• 7th or 8th level – DC 18, +10 attack (Very Rare)\n"
    "• 9th level – DC 19, +11 attack (Legendary)\n"
    "The scroll is consumed when used.",
    0, True, 'Common', 'Scroll'),

    ('spell-scroll-cantrip', 'Spell Scroll (Cantrip)', 100, 'gp', 0.0,
     "This scroll contains the words of a cantrip, written in a mystical cipher. If the cantrip is on your spell list, you can cast it without Material components. "
     "Otherwise, the scroll is unintelligible. Casting uses the cantrip’s normal casting time. Once cast, the scroll crumbles to dust. If interrupted, the scroll is not lost.\n"
     "Save DC 13, Spell Attack Bonus +5. The scroll is consumed when used.",
     0, True, 'Common', 'Scroll'),

    ('spell-scroll-level-1', 'Spell Scroll (1st Level)', 100, 'gp', 0.0,
     "This scroll contains the words of a 1st-level spell, written in a mystical cipher. If the spell is on your spell list, you can cast it without Material components. "
     "Otherwise, the scroll is unintelligible. Casting uses the spell’s normal casting time. Once cast, the scroll crumbles to dust. If interrupted, the scroll is not lost.\n"
     "Save DC 13, Spell Attack Bonus +5. The scroll is consumed when used.",
     0, True, 'Common', 'Scroll'),

    ('spell-scroll-level-2', 'Spell Scroll (2nd Level)', 400, 'gp', 0.0,
     "This scroll contains the words of a 2nd-level spell, written in a mystical cipher. If the spell is on your spell list, you can cast it without Material components. "
     "Otherwise, the scroll is unintelligible. Casting uses the spell’s normal casting time. Once cast, the scroll crumbles to dust. If interrupted, the scroll is not lost.\n"
     "If the spell is higher than you can normally cast, you must succeed on a DC 12 spellcasting ability check. On a failure, the scroll is wasted.\n"
     "Save DC 13, Spell Attack Bonus +5. The scroll is consumed when used.",
     0, True, 'Uncommon', 'Scroll'),

    ('spell-scroll-level-3', 'Spell Scroll (3rd Level)', 400, 'gp', 0.0,
     "This scroll contains the words of a 3rd-level spell, written in a mystical cipher. If the spell is on your spell list, you can cast it without Material components. "
     "Otherwise, the scroll is unintelligible. Casting uses the spell’s normal casting time. Once cast, the scroll crumbles to dust. If interrupted, the scroll is not lost.\n"
     "If the spell is higher than you can normally cast, you must succeed on a DC 13 spellcasting ability check. On a failure, the scroll is wasted.\n"
     "Save DC 15, Spell Attack Bonus +7. The scroll is consumed when used.",
     0, True, 'Uncommon', 'Scroll'),

    ('spell-scroll-level-4', 'Spell Scroll (4th Level)', 4000, 'gp', 0.0,
     "This scroll contains the words of a 4th-level spell, written in a mystical cipher. If the spell is on your spell list, you can cast it without Material components. "
     "Otherwise, the scroll is unintelligible. Casting uses the spell’s normal casting time. Once cast, the scroll crumbles to dust. If interrupted, the scroll is not lost.\n"
     "If the spell is higher than you can normally cast, you must succeed on a DC 14 spellcasting ability check. On a failure, the scroll is wasted.\n"
     "Save DC 15, Spell Attack Bonus +7. The scroll is consumed when used.",
     0, True, 'Rare', 'Scroll'),

    ('spell-scroll-level-5', 'Spell Scroll (5th Level)', 4000, 'gp', 0.0,
     "This scroll contains the words of a 5th-level spell, written in a mystical cipher. If the spell is on your spell list, you can cast it without Material components. "
     "Otherwise, the scroll is unintelligible. Casting uses the spell’s normal casting time. Once cast, the scroll crumbles to dust. If interrupted, the scroll is not lost.\n"
     "If the spell is higher than you can normally cast, you must succeed on a DC 15 spellcasting ability check. On a failure, the scroll is wasted.\n"
     "Save DC 17, Spell Attack Bonus +9. The scroll is consumed when used.",
     0, True, 'Rare', 'Scroll'),

    ('spell-scroll-level-6', 'Spell Scroll (6th Level)', 40000, 'gp', 0.0,
     "This scroll contains the words of a 6th-level spell, written in a mystical cipher. If the spell is on your spell list, you can cast it without Material components. "
     "Otherwise, the scroll is unintelligible. Casting uses the spell’s normal casting time. Once cast, the scroll crumbles to dust. If interrupted, the scroll is not lost.\n"
     "If the spell is higher than you can normally cast, you must succeed on a DC 16 spellcasting ability check. On a failure, the scroll is wasted.\n"
     "Save DC 17, Spell Attack Bonus +9. The scroll is consumed when used.",
     0, True, 'Very Rare', 'Scroll'),

    ('spell-scroll-level-7', 'Spell Scroll (7th Level)', 40000, 'gp', 0.0,
     "This scroll contains the words of a 7th-level spell, written in a mystical cipher. If the spell is on your spell list, you can cast it without Material components. "
     "Otherwise, the scroll is unintelligible. Casting uses the spell’s normal casting time. Once cast, the scroll crumbles to dust. If interrupted, the scroll is not lost.\n"
     "If the spell is higher than you can normally cast, you must succeed on a DC 17 spellcasting ability check. On a failure, the scroll is wasted.\n"
     "Save DC 18, Spell Attack Bonus +10. The scroll is consumed when used.",
     0, True, 'Very Rare', 'Scroll'),

    ('spell-scroll-level-8', 'Spell Scroll (8th Level)', 40000, 'gp', 0.0,
     "This scroll contains the words of an 8th-level spell, written in a mystical cipher. If the spell is on your spell list, you can cast it without Material components. "
     "Otherwise, the scroll is unintelligible. Casting uses the spell’s normal casting time. Once cast, the scroll crumbles to dust. If interrupted, the scroll is not lost.\n"
     "If the spell is higher than you can normally cast, you must succeed on a DC 18 spellcasting ability check. On a failure, the scroll is wasted.\n"
     "Save DC 18, Spell Attack Bonus +10. The scroll is consumed when used.",
     0, True, 'Very Rare', 'Scroll'),

    ('spell-scroll-level-9', 'Spell Scroll (9th Level)', 200000, 'gp', 0.0,
     "This scroll contains the words of a 9th-level spell, written in a mystical cipher. If the spell is on your spell list, you can cast it without Material components. "
     "Otherwise, the scroll is unintelligible. Casting uses the spell’s normal casting time. Once cast, the scroll crumbles to dust. If interrupted, the scroll is not lost.\n"
     "If the spell is higher than you can normally cast, you must succeed on a DC 19 spellcasting ability check. On a failure, the scroll is wasted.\n"
     "Save DC 19, Spell Attack Bonus +11. The scroll is consumed when used.",
     0, True, 'Legendary', 'Scroll'),

#protection scrolls---------------------------
    ('scroll-of-protection-classic', 'Scroll of Protection (Classic)', 4000, 'gp', 0.0,
    "When you read this scroll, you create a 5-foot-radius, 10-foot-high invisible barrier centered on you for 5 minutes. The scroll protects against one creature type, determined randomly by rolling 1d100. Refer to the Protection Scroll table in the DMG. Affected creatures cannot enter or affect anything within the barrier unless they succeed on a DC 15 Charisma saving throw. The scroll is consumed.",
    0, True, 'Rare', 'Scroll'),

    ('scroll-of-protection-aberrations', 'Scroll of Protection (Aberrations)', 4000, 'gp', 0.0,
     "This scroll protects against Aberrations. It creates a 5-foot-radius, 10-foot-high invisible barrier around you for 5 minutes. Aberrations cannot enter or affect the area unless they succeed on a DC 15 Charisma saving throw. "
     "This is obtained from rolling 01–10 on a d100 roll. The scroll is consumed.",
     0, True, 'Rare', 'Scroll'),

    ('scroll-of-protection-beasts', 'Scroll of Protection (Beasts)', 4000, 'gp', 0.0,
     "This scroll protects against Beasts. It creates a 5-foot-radius, 10-foot-high invisible barrier around you for 5 minutes. Beasts cannot enter or affect the area unless they succeed on a DC 15 Charisma saving throw. "
     "This is obtained from rolling 11–15 on a d100 roll. The scroll is consumed.",
     0, True, 'Rare', 'Scroll'),

    ('scroll-of-protection-celestials', 'Scroll of Protection (Celestials)', 4000, 'gp', 0.0,
     "This scroll protects against Celestials. It creates a 5-foot-radius, 10-foot-high invisible barrier around you for 5 minutes. Celestials cannot enter or affect the area unless they succeed on a DC 15 Charisma saving throw. "
     "This is obtained from rolling 16–20 on a d100 roll. The scroll is consumed.",
     0, True, 'Rare', 'Scroll'),

    ('scroll-of-protection-constructs', 'Scroll of Protection (Constructs)', 4000, 'gp', 0.0,
     "This scroll protects against Constructs. It creates a 5-foot-radius, 10-foot-high invisible barrier around you for 5 minutes. Constructs cannot enter or affect the area unless they succeed on a DC 15 Charisma saving throw. "
     "This is obtained from rolling 21–25 on a d100 roll. The scroll is consumed.",
     0, True, 'Rare', 'Scroll'),

    ('scroll-of-protection-dragons', 'Scroll of Protection (Dragons)', 4000, 'gp', 0.0,
     "This scroll protects against Dragons. It creates a 5-foot-radius, 10-foot-high invisible barrier around you for 5 minutes. Dragons cannot enter or affect the area unless they succeed on a DC 15 Charisma saving throw. "
     "This is obtained from rolling 26–35 on a d100 roll. The scroll is consumed.",
     0, True, 'Rare', 'Scroll'),

    ('scroll-of-protection-elementals', 'Scroll of Protection (Elementals)', 4000, 'gp', 0.0,
     "This scroll protects against Elementals. It creates a 5-foot-radius, 10-foot-high invisible barrier around you for 5 minutes. Elementals cannot enter or affect the area unless they succeed on a DC 15 Charisma saving throw. "
     "This is obtained from rolling 36–45 on a d100 roll. The scroll is consumed.",
     0, True, 'Rare', 'Scroll'),

    ('scroll-of-protection-humanoids', 'Scroll of Protection (Humanoids)', 4000, 'gp', 0.0,
     "This scroll protects against Humanoids. It creates a 5-foot-radius, 10-foot-high invisible barrier around you for 5 minutes. Humanoids cannot enter or affect the area unless they succeed on a DC 15 Charisma saving throw. "
     "This is obtained from rolling 46–50 on a d100 roll. The scroll is consumed.",
     0, True, 'Rare', 'Scroll'),

    ('scroll-of-protection-fey', 'Scroll of Protection (Fey)', 4000, 'gp', 0.0,
     "This scroll protects against Fey. It creates a 5-foot-radius, 10-foot-high invisible barrier around you for 5 minutes. Fey cannot enter or affect the area unless they succeed on a DC 15 Charisma saving throw. "
     "This is obtained from rolling 51–60 on a d100 roll. The scroll is consumed.",
     0, True, 'Rare', 'Scroll'),

    ('scroll-of-protection-fiends', 'Scroll of Protection (Fiends)', 4000, 'gp', 0.0,
     "This scroll protects against Fiends. It creates a 5-foot-radius, 10-foot-high invisible barrier around you for 5 minutes. Fiends cannot enter or affect the area unless they succeed on a DC 15 Charisma saving throw. "
     "This is obtained from rolling 61–70 on a d100 roll. The scroll is consumed.",
     0, True, 'Rare', 'Scroll'),

    ('scroll-of-protection-giants', 'Scroll of Protection (Giants)', 4000, 'gp', 0.0,
     "This scroll protects against Giants. It creates a 5-foot-radius, 10-foot-high invisible barrier around you for 5 minutes. Giants cannot enter or affect the area unless they succeed on a DC 15 Charisma saving throw. "
     "This is obtained from rolling 71–75 on a d100 roll. The scroll is consumed.",
     0, True, 'Rare', 'Scroll'),

    ('scroll-of-protection-monstrosities', 'Scroll of Protection (Monstrosities)', 4000, 'gp', 0.0,
     "This scroll protects against Monstrosities. It creates a 5-foot-radius, 10-foot-high invisible barrier around you for 5 minutes. Monstrosities cannot enter or affect the area unless they succeed on a DC 15 Charisma saving throw. "
     "This is obtained from rolling 76–80 on a d100 roll. The scroll is consumed.",
     0, True, 'Rare', 'Scroll'),

    ('scroll-of-protection-oozes', 'Scroll of Protection (Oozes)', 4000, 'gp', 0.0,
     "This scroll protects against Oozes. It creates a 5-foot-radius, 10-foot-high invisible barrier around you for 5 minutes. Oozes cannot enter or affect the area unless they succeed on a DC 15 Charisma saving throw. "
     "This is obtained from rolling 81–85 on a d100 roll. The scroll is consumed.",
     0, True, 'Rare', 'Scroll'),

    ('scroll-of-protection-plants', 'Scroll of Protection (Plants)', 4000, 'gp', 0.0,
     "This scroll protects against Plants. It creates a 5-foot-radius, 10-foot-high invisible barrier around you for 5 minutes. Plants cannot enter or affect the area unless they succeed on a DC 15 Charisma saving throw. "
     "This is obtained from rolling 86–90 on a d100 roll. The scroll is consumed.",
     0, True, 'Rare', 'Scroll'),

    ('scroll-of-protection-undead', 'Scroll of Protection (Undead)', 4000, 'gp', 0.0,
     "This scroll protects against Undead. It creates a 5-foot-radius, 10-foot-high invisible barrier around you for 5 minutes. Undead cannot enter or affect the area unless they succeed on a DC 15 Charisma saving throw. "
     "This is obtained from rolling 91–100 on a d100 roll. The scroll is consumed.",
     0, True, 'Rare', 'Scroll'),

    #titan scrolls----------------------------------
    ('scroll-of-titan-summoning-classic', 'Scroll of Titan Summoning (Classic)', 200000, 'gp', 0.0,
     "When you read this scroll, you summon a titan randomly determined by rolling 1d100. The summoned titan appears in an open space within 1 mile that you can see. "
     "The titan is hostile to all creatures, including you, and remains until it is destroyed. If no valid space is available, the scroll is wasted. "
     "The scroll is consumed. Refer to the Titan Summoning table in the DMG for d100 results.",
     0, True, 'Legendary', 'Scroll'),

    ('scroll-of-animal-lord-summoning', 'Scroll of Titan Summoning (Animal Lord)', 200000, 'gp', 0.0,
     "This scroll summons an Animal Lord within 1 mile in a space you can see. The Animal Lord is hostile to all creatures, including you, and remains until destroyed. "
     "This is obtained from rolling 01–15 on a d100 roll. The scroll is consumed.",
     0, True, 'Legendary', 'Scroll'),

    ('scroll-of-blob-of-annihilation-summoning', 'Scroll of Titan Summoning (Blob of Annihilation)', 200000, 'gp', 0.0,
     "This scroll summons a Blob of Annihilation within 1 mile in a space you can see. The blob is hostile to all creatures, including you, and remains until destroyed. "
     "This is obtained from rolling 16–30 on a d100 roll. The scroll is consumed.",
     0, True, 'Legendary', 'Scroll'),

    ('scroll-of-colossus-summoning', 'Scroll of Titan Summoning (Colossus)', 200000, 'gp', 0.0,
     "This scroll summons a Colossus within 1 mile in a space you can see. The Colossus is hostile to all creatures, including you, and remains until destroyed. "
     "This is obtained from rolling 31–45 on a d100 roll. The scroll is consumed.",
     0, True, 'Legendary', 'Scroll'),

    ('scroll-of-elemental-cataclysm-summoning', 'Scroll of Titan Summoning (Elemental Cataclysm)', 200000, 'gp', 0.0,
     "This scroll summons an Elemental Cataclysm within 1 mile in a space you can see. The titan is hostile to all creatures, including you, and remains until destroyed. "
     "This is obtained from rolling 46–60 on a d100 roll. The scroll is consumed.",
     0, True, 'Legendary', 'Scroll'),

    ('scroll-of-empyrean-summoning', 'Scroll of Titan Summoning (Empyrean)', 200000, 'gp', 0.0,
     "This scroll summons an Empyrean within 1 mile in a space you can see. The Empyrean is hostile to all creatures, including you, and remains until destroyed. "
     "This is obtained from rolling 61–75 on a d100 roll. The scroll is consumed.",
     0, True, 'Legendary', 'Scroll'),

    ('scroll-of-kraken-summoning', 'Scroll of Titan Summoning (Kraken)', 200000, 'gp', 0.0,
     "This scroll summons a Kraken within 1 mile in a body of water large enough to contain it. If no valid water exists, the scroll is wasted. "
     "The Kraken is hostile to all creatures, including you, and remains until destroyed. This is obtained from rolling 76–90 on a d100 roll. The scroll is consumed.",
     0, True, 'Legendary', 'Scroll'),

    ('scroll-of-tarrasque-summoning', 'Scroll of Titan Summoning (Tarrasque)', 200000, 'gp', 0.0,
     "This scroll summons the Tarrasque within 1 mile in a space you can see. The Tarrasque is hostile to all creatures, including you, and remains until destroyed. "
     "This is obtained from rolling 91–100 on a d100 roll. The scroll is consumed.",
     0, True, 'Legendary', 'Scroll'),

]

CONSUMABLE_MAGIC_ITEMS_ROWS: list[tuple[str, str, int, str, float, str, int, bool, str, str]] = [
*AMMUNITION_ROWS,
*POTION_ROWS,
*SCROLL_ROWS,

]
#--CONSUMABLES-END----------------------------------------

#--EQUIPABLE-START----------------------------------------
ROD_ROWS: list[tuple[str, str, int, str, float, str, int, bool, str, str]] = [
    ('immovable-rod', 'Immovable Rod', 400, 'gp', 2.0,
     "This iron rod has a button on one end. You can take a Utilize action to press the button, causing it to become magically fixed in place. "
     "It holds up to 8,000 pounds and defies gravity. A creature can make a DC 30 Strength (Athletics) check to move the rod up to 10 feet. Requires attunement.",
     0, True, 'Uncommon', 'Rod'),

    ('rod-of-absorption', 'Rod of Absorption', 40000, 'gp', 2.5,
     "While holding this rod, you can use a Reaction to absorb a spell targeting only you (no AoE). The spell’s energy is stored in the rod (up to 50 levels total). "
     "A spellcaster can convert stored levels into spell slots (up to 5th level). If it reaches its capacity or absorbs an invalid spell, the rod has no effect. Requires attunement.",
     0, True, 'Very Rare', 'Rod'),

    ('rod-of-alertness', 'Rod of Alertness', 40000, 'gp', 2.0,
     "While holding this rod, you have advantage on Wisdom (Perception) checks and Initiative rolls. "
     "It can also cast *Detect Evil and Good*, *Detect Magic*, *Detect Poison and Disease*, and *See Invisibility*. "
     "You can plant the rod in the ground to create a glowing aura that grants +1 AC and saving throws in bright light and reveals invisible creatures. Usable once per day. Requires attunement.",
     0, True, 'Very Rare', 'Rod'),

    ('rod-of-lordly-might', 'Rod of Lordly Might', 200000, 'gp', 5.0,
     "This rod functions as a +3 mace and has 6 transformation buttons to become a flame blade, battleaxe, spear, climbing pole, battering ram, or compass. "
     "It also has 3 special abilities: Drain Life (4d6 necrotic), Paralyze, and Terrify—each usable once per day. Requires attunement.",
     3, True, 'Legendary', 'Rod'),

    ('rod-of-resurrection', 'Rod of Resurrection', 200000, 'gp', 2.0,
     "This rod has 5 charges and allows casting *Heal* (1 charge) or *Resurrection* (5 charges). Regains 1 charge daily. "
     "If you expend the last charge, roll a d20; on a 1, it vanishes in radiant light. Requires attunement by a cleric, druid, or paladin.",
     0, True, 'Legendary', 'Rod'),

    ('rod-of-rulership', 'Rod of Rulership', 4000, 'gp', 2.0,
     "While holding this rod, you can take a Magic action to command obedience from creatures you can see within 120 feet. "
     "Each must make a DC 15 Wisdom save or be Charmed for 8 hours. The effect ends early if you or an ally harms the target or commands it to act against its nature. Usable once per day. Requires attunement.",
     0, True, 'Rare', 'Rod'),

    ('rod-of-security', 'Rod of Security', 40000, 'gp', 2.5,
     "While holding this rod, you can transport up to 199 creatures you can see to a tranquil, nourishing demiplane. "
     "You regain HP as if using Hit Dice, and don’t age. Duration depends on number of creatures (200 days divided among them). Usable once every 10 days.",
     0, True, 'Very Rare', 'Rod'),

    ('rod-of-the-pact-keeper-plus-one', 'Rod of the Pact Keeper +1', 4000, 'gp', 1.5,
     "Grants a +1 bonus to spell attack rolls and save DCs for Warlock spells. Once per long rest, regain one Warlock spell slot. Requires attunement by a Warlock.",
     1, True, 'Rare', 'Rod'),

    ('rod-of-the-pact-keeper-plus-two', 'Rod of the Pact Keeper +2', 40000, 'gp', 1.5,
     "Grants a +2 bonus to spell attack rolls and save DCs for Warlock spells. Once per long rest, regain one Warlock spell slot. Requires attunement by a Warlock.",
     2, True, 'Very Rare', 'Rod'),

    ('rod-of-the-pact-keeper-plus-three', 'Rod of the Pact Keeper +3', 200000, 'gp', 1.5,
     "Grants a +3 bonus to spell attack rolls and save DCs for Warlock spells. Once per long rest, regain one Warlock spell slot. Requires attunement by a Warlock.",
     3, True, 'Legendary', 'Rod'),

    ('tentacle-rod', 'Tentacle Rod', 4000, 'gp', 2.5,
     "This rod has three tentacles. As a Magic action, each tentacle can strike a creature within 15 feet. Each hit deals 1d6 psychic damage. "
     "If all three hit the same target, it must succeed on a DC 15 Dex save or be Restrained. While restrained, it takes 3d6 psychic at the start of each of its turns. The target can repeat the save at the end of each turn. Requires attunement.",
     0, True, 'Rare', 'Rod'),
]
STAFF_ROWS: list[tuple[str, str, int, str, float, str, int, bool, str, str]]= [

    ('enspell-staff-classic', 'Enspelled Staff (Classic)', 400, 'gp', 4.0,
    "Bound into this staff is a spell of level 8 or lower. The spell is determined when the staff is created and can be of any school of magic. "
    "The staff has 6 charges and regains 1d6 expended charges daily at dawn. While holding the staff, you can expend 1 charge to cast its spell. "
    "If you expend the last charge, roll a d20. On a 1, the staff loses all magical properties and becomes a nonmagical quarterstaff.\n"
    "The spell's level determines the staff’s rarity, save DC, and attack bonus.",
    0, True, 'Varies', 'Staff'),

    ('enspell-staff-cantrip', 'Enspelled Staff (Cantrip)', 400, 'gp', 4.0,
     "This staff contains a cantrip of your choice. It has 6 charges and regains 1d6 daily at dawn. You can expend 1 charge to cast the cantrip. "
     "If the last charge is used, roll a d20. On a 1, the staff becomes nonmagical. Save DC 13, Spell Attack +5. Requires attunement by a spellcaster.",
     0, True, 'Uncommon', 'Staff'),

    ('enspell-staff-level-1', 'Enspelled Staff (1st Level)', 400, 'gp', 4.0,
     "This staff contains a 1st-level spell of your choice. It has 6 charges and regains 1d6 daily at dawn. You can expend 1 charge to cast the spell. "
     "If the last charge is used, roll a d20. On a 1, the staff becomes nonmagical. Save DC 13, Spell Attack +5. Requires attunement by a spellcaster.",
     0, True, 'Uncommon', 'Staff'),

    ('enspell-staff-level-2', 'Enspelled Staff (2nd Level)', 4000, 'gp', 4.0,
     "This staff contains a 2nd-level spell of your choice. It has 6 charges and regains 1d6 daily at dawn. You can expend 1 charge to cast the spell. "
     "If the last charge is used, roll a d20. On a 1, the staff becomes nonmagical. Save DC 13, Spell Attack +5. Requires attunement by a spellcaster.",
     0, True, 'Rare', 'Staff'),

    ('enspell-staff-level-3', 'Enspelled Staff (3rd Level)', 4000, 'gp', 4.0,
     "This staff contains a 3rd-level spell of your choice. It has 6 charges and regains 1d6 daily at dawn. You can expend 1 charge to cast the spell. "
     "If the last charge is used, roll a d20. On a 1, the staff becomes nonmagical. Save DC 15, Spell Attack +7. Requires attunement by a spellcaster.",
     0, True, 'Rare', 'Staff'),

    ('enspell-staff-level-4', 'Enspelled Staff (4th Level)', 40000, 'gp', 4.0,
     "This staff contains a 4th-level spell of your choice. It has 6 charges and regains 1d6 daily at dawn. You can expend 1 charge to cast the spell. "
     "If the last charge is used, roll a d20. On a 1, the staff becomes nonmagical. Save DC 15, Spell Attack +7. Requires attunement by a spellcaster.",
     0, True, 'Very Rare', 'Staff'),

    ('enspell-staff-level-5', 'Enspelled Staff (5th Level)', 40000, 'gp', 4.0,
     "This staff contains a 5th-level spell of your choice. It has 6 charges and regains 1d6 daily at dawn. You can expend 1 charge to cast the spell. "
     "If the last charge is used, roll a d20. On a 1, the staff becomes nonmagical. Save DC 17, Spell Attack +9. Requires attunement by a spellcaster.",
     0, True, 'Very Rare', 'Staff'),

    ('enspell-staff-level-6', 'Enspelled Staff (6th Level)', 200000, 'gp', 4.0,
     "This staff contains a 6th-level spell of your choice. It has 6 charges and regains 1d6 daily at dawn. You can expend 1 charge to cast the spell. "
     "If the last charge is used, roll a d20. On a 1, the staff becomes nonmagical. Save DC 17, Spell Attack +9. Requires attunement by a spellcaster.",
     0, True, 'Legendary', 'Staff'),

    ('enspell-staff-level-7', 'Enspelled Staff (7th Level)', 200000, 'gp', 4.0,
     "This staff contains a 7th-level spell of your choice. It has 6 charges and regains 1d6 daily at dawn. You can expend 1 charge to cast the spell. "
     "If the last charge is used, roll a d20. On a 1, the staff becomes nonmagical. Save DC 18, Spell Attack +10. Requires attunement by a spellcaster.",
     0, True, 'Legendary', 'Staff'),

    ('enspell-staff-level-8', 'Enspelled Staff (8th Level)', 200000, 'gp', 4.0,
     "This staff contains an 8th-level spell of your choice. It has 6 charges and regains 1d6 daily at dawn. You can expend 1 charge to cast the spell. "
     "If the last charge is used, roll a d20. On a 1, the staff becomes nonmagical. Save DC 18, Spell Attack +10. Requires attunement by a spellcaster.",
     0, True, 'Legendary', 'Staff'),

    ('quarterstaff-of-the-acrobat', 'Quarterstaff of the Acrobat', 40000, 'gp', 4.0,
     "You have a +2 bonus to attack rolls and damage rolls made with this magic weapon.\n\n"
     "While holding this weapon, you can cause it to emit green Dim Light out to 10 feet, either as a Bonus Action or after you roll Initiative, or you can extinguish the light as a Bonus Action.\n\n"
     "While holding this weapon, you can take a Bonus Action to alter its form, turning it into a 6-inch rod (for ease of storage) or a 10-foot pole, or reverting it to a Quarterstaff; the weapon will elongate only as far as the surrounding space allows.\n\n"
     "Acrobatic Assist (Quarterstaff and 10-Foot Pole Forms Only). While holding this weapon, you have Advantage on Dexterity (Acrobatics) checks.\n\n"
     "Attack Deflection (Quarterstaff Form Only). When you are hit by an attack while holding the weapon, you can take a Reaction to twirl the weapon around you, gaining a +5 bonus to your Armor Class against the triggering attack, potentially causing the attack to miss you. You can’t use this property again until you finish a Short or Long Rest.\n\n"
     "Ranged Weapon (Quarterstaff Form Only). This weapon has the Thrown property with a normal range of 30 feet and a long range of 120 feet. Immediately after you make a ranged attack with the weapon, it flies back to your hand.\n\n"
     "Topple. If you hit a creature with this weapon, you can force the creature to make a Constitution saving throw (DC 8 + your attack modifier + proficiency). On a failed save, the creature is knocked Prone.\n\n"
     "Requires attunement.",
     2, True, 'Very Rare', 'Staff'),

    ('staff-of-adornment', 'Staff of Adornment', 100, 'gp', 4.0,
     "If you place a Tiny object weighing no more than 1 pound (such as a shard of crystal, an egg, or a stone) above the tip of this staff while holding it, "
     "the object floats an inch from the staff’s tip and remains there until it is removed or until the staff is no longer in your possession. "
     "The staff can have up to three such objects floating over its tip at any given time. While holding the staff, you can make one or more of the objects slowly spin or turn in place.",
     0, True, 'Common', 'Staff'),

    ('staff-of-birdcalls', 'Staff of Birdcalls', 100, 'gp', 4.0,
     "This wooden staff is decorated with bird carvings. It has 10 charges. While holding it, you can take a Magic action to expend 1 charge and cause it to create one of the following sounds, audible out to 120 feet: "
     "a finch’s chirp, a raven’s caw, a duck’s quack, a chicken’s cluck, a goose’s honk, a loon’s call, a turkey’s gobble, a seagull’s cry, an owl’s hoot, or an eagle’s shriek.\n\n"
     "Regaining Charges. The staff regains 1d6 + 4 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the staff explodes in a harmless cloud of bird feathers and is lost forever.",
     0, True, 'Common', 'Staff'),

    ('staff-of-charming', 'Staff of Charming', 4000, 'gp', 4.0,
     "This staff has 10 charges. While holding it, you can use any of the following properties:\n\n"
     "• **Cast Spell.** You can expend 1 charge to cast *Charm Person*, *Command*, or *Comprehend Languages* using your spell save DC.\n"
     "• **Reflect Enchantment.** If you succeed on a saving throw against an Enchantment spell that targets only you, you can use a Reaction to expend 1 charge and turn the spell back on its caster as if you had cast it.\n"
     "• **Resist Enchantment.** If you fail a saving throw against an Enchantment spell that targets only you, you can choose to succeed instead. You can’t use this property again until the next dawn.\n\n"
     "The staff regains 1d8 + 2 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the staff crumbles to dust and is destroyed.\n\n"
     "Requires attunement by a Bard, Cleric, Druid, Sorcerer, Warlock, or Wizard.",
     0, True, 'Rare', 'Staff'),

    ('staff-of-fire', 'Staff of Fire', 40000, 'gp', 4.0,
     "You have Resistance to Fire damage while you hold this staff.\n\n"
     "The staff has 10 charges. While holding it, you can cast the following spells from it using your spell save DC:\n"
     "• *Burning Hands* (1 charge)\n"
     "• *Fireball* (3 charges)\n"
     "• *Wall of Fire* (4 charges)\n\n"
     "The staff regains 1d6 + 4 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the staff crumbles into cinders and is destroyed.\n\n"
     "Requires attunement by a Druid, Sorcerer, Warlock, or Wizard.",
     0, True, 'Very Rare', 'Staff'),

    ('staff-of-flowers', 'Staff of Flowers', 100, 'gp', 4.0,
     "This wooden staff has 10 charges. While holding it, you can take a Magic action to expend 1 charge and cause a flower to sprout from a patch of earth or soil within 5 feet of yourself, or from the staff itself. "
     "Unless you choose a specific kind of flower, the staff creates a mild-scented daisy. The flower is harmless and nonmagical, and it grows or withers as a normal flower would.\n\n"
     "The staff regains 1d6 + 4 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the staff turns into flower petals and is lost forever.",
     0, True, 'Common', 'Staff'),

    ('staff-of-frost', 'Staff of Frost', 40000, 'gp', 4.0,
     "You have Resistance to Cold damage while you hold this staff.\n\n"
     "The staff has 10 charges. While holding it, you can cast the following spells from it using your spell save DC:\n"
     "• *Cone of Cold* (5 charges)\n"
     "• *Fog Cloud* (1 charge)\n"
     "• *Ice Storm* (4 charges)\n"
     "• *Wall of Ice* (4 charges)\n\n"
     "The staff regains 1d6 + 4 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the staff turns to water and is destroyed.\n\n"
     "Requires attunement by a Druid, Sorcerer, Warlock, or Wizard.",
     0, True, 'Very Rare', 'Staff'),

    ('staff-of-healing', 'Staff of Healing', 4000, 'gp', 4.0,
     "This staff has 10 charges. While holding it, you can cast the following spells from it using your spellcasting ability modifier:\n"
     "• *Cure Wounds* – 1 charge per spell level (maximum 4 for a 4th-level casting)\n"
     "• *Lesser Restoration* – 2 charges\n"
     "• *Mass Cure Wounds* – 5 charges\n\n"
     "The staff regains 1d6 + 4 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the staff vanishes in a flash of light and is lost forever.\n\n"
     "Requires attunement by a Bard, Cleric, or Druid.",
     0, True, 'Rare', 'Staff'),

    ('staff-of-power', 'Staff of Power', 40000, 'gp', 4.0,
     "This staff has 20 charges and can be wielded as a magic Quarterstaff that grants a +2 bonus to attack and damage rolls. While holding it, you gain a +2 bonus to AC, saving throws, and spell attack rolls.\n\n"
     "You can cast the following spells from the staff using your spell save DC:\n"
     "• *Cone of Cold* (5 charges)\n"
     "• *Fireball* (5 charges, cast at 5th level)\n"
     "• *Globe of Invulnerability* (6 charges)\n"
     "• *Hold Monster* (5 charges)\n"
     "• *Levitate* (2 charges)\n"
     "• *Lightning Bolt* (5 charges, cast at 5th level)\n"
     "• *Magic Missile* (1 charge)\n"
     "• *Ray of Enfeeblement* (1 charge)\n"
     "• *Wall of Force* (5 charges)\n\n"
     "The staff regains 2d8 + 4 expended charges daily at dawn. If the last charge is expended, roll a d20. On a 1, the staff loses all properties except its +2 bonus to attack and damage. On a 20, it regains 1d8 + 2 charges.\n\n"
     "**Retributive Strike.** You can use a Magic action to break the staff. It explodes in a 30-foot radius. You have a 50% chance to teleport to a random plane. If not, you take 16 × charges in Force damage. Each creature in the area makes a DC 17 Dexterity saving throw, taking 4 × charges on a failure or half on a success.\n\n"
     "Requires attunement by a Sorcerer, Warlock, or Wizard.",
     2, True, 'Very Rare', 'Staff'),

    ('staff-of-swarming-insects', 'Staff of Swarming Insects', 4000, 'gp', 4.0,
     "This staff has 10 charges.\n\n"
     "**Insect Cloud.** While holding the staff, you can take a Magic action and expend 1 charge to cause a swarm of harmless flying insects to fill a 30-foot Emanation originating from you. "
     "The insects remain for 10 minutes, making the area Heavily Obscured for creatures other than you. A strong wind (such as *Gust of Wind*) disperses the swarm and ends the effect.\n\n"
     "**Spells.** While holding the staff, you can cast the following spells using your spell save DC and spell attack modifier:\n"
     "• *Giant Insect* – 4 charges\n"
     "• *Insect Plague* – 5 charges\n\n"
     "The staff regains 1d6 + 4 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, a swarm of insects consumes and destroys the staff, then disperses.\n\n"
     "Requires attunement by a Bard, Cleric, Druid, Sorcerer, Warlock, or Wizard.",
     0, True, 'Rare', 'Staff'),

    ('staff-of-the-adder', 'Staff of the Adder', 400, 'gp', 4.0,
     "As a Bonus Action, you can turn the head of this staff into that of an animate, venomous snake for 1 minute or revert it to its inanimate form.\n\n"
     "When you take the Attack action, you can make one of the attacks using the animated snake head (reach 5 feet). Use your Proficiency Bonus and Wisdom modifier for the attack roll. "
     "On a hit, the target takes 1d6 Piercing damage and 3d6 Poison damage.\n\n"
     "While animate, the snake head can be attacked (AC 15, 20 HP, immune to Poison and Psychic damage). If reduced to 0 HP, the staff is destroyed. "
     "If not destroyed, the staff regains all lost HP when it reverts to inanimate form.\n\n"
     "Requires attunement.",
     0, True, 'Uncommon', 'Staff'),

    ('staff-of-the-magi', 'Staff of the Magi', 200000, 'gp', 4.0,
     "This staff has 50 charges and can be wielded as a magic Quarterstaff that grants a +2 bonus to attack and damage rolls made with it. While holding it, you also gain a +2 bonus to spell attack rolls.\n\n"
     "**Spell Absorption.** While holding the staff, you have Advantage on saving throws against spells. You can take a Reaction when a spell targets only you to absorb it, canceling its effect and gaining charges equal to the spell’s level. "
     "If this brings the total charges above 50, the staff explodes as if you activated Retributive Strike.\n\n"
     "**Spells.** You can cast the following spells from the staff using your spell save DC:\n"
     "• *Arcane Lock*, *Detect Magic*, *Enlarge/Reduce*, *Light*, *Mage Hand*, *Protection from Evil and Good* (0 charges each)\n"
     "• *Flaming Sphere*, *Invisibility*, *Knock*, *Web* (2 charges each)\n"
     "• *Dispel Magic* (3), *Ice Storm*, *Wall of Fire* (4), *Passwall*, *Telekinesis* (5)\n"
     "• *Fireball* (7th-level), *Lightning Bolt* (7th-level), *Conjure Elemental*, *Plane Shift* (7 charges each)\n\n"
     "The staff regains 4d6 + 2 charges daily at dawn. If you expend the last charge, roll a d20. On a 20, it regains 1d12 + 1 charges.\n\n"
     "**Retributive Strike.** As a Magic action, break the staff to cause a 30-foot explosion. You have a 50% chance to teleport to a random plane. If you fail, you take Force damage equal to 16 × the number of charges. "
     "Creatures in the area must make a DC 17 Dexterity saving throw, taking 6 × charges on a failed save, or half on a success.\n\n"
     "Requires attunement by a Sorcerer, Warlock, or Wizard.",
     2, True, 'Legendary', 'Staff'),

    ('staff-of-the-python', 'Staff of the Python', 400, 'gp', 4.0,
     "As a Magic action, you can throw this staff to an unoccupied space within 10 feet, causing it to transform into a Giant Constrictor Snake under your control. "
     "The snake shares your Initiative count and takes its turn immediately after yours.\n\n"
     "You can mentally command the snake on your turn (no action required) if it is within 60 feet and you aren't Incapacitated. You choose its actions or give it general commands like guarding or attacking. "
     "Without a command, it acts defensively.\n\n"
     "As a Bonus Action, you can command the snake to revert to its staff form in its current space. You can’t use this ability again for 1 hour. "
     "If reduced to 0 HP, the snake dies, reverts to the staff, and the staff is destroyed. If it reverts before losing all HP, it regains all of them.\n\n"
     "Requires attunement.",
     0, True, 'Uncommon', 'Staff'),

    ('staff-of-the-woodlands', 'Staff of the Woodlands', 4000, 'gp', 4.0,
     "This staff has 6 charges and can be wielded as a magic Quarterstaff that grants a +2 bonus to attack and damage rolls made with it. While holding it, you gain a +2 bonus to spell attack rolls.\n\n"
     "**Spells.** While holding the staff, you can cast the following spells using your spell save DC:\n"
     "• *Animal Friendship* – 1 charge\n"
     "• *Awaken* – 5 charges\n"
     "• *Barkskin* – 2 charges\n"
     "• *Locate Animals or Plants* – 2 charges\n"
     "• *Pass without Trace* – 2 charges\n"
     "• *Speak with Animals* – 1 charge\n"
     "• *Speak with Plants* – 3 charges\n"
     "• *Wall of Thorns* – 6 charges\n\n"
     "**Tree Form.** You can take a Magic action to plant the staff in the earth and expend 1 charge to transform it into a healthy 60-foot tree with a 5-foot trunk and 20-foot branch radius. The tree radiates faint Transmutation magic. "
     "While touching the tree, you can return it to staff form with a Magic action. Any creature in the tree falls when it reverts.\n\n"
     "The staff regains 1d6 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the staff becomes a nonmagical Quarterstaff.\n\n"
     "Requires attunement by a Druid.",
     2, True, 'Rare', 'Staff'),

    ('staff-of-thunder-and-lightning', 'Staff of Thunder and Lightning', 40000, 'gp', 4.0,
     "This staff can be wielded as a magic Quarterstaff that grants a +2 bonus to attack and damage rolls made with it. It has the following properties (each usable once per day):\n\n"
     "**Lightning.** When you hit with a melee attack, deal an extra 2d6 Lightning damage (no action required).\n\n"
     "**Thunder.** When you hit with a melee attack, the staff emits a thunderous crack audible out to 300 feet. The target must succeed on a DC 17 Constitution saving throw or be Stunned until the end of your next turn.\n\n"
     "**Thunder and Lightning.** After a melee hit, take a Bonus Action to apply both Lightning and Thunder effects simultaneously. This does not consume the daily uses of those individual effects, only this one.\n\n"
     "**Lightning Strike.** Take a Magic action to release a 120-foot-long, 5-foot-wide Lightning bolt. Each creature in the Line makes a DC 17 Dexterity save, taking 9d6 Lightning damage on a fail or half on success.\n\n"
     "**Thunderclap.** Take a Magic action to unleash a thunderclap audible out to 600 feet. Each creature within 60 feet makes a DC 17 Constitution save, taking 2d6 Thunder damage and becoming Deafened for 1 minute on a fail, or half damage on a success.\n\n"
     "Requires attunement.",
     2, True, 'Very Rare', 'Staff'),

    ('staff-of-withering', 'Staff of Withering', 4000, 'gp', 4.0,
     "This staff has 3 charges and regains 1d3 expended charges daily at dawn. It can be wielded as a magic Quarterstaff.\n\n"
     "On a hit, it deals normal Quarterstaff damage, and you can expend 1 charge to deal an extra 2d10 Necrotic damage. "
     "The target must succeed on a DC 15 Constitution saving throw or suffer Disadvantage for 1 hour on Strength and Constitution checks and saving throws.\n\n"
     "Requires attunement by a Cleric, Druid, or Warlock.",
     0, True, 'Rare', 'Staff'),

]
WAND_ROWS: list[tuple[str, str, int, str, float, str, int, bool, str, str]]= [

    ('wand-of-binding', 'Wand of Binding', 4000, 'gp', 0.1,
     "This wand has 7 charges.\n\n"
     "**Spells.** While holding the wand, you can cast the following spells using a spell save DC of 17:\n"
     "• *Hold Monster* – 5 charges\n"
     "• *Hold Person* – 2 charges\n\n"
     "The wand regains 1d6 + 1 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the wand crumbles into ashes and is destroyed.\n\n"
     "Requires attunement.",
     0, True, 'Rare', 'Wand'),

    ('wand-of-conducting', 'Wand of Conducting', 100, 'gp', 0.1,
     "This wand has 3 charges. While holding it, you can take a Magic action to expend 1 charge and create orchestral music by waving it. "
     "The music can be heard out to 120 feet and ends when you stop waving the wand.\n\n"
     "The wand regains all expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, a sad tuba sound plays as the wand crumbles into dust and is destroyed.",
     0, True, 'Common', 'Wand'),

    ('wand-of-enemy-detection', 'Wand of Enemy Detection', 4000, 'gp', 0.1,
     "This wand has 7 charges. While holding it, you can take a Magic action to expend 1 charge. For 1 minute, you know the direction of the nearest creature Hostile to you within 60 feet, "
     "but not its distance. The wand can detect creatures that are Invisible, ethereal, disguised, hidden, or in plain sight. The effect ends if you stop holding the wand.\n\n"
     "The wand regains 1d6 + 1 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the wand crumbles into ashes and is destroyed.",
     0, True, 'Rare', 'Wand'),

    ('wand-of-fear', 'Wand of Fear', 4000, 'gp', 0.1,
     "This wand has 7 charges.\n\n"
     "**Spells.** While holding the wand, you can cast the following spells using a spell save DC of 15:\n"
     "• *Command* (\"flee\" or \"grovel\" only) – 1 charge\n"
     "• *Fear* (60-foot cone) – 3 charges\n\n"
     "The wand regains 1d6 + 1 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the wand crumbles into ashes and is destroyed.\n\n"
     "Requires attunement.",
     0, True, 'Rare', 'Wand'),

    ('wand-of-fireballs', 'Wand of Fireballs', 4000, 'gp', 0.1,
     "This wand has 7 charges. While holding it, you can expend up to 3 charges to cast *Fireball* (save DC 15).\n"
     "• 1 charge: casts *Fireball* at 3rd level\n"
     "• +1 charge: increases spell level by +1 (up to a maximum of 6th level)\n\n"
     "The wand regains 1d6 + 1 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the wand crumbles into ashes and is destroyed.\n\n"
     "Requires attunement by a Spellcaster.",
     0, True, 'Rare', 'Wand'),

    ('wand-of-lightning-bolts', 'Wand of Lightning Bolts', 4000, 'gp', 0.1,
     "This wand has 7 charges. While holding it, you can expend up to 3 charges to cast *Lightning Bolt* (save DC 15).\n"
     "• 1 charge: casts *Lightning Bolt* at 3rd level\n"
     "• +1 charge: increases spell level by +1 (up to a maximum of 6th level)\n\n"
     "The wand regains 1d6 + 1 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the wand crumbles into ashes and is destroyed.\n\n"
     "Requires attunement by a Spellcaster.",
     0, True, 'Rare', 'Wand'),

    ('wand-of-magic-detection', 'Wand of Magic Detection', 400, 'gp', 0.1,
     "This wand has 3 charges. While holding it, you can expend 1 charge to cast *Detect Magic* from it.\n\n"
     "The wand regains 1d3 expended charges daily at dawn.",
     0, True, 'Uncommon', 'Wand'),

    ('wand-of-magic-missiles', 'Wand of Magic Missiles', 400, 'gp', 0.1,
     "This wand has 7 charges. While holding it, you can expend up to 3 charges to cast *Magic Missile*.\n"
     "• 1 charge: casts *Magic Missile* at 1st level\n"
     "• +1 charge: increases spell level by +1 (up to a maximum of 3rd level)\n\n"
     "The wand regains 1d6 + 1 expended charges daily at dawn. If you expend the last charge, roll a d20. On a 1, the wand crumbles into ashes and is destroyed.",
     0, True, 'Uncommon', 'Wand'),

    ('wand-of-orcus', 'Wand of Orcus', 500000, 'gp', 3.0,
     "Wand, artifact (requires attunement)\n"
     "Crafted by Orcus, this skull-topped wand serves his unholy will. You can wield it as a +3 magic Mace that deals an extra 2d12 Necrotic damage. "
     "While holding it, you gain a +3 bonus to AC and may cast Animate Dead (1 charge), Blight (2), Circle of Death (3), Finger of Death (3), Power Word Kill (4), and Speak with Dead (1) (save DC 18). "
     "The wand has 7 charges and regains 1d4 + 3 expended daily at dawn.\n\n"
     "Call Undead. As a Magic action, you can summon 15 Skeletons and 15 Zombies. They obey you until destroyed or until the next dawn. Once used, this property can’t be used again until the next dawn.\n\n"
     "Any non-Orcus attunement attempt causes a DC 17 Con save: on success, take 10d6 Necrotic damage; on failure, die and become a Zombie if Humanoid.\n\n"
     "Sentient (Chaotic Evil, INT 16, WIS 12, CHA 16). Speaks Abyssal and Common. Darkvision 120 ft. Telepathic.\n\n"
     "Personality. The wand seeks the extinction of all life, deceives its wielder, and pretends loyalty to them.\n\n"
     "Destruction. To destroy the wand, the skull must be restored to life and brought to the Positive Plane, where the wand may explode if bathed in positive energy.",
     0, True, 'Artifact', 'Wand'),

    ('wand-of-paralysis', 'Wand of Paralysis', 4000, 'gp', 0.05,
     "Wand, rare (requires attunement by a Spellcaster)\n"
     "This wand has 7 charges. While holding it, you can take a Magic action to expend 1 charge to cause a thin blue ray to streak from the tip toward a creature you can see within 60 feet. "
     "The target must succeed on a DC 15 Constitution saving throw or have the Paralyzed condition for 1 minute. At the end of each of the target’s turns, it repeats the save, ending the effect on a success.\n\n"
     "The wand regains 1d6 + 1 expended charges daily at dawn. If you expend the wand’s last charge, roll a d20. On a 1, the wand crumbles into ashes and is destroyed.",
     0, True, 'Rare', 'Wand'),

    ('wand-of-polymorph', 'Wand of Polymorph', 40000, 'gp', 0.05,
     "Wand, very rare (requires attunement by a Spellcaster)\n"
     "This wand has 7 charges. While holding it, you can expend 1 charge to cast *Polymorph* (save DC 15) from it.\n\n"
     "Regaining Charges. The wand regains 1d6 + 1 expended charges daily at dawn. If you expend the wand’s last charge, roll a d20. On a 1, the wand crumbles into ashes and is destroyed.",
     0, True, 'Very Rare', 'Wand'),

    ('wand-of-pyrotechnics', 'Wand of Pyrotechnics', 100, 'gp', 0.05,
     "Wand, common\n"
     "This wand has 7 charges. While holding it, you can take a Magic action to expend 1 charge and create a harmless burst of multicolored light at a point you can see up to 120 feet away. "
     "The burst of light is accompanied by a crackling noise that can be heard up to 300 feet away. The light is as bright as a torch flame but lasts only a second.\n\n"
     "Regaining Charges. The wand regains 1d6 + 1 expended charges daily at dawn. If you expend the wand's last charge, roll a d20. On a 1, the wand erupts in a harmless pyrotechnic display and is destroyed.",
     0, True, 'Common', 'Wand'),

    ('wand-of-secrets', 'Wand of Secrets', 400, 'gp', 0.05,
     "Wand, uncommon\n"
     "This wand has 3 charges and regains 1d3 expended charges daily at dawn. While holding it, you can take a Magic action to expend 1 charge. "
     "If a secret door or trap is within 60 feet of you, the wand pulses and points at the one nearest to you.",
     0, True, 'Uncommon', 'Wand'),

    ('wand-of-the-war-mage-plus-one', 'Wand of the War Mage +1', 4000, 'gp', 0.05,
     "Wand, uncommon (requires attunement by a Spellcaster)\n"
     "While holding this wand, you gain a +1 bonus to spell attack rolls. In addition, you ignore Half Cover when making a spell attack roll.",
     0, True, 'Uncommon', 'Wand'),

    ('wand-of-the-war-mage-plus-two', 'Wand of the War Mage +2', 40000, 'gp', 0.05,
     "Wand, rare (requires attunement by a Spellcaster)\n"
     "While holding this wand, you gain a +2 bonus to spell attack rolls. In addition, you ignore Half Cover when making a spell attack roll.",
     0, True, 'Rare', 'Wand'),

    ('wand-of-the-war-mage-plus-three', 'Wand of the War Mage +3', 200000, 'gp', 0.05,
     "Wand, very rare (requires attunement by a Spellcaster)\n"
     "While holding this wand, you gain a +3 bonus to spell attack rolls. In addition, you ignore Half Cover when making a spell attack roll.",
     0, True, 'Very Rare', 'Wand'),

    ('wand-of-web', 'Wand of Web', 4000, 'gp', 0.05,
     "Wand, uncommon (requires attunement by a Spellcaster)\n"
     "This wand has 7 charges. While holding it, you can expend 1 charge to cast *Web* (save DC 13) from it.\n\n"
     "Regaining Charges. The wand regains 1d6 + 1 expended charges daily at dawn. If you expend the wand’s last charge, roll 1d20. On a 1, the wand crumbles into ashes and is destroyed.",
     0, True, 'Uncommon', 'Wand'),

    ('wand-of-wonder', 'Wand of Wonder', 4000, 'gp', 0.05,
     "Wand, rare (requires attunement)\n"
     "This wand has 7 charges. While holding it, you can take a Magic action to expend 1 charge and cause a magical effect at a point within 120 feet, as determined by a d100 roll on the Wand of Wonder Effects table. Spells cast from the wand have a save DC of 15 and a range of 120 feet. If the spell has multiple possible targets, the DM chooses randomly.\n\n"
     "Wand of Wonder Effects (1d100):\n"
     "01–20: Cast a random spell (Darkness, Faerie Fire, Fireball, Slow, or Stinking Cloud).\n"
     "21–25: You are Stunned until the start of your next turn.\n"
     "26–30: Cast Gust of Wind from you to the point.\n"
     "31–35: You take 1d6 Psychic damage.\n"
     "36–40: Heavy rain in a 60-ft-radius Cylinder for 1 min.\n"
     "41–45: 600 butterflies heavily obscure a 30-ft-radius Cylinder.\n"
     "46–50: Cast Lightning Bolt from you to the point.\n"
     "51–55: Nearest creature is enlarged (or you, if invalid).\n"
     "56–60: A random creature (Rhino, Elephant, Rat) appears for 1 hour.\n"
     "61–64: Grass overgrows a 60-ft-radius circle.\n"
     "65–68: Object vanishes into the Ethereal Plane.\n"
     "69–72: You shrink for 1 minute.\n"
     "73–77: Leaves grow from the nearest creature for 24 hours.\n"
     "78–82: 30-ft burst of light may Blind (DC 15 Con save).\n"
     "83–87: You cast Invisibility on yourself.\n"
     "88–92: 1d4×10 gems (1gp each) shoot in a 30-ft Line, dividing 1 Bludgeoning dmg each.\n"
     "93–97: Cast Polymorph on nearest creature (Bear, Wasp, or Frog).\n"
     "98–00: Creature must save (DC 15 Con) or become Petrified over 2 rounds.\n\n"
     "Regaining Charges. The wand regains 1d6 + 1 expended charges daily at dawn. If you expend the last charge, roll 1d20. On a 1, the wand crumbles into dust and is destroyed.",
     0, True, 'Rare', 'Wand'),

]
RING_ROWS: list[tuple[str, str, int, str, float, str, int, bool, str, str]] = [

    # rings
    ('ring-of-animal-influence', 'Ring of Animal Influence', 4000, 'gp', 0.05,
     "This ring has 3 charges, and it regains 1d3 expended charges daily at dawn. While wearing the ring, you can expend 1 charge to cast one of the following spells (save DC 13) from it: 1.) *Animal Friendship*, 2.) *Fear (affects Beasts only)*, 3.) *Speak with Animals*",
     0, True, 'Rare', 'Ring'),

    ('ring-of-djinni-summoning', 'Ring of Djinni Summoning', 200000, 'gp', 0.05,
     "While wearing this ring, you can take a Magic action to summon a particular Djinni from the Elemental Plane of Air. The djinni appears in an unoccupied space you choose within 120 feet of yourself. It remains as long as you maintain Concentration, to a maximum of 1 hour, or until it drops to 0 Hit Points."
     " While summoned, the djinni is Friendly to you and your allies, and it obeys your commands. If you fail to command it, the djinni defends itself against attackers but takes no other actions. After the djinni departs, it can’t be summoned again for 24 hours, and the ring becomes nonmagical if the djinni dies."
     " Rings of Djinni Summoning are often created by the djinn they summon and given to mortals as gifts of friendship or tokens of esteem.",
     0, True, 'Legendary', 'Ring'),

    ('ring-of-elemental-command-air', 'Ring of Elemental Command (Air)', 200000, 'gp', 0.05,
     "This ring is linked to the Elemental Plane of Air.\n"
     "Elemental Bane: While wearing the ring, you have advantage on attack rolls against Elementals and they have disadvantage on attack rolls against you.\n"
     "Elemental Compulsion: As a Magic action, you can attempt to compel an Elemental within 60 ft (DC 18 Wisdom save). On a failure, it is charmed until the start of your next turn and follows your commands.\n"
     "Elemental Focus – Air: You know Auran, gain resistance to lightning damage, and have a fly speed equal to your walking speed. You can hover.\n"
     "Spellcasting: The ring has 5 charges and regains 1d4+1 daily at dawn. You can expend charges to cast Air-aligned spells (DC 18).",
     0, True, 'Legendary', 'Ring'),

    ('ring-of-elemental-command-earth', 'Ring of Elemental Command (Earth)', 200000, 'gp', 0.05,
     "This ring is linked to the Elemental Plane of Earth.\n"
     "Elemental Bane: While wearing the ring, you have advantage on attack rolls against Elementals and they have disadvantage on attack rolls against you.\n"
     "Elemental Compulsion: As a Magic action, you can attempt to compel an Elemental within 60 ft (DC 18 Wisdom save). On a failure, it is charmed until the start of your next turn and follows your commands.\n"
     "Elemental Focus – Earth: You know Terran, gain resistance to acid damage, ignore rocky difficult terrain, and can move through earth/rock as if it were difficult terrain. If you end your turn inside solid matter, you are shunted to your last space.\n"
     "Spellcasting: The ring has 5 charges and regains 1d4+1 daily at dawn. You can expend charges to cast Earth-aligned spells (DC 18).",
     0, True, 'Legendary', 'Ring'),

    ('ring-of-elemental-command-fire', 'Ring of Elemental Command (Fire)', 200000, 'gp', 0.05,
     "This ring is linked to the Elemental Plane of Fire.\n"
     "Elemental Bane: While wearing the ring, you have advantage on attack rolls against Elementals and they have disadvantage on attack rolls against you.\n"
     "Elemental Compulsion: As a Magic action, you can attempt to compel an Elemental within 60 ft (DC 18 Wisdom save). On a failure, it is charmed until the start of your next turn and follows your commands.\n"
     "Elemental Focus – Fire: You know Ignan and gain immunity to fire damage.\n"
     "Spellcasting: The ring has 5 charges and regains 1d4+1 daily at dawn. You can expend charges to cast Fire-aligned spells (DC 18).",
     0, True, 'Legendary', 'Ring'),

    ('ring-of-elemental-command-water', 'Ring of Elemental Command (Water)', 200000, 'gp', 0.05,
     "This ring is linked to the Elemental Plane of Water.\n"
     "Elemental Bane: While wearing the ring, you have advantage on attack rolls against Elementals and they have disadvantage on attack rolls against you.\n"
     "Elemental Compulsion: As a Magic action, you can attempt to compel an Elemental within 60 ft (DC 18 Wisdom save). On a failure, it is charmed until the start of your next turn and follows your commands.\n"
     "Elemental Focus – Water: You know Aquan, gain a swim speed of 60 feet, and can breathe underwater.\n"
     "Spellcasting: The ring has 5 charges and regains 1d4+1 daily at dawn. You can expend charges to cast Water-aligned spells (DC 18).",
     0, True, 'Legendary', 'Ring'),

    ('ring-of-elemental-command-classic', 'Ring of Elemental Command (Classic)', 200000, 'gp', 0.05,
    "This powerful ring is linked to one of the four Elemental Planes: Air, Earth, Fire, or Water. The DM chooses the linked plane or determines it randomly.\n"
    "Elemental Bane: While wearing the ring, you have advantage on attack rolls against Elementals and they have disadvantage on attack rolls against you.\n"
    "Elemental Compulsion: As a Magic action, you can attempt to compel an Elemental within 60 ft (DC 18 Wisdom save). On a failed save, it is charmed until the start of your next turn and follows your commands.\n"
    "Elemental Focus: You gain the language, resistance or immunity, movement mode, and other traits based on the linked plane (see individual variants).\n"
    "Spellcasting: The ring has 5 charges and regains 1d4+1 expended charges daily at dawn. You can cast spells associated with the linked plane by expending charges (DC 18).",
    0, True, 'Legendary', 'Ring'),

    ('ring-of-evasion', 'Ring of Evasion', 4000, 'gp', 0.05,
     "This ring has 3 charges, and it regains 1d3 expended charges daily at dawn. When you fail a Dexterity saving throw while wearing the ring, you can take a Reaction to expend 1 charge to succeed on that save instead.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-feather-falling', 'Ring of Feather Falling', 4000, 'gp', 0.05,
     "When you fall while wearing this ring, you descend 60 feet per round and take no damage from falling.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-free-action', 'Ring of Free Action', 9000, 'gp', 0.05,
     "While you wear this ring, difficult terrain doesn’t cost you extra movement. In addition, magic can’t reduce any of your speeds or cause you to be paralyzed or restrained. Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-invisibility', 'Ring of Invisibility', 200000, 'gp', 0.05,
     "While wearing this ring, you can take a Magic action to give yourself the Invisible condition. You remain Invisible until the ring is removed or until you take a Bonus Action to become visible again. Requires attunement.",
     0, True, 'Legendary', 'Ring'),

    ('ring-of-jumping', 'Ring of Jumping', 400, 'gp', 0.05,
     "While wearing this ring, you can cast the *Jump* spell from it, but can only target yourself when you do so.",
     0, True, 'Uncommon', 'Ring'),

    ('ring-of-mind-shielding', 'Ring of Mind Shielding', 4000, 'gp', 0.05,
     "While wearing this ring, you are immune to magic that allows other creatures to read your thoughts, determine whether you are lying, know your alignment, or know your creature type. Creatures can telepathically communicate with you only if you allow it.\n"
     "You can take a Magic action to cause the ring to become imperceptible until you take another Magic action to make it perceptible, until you remove the ring, or until you die.\n"
     "If you die while wearing the ring, your soul enters it, unless it already houses a soul. You can remain in the ring or depart for the afterlife. As long as your soul is in the ring, you can telepathically communicate with any creature wearing it. A wearer can’t prevent this telepathic communication. Requires attunement.",
     0, True, 'Uncommon', 'Ring'),

    ('ring-of-protection', 'Ring of Protection', 4000, 'gp', 0.05,
     "You gain a +1 bonus to Armor Class and saving throws while wearing this ring. Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-regeneration', 'Ring of Regeneration', 40000, 'gp', 0.05,
     "While wearing this ring, you regain 1d6 hit points every 10 minutes if you have at least 1 hit point. "
     "If you lose a body part, the ring causes the missing part to regrow and return to full functionality after 1d6 + 1 days, "
     "provided you have at least 1 hit point for the entire duration. Requires attunement.",
     0, True, 'Very Rare', 'Ring'),

    ('ring-of-resistance-acid', 'Ring of Resistance (Acid)', 4000, 'gp', 0.05,
     "While wearing this ring, you have resistance to acid damage. The gemstone set in the ring is a pearl. Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-resistance-cold', 'Ring of Resistance (Cold)', 4000, 'gp', 0.05,
     "While wearing this ring, you have resistance to cold damage. The gemstone set in the ring is a tourmaline. Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-resistance-fire', 'Ring of Resistance (Fire)', 4000, 'gp', 0.05,
     "While wearing this ring, you have resistance to fire damage. The gemstone set in the ring is a garnet. Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-resistance-force', 'Ring of Resistance (Force)', 4000, 'gp', 0.05,
     "While wearing this ring, you have resistance to force damage. The gemstone set in the ring is a sapphire. Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-resistance-lightning', 'Ring of Resistance (Lightning)', 4000, 'gp', 0.05,
     "While wearing this ring, you have resistance to lightning damage. The gemstone set in the ring is a citrine. Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-resistance-necrotic', 'Ring of Resistance (Necrotic)', 4000, 'gp', 0.05,
     "While wearing this ring, you have resistance to necrotic damage. The gemstone set in the ring is a jet. Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-resistance-poison', 'Ring of Resistance (Poison)', 4000, 'gp', 0.05,
     "While wearing this ring, you have resistance to poison damage. The gemstone set in the ring is an amethyst. Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-resistance-psychic', 'Ring of Resistance (Psychic)', 4000, 'gp', 0.05,
     "While wearing this ring, you have resistance to psychic damage. The gemstone set in the ring is a jade. Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-resistance-radiant', 'Ring of Resistance (Radiant)', 4000, 'gp', 0.05,
     "While wearing this ring, you have resistance to radiant damage. The gemstone set in the ring is a topaz. Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-resistance-thunder', 'Ring of Resistance (Thunder)', 4000, 'gp', 0.05,
     "While wearing this ring, you have resistance to thunder damage. The gemstone set in the ring is a spinel. Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-resistance-classic', 'Ring of Resistance (Classic)', 4000, 'gp', 0.05,
     "While wearing this ring, you have resistance to one damage type. The type is chosen by the DM or determined randomly. The ring's gemstone changes based on the damage type:\n"
     "1. Acid – Pearl\n2. Cold – Tourmaline\n3. Fire – Garnet\n4. Force – Sapphire\n5. Lightning – Citrine\n"
     "6. Necrotic – Jet\n7. Poison – Amethyst\n8. Psychic – Jade\n9. Radiant – Topaz\n10. Thunder – Spinel\n"
     "Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-shooting-stars', 'Ring of Shooting Stars', 40000, 'gp', 0.05,
     "While wearing this ring, you can cast *Dancing Lights* or *Light*.\n"
     "The ring has 6 charges and regains 1d6 expended charges daily at dawn. You can expend charges to use the following properties:\n"
     "- **Faerie Fire** (1 charge): Cast *Faerie Fire*.\n"
     "- **Lightning Spheres** (2 charges): As a Magic action, create up to four 3-foot lightning spheres within 120 ft. Each emits dim light in a 30-foot radius. As a bonus action, move each up to 30 ft. When a sphere comes within 5 ft of a creature, it discharges lightning and vanishes (DC 15 Dex save). Damage varies by number of spheres:\n"
     "   • 1 sphere: 4d12 lightning\n   • 2 spheres: 5d4\n   • 3 spheres: 2d6\n   • 4 spheres: 2d4\n"
     "- **Shooting Stars** (1–3 charges): For each charge, launch a mote of light at a point within 60 ft. Each creature in a 15-ft cube from that point must make a DC 15 Dex save, taking 5d4 radiant damage on a fail, or half on a success.\n"
     "Requires attunement. Functions best in dim light or darkness.",
     0, True, 'Very Rare', 'Ring'),

    ('ring-of-spell-storing', 'Ring of Spell Storing', 40000, 'gp', 0.05,
     "This ring stores spells cast into it, holding them until the attuned wearer uses them. The ring can store up to 5 levels worth of spells at a time. When found, it contains 1d6 − 1 levels of stored spells chosen by the DM.\n"
     "Any creature can cast a spell of level 1 through 5 into the ring by touching it while casting. The spell has no effect other than to be stored in the ring. If there isn’t enough space, the spell is wasted.\n"
     "While wearing this ring, you can cast any stored spell. The spell uses the original caster's slot level, save DC, attack bonus, and spellcasting ability, but is otherwise treated as if you cast it. Once used, the spell leaves the ring, freeing up space.\n"
     "Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-spell-turning', 'Ring of Spell Turning', 200000, 'gp', 0.05,
     "While wearing this ring, you have advantage on saving throws against spells. If you succeed on a save against a spell of 7th level or lower, the spell has no effect on you. "
     "If the spell targeted only you and did not create an area of effect, you can use your reaction to turn the spell back on its caster. The caster must make a saving throw against their own spell save DC. Requires attunement.",
     0, True, 'Legendary', 'Ring'),

    ('ring-of-swimming', 'Ring of Swimming', 400, 'gp', 0.05,
     "While wearing this ring, you have a swim speed of 40 feet.",
     0, True, 'Uncommon', 'Ring'),

    ('ring-of-telekinesis', 'Ring of Telekinesis', 20000, 'gp', 0.05,
     "While wearing this ring, you can cast Telekinesis from it. Requires attunement.",
     0, True, 'Very Rare', 'Ring'),

    ('ring-of-the-ram', 'Ring of the Ram', 4000, 'gp', 0.05,
     "This ring has 3 charges and regains 1d3 expended charges daily at dawn. While wearing the ring, you can take a Magic action to expend 1 to 3 charges to make a ranged spell attack against one creature you can see within 60 feet. The ring creates a spectral ram's head with a +7 attack bonus. On a hit, the target takes 2d10 force damage per charge spent and is pushed 5 feet away from you per charge.\n"
     "Alternatively, you can use 1 to 3 charges to try breaking a nonmagical object within 60 feet that isn't being worn or carried. The ring makes a Strength check with a +5 bonus per charge spent. Requires attunement.",
     0, True, 'Rare', 'Ring'),

    ('ring-of-three-wishes', 'Ring of Three Wishes', 200000, 'gp', 0.05,
     "While wearing this ring, you can expend one of its 3 charges to cast *Wish*. When the last charge is used, the ring becomes nonmagical. Requires attunement. Consumable.",
     0, True, 'Legendary', 'Ring'),

    ('ring-of-warmth', 'Ring of Warmth', 400, 'gp', 0.05,
     "If you take cold damage while wearing this ring, the damage is reduced by 2d8. In addition, you and everything you wear and carry are unharmed by temperatures of 0°F or lower. Requires attunement.",
     0, True, 'Uncommon', 'Ring'),

    ('ring-of-water-walking', 'Ring of Water Walking', 400, 'gp', 0.05,
    "While wearing this ring, you can cast *Water Walk*, targeting only yourself. Requires attunement.",
    0, True, 'Uncommon', 'Ring'),

    ('ring-of-xray-vision', 'Ring of X-Ray Vision', 4000, 'gp', 0.05,
    "While wearing this ring, you can take a Magic action to gain X-ray vision with a range of 30 feet for 1 minute. Solid objects within that radius appear transparent and don’t block light. The vision can penetrate 1 foot of stone, 1 inch of common metal, or up to 3 feet of wood or dirt. Thicker substances or a thin sheet of lead block the effect.\n"
    "If you use the ring again before finishing a long rest, you must succeed on a DC 15 Constitution saving throw or gain 1 level of exhaustion. Requires attunement.",
    0, True, 'Rare', 'Ring'),


]

EQUIPABLE_MAGIC_ITEMS_ROWS: list[tuple[str, str, int, str, float, str, int, bool, str, str]] = [
    *ROD_ROWS,
    *WAND_ROWS,
    *STAFF_ROWS,
    *RING_ROWS,
]
#--EQUIPABLE-END----------------------------------------

# pg 288+
# c100, u400, r4000, vr40000, l200000, a500000*

##todo: WONDROUS ITEMS
##TODO: EQUIPABBLE +1 BONUSES ETC FOR CUSTOM ITEMS MIGHT NEED SAME INTSERT AS WEAPONS