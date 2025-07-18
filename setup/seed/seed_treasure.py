# Gemstone seed rows (srd_index, item_name, base_price, description)
GEM_ROWS: list[tuple[str, str, int, str, str]] = [
    ("azurite", "Azurite", 10, "opaque mottled deep blue. This gem drops on a \"1\" from a D12 roll", "Common"),
    ("banded-agate", "Banded agate", 10, "translucent striped brown, blue, white, or red. This gem drops on a \"2\" from a D12 roll", "Common"),
    ("blue-quartz", "Blue quartz", 10, "transparent pale blue. This gem drops on a \"3\" from a D12 roll", "Common"),
    ("eye-agate", "Eye agate", 10, "translucent circles of gray, white, brown, blue, or green. This gem drops on a \"4\" from a D12 roll", "Common"),
    ("hematite", "Hematite", 10, "opaque gray-black. This gem drops on a \"5\" from a D12 roll", "Common"),
    ("lapis-lazuli", "Lapis lazuli", 10, "opaque light and dark blue with yellow flecks. This gem drops on a \"6\" from a D12 roll", "Common"),
    ("malachite", "Malachite", 10, "opaque striated light and dark green. This gem drops on a \"7\" from a D12 roll", "Common"),
    ("moss-agate", "Moss agate", 10, "translucent pink or yellow-white with mossy gray or green markings. This gem drops on a \"8\" from a D12 roll", "Common"),
    ("obsidian", "Obsidian", 10, "opaque black. This gem drops on a \"9\" from a D12 roll", "Common"),
    ("rhodochrosite", "Rhodochrosite", 10, "opaque light pink. This gem drops on a \"10\" from a D12 roll", "Common"),
    ("tiger-eye", "Tiger eye", 10, "translucent brown with golden center. This gem drops on a \"11\" from a D12 roll", "Common"),
    ("turquoise", "Turquoise", 10, "opaque light blue-green. This gem drops on a \"12\" from a D12 roll", "Common"),
    ("bloodstone", "Bloodstone", 50, "opaque dark gray with red flecks. This gem drops on a \"1\" from a D10 roll", "Uncommon"),
    ("carnelian", "Carnelian", 50, "opaque orange to red-brown. This gem drops on a \"2\" from a D10 roll", "Uncommon"),
    ("chalcedony", "Chalcedony", 50, "opaque white. This gem drops on a \"3\" from a D10 roll", "Uncommon"),
    ("chrysoprase", "Chrysoprase", 50, "translucent green. This gem drops on a \"4\" from a D10 roll", "Uncommon"),
    ("citrine", "Citrine", 50, "transparent pale yellow-brown. This gem drops on a \"5\" from a D10 roll", "Uncommon"),
    ("jasper", "Jasper", 50, "opaque blue, black, or brown. This gem drops on a \"6\" from a D10 roll", "Uncommon"),
    ("moonstone", "Moonstone", 50, "translucent white with pale blue glow. This gem drops on a \"7\" from a D10 roll", "Uncommon"),
    ("onyx", "Onyx", 50, "opaque bands of black and white, or pure black or white. This gem drops on a \"8\" from a D10 roll", "Uncommon"),
    ("quartz", "Quartz", 50, "transparent white, smoky gray, or yellow. This gem drops on a \"9\" from a D10 roll", "Uncommon"),
    ("sardonyx", "Sardonyx", 50, "opaque bands of red and white. This gem drops on a \"10\" from a D10 roll", "Uncommon"),
    ("star-rose-quartz", "Star rose quartz", 50, "translucent rosy stone with white star-shaped center. This gem drops on a \"11\" from a D10 roll", "Uncommon"),
    ("zircon", "Zircon", 50, "transparent pale blue-green. This gem drops on a \"12\" from a D10 roll", "Uncommon"),
    ("amber", "Amber", 100, "watery gold to rich gold. This gem drops on a \"1\" from a D8 roll", "Rare"),
    ("amethyst", "Amethyst", 100, "deep purple. This gem drops on a \"2\" from a D8 roll", "Rare"),
    ("chrysoberyl", "Chrysoberyl", 100, "yellow-green to pale green. This gem drops on a \"3\" from a D8 roll", "Rare"),
    ("coral", "Coral", 100, "crimson. This gem drops on a \"4\" from a D8 roll", "Rare"),
    ("garnet", "Garnet", 100, "red, brown-green, or violet. This gem drops on a \"5\" from a D8 roll", "Rare"),
    ("jade", "Jade", 100, "light green, deep green or white. This gem drops on a \"6\" from a D8 roll", "Rare"),
    ("jet", "Jet", 100, "deep black. This gem drops on a \"7\" from a D8 roll", "Rare"),
    ("pearl", "Pearl", 100, "lustrous white, yellow or pink. This gem drops on a \"8\" from a D8 roll", "Rare"),
    ("spinel", "Spinel", 100, "red, red-brown, or deep green. This gem drops on a \"9\" from a D8 roll", "Rare"),
    ("tourmaline", "Tourmaline", 100, "pale green, blue, brown or red. This gem drops on a \"10\" from a D8 roll", "Rare"),
    ("alexandrite", "Alexandrite", 500, "transparent dark green. This gem drops on a \"1\" from a D6 roll", "Rare"),
    ("aquamarine", "Aquamarine", 500, "transparent pale blue-green. This gem drops on a \"2\" from a D6 roll", "Rare"),
    ("black-pearl", "Black pearl", 500, "opaque pure black. This gem drops on a \"3\" from a D6 roll", "Rare"),
    ("blue-spinel", "Blue spinel", 500, "transparent deep blue. This gem drops on a \"4\" from a D6 roll" , "Rare"),
    ("peridot", "Peridot", 500, "transparent rich olive green. This gem drops on a \"5\" from a D6 roll","Rare"),
    ("topaz", "Topaz", 500, "transparent golden yellow. This gem drops on a \"6\" from a D6 roll", "Rare"),
    ("black-opal", "Black opal", 1000, "translucent dark green with black mottling and golden flecks. This gem drops on a \"1\" from a D8 roll", "Very Rare"),
    ("blue-sapphire", "Blue sapphire", 1000, "transparent blue-white to medium blue. This gem drops on a \"2\" from a D8 roll", "Very Rare"),
    ("emerald", "Emerald", 1000, "transparent deep bright green. This gem drops on a \"3\" from a D8 roll", "Very Rare"),
    ("fire-opal", "Fire opal", 1000, "translucent fiery red. This gem drops on a \"4\" from a D8 roll", "Very Rare"),
    ("opal", "Opal", 1000, "translucent pale blue with green and golden mottling. This gem drops on a \"5\" from a D8 roll", "Very Rare"),
    ("star-ruby", "Star ruby", 1000, "translucent ruby with white star-shaped center. This gem drops on a \"6\" from a D8 roll", "Very Rare"),
    ("star-sapphire", "Star sapphire", 1000, "translucent blue sapphire with white star-shaped center. This gem drops on a \"7\" from a D8 roll", "Very Rare"),
    ("yellow-sapphire", "Yellow sapphire", 1000, "transparent fiery yellow or yellow-green. This gem drops on a \"8\" from a D8 roll", "Very Rare"),
    ("black-sapphire", "Black sapphire", 5000, "translucent lustrous black with glowing highlights. This gem drops on a \"1\" from a D4 roll", "Very Rare"),
    ("diamond", "Diamond", 5000, "transparent blue-white, canary, pink, brown, or blue. This gem drops on a \"2\" from a D4 roll", "Very Rare"),
    ("jacinth", "Jacinth", 5000, "transparent fiery orange. This gem drops on a \"3\" from a D4 roll", "Very Rare"),
    ("ruby", "Ruby", 5000, "transparent clear red to deep crimson. This gem drops on a \"4\" from a D4 roll", "Very Rare"),
]

