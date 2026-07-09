from BaseClasses import Item, ItemClassification
from typing import NamedTuple, Optional
from .game_id import game_name

IC = ItemClassification


class FFCCItemData(NamedTuple):
    type:           str
    classification: IC
    code:           int            # AP item code (= in-game hex ID; traps/progressive use 0x200+)
    item_id:        Optional[int]  # in-game hex ID (None for meta-items like traps/progressive)
    object_name:    str = "ap_item"
    qty:            int = 1
    special:        bool = False


class FFCCItem(Item):
    game: str = game_name
    type: Optional[str]

    def __init__(self, name: str, player: int, data: FFCCItemData,
                 classification: Optional[IC] = None) -> None:
        super().__init__(
            name,
            data.classification if classification is None else classification,
            None if data.code is None else FFCCItem.get_apid(data.code),
            player,
        )
        self.type        = data.type
        self.item_id     = data.item_id
        self.object_name = data.object_name

    @staticmethod
    def get_apid(code: int) -> int:
        return 2322432 + code


# ── Artifacts (in-game IDs 0x9f–0xe7) ─────────────────────────────────────────
_ARTIFACTS = [
    ("Shuriken", 0x9f), ("Maneater", 0xa0), ("Double Axe", 0xa1), ("Ashura", 0xa2),
    ("Kaiser Knuckles", 0xa3), ("Flametongue", 0xa4), ("Ice Brand", 0xa5),
    ("Loaded Dice", 0xa6), ("Ogrekiller", 0xa7), ("Engetsurin", 0xa8),
    ("Sasuke's Blade", 0xa9), ("Mjollnir", 0xaa), ("Masquerade", 0xab),
    ("Murasame", 0xac), ("Masamune", 0xad), ("Gekkabijin", 0xae),
    ("Onion Sword", 0xaf), ("Power Wristband", 0xb0), ("Green Beret", 0xb1),
    ("Fang Charm", 0xb2), ("Twisted Headband", 0xb3), ("Heavy Armband", 0xb4),
    ("Giant's Glove", 0xb5), ("Dragon's Whisker", 0xb6), ("Mage Masher", 0xb7),
    ("Rune Staff", 0xb8), ("Book of Light", 0xb9), ("Sage's Staff", 0xba),
    ("Wonder Wand", 0xbb), ("Rune Bell", 0xbc), ("Mage's Staff", 0xbd),
    ("Noah's Lute", 0xbe), ("Galatyn", 0xbf), ("Tome of Ultima", 0xc0),
    ("Silver Bracer", 0xc1), ("Cat's Bell", 0xc2), ("Faerie Ring", 0xc3),
    ("Winged Cap", 0xc4), ("Candy Ring", 0xc5), ("Kris", 0xc6),
    ("Red Slippers", 0xc7), ("Dark Matter", 0xc8), ("Gold Hairpin", 0xc9),
    ("Taotie Motif", 0xca), ("Ribbon", 0xcb), ("Main Gauche", 0xcc),
    ("Chicken Knife", 0xcd), ("Save the Queen", 0xce), ("Drill", 0xcf),
    ("Buckler", 0xd0), ("Silver Spectacles", 0xd1), ("Sparkling Bracer", 0xd2),
    ("Black Hood", 0xd3), ("Helm of Arai", 0xd4), ("Elven Mantle", 0xd5),
    ("Wonder Bangle", 0xd6), ("Ring of Protection", 0xd7), ("Aegis", 0xd8),
    ("Rat's Tail", 0xd9), ("Teddy Bear", 0xda), ("Moogle Pocket", 0xdb),
    ("Chocobo Pocket", 0xdc), ("Gobbie Pocket", 0xdd), ("Ultimate Pocket", 0xde),
    ("Ring of Cure", 0xe2), ("Earth Pendant", 0xe4),
    ("Moon Pendant", 0xe5), ("Star Pendant", 0xe6), ("Sun Pendant", 0xe7),
]

# ── Spell Rings (permanent magic slots — always in pool, gate dungeon rules) ───
# Separated from _ARTIFACTS so they're never replaced by Progressive Artifacts.
_SPELL_RINGS = [
    ("Ring of Fire",     0xdf),  # gates Tida (ivy) and Rebena Te Ra (fire switch)
    ("Ring of Blizzard", 0xe0),  # gates Rebena Te Ra (blizzard switch)
    ("Ring of Thunder",  0xe1),  # gates Rebena Te Ra (thunder switch)
    ("Ring of Life",     0xe3),  # gates Lynari Desert / Mount Vellenge (Holy = Life + element)
]

