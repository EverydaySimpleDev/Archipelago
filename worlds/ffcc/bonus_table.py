"""
The end-of-dungeon bonus. Each dungeon has 8 reward entries
of 4 items. The game offers entry (cycle start + tier): cycle start is
0 / 2 / 4 for Cycles 1 / 2 / 3, tier is 0-3 by the party's score, and the
player picks one of the entry's 4 items. A tier is reached when the bonus
points times the player-count factor (x1.35 solo, x1.25, x1.1, x1.0 for
2-4 players) are at least its threshold.

BONUS_TABLE[dungeon] = (thresholds, entries)
BONUS_CANDIDATES = the items a randomized slot can get.
"""

BONUS_TABLE = {
    'River Belle Path': ((0, 127, 160, 200), (
        (0x09f, 0x0b6, 0x0d0, 0x0db),   # 0: Shuriken, Dragon's Whisker, Buckler, Moogle Pocket
        (0x0a0, 0x0b7, 0x0d1, 0x0db),   # 1: Maneater, Mage Masher, Silver Spectacles, Moogle Pocket
        (0x0a1, 0x0c6, 0x0d0, 0x127),   # 2: Double Axe, Kris, Buckler, Iron
        (0x0a5, 0x0c1, 0x0d1, 0x127),   # 3: Ice Brand, Silver Bracer, Silver Spectacles, Iron
        (0x0a6, 0x0bd, 0x0d6, 0x128),   # 4: Loaded Dice, Mage's Staff, Wonder Bangle, Mythril
        (0x0a9, 0x0a4, 0x0d3, 0x197),   # 5: Sasuke's Blade, Flametongue, Black Hood, Legendary Weapon
        (0x09f, 0x0b6, 0x0d1, 0x129),   # 6: Shuriken, Dragon's Whisker, Silver Spectacles, Orichalcum
        (0x0a0, 0x0b7, 0x0ce, 0x140),   # 7: Maneater, Mage Masher, Save the Queen, Ancient Sword
    )),
    'Goblin Wall': ((0, 148, 185, 232), (
        (0x0a1, 0x0c4, 0x0d2, 0x0e4),   # 0: Double Axe, Winged Cap, Sparkling Bracer, Earth Pendant
        (0x0a3, 0x0bb, 0x0d2, 0x0e4),   # 1: Kaiser Knuckles, Wonder Wand, Sparkling Bracer, Earth Pendant
        (0x0a2, 0x0c3, 0x0d4, 0x0db),   # 2: Ashura, Faerie Ring, Helm of Arai, Moogle Pocket
        (0x0b2, 0x0c8, 0x0d2, 0x0db),   # 3: Fang Charm, Dark Matter, Sparkling Bracer, Moogle Pocket
        (0x0aa, 0x0c7, 0x0d4, 0x15a),   # 4: Mjollnir, Red Slippers, Helm of Arai, Ancient Potion
        (0x0a8, 0x0be, 0x0d4, 0x129),   # 5: Engetsurin, Noah's Lute, Helm of Arai, Orichalcum
        (0x0b2, 0x0c5, 0x0d6, 0x1cc),   # 6: Fang Charm, Candy Ring, Wonder Bangle, Diamond Belt
        (0x0b1, 0x0bf, 0x0d2, 0x141),   # 7: Green Beret, Galatyn, Sparkling Bracer, Cursed Crook
    )),
    'The Mine of Cathuriges': ((0, 156, 195, 244), (
        (0x09f, 0x0b6, 0x0d0, 0x0e4),   # 0: Shuriken, Dragon's Whisker, Buckler, Earth Pendant
        (0x0a6, 0x0b7, 0x0d1, 0x0db),   # 1: Loaded Dice, Mage Masher, Silver Spectacles, Moogle Pocket
        (0x0a0, 0x0bc, 0x0d0, 0x0e4),   # 2: Maneater, Rune Bell, Buckler, Earth Pendant
        (0x0a1, 0x0c1, 0x0d3, 0x0db),   # 3: Double Axe, Silver Bracer, Black Hood, Moogle Pocket
        (0x0a9, 0x0c2, 0x0d6, 0x197),   # 4: Sasuke's Blade, Cat's Bell, Wonder Bangle, Legendary Weapon
        (0x0b1, 0x0bd, 0x0d6, 0x129),   # 5: Green Beret, Mage's Staff, Wonder Bangle, Orichalcum
        (0x0a3, 0x0c3, 0x0de, 0x142),   # 6: Kaiser Knuckles, Faerie Ring, Ultimate Pocket, Orc Belt
        (0x0af, 0x0c4, 0x0e4, 0x0ac),   # 7: Onion Sword, Winged Cap, Earth Pendant, Murasame
    )),
    'The Mushroom Forest': ((0, 145, 181, 227), (
        (0x09f, 0x0b6, 0x0d0, 0x0e4),   # 0: Shuriken, Dragon's Whisker, Buckler, Earth Pendant
        (0x0a4, 0x0b7, 0x0d1, 0x0db),   # 1: Flametongue, Mage Masher, Silver Spectacles, Moogle Pocket
        (0x0a0, 0x0ba, 0x0d0, 0x0e4),   # 2: Maneater, Sage's Staff, Buckler, Earth Pendant
        (0x0a1, 0x0c1, 0x0d3, 0x0db),   # 3: Double Axe, Silver Bracer, Black Hood, Moogle Pocket
        (0x0a9, 0x0c2, 0x0d6, 0x15a),   # 4: Sasuke's Blade, Cat's Bell, Wonder Bangle, Ancient Potion
        (0x0b1, 0x0bd, 0x0d6, 0x129),   # 5: Green Beret, Mage's Staff, Wonder Bangle, Orichalcum
        (0x0a1, 0x0c1, 0x0db, 0x1a8),   # 6: Double Axe, Silver Bracer, Moogle Pocket, Diamond Armor
        (0x0a2, 0x0c2, 0x0e4, 0x146),   # 7: Ashura, Cat's Bell, Earth Pendant, Malboro Seed
    )),
    'Tida': ((0, 208, 260, 325), (
        (0x0b3, 0x0b6, 0x0d1, 0x0dc),   # 0: Twisted Headband, Dragon's Whisker, Silver Spectacles, Chocobo Pocket
        (0x09f, 0x0c6, 0x0d2, 0x0db),   # 1: Shuriken, Kris, Sparkling Bracer, Moogle Pocket
        (0x0a0, 0x0c1, 0x0d5, 0x0dc),   # 2: Maneater, Silver Bracer, Elven Mantle, Chocobo Pocket
        (0x0b0, 0x0c2, 0x0d2, 0x0a9),   # 3: Power Wristband, Cat's Bell, Sparkling Bracer, Sasuke's Blade
        (0x0b5, 0x0a4, 0x0d6, 0x15a),   # 4: Giant's Glove, Flametongue, Wonder Bangle, Ancient Potion
        (0x0bc, 0x0c9, 0x0d6, 0x129),   # 5: Rune Bell, Gold Hairpin, Wonder Bangle, Orichalcum
        (0x0b0, 0x0c1, 0x0dc, 0x197),   # 6: Power Wristband, Silver Bracer, Chocobo Pocket, Legendary Weapon
        (0x0b1, 0x0c2, 0x1da, 0x14b),   # 7: Green Beret, Cat's Bell, Brigandology, Dweomer Spore
    )),
    'Moschet Manor': ((0, 113, 141, 177), (
        (0x0a4, 0x0b8, 0x0d0, 0x0dc),   # 0: Flametongue, Rune Staff, Buckler, Chocobo Pocket
        (0x0b1, 0x0c7, 0x0d1, 0x0e4),   # 1: Green Beret, Red Slippers, Silver Spectacles, Earth Pendant
        (0x0b2, 0x0b9, 0x0d3, 0x0e5),   # 2: Fang Charm, Book of Light, Black Hood, Moon Pendant
        (0x0a3, 0x0c3, 0x0d4, 0x0dc),   # 3: Kaiser Knuckles, Faerie Ring, Helm of Arai, Chocobo Pocket
        (0x0a5, 0x0ba, 0x0dc, 0x0e5),   # 4: Ice Brand, Sage's Staff, Chocobo Pocket, Moon Pendant
        (0x0ab, 0x0bd, 0x0d6, 0x129),   # 5: Masquerade, Mage's Staff, Wonder Bangle, Orichalcum
        (0x0b0, 0x0dc, 0x197, 0x14c),   # 6: Power Wristband, Chocobo Pocket, Legendary Weapon, Lord's Robe
        (0x0ae, 0x0c5, 0x0dc, 0x1b2),   # 7: Gekkabijin, Candy Ring, Chocobo Pocket, Legendary Shield
    )),
    'Mount Kilanda': ((0, 137, 171, 214), (
        (0x0a8, 0x0b9, 0x0cf, 0x0e5),   # 0: Engetsurin, Book of Light, Drill, Moon Pendant
        (0x0b0, 0x0c6, 0x0cf, 0x0e6),   # 1: Power Wristband, Kris, Drill, Star Pendant
        (0x0b1, 0x0c1, 0x0cc, 0x0df),   # 2: Green Beret, Silver Bracer, Main Gauche, Ring of Fire
        (0x0b2, 0x0c2, 0x0cf, 0x0df),   # 3: Fang Charm, Cat's Bell, Drill, Ring of Fire
        (0x0aa, 0x0c7, 0x0cd, 0x0e6),   # 4: Mjollnir, Red Slippers, Chicken Knife, Star Pendant
        (0x0a4, 0x0bd, 0x0df, 0x129),   # 5: Flametongue, Mage's Staff, Ring of Fire, Orichalcum
        (0x0b3, 0x0bb, 0x197, 0x14a),   # 6: Twisted Headband, Wonder Wand, Legendary Weapon, Red Eye
        (0x0ad, 0x0bc, 0x0cc, 0x199),   # 7: Masamune, Rune Bell, Main Gauche, Celestial Weapon
    )),
    "Daemon's Court": ((0, 138, 172, 216), (
        (0x0a6, 0x0c4, 0x0d0, 0x0dc),   # 0: Loaded Dice, Winged Cap, Buckler, Chocobo Pocket
        (0x09f, 0x0bb, 0x0d1, 0x0e5),   # 1: Shuriken, Wonder Wand, Silver Spectacles, Moon Pendant
        (0x0a0, 0x0c5, 0x0d9, 0x0dc),   # 2: Maneater, Candy Ring, Rat's Tail, Chocobo Pocket
        (0x0a1, 0x0b6, 0x0d2, 0x0e5),   # 3: Double Axe, Dragon's Whisker, Sparkling Bracer, Moon Pendant
        (0x0b5, 0x0bc, 0x0d6, 0x0e5),   # 4: Giant's Glove, Rune Bell, Wonder Bangle, Moon Pendant
        (0x0a7, 0x0c8, 0x0dc, 0x129),   # 5: Ogrekiller, Dark Matter, Chocobo Pocket, Orichalcum
        (0x0a4, 0x0c6, 0x1ba, 0x143),   # 6: Flametongue, Kris, Diamond Gloves, King's Scale
        (0x0a5, 0x0c7, 0x0d8, 0x1b0),   # 7: Ice Brand, Red Slippers, Aegis, Diamond Shield
    )),
    'Selepation Cave': ((0, 212, 265, 332), (
        (0x0a7, 0x0b6, 0x0d0, 0x0dc),   # 0: Ogrekiller, Dragon's Whisker, Buckler, Chocobo Pocket
        (0x0a2, 0x0bc, 0x0d1, 0x0e1),   # 1: Ashura, Rune Bell, Silver Spectacles, Ring of Thunder
        (0x0a3, 0x0b7, 0x0d2, 0x0e5),   # 2: Kaiser Knuckles, Mage Masher, Sparkling Bracer, Moon Pendant
        (0x0b0, 0x0b8, 0x0da, 0x0e1),   # 3: Power Wristband, Rune Staff, Teddy Bear, Ring of Thunder
        (0x0a9, 0x0c6, 0x0d3, 0x1a8),   # 4: Sasuke's Blade, Kris, Black Hood, Diamond Armor
        (0x0b3, 0x0c9, 0x0e5, 0x129),   # 5: Twisted Headband, Gold Hairpin, Moon Pendant, Orichalcum
        (0x0a6, 0x0ba, 0x0e1, 0x148),   # 6: Loaded Dice, Sage's Staff, Ring of Thunder, Wind Crystal
        (0x0a7, 0x0bb, 0x1a9, 0x0d7),   # 7: Ogrekiller, Wonder Wand, Earth Armor, Ring of Protection
    )),
    'Veo Lu Sluice': ((0, 123, 154, 193), (
        (0x0a5, 0x0c1, 0x0d0, 0x0e0),   # 0: Ice Brand, Silver Bracer, Buckler, Ring of Blizzard
        (0x0b1, 0x0ba, 0x0d1, 0x0e5),   # 1: Green Beret, Sage's Staff, Silver Spectacles, Moon Pendant
        (0x0b2, 0x0c2, 0x0d5, 0x0e5),   # 2: Fang Charm, Cat's Bell, Elven Mantle, Moon Pendant
        (0x09f, 0x0c3, 0x0d2, 0x0e0),   # 3: Shuriken, Faerie Ring, Sparkling Bracer, Ring of Blizzard
        (0x0b4, 0x0bb, 0x0d9, 0x0e5),   # 4: Heavy Armband, Wonder Wand, Rat's Tail, Moon Pendant
        (0x0a6, 0x0be, 0x0e0, 0x129),   # 5: Loaded Dice, Noah's Lute, Ring of Blizzard, Orichalcum
        (0x0b1, 0x0c4, 0x1c3, 0x144),   # 6: Green Beret, Winged Cap, Diamond Sallet, Green Sphere
        (0x0b2, 0x0c5, 0x0ca, 0x1a8),   # 7: Fang Charm, Candy Ring, Taotie Motif, Diamond Armor
    )),
    'Lynari Desert': ((0, 194, 243, 304), (
        (0x0ab, 0x0ba, 0x0cc, 0x0e6),   # 0: Masquerade, Sage's Staff, Main Gauche, Star Pendant
        (0x0a4, 0x0be, 0x0d3, 0x0dd),   # 1: Flametongue, Noah's Lute, Black Hood, Gobbie Pocket
        (0x0a5, 0x0bb, 0x0cd, 0x0dd),   # 2: Ice Brand, Wonder Wand, Chicken Knife, Gobbie Pocket
        (0x0b4, 0x0bc, 0x0d4, 0x0e6),   # 3: Heavy Armband, Rune Bell, Helm of Arai, Star Pendant
        (0x0a6, 0x0c8, 0x0d5, 0x198),   # 4: Loaded Dice, Dark Matter, Elven Mantle, Hero's Weapon
        (0x0a7, 0x0c6, 0x0d6, 0x129),   # 5: Ogrekiller, Kris, Wonder Bangle, Orichalcum
        (0x0a8, 0x0c7, 0x0dd, 0x147),   # 6: Engetsurin, Red Slippers, Gobbie Pocket, Desert Fang
        (0x0b3, 0x0c0, 0x1a8, 0x0e7),   # 7: Twisted Headband, Tome of Ultima, Diamond Armor, Sun Pendant
    )),
    'Conall Curach': ((0, 260, 324, 406), (
        (0x0b5, 0x0ba, 0x0d9, 0x0dd),   # 0: Giant's Glove, Sage's Staff, Rat's Tail, Gobbie Pocket
        (0x0a4, 0x0c9, 0x0da, 0x0e2),   # 1: Flametongue, Gold Hairpin, Teddy Bear, Ring of Cure
        (0x0a5, 0x0bb, 0x0d6, 0x0e6),   # 2: Ice Brand, Wonder Wand, Wonder Bangle, Star Pendant
        (0x0a6, 0x0bc, 0x0d9, 0x0e2),   # 3: Loaded Dice, Rune Bell, Rat's Tail, Ring of Cure
        (0x0a7, 0x0c9, 0x0da, 0x0e6),   # 4: Ogrekiller, Gold Hairpin, Teddy Bear, Star Pendant
        (0x0a9, 0x0c6, 0x0e2, 0x129),   # 5: Sasuke's Blade, Kris, Ring of Cure, Orichalcum
        (0x0b3, 0x0c7, 0x145, 0x19b),   # 6: Twisted Headband, Red Slippers, Dragon's Fang, Lunar Weapon
        (0x0a8, 0x0c0, 0x1a8, 0x0e3),   # 7: Engetsurin, Tome of Ultima, Diamond Armor, Ring of Life
    )),
    'Rebena Te Ra': ((0, 200, 250, 312), (
        (0x0aa, 0x0ba, 0x0cc, 0x0e6),   # 0: Mjollnir, Sage's Staff, Main Gauche, Star Pendant
        (0x0a4, 0x0bd, 0x0d3, 0x0dd),   # 1: Flametongue, Mage's Staff, Black Hood, Gobbie Pocket
        (0x0a5, 0x0bb, 0x0cd, 0x0e6),   # 2: Ice Brand, Wonder Wand, Chicken Knife, Star Pendant
        (0x0a6, 0x0bc, 0x0d4, 0x0dd),   # 3: Loaded Dice, Rune Bell, Helm of Arai, Gobbie Pocket
        (0x0ab, 0x0c6, 0x0d5, 0x0e6),   # 4: Masquerade, Kris, Elven Mantle, Star Pendant
        (0x0a7, 0x0be, 0x0dd, 0x129),   # 5: Ogrekiller, Noah's Lute, Gobbie Pocket, Orichalcum
        (0x0a8, 0x0c7, 0x19a, 0x149),   # 6: Engetsurin, Red Slippers, Dark Weapon, Ethereal Orb
        (0x0b3, 0x0cb, 0x0cf, 0x1eb),   # 7: Twisted Headband, Ribbon, Drill, Forbidden Tome
    )),
}