TRADEBAR_ROWS: list[tuple[str, str, int, str, str]] = [

    ("2-lb-silver", "2-pound silver bar", 10, "Dimensions: 5 inch long x 2 inch wide x 1/2 inch thick", "Common"),
    ("5-lb-silver", "5-pound silver bar", 25, "Dimensions: 6 inch long x 2 inch wide x 1 inch thick", "Uncommon"),
    ("5-lb-gold", "5-pound gold bar", 250, "Dimensions: 5 inch long x 2 inch wide x 3/4 inch thick", "Rare"),
]

TRADEGOODS_ROWS: list[tuple[str, str, int, str, str]] = [

    ("1-lb-wheat", "1 lb of wheat", 1, "1 pound of the finest wheat", "Common"),
    ("2-lb-flour", "2 lb of flour", 2, "2 pounds of finely ground flour", "Common"),
    ("chicken", "domestic chicken", 2, "pukaww", "Common"),
    ("1-lb-salt", "1 lb of salt", 5, "1 pound of salt grains", "Common"),
    ("1-lb-iron", "1 lb of iron", 50, "1 pound of pure iron", "Common"),
    ("1-yrd-canvas", "1 sq. yd. of canvas", 250, "1 square yard of canvas", "Common"),
    ("1-yrd-cloth", "1 sq. yd. of cotton cloth", 250, "1 square yard of cotton cloth", "Common"),
    ("1-lb-ginger", "1 lb of ginger", 100, "1 pound of ginger", "Common"),
    ("goat", "goat", 100, " 4 legged creature with horns and a funny look in it's eye", "Common"),
    ("1-lb-cinnamon", "1 lb of cinnamon", 100, " 1 lb of sweet cinnamon", "Common"),
    ("1-lb-pepper", "1 lb of pepper", 100, " 1 pound of pepper", "Common"),
    ("sheep", "domestic sheep", 200, " Highly cuddly 4 legged creature", "Common"),
    ("1-lb-cloves", "1 lb of cloves", 300, " Highly cuddly 4 legged creature", "Common"),
    ("pig", "domestic pig", 300, "A perfectly porcine specimen", "Common"),
    ("1-lb-silver", "1 lb of silver", 500, "1 pound of pure silver", "Uncommon"),
    ("1-yrd-linen", "1 sq. yd. of linen", 500, "1 square yard of linen", "Uncommon"),
    ("1-lb-silk", "1 lb of silk", 1000, "1 pound of the finest silk, it is cool and pleasant to the touch.", "Uncommon"),
    ("cow", "domestic cow", 1000, "A perfectly fine bovine", "Uncommon"),
    ("1-lb-saffron", "1 lb of saffron", 1500, "Perfectly coloured saffron", "Rare"),
    ("Ox", "a domestic ox", 1000, "Another perfectly fine bovine", "Rare"),
    ("1lb. of gold", "1 lb of gold", 5000, "1 pound of pure gold", "Rare"),
    ("1lb. of platinum", "1 lb of platinum", 50000, "1 pound of the finest platinum", "Very Rare"),
]