# ── Valid Magicite (spells that appear in dungeon chests) ──────────────────────
_MAGICITE = [
    ("Stone of Fire",     0x100),
    ("Stone of Blizzard", 0x101),
    ("Stone of Thunder",  0x102),
    ("Stone of Cure",     0x105),
    ("Stone of Clear",    0x106),
    ("Stone of Life",     0x107),
]

# ── Phoenix Down ───────────────────────────────────────────────────────────────
_PHOENIX_DOWN = [("Phoenix Down", 0x125)]

# ── Crafting Materials (0x126–0x161) ──────────────────────────────────────────
_MATERIALS = [
    ("Bronze", 0x126), ("Iron", 0x127), ("Mythril", 0x128), ("Orichalcum", 0x129),
    ("Diamond Ore", 0x12a), ("Gold", 0x12b), ("Silver", 0x12c),
    ("Bronze Shard", 0x12d), ("Iron Shard", 0x12e), ("Tiny Crystal", 0x12f),
    ("Crystal Ball", 0x130), ("Ruby", 0x131), ("Jade", 0x132), ("Alloy", 0x133),
    ("Magma Rock", 0x134), ("Chilly Gel", 0x135), ("Thunderball", 0x136),
    ("Holy Water", 0x137), ("Heavenly Dust", 0x138), ("Yellow Feather", 0x139),
    ("Blue Silk", 0x13a), ("White Silk", 0x13b), ("Fiend's Claw", 0x13c),
    ("Devil's Claw", 0x13d), ("Faerie's Tear", 0x13e), ("Angel's Tear", 0x13f),
    ("Ancient Sword", 0x140), ("Cursed Crook", 0x141), ("Orc Belt", 0x142),
    ("King's Scale", 0x143), ("Green Sphere", 0x144), ("Dragon's Fang", 0x145),
    ("Malboro Seed", 0x146), ("Desert Fang", 0x147), ("Wind Crystal", 0x148),
    ("Ethereal Orb", 0x149), ("Red Eye", 0x14a), ("Dweomer Spore", 0x14b),
    ("Lord's Robe", 0x14c), ("Griffin's Wing", 0x14d), ("Cerberus Fang", 0x14e),
    ("Needle", 0x14f), ("Hard Shell", 0x150), ("Worm Antenna", 0x151),
    ("Toad Oil", 0x152), ("Jagged Scythe", 0x153), ("Ogre Fang", 0x154),
    ("Chimera's Horn", 0x155), ("Crop Seed", 0x156), ("Coeurl Whisker", 0x157),
    ("Zu's Beak", 0x158), ("Cockatrice Scale", 0x159), ("Ancient Potion", 0x15a),
    ("Shiny Shard", 0x15b), ("Gigas Claw", 0x15c), ("Gear", 0x15d),
    ("Pressed Flower", 0x15e), ("Remedy", 0x15f), ("Goddess Statuette", 0x160),
    ("Devil's Mask", 0x161),
]

# ── Food (0x17d–0x18e) ─────────────────────────────────────────────────────────
_FOOD = [
    ("Striped Apple", 0x17d), ("Cherry Cluster", 0x17e), ("Rainbow Grapes", 0x17f),
    ("Star Carrot", 0x180), ("Gourd Potato", 0x181), ("Round Corn", 0x182),
    ("Meat", 0x183), ("Fish", 0x184), ("Bannock", 0x185), ("Spring Water", 0x186),
    ("Milk", 0x187), ("Strange Liquid", 0x188), ("Wheat", 0x18d), ("Flour", 0x18e),
]