BONUS_CANDIDATES = (
    0x09f, 0x0a0, 0x0a1, 0x0a2, 0x0a3, 0x0a4, 0x0a5, 0x0a6, 0x0a7, 0x0a8,
    0x0a9, 0x0aa, 0x0ab, 0x0ac, 0x0ad, 0x0ae, 0x0af, 0x0b0, 0x0b1, 0x0b2,
    0x0b3, 0x0b4, 0x0b5, 0x0b6, 0x0b7, 0x0b8, 0x0b9, 0x0ba, 0x0bb, 0x0bc,
    0x0bd, 0x0be, 0x0bf, 0x0c0, 0x0c1, 0x0c2, 0x0c3, 0x0c4, 0x0c5, 0x0c6,
    0x0c7, 0x0c8, 0x0c9, 0x0ca, 0x0cb, 0x0cc, 0x0cd, 0x0ce, 0x0cf, 0x0d0,
    0x0d1, 0x0d2, 0x0d3, 0x0d4, 0x0d5, 0x0d6, 0x0d7, 0x0d8, 0x0d9, 0x0da,
    0x0db, 0x0dc, 0x0dd, 0x0de, 0x0df, 0x0e0, 0x0e1, 0x0e2, 0x0e3, 0x0e4,
    0x0e5, 0x0e6, 0x0e7, 0x100, 0x101, 0x102, 0x105, 0x106, 0x107, 0x125,
    0x126, 0x127, 0x128, 0x129, 0x12a, 0x12b, 0x12c, 0x12d, 0x12e, 0x12f,
    0x130, 0x131, 0x132, 0x133, 0x134, 0x135, 0x136, 0x137, 0x138, 0x139,
    0x13a, 0x13b, 0x13c, 0x13d, 0x13e, 0x13f, 0x140, 0x141, 0x142, 0x143,
    0x144, 0x145, 0x146, 0x147, 0x148, 0x149, 0x14a, 0x14b, 0x14c, 0x14d,
    0x14e, 0x14f, 0x150, 0x151, 0x152, 0x153, 0x154, 0x155, 0x157, 0x158,
    0x159, 0x15a, 0x15b, 0x15c, 0x15d, 0x15e, 0x15f, 0x163, 0x164, 0x165,
    0x166, 0x167, 0x168, 0x169, 0x16a, 0x16b, 0x16c, 0x16d, 0x16e, 0x16f,
    0x171, 0x172, 0x17d, 0x17e, 0x17f, 0x180, 0x181, 0x182, 0x183, 0x184,
    0x185, 0x186, 0x187, 0x188, 0x191, 0x192, 0x193, 0x194, 0x195, 0x196,
    0x197, 0x198, 0x199, 0x19a, 0x19b, 0x19c, 0x19d, 0x19e, 0x19f, 0x1a0,
    0x1a1, 0x1a2, 0x1a3, 0x1a4, 0x1a5, 0x1a6, 0x1a7, 0x1a8, 0x1a9, 0x1aa,
    0x1ab, 0x1ac, 0x1ad, 0x1ae, 0x1af, 0x1b0, 0x1b1, 0x1b2, 0x1b3, 0x1b4,
    0x1b5, 0x1b6, 0x1b7, 0x1b8, 0x1b9, 0x1ba, 0x1bb, 0x1bc, 0x1bd, 0x1be,
    0x1bf, 0x1c0, 0x1c1, 0x1c2, 0x1c3, 0x1c4, 0x1c5, 0x1c6, 0x1c7, 0x1c8,
    0x1c9, 0x1ca, 0x1cb, 0x1cc, 0x1cd, 0x1ce, 0x1cf, 0x1d0, 0x1d1, 0x1d2,
    0x1d3, 0x1d4, 0x1d5, 0x1d6, 0x1d7, 0x1d8, 0x1d9, 0x1da, 0x1db, 0x1dc,
    0x1dd, 0x1de, 0x1df, 0x1e0, 0x1e1, 0x1e2, 0x1e3, 0x1e4, 0x1e5, 0x1e6,
    0x1e7, 0x1e8, 0x1e9, 0x1ea, 0x1eb, 0x1ec, 0x1ed,
)

