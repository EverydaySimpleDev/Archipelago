from BaseClasses import Item, ItemClassification
from typing import TYPE_CHECKING, NamedTuple, Optional, Dict, List
from BaseClasses import ItemClassification as IC
from collections.abc import Iterable
from worlds.AutoWorld import World

class FFCCItemData(NamedTuple):
    """
    This class represents the data for an item.

    :param type: The type of the item.
    :param classification: The item's classification (progression, useful, filler).
    :param code: The unique code identifier for the item.
    :param item_id: The ID used to represent the item in-game.
    """

    type: str
    classification: IC
    code: Optional[int]
    item_id: Optional[int]
    object_name: Optional[str]
    qty: Optional[int]
    special: Optional[bool] = False


class FFCCItem(Item):
    game: str = "Final Fantasy Crystal Chronicles"
    type: Optional[str]

    def __init__(self, name: str, player: int, data: FFCCItemData, classification: Optional[IC] = None) -> None:
        super().__init__(
            name,
            data.classification if classification is None else classification,
            None if data.code is None else FFCCItem.get_apid(data.code),
            player,
        )

        self.type = data.type
        self.item_id = data.item_id
        self.object_name = data.object_name
        self.maxDiff = None

    @staticmethod
    def get_apid(code: int) -> int:
        """
        Compute the Archipelago ID for the given item code.

        :param code: The unique code for the item.
        :return: The computed Archipelago ID.
        """
        base_id: int = 2322432
        return base_id + code

ITEM_TABLE: dict[str, FFCCItemData] = {
    "Copper Sword": FFCCItemData("Item", IC.useful, 0, 0x01, "ap_item", 1),
}