# ── Recipes / Scrolls (0x191–0x1ed) ───────────────────────────────────────────
_RECIPES = [
    ("Novice's Weapon", 0x191), ("Warrior's Weapon", 0x192), ("Valiant Weapon", 0x193),
    ("Mighty Weapon", 0x194), ("Victorious Weapon", 0x195), ("Master's Weapon", 0x196),
    ("Legendary Weapon", 0x197), ("Hero's Weapon", 0x198), ("Celestial Weapon", 0x199),
    ("Dark Weapon", 0x19a), ("Lunar Weapon", 0x19b),
    ("Bronze Armor", 0x19c), ("Iron Armor", 0x19d), ("Mythril Armor", 0x19e),
    ("Flame Armor", 0x19f), ("Frost Armor", 0x1a0), ("Lightning Armor", 0x1a1),
    ("Time Armor", 0x1a2), ("Eternal Armor", 0x1a3), ("Pure Armor", 0x1a4),
    ("Holy Armor", 0x1a5), ("Gold Armor", 0x1a6), ("Radiant Armor", 0x1a7),
    ("Diamond Armor", 0x1a8), ("Earth Armor", 0x1a9),
    ("Iron Shield", 0x1aa), ("Mythril Shield", 0x1ab), ("Flame Shield", 0x1ac),
    ("Frost Shield", 0x1ad), ("Lightning Shield", 0x1ae), ("Holy Shield", 0x1af),
    ("Diamond Shield", 0x1b0), ("Magic Shield", 0x1b1), ("Legendary Shield", 0x1b2),
    ("Bronze Gloves", 0x1b3), ("Iron Gloves", 0x1b4), ("Mythril Gloves", 0x1b5),
    ("Flame Gloves", 0x1b6), ("Frost Gloves", 0x1b7), ("Lightning Gloves", 0x1b8),
    ("Gold Gloves", 0x1b9), ("Diamond Gloves", 0x1ba),
    ("Bronze Sallet", 0x1bb), ("Iron Sallet", 0x1bc), ("Mythril Sallet", 0x1bd),
    ("Flame Sallet", 0x1be), ("Frost Sallet", 0x1bf), ("Lightning Sallet", 0x1c0),
    ("Time Sallet", 0x1c1), ("Eternal Sallet", 0x1c2), ("Diamond Sallet", 0x1c3),
    ("Bronze Belt", 0x1c4), ("Iron Belt", 0x1c5), ("Mythril Belt", 0x1c6),
    ("Flame Belt", 0x1c7), ("Frost Belt", 0x1c8), ("Lightning Belt", 0x1c9),
    ("Pure Belt", 0x1ca), ("Wind Belt", 0x1cb), ("Diamond Belt", 0x1cc),
    ("Flame Craft", 0x1cd), ("Frost Craft", 0x1ce), ("Lightning Craft", 0x1cf),
    ("Clockwork", 0x1d0), ("New Clockwork", 0x1d1), ("Blue Yarn", 0x1d2),
    ("White Yarn", 0x1d3), ("Gold Craft", 0x1d4), ("Wisdom Tome", 0x1d5),
    ("Wisdom Secrets", 0x1d6), ("Lady's Accessories", 0x1d7), ("Speed Tome", 0x1d8),
    ("Speed Secrets", 0x1d9), ("Brigandology", 0x1da), ("Zeal Kit", 0x1db),
    ("Fiend Kit", 0x1dc), ("Daemon Kit", 0x1dd), ("Faerie Kit", 0x1de),
    ("Angel Kit", 0x1df), ("Ring of Light", 0x1e0), ("Eyewear Techniques", 0x1e1),
    ("Designer Glasses", 0x1e2), ("Healing Kit", 0x1e3), ("Fashion Kit", 0x1e4),
    ("Goggle Techniques", 0x1e5), ("Designer Goggles", 0x1e6),
    ("Soul of the Lion", 0x1e7), ("Soul of the Dragon", 0x1e8),
    ("Magic Tome", 0x1e9), ("Sorcery Tome", 0x1ea), ("Forbidden Tome", 0x1eb),
    ("Greatest Weapon", 0x1ec), ("Ring of Invincibility", 0x1ed),
]
# Recipes that are useful (needed for the best end-game crafting)
_USEFUL_RECIPE_IDS = {0x1e7, 0x1e8, 0x1ec, 0x1ed}

# ── Cycle advancement placeholder (used when cycle_location_checks option is off) ─
# Placed at cycle event locations so they don't consume the random item pool.
# item_id=None means the client receives it but writes nothing to game memory.
CYCLE_PLACEHOLDER_ITEM = "Cycle Advance"
_CYCLE_PLACEHOLDER_CODE = 0x208
YEAR_PLACEHOLDER_ITEM = "Year Advance"
_YEAR_PLACEHOLDER_CODE = 0x209

# ── Year progression keys (pre-placed at Year N Begins pseudo-locations) ─────
# IC.progression so AP treats them as sphere gates; item_id=None means no
# in-game write (the client silently acknowledges them).
YEAR_KEY_NAMES = ["Year 2 Key", "Year 3 Key", "Year 4 Key", "Year 5 Key"]
_YEAR_KEY_CODES = [0x20a, 0x20b, 0x20c, 0x20d]

# ── Trap items (no in-game ID — client handles them via memory writes) ─────────
# Codes are above all valid in-game item IDs.
_TRAPS = [
    ("Frozen Trap",          0x200),
    ("Burned Trap",          0x201),
    ("Slowed Trap",          0x202),
    ("Poisoned Trap",        0x203),
    ("Chalice Element Trap", 0x204),
    ("Bonus Set Trap",       0x205),
    ("Food Preference Trap", 0x206),
]