ITEM_NAMES = {
    0x09f: 'Shuriken',
    0x0a0: 'Maneater',
    0x0a1: 'Double Axe',
    0x0a2: 'Ashura',
    0x0a3: 'Kaiser Knuckles',
    0x0a4: 'Flametongue',
    0x0a5: 'Ice Brand',
    0x0a6: 'Loaded Dice',
    0x0a7: 'Ogrekiller',
    0x0a8: 'Engetsurin',
    0x0a9: "Sasuke's Blade",
    0x0aa: 'Mjollnir',
    0x0ab: 'Masquerade',
    0x0ac: 'Murasame',
    0x0ad: 'Masamune',
    0x0ae: 'Gekkabijin',
    0x0af: 'Onion Sword',
    0x0b0: 'Power Wristband',
    0x0b1: 'Green Beret',
    0x0b2: 'Fang Charm',
    0x0b3: 'Twisted Headband',
    0x0b4: 'Heavy Armband',
    0x0b5: "Giant's Glove",
    0x0b6: "Dragon's Whisker",
    0x0b7: 'Mage Masher',
    0x0b8: 'Rune Staff',
    0x0b9: 'Book of Light',
    0x0ba: "Sage's Staff",
    0x0bb: 'Wonder Wand',
    0x0bc: 'Rune Bell',
    0x0bd: "Mage's Staff",
    0x0be: "Noah's Lute",
    0x0bf: 'Galatyn',
    0x0c0: 'Tome of Ultima',
    0x0c1: 'Silver Bracer',
    0x0c2: "Cat's Bell",
    0x0c3: 'Faerie Ring',
    0x0c4: 'Winged Cap',
    0x0c5: 'Candy Ring',
    0x0c6: 'Kris',
    0x0c7: 'Red Slippers',
    0x0c8: 'Dark Matter',
    0x0c9: 'Gold Hairpin',
    0x0ca: 'Taotie Motif',
    0x0cb: 'Ribbon',
    0x0cc: 'Main Gauche',
    0x0cd: 'Chicken Knife',
    0x0ce: 'Save the Queen',
    0x0cf: 'Drill',
    0x0d0: 'Buckler',
    0x0d1: 'Silver Spectacles',
    0x0d2: 'Sparkling Bracer',
    0x0d3: 'Black Hood',
    0x0d4: 'Helm of Arai',
    0x0d5: 'Elven Mantle',
    0x0d6: 'Wonder Bangle',
    0x0d7: 'Ring of Protection',
    0x0d8: 'Aegis',
    0x0d9: "Rat's Tail",
    0x0da: 'Teddy Bear',
    0x0db: 'Moogle Pocket',
    0x0dc: 'Chocobo Pocket',
    0x0dd: 'Gobbie Pocket',
    0x0de: 'Ultimate Pocket',
    0x0df: 'Ring of Fire',
    0x0e0: 'Ring of Blizzard',
    0x0e1: 'Ring of Thunder',
    0x0e2: 'Ring of Cure',
    0x0e3: 'Ring of Life',
    0x0e4: 'Earth Pendant',
    0x0e5: 'Moon Pendant',
    0x0e6: 'Star Pendant',
    0x0e7: 'Sun Pendant',
    0x100: 'Stone of Fire',
    0x101: 'Stone of Blizzard',
    0x102: 'Stone of Thunder',
    0x105: 'Stone of Cure',
    0x106: 'Stone of Clear',
    0x107: 'Stone of Life',
    0x125: 'Phoenix Down',
    0x126: 'Bronze',
    0x127: 'Iron',
    0x128: 'Mythril',
    0x129: 'Orichalcum',
    0x12a: 'Diamond Ore',
    0x12b: 'Gold',
    0x12c: 'Silver',
    0x12d: 'Bronze Shard',
    0x12e: 'Iron Shard',
    0x12f: 'Tiny Crystal',
    0x130: 'Crystal Ball',
    0x131: 'Ruby',
    0x132: 'Jade',
    0x133: 'Alloy',
    0x134: 'Magma Rock',
    0x135: 'Chilly Gel',
    0x136: 'Thunderball',
    0x137: 'Holy Water',
    0x138: 'Heavenly Dust',
    0x139: 'Yellow Feather',
    0x13a: 'Blue Silk',
    0x13b: 'White Silk',
    0x13c: "Fiend's Claw",
    0x13d: "Devil's Claw",
    0x13e: "Faerie's Tear",
    0x13f: "Angel's Tear",
    0x140: 'Ancient Sword',
    0x141: 'Cursed Crook',
    0x142: 'Orc Belt',
    0x143: "King's Scale",
    0x144: 'Green Sphere',
    0x145: "Dragon's Fang",
    0x146: 'Malboro Seed',
    0x147: 'Desert Fang',
    0x148: 'Wind Crystal',
    0x149: 'Ethereal Orb',
    0x14a: 'Red Eye',
    0x14b: 'Dweomer Spore',
    0x14c: "Lord's Robe",
    0x14d: "Griffin's Wing",
    0x14e: 'Cerberus Fang',
    0x14f: 'Needle',
    0x150: 'Hard Shell',
    0x151: 'Worm Antenna',
    0x152: 'Toad Oil',
    0x153: 'Jagged Scythe',
    0x154: 'Ogre Fang',
    0x155: "Chimera's Horn",
    0x157: 'Coeurl Whisker',
    0x158: "Zu's Beak",
    0x159: 'Cockatrice Scale',
    0x15a: 'Ancient Potion',
    0x15b: 'Shiny Shard',
    0x15c: 'Gigas Claw',
    0x15d: 'Gear',
    0x15e: 'Pressed Flower',
    0x15f: 'Remedy',
    0x163: 'Flower Seed',
    0x164: 'Strange Seed',
    0x165: 'Fruit Seed',
    0x166: 'Fruit Seed',
    0x167: 'Fruit Seed',
    0x168: 'Vegetable Seed',
    0x169: 'Vegetable Seed',
    0x16a: 'Vegetable Seed',
    0x16b: 'Wheat Seed',
    0x16c: 'Worn Bandanna',
    0x16d: 'Shella Mark',
    0x16e: 'Kilanda Sulfur',
    0x16f: 'Cactus Flower',
    0x171: 'Ultimite',
    0x172: 'Dark Sphere',
    0x17d: 'Striped Apple',
    0x17e: 'Cherry Cluster',
    0x17f: 'Rainbow Grapes',
    0x180: 'Star Carrot',
    0x181: 'Gourd Potato',
    0x182: 'Round Corn',
    0x183: 'Meat',
    0x184: 'Fish',
    0x185: 'Bannock',
    0x186: 'Spring Water',
    0x187: 'Milk',
    0x188: 'Strange Liquid',
    0x191: "Novice's Weapon",
    0x192: "Warrior's Weapon",
    0x193: 'Valiant Weapon',
    0x194: 'Mighty Weapon',
    0x195: 'Victorious Weapon',
    0x196: "Master's Weapon",
    0x197: 'Legendary Weapon',
    0x198: "Hero's Weapon",
    0x199: 'Celestial Weapon',
    0x19a: 'Dark Weapon',
    0x19b: 'Lunar Weapon',
    0x19c: 'Bronze Armor',
    0x19d: 'Iron Armor',
    0x19e: 'Mythril Armor',
    0x19f: 'Flame Armor',
    0x1a0: 'Frost Armor',
    0x1a1: 'Lightning Armor',
    0x1a2: 'Time Armor',
    0x1a3: 'Eternal Armor',
    0x1a4: 'Pure Armor',
    0x1a5: 'Holy Armor',
    0x1a6: 'Gold Armor',
    0x1a7: 'Radiant Armor',
    0x1a8: 'Diamond Armor',
    0x1a9: 'Earth Armor',
    0x1aa: 'Iron Shield',
    0x1ab: 'Mythril Shield',
    0x1ac: 'Flame Shield',
    0x1ad: 'Frost Shield',
    0x1ae: 'Lightning Shield',
    0x1af: 'Holy Shield',
    0x1b0: 'Diamond Shield',
    0x1b1: 'Magic Shield',
    0x1b2: 'Legendary Shield',
    0x1b3: 'Bronze Gloves',
    0x1b4: 'Iron Gloves',
    0x1b5: 'Mythril Gloves',
    0x1b6: 'Flame Gloves',
    0x1b7: 'Frost Gloves',
    0x1b8: 'Lightning Gloves',
    0x1b9: 'Gold Gloves',
    0x1ba: 'Diamond Gloves',
    0x1bb: 'Bronze Sallet',
    0x1bc: 'Iron Sallet',
    0x1bd: 'Mythril Sallet',
    0x1be: 'Flame Sallet',
    0x1bf: 'Frost Sallet',
    0x1c0: 'Lightning Sallet',
    0x1c1: 'Time Sallet',
    0x1c2: 'Eternal Sallet',
    0x1c3: 'Diamond Sallet',
    0x1c4: 'Bronze Belt',
    0x1c5: 'Iron Belt',
    0x1c6: 'Mythril Belt',
    0x1c7: 'Flame Belt',
    0x1c8: 'Frost Belt',
    0x1c9: 'Lightning Belt',
    0x1ca: 'Pure Belt',
    0x1cb: 'Wind Belt',
    0x1cc: 'Diamond Belt',
    0x1cd: 'Flame Craft',
    0x1ce: 'Frost Craft',
    0x1cf: 'Lightning Craft',
    0x1d0: 'Clockwork',
    0x1d1: 'New Clockwork',
    0x1d2: 'Blue Yarn',
    0x1d3: 'White Yarn',
    0x1d4: 'Gold Craft',
    0x1d5: 'Wisdom Tome',
    0x1d6: 'Wisdom Secrets',
    0x1d7: "Lady's Accessories",
    0x1d8: 'Speed Tome',
    0x1d9: 'Speed Secrets',
    0x1da: 'Brigandology',
    0x1db: 'Zeal Kit',
    0x1dc: 'Fiend Kit',
    0x1dd: 'Daemon Kit',
    0x1de: 'Faerie Kit',
    0x1df: 'Angel Kit',
    0x1e0: 'Ring of Light',
    0x1e1: 'Eyewear Techniques',
    0x1e2: 'Designer Glasses',
    0x1e3: 'Healing Kit',
    0x1e4: 'Fashion Kit',
    0x1e5: 'Goggle Techniques',
    0x1e6: 'Designer Goggles',
    0x1e7: 'Soul of the Lion',
    0x1e8: 'Soul of the Dragon',
    0x1e9: 'Magic Tome',
    0x1ea: 'Sorcery Tome',
    0x1eb: 'Forbidden Tome',
    0x1ec: 'Greatest Weapon',
    0x1ed: 'Ring of Invincibility',
}