WEAPON_TABLE: dict[str, FFCCItemData] = {
    "Copper Sword": FFCCItemData("Item", IC.useful, 0, 0x01, "ap_item", 1),
    "Iron Sword": FFCCItemData("Item", IC.useful, 1, 0x02, "ap_item", 1),
    "Steel Blade": FFCCItemData("Item", IC.useful, 2, 0x03, "ap_item", 1),
    "Feather Saber": FFCCItemData("Item", IC.useful, 3, 0x04, "ap_item", 1),
    "Bastard Sword": FFCCItemData("Item", IC.useful, 4, 0x05, "ap_item", 1),
    "Defender": FFCCItemData("Item", IC.useful, 5, 0x06, "ap_item", 1),
    "Rune Blade": FFCCItemData("Item", IC.useful, 6, 0x07, "ap_item", 1),
    "Excalibur": FFCCItemData("Item", IC.useful, 7, 0x08, "ap_item", 1),
    "Ragnarok": FFCCItemData("Item", IC.useful, 8, 0x09, "ap_item", 1),
    "Treas. Sword": FFCCItemData("Item", IC.useful, 9, 0x0a, "ap_item", 1),
    "Fthr. Sword": FFCCItemData("Item", IC.useful, 10, 0x0b, "ap_item", 1),
    "Marr Sword": FFCCItemData("Item", IC.useful, 11, 0x0c, "ap_item", 1),
    "Ultima Sword": FFCCItemData("Item", IC.useful, 12, 0x0f, "ap_item", 1),

    "Iron Lance": FFCCItemData("Item", IC.useful, 12, 0x12, "ap_item", 1),
    "Partisan": FFCCItemData("Item", IC.useful, 13, 0x13, "ap_item", 1),
    "Sonic Lance": FFCCItemData("Item", IC.useful, 14, 0x14, "ap_item", 1),
    "Titan Lance": FFCCItemData("Item", IC.useful, 15, 0x15, "ap_item", 1),
    "Halberd": FFCCItemData("Item", IC.useful, 16, 0x16, "ap_item", 1),
    "Highwind": FFCCItemData("Item", IC.useful, 17, 0x17, "ap_item", 1),
    "Dragon Lance": FFCCItemData("Item", IC.useful, 18, 0x18, "ap_item", 1),
    "Dragoon Spear": FFCCItemData("Item", IC.useful, 19, 0x19, "ap_item", 1),
    "Gungnir": FFCCItemData("Item", IC.useful, 20, 0x1a, "ap_item", 1),
    "Longinus": FFCCItemData("Item", IC.useful, 21, 0x1b, "ap_item", 1),
    "Treas. Spear": FFCCItemData("Item", IC.useful, 22, 0x1c, "ap_item", 1),
    "Fthr. Spear": FFCCItemData("Item", IC.useful, 23, 0x1d, "ap_item", 1),
    "Marr Spear": FFCCItemData("Item", IC.useful, 24, 0x1e, "ap_item", 1),
    "Ultima Lance": FFCCItemData("Item", IC.useful, 25, 0x1f, "ap_item", 1),

    "Orc Hammer": FFCCItemData("Item", IC.useful, 26, 0x24, "ap_item", 1),
    "Wave Hammer": FFCCItemData("Item", IC.useful, 27, 0x25, "ap_item", 1),
    "Rune Hammer": FFCCItemData("Item", IC.useful, 28, 0x26, "ap_item", 1),
    "Goblin Hammer": FFCCItemData("Item", IC.useful, 29, 0x27, "ap_item", 1),
    "Sonic Hammer": FFCCItemData("Item", IC.useful, 30, 0x28, "ap_item", 1),
    "Prism Hammer": FFCCItemData("Item", IC.useful, 31, 0x29, "ap_item", 1),
    "Mythril Hammer": FFCCItemData("Item", IC.useful, 32, 0x2a, "ap_item", 1),
    "Mystic Hammer": FFCCItemData("Item", IC.useful, 33, 0x2b, "ap_item", 1),
    "Treas. Hammer": FFCCItemData("Item", IC.useful, 34, 0x2c, "ap_item", 1),
    "Fthr. Hammer": FFCCItemData("Item", IC.useful, 35, 0x2d, "ap_item", 1),
    "Marr Hammer": FFCCItemData("Item", IC.useful, 36, 0x2e, "ap_item", 1),
    "Ultima Hammer": FFCCItemData("Item", IC.useful, 37, 0x2f, "ap_item", 1),

    "Aura Racket": FFCCItemData("Item", IC.useful, 38, 0x34, "ap_item", 1),
    "Solid Racket": FFCCItemData("Item", IC.useful, 39, 0x35, "ap_item", 1),
    "Dual Shooter": FFCCItemData("Item", IC.useful, 40, 0x36, "ap_item", 1),
    "Elemnt. Cudgel": FFCCItemData("Item", IC.useful, 41, 0x37, "ap_item", 1),
    "Steel Cudgel": FFCCItemData("Item", IC.useful, 42, 0x38, "ap_item", 1),
    "Prism Bludgeon": FFCCItemData("Item", IC.useful, 43, 0x39, "ap_item", 1),
    "Butterfly Head": FFCCItemData("Item", IC.useful, 44, 0x3a, "ap_item", 1),
    "Queen's Heel": FFCCItemData("Item", IC.useful, 45, 0x3b, "ap_item", 1),
    "Drmcatcher": FFCCItemData("Item", IC.useful, 46, 0x3c, "ap_item", 1),
    "Treas. Maul": FFCCItemData("Item", IC.useful, 47, 0x3d, "ap_item", 1),
    "Fthr. Maul": FFCCItemData("Item", IC.useful, 48, 0x3e, "ap_item", 1),
    "Marr Maul": FFCCItemData("Item", IC.useful, 49, 0x3f, "ap_item", 1),
    "Ultima Maul": FFCCItemData("Item", IC.useful, 50, 0x40, "ap_item", 1),


}