# ── Progressive Artifact ───────────────────────────────────────────────────────
PROGRESSIVE_ARTIFACT_CODE = 0x207
PROGRESSIVE_ARTIFACT_NAME = "Progressive Artifact"

# Ordered list of all artifact IDs for progressive giving (index 0 = first given)
PROGRESSIVE_ARTIFACT_ORDER = [iid for _, iid in _ARTIFACTS]


# Items excluded from in-game chest drops (banned by randomizer.py EXCLUDE set).
# These items CAN exist in inventory but cannot be physically placed in chests;
# the hybrid patcher will write AP Item for them, and the client delivers via memory write.
_NON_PHYSICAL_IDS = {0x156, 0x160, 0x161, 0x18d, 0x18e}


# ── Build the master item table ────────────────────────────────────────────────
def _build_item_table() -> dict:
    table = {}
    for name, iid in _ARTIFACTS:
        table[name] = FFCCItemData("Artifact", IC.useful, iid, iid)
    for name, iid in _SPELL_RINGS:
        table[name] = FFCCItemData("Spell Ring", IC.progression, iid, iid)
    for name, iid in _MAGICITE:
        table[name] = FFCCItemData("Magicite", IC.useful, iid, iid)
    for name, iid in _PHOENIX_DOWN:
        table[name] = FFCCItemData("Phoenix Down", IC.filler, iid, iid)
    for name, iid in _MATERIALS:
        table[name] = FFCCItemData("Material", IC.filler, iid, None if iid in _NON_PHYSICAL_IDS else iid)
    for name, iid in _FOOD:
        table[name] = FFCCItemData("Food", IC.filler, iid, None if iid in _NON_PHYSICAL_IDS else iid)
    for name, iid in _RECIPES:
        cls = IC.useful if iid in _USEFUL_RECIPE_IDS else IC.filler
        table[name] = FFCCItemData("Recipe", cls, iid, iid)
    for name, code in _TRAPS:
        table[name] = FFCCItemData("Trap", IC.trap, code, None)
    table[PROGRESSIVE_ARTIFACT_NAME] = FFCCItemData(
        "Progressive Artifact", IC.useful, PROGRESSIVE_ARTIFACT_CODE, None
    )
    table[CYCLE_PLACEHOLDER_ITEM] = FFCCItemData(
        "Placeholder", IC.filler, _CYCLE_PLACEHOLDER_CODE, None
    )
    table[YEAR_PLACEHOLDER_ITEM] = FFCCItemData(
        "Placeholder", IC.filler, _YEAR_PLACEHOLDER_CODE, None
    )
    for name, code in zip(YEAR_KEY_NAMES, _YEAR_KEY_CODES):
        table[name] = FFCCItemData("Year Key", IC.progression, code, None)
    return table


ITEM_TABLE: dict[str, FFCCItemData] = _build_item_table()

# Filler item names (used for padding the item pool and get_filler_item_name)
# Excludes the Placeholder type so "Cycle Advance" never ends up in the random pool.
FILLER_ITEM_TABLE: dict[str, FFCCItemData] = {
    name: data for name, data in ITEM_TABLE.items()
    if data.classification == IC.filler and data.type != "Placeholder"
}

# Trap item names (used for weighted trap selection in create_items)
TRAP_ITEMS: list[str] = [name for name, _ in _TRAPS]

# AP ID → item name lookup (used by client when receiving items)
LOOKUP_ID_TO_NAME: dict[int, str] = {
    FFCCItem.get_apid(data.code): name
    for name, data in ITEM_TABLE.items()
    if data.code is not None
}

ITEM_TABLE_DESC: dict[str, str] = {}

item_name_groups: dict[str, set] = {
    "Artifacts":   {n for n, d in ITEM_TABLE.items() if d.type == "Artifact"},
    "Spell Rings": {n for n, d in ITEM_TABLE.items() if d.type == "Spell Ring"},
    "Magicite":    {n for n, d in ITEM_TABLE.items() if d.type == "Magicite"},
    "Materials":  {n for n, d in ITEM_TABLE.items() if d.type == "Material"},
    "Food":       {n for n, d in ITEM_TABLE.items() if d.type == "Food"},
    "Recipes":    {n for n, d in ITEM_TABLE.items() if d.type == "Recipe"},
    "Traps":      {n for n, d in ITEM_TABLE.items() if d.type == "Trap"},
}