ARTOBJECTS_ROWS: list[tuple[str, str, int, str, str]] = [

    ("silver-ewer", "Silver ewer", 25, "Silver ewer is a fine art object, valued by collectors and nobles. Drops on a \"1\" on a d10 roll.", "Common"),
    ("carved-bone-statuette", "Carved bone statuette", 25, "Carved bone statuette is a fine art object, valued by collectors and nobles. Drops on a \"2\" on a d10 roll.", "Common"),
    ("small-gold-bracelet", "Small gold bracelet", 25, "Small gold bracelet is a fine art object, valued by collectors and nobles. Drops on a \"3\" on a d10 roll.", "Common"),
    ("cloth-of-gold-vestments", "Cloth-of-gold vestments", 25, "Cloth-of-gold vestments is a fine art object, valued by collectors and nobles. Drops on a \"4\" on a d10 roll.", "Common"),
    ("black-velvet-mask-stitched-with-", "Black velvet mask stitched with silver thread", 25, "Black velvet mask stitched with silver thread is a fine art object, valued by collectors and nobles. Drops on a \"5\" on a d10 roll.", "Common"),
    ("copper-chalice-with-silver-filig", "Copper chalice with silver filigree", 25, "Copper chalice with silver filigree is a fine art object, valued by collectors and nobles. Drops on a \"6\" on a d10 roll.", "Common"),
    ("pair-of-engraved-bone-dice", "Pair of engraved bone dice", 25, "Pair of engraved bone dice is a fine art object, valued by collectors and nobles. Drops on a \"7\" on a d10 roll.", "Common"),
    ("small-mirror-set-in-a-painted-wo", "Small mirror set in a painted wooden frame", 25, "Small mirror set in a painted wooden frame is a fine art object, valued by collectors and nobles. Drops on a \"8\" on a d10 roll.", "Common"),
    ("embroidered-silk-handkerchief", "Embroidered silk handkerchief", 25, "Embroidered silk handkerchief is a fine art object, valued by collectors and nobles. Drops on a \"9\" on a d10 roll.", "Common"),
    ("gold-locket-with-a-painted-portr", "Gold locket with a painted portrait inside", 25, "Gold locket with a painted portrait inside is a fine art object, valued by collectors and nobles. Drops on a \"10\" on a d10 roll.", "Common"),

    ("gold-ring-set-with-bloodstones", "Gold ring set with bloodstones", 250, "Gold ring set with bloodstones is a fine art object, valued by collectors and nobles. Drops on a \"1\" on a d10 roll.", "Uncommon"),
    ("carved-ivory-statuette", "Carved ivory statuette", 250, "Carved ivory statuette is a fine art object, valued by collectors and nobles. Drops on a \"2\" on a d10 roll.", "Uncommon"),
    ("large-gold-bracelet", "Large gold bracelet", 250, "Large gold bracelet is a fine art object, valued by collectors and nobles. Drops on a \"3\" on a d10 roll.", "Uncommon"),
    ("silver-necklace-with-a-gemstone-", "Silver necklace with a gemstone pendant", 250, "Silver necklace with a gemstone pendant is a fine art object, valued by collectors and nobles. Drops on a \"4\" on a d10 roll.", "Uncommon"),
    ("bronze-crown", "Bronze crown", 250, "Bronze crown is a fine art object, valued by collectors and nobles. Drops on a \"5\" on a d10 roll.", "Uncommon"),
    ("silk-robe-with-gold-embroidery", "Silk robe with gold embroidery", 250, "Silk robe with gold embroidery is a fine art object, valued by collectors and nobles. Drops on a \"6\" on a d10 roll.", "Uncommon"),
    ("large-well-made-tapestry", "Large well-made tapestry", 250, "Large well-made tapestry is a fine art object, valued by collectors and nobles. Drops on a \"7\" on a d10 roll.", "Uncommon"),
    ("brass-mug-with-jade-inlay", "Brass mug with jade inlay", 250, "Brass mug with jade inlay is a fine art object, valued by collectors and nobles. Drops on a \"8\" on a d10 roll.", "Uncommon"),
    ("box-of-turquoise-animal-figurine", "Box of turquoise animal figurines", 250, "Box of turquoise animal figurines is a fine art object, valued by collectors and nobles. Drops on a \"9\" on a d10 roll.", "Uncommon"),
    ("gold-bird-cage-with-electrum-fil", "Gold bird cage with electrum filigree", 250, "Gold bird cage with electrum filigree is a fine art object, valued by collectors and nobles. Drops on a \"10\" on a d10 roll.", "Uncommon"),

    ("silver-chalice-set-with-moonston", "Silver chalice set with moonstones", 750, "Silver chalice set with moonstones is a fine art object, valued by collectors and nobles. Drops on a \"1\" on a d10 roll.", "Rare"),
    ("silver-plated-steellongsword-wit", "Silver-plated steellongsword with jet set in hilt", 750, "Silver-plated steellongsword with jet set in hilt is a fine art object, valued by collectors and nobles. Drops on a \"2\" on a d10 roll.", "Rare"),
    ("carved-harp-of-exotic-wood-with-", "Carved harp of exotic wood with ivory inlay and zircon gems", 750, "Carved harp of exotic wood with ivory inlay and zircon gems is a fine art object, valued by collectors and nobles. Drops on a \"3\" on a d10 roll.", "Rare"),
    ("small-gold-idol", "Small gold idol", 750, "Small gold idol is a fine art object, valued by collectors and nobles. Drops on a \"4\" on a d10 roll.", "Rare"),
    ("gold-dragon-comb-set-with-red-ga", "Gold dragon comb set with red garnets as eyes", 750, "Gold dragon comb set with red garnets as eyes is a fine art object, valued by collectors and nobles. Drops on a \"5\" on a d10 roll.", "Rare"),
    ("bottle-stopper-cork-embossed-wit", "Bottle stopper cork embossed with gold leaf and set with amethysts", 750, "Bottle stopper cork embossed with gold leaf and set with amethysts is a fine art object, valued by collectors and nobles. Drops on a \"6\" on a d10 roll.", "Rare"),
    ("ceremonial-electrum-dagger-with-", "Ceremonial electrum dagger with a black pearl in the pommel", 750, "Ceremonial electrum dagger with a black pearl in the pommel is a fine art object, valued by collectors and nobles. Drops on a \"7\" on a d10 roll.", "Rare"),
    ("silver-and-gold-brooch", "Silver and gold brooch", 750, "Silver and gold brooch is a fine art object, valued by collectors and nobles. Drops on a \"8\" on a d10 roll.", "Rare"),
    ("obsidian-statuette-with-gold-fit", "Obsidian statuette with gold fittings and inlay", 750, "Obsidian statuette with gold fittings and inlay is a fine art object, valued by collectors and nobles. Drops on a \"9\" on a d10 roll.", "Rare"),
    ("painted-gold-war-mask", "Painted gold war mask", 750, "Painted gold war mask is a fine art object, valued by collectors and nobles. Drops on a \"10\" on a d10 roll.", "Rare"),

    ("fine-gold-chain-set-with-a-fire-", "Fine gold chain set with a fire opal", 2500, "Fine gold chain set with a fire opal is a fine art object, valued by collectors and nobles. Drops on a \"1\" on a d10 roll.", "Rare"),
    ("old-masterpiece-painting", "Old masterpiece painting", 2500, "Old masterpiece painting is a fine art object, valued by collectors and nobles. Drops on a \"2\" on a d10 roll.", "Rare"),
    ("embroidered-silk-and-velvet", "Embroidered silk and velvet mantle set with numerous moonstones", 2500, "Embroidered silk and velvet mantle set with numerous moonstones is a fine art object, valued by collectors and nobles. Drops on a \"3\" on a d10 roll.", "Rare"),
    ("platinum-bracelet-set-with-a-sap", "Platinum bracelet set with a sapphire", 2500, "Platinum bracelet set with a sapphire is a fine art object, valued by collectors and nobles. Drops on a \"4\" on a d10 roll.", "Rare"),
    ("embroidered-glove-set-with-jewel", "Embroidered glove set with jewel chips", 2500, "Embroidered glove set with jewel chips is a fine art object, valued by collectors and nobles. Drops on a \"5\" on a d10 roll.", "Rare"),
    ("jeweled-anklet", "Jeweled anklet", 2500, "Jeweled anklet is a fine art object, valued by collectors and nobles. Drops on a \"6\" on a d10 roll.", "Rare"),
    ("gold-music-box", "Gold music box", 2500, "Gold music box is a fine art object, valued by collectors and nobles. Drops on a \"7\" on a d10 roll.", "Rare"),
    ("gold-circlet-set-with-aquam", "Gold circlet set with four aquamarines", 2500, "Gold circlet set with four aquamarines is a fine art object, valued by collectors and nobles. Drops on a \"8\" on a d10 roll.", "Rare"),
    ("eye-patch-with-a-mock-eye-set-in", "Eye patch with a mock eye set in blue sapphire and moonstone", 2500,  "Eye patch with a mock eye set in blue sapphire and moonstone is a fine art object, valued by collectors and nobles. Drops on a \"9\" on a d10 roll.", "Rare"),
    ("a-necklace-string-of-small-pink-", "A necklace string of small pink pearls", 2500, "A necklace string of small pink pearls is a fine art object, valued by collectors and nobles. Drops on a \"10\" on a d10 roll.", "Rare"),

    ("jeweled-gold-crown", "Jeweled gold crown", 7500, "Jeweled gold crown is a fine art object, valued by collectors and nobles. Drops on a \"1\" on a d10 roll.", "Very Rare"),
    ("jeweled-platinum-ring", "Jeweled platinum ring", 7500, "Jeweled platinum ring is a fine art object, valued by collectors and nobles. Drops on a \"2\" on a d10 roll.", "Very Rare"),
    ("small-gold-statuette", "Small gold statuette set with rubies", 7500, "Small gold statuette set with rubies is a fine art object, valued by collectors and nobles. Drops on a \"3\" on a d10 roll.", "Very Rare"),
    ("gold-cup-set-with-emeralds", "Gold cup set with emeralds", 7500, "Gold cup set with emeralds is a fine art object, valued by collectors and nobles. Drops on a \"4\" on a d10 roll.", "Very Rare"),
    ("gold-jewelry-box-with-platinum-f", "Gold jewelry box with platinum filigree", 7500, "Gold jewelry box with platinum filigree is a fine art object, valued by collectors and nobles. Drops on a \"5\" on a d10 roll.", "Very Rare"),
    ("painted-gold-child's-sarcophagus", "Painted gold child's sarcophagus", 7500, "Painted gold child's sarcophagus is a fine art object, valued by collectors and nobles. Drops on a \"6\" on a d10 roll.", "Very Rare"),
    ("jade-game-board-with-solid-gold-", "Jade game board with solid gold playing pieces", 7500, "Jade game board with solid gold playing pieces is a fine art object, valued by collectors and nobles. Drops on a \"7\" on a d10 roll.", "Very Rare"),
    ("bejeweled-ivory-drinking-horn", "Bejeweled ivory drinking horn with gold filigree", 7500, "Bejeweled ivory drinking horn with gold filigree is a fine art object, valued by collectors and nobles. Drops on a \"8\" on a d10 roll.", "Very Rare"),
    ("gilded-royal-coach", "Gilded royal coach / funeral barge", 7500, "Gilded royal coach / funeral barge is a fine art object, valued by collectors and nobles. Drops on a \"9\" on a d10 roll.", "Very Rare"),
    ("ceremonial-gold-armor-black-pearls", "Ceremonial gold armor with black pearls", 7500, "Ceremonial gold armor with black pearls is a fine art object, valued by collectors and nobles. Drops on a \"10\" on a d10 roll.", "Very Rare")

]

