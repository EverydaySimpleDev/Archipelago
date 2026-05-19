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
    "Toothbrush Chibi-Gear": FFCCItemData("Item", IC.progression, 0, 0x10, "item_brush", 1),

    "Candy Wrapper": FFCCItemData("Item", IC.filler, 51, 0x88, "item_candy_gomi", 1),
}

FILLER_ITEM_TABLE: dict[str, FFCCItemData] = {
    "Candy Wrapper": FFCCItemData("Item", IC.filler, 54, 0x88, "item_candy_gomi", 1),
}

ITEM_TABLE_DESC: dict[str, str] = {
    "Toothbrush Chibi-Gear": "You can clean up most any footprint, pawprint, or spilled liquid on the floor. Also, for some strange reason, you can use it to defeat Spydorz.",

}

LOOKUP_ID_TO_NAME: dict[int, str] = {
    ChibiRoboItem.get_apid(data.code): item for item, data in ITEM_TABLE.items() if data.code is not None
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