ARMOR_TABLE: dict[str, FFCCItemData] = {
    "Travel Clothes": FFCCItemData("Item", IC.useful, 51, 0x45, "ap_item", 1),
    "Bronze Plate": FFCCItemData("Item", IC.useful, 52, 0x46, "ap_item", 1),
    "Iron Plate": FFCCItemData("Item", IC.useful, 53, 0x47, "ap_item", 1),
    "Mythril Haub.": FFCCItemData("Item", IC.useful, 54, 0x48, "ap_item", 1),
    "Flame Mail": FFCCItemData("Item", IC.useful, 55, 0x49, "ap_item", 1),
    "Frost Mail": FFCCItemData("Item", IC.useful, 56, 0x4a, "ap_item", 1),
    "Storm Mail": FFCCItemData("Item", IC.useful, 57, 0x4b, "ap_item", 1),
    "Time Mail": FFCCItemData("Item", IC.useful, 58, 0x4c, "ap_item", 1),
    "Eternal Mail": FFCCItemData("Item", IC.useful, 59, 0x4d, "ap_item", 1),
    "Blessed Mail": FFCCItemData("Item", IC.useful, 60, 0x4e, "ap_item", 1),
    "Saintly Mail": FFCCItemData("Item", IC.useful, 61, 0x4f, "ap_item", 1),
    "Gold Mail": FFCCItemData("Item", IC.useful, 62, 0x50, "ap_item", 1),
    "Crystal Mail": FFCCItemData("Item", IC.useful, 63, 0x51, "ap_item", 1),
    "Diamond Plate": FFCCItemData("Item", IC.useful, 64, 0x52, "ap_item", 1),
    "Gaia Plate": FFCCItemData("Item", IC.useful, 65, 0x53, "ap_item", 1),
    "Mystic Armor": FFCCItemData("Item", IC.useful, 66, 0x54, "ap_item", 1),
    "Trtskn. Coat": FFCCItemData("Item", IC.useful, 67, 0x55, "ap_item", 1),
    "Coat": FFCCItemData("Item", IC.useful, 68, 0x56, "ap_item", 1),
    "Ovrszd. Coat": FFCCItemData("Item", IC.useful, 69, 0x57, "ap_item", 1),

    "Makeshift Shd.": FFCCItemData("Item", IC.useful, 70, 0x58, "ap_item", 1),
    "Iron Shield": FFCCItemData("Item", IC.useful, 71, 0x59, "ap_item", 1),
    "Mythril Shield": FFCCItemData("Item", IC.useful, 72, 0x5a, "ap_item", 1),
    "Flame Shield": FFCCItemData("Item", IC.useful, 73, 0x5b, "ap_item", 1),
    "Frost Shield": FFCCItemData("Item", IC.useful, 74, 0x5c, "ap_item", 1),
    "Storm Shield": FFCCItemData("Item", IC.useful, 75, 0x5d, "ap_item", 1),
    "Saintly Sheild": FFCCItemData("Item", IC.useful, 76, 0x5e, "ap_item", 1),
    "Diamond Shield": FFCCItemData("Item", IC.useful, 77, 0x5f, "ap_item", 1),
    "Rune Shield": FFCCItemData("Item", IC.useful, 78, 0x60, "ap_item", 1),
    "Chocobo Shield": FFCCItemData("Item", IC.useful, 79, 0x61, "ap_item", 1),

    "Gauntlets": FFCCItemData("Item", IC.useful, 80, 0x62, "ap_item", 1),
    "Bronze Gntls.": FFCCItemData("Item", IC.useful, 81, 0x63, "ap_item", 1),
    "Iron Gntls.": FFCCItemData("Item", IC.useful, 82, 0x64, "ap_item", 1),
    "Mythril Gntls.": FFCCItemData("Item", IC.useful, 83, 0x65, "ap_item", 1),
    "Flame Armlets": FFCCItemData("Item", IC.useful, 84, 0x66, "ap_item", 1),
    "Frost Armlets": FFCCItemData("Item", IC.useful, 85, 0x67, "ap_item", 1),
    "Storm Armlets": FFCCItemData("Item", IC.useful, 86, 0x68, "ap_item", 1),
    "Gold Armlets": FFCCItemData("Item", IC.useful, 87, 0x69, "ap_item", 1),
    "Diamond Arms.": FFCCItemData("Item", IC.useful, 88, 0x6a, "ap_item", 1),

    "Helm": FFCCItemData("Item", IC.useful, 89, 0x6b, "ap_item", 1),
    "Bronze Helm": FFCCItemData("Item", IC.useful, 90, 0x6c, "ap_item", 1),
    "Iron Helm": FFCCItemData("Item", IC.useful, 91, 0x6d, "ap_item", 1),
    "Mythril Helm": FFCCItemData("Item", IC.useful, 92, 0x6e, "ap_item", 1),
    "Flame Helm": FFCCItemData("Item", IC.useful, 93, 0x6f, "ap_item", 1),
    "Frost Helm": FFCCItemData("Item", IC.useful, 94, 0x70, "ap_item", 1),
    "Storm Helm": FFCCItemData("Item", IC.useful, 95, 0x71, "ap_item", 1),
    "Time Helm": FFCCItemData("Item", IC.useful, 96, 0x72, "ap_item", 1),
    "Eternal Helm": FFCCItemData("Item", IC.useful, 97, 0x73, "ap_item", 1),
    "Diamond Helm": FFCCItemData("Item", IC.useful, 98, 0x74, "ap_item", 1),
}

FILLER_ITEM_TABLE: dict[str, FFCCItemData] = {
    "Candy Wrapper": FFCCItemData("Item", IC.filler, 54, 0x88, "ap_item", 1),
}

ITEM_TABLE_DESC: dict[str, str] = {
    "Toothbrush Chibi-Gear": "You can clean up most any footprint, pawprint, or spilled liquid on the floor. Also, for some strange reason, you can use it to defeat Spydorz.",

}

LOOKUP_ID_TO_NAME: dict[int, str] = {
    FFCCItem.get_apid(data.code): item for item, data in ITEM_TABLE.items() if data.code is not None
}

item_name_groups = {
    "Chibi-Gear": {
        "Toothbrush Chibi-Gear",
        "Squirter Chibi-Gear",
        "Chibi-Blaster Chibi-Gear",
        "Chibi-Radar Chibi-Gear",
        "Mug Chibi-Gear",
        "Spoon Chibi-Gear",
    },
    "Story Items": {
        "Giga-Charger",
        "Giga-Battery",
        "Charge Chip",
        "Toy Receipt",
        "Alien Ear Chip",
        "Range Chip",
        "Wedding Band",
    },
    "Suits": {
        "Drake Redcrest Suit",
        "Toa Suit",
        "Frog Suit",
        "Trauma Suit",
        "Ghost Suit",
        "Pajamas Suit"
    },
    "Frog Rings": {
        "Foyer Waterfall Frog Ring",
        "Basement Frog Ring",
        "Backyard Frog Ring",
        "Jenny's Room Frog Ring",
        "Living Room Frog Ring (Behind Window)",
        "Living Room Frog Ring (Corkboard)",
        "Living Room Frog Ring (Shelf)",
        "Kitchen Frog Ring (Table)",
        "Sink Drain Frog Ring",
    },
    "Misc": {
        "Red Brick",
        "Green Brick",
        "White Brick",
        "Red Crayon",
        "Yellow Crayon",
        "Green Crayon",
        "Purple Crayon",
        "Dog Tags",
        "Bandage",
        "Ticket Stub",
        "Gunpowder",
        "Hot Rod",
        "Space Scrambler",
        "Scurvy Splinter",
        "Passed-out Frog",
        "Dinahs Teeth",
        "Snorkel",
        "AA Battery",
        "C Battery",
        "D Battery",
        "Free Rangers Photo",
    },
}
_simple_groups = {
    ("Frog Rings", "Frog Ring"),
    ("Chibi-Gear", "Chibi-Gear"),
    ("Crayons", "Crayon"),
    ("Battery's", "Battery"),
    ("Bricks", "Brick"),
    ("Suits", "Suit"),
}

for basename, substring in _simple_groups:
    if basename not in item_name_groups:
        item_name_groups[basename] = set()
    for itemname in ITEM_TABLE:
        if substring in itemname:
            item_name_groups[basename].add(itemname)
