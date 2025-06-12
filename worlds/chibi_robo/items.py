from BaseClasses import Item, ItemClassification
from .game_id import game_name
from typing import TYPE_CHECKING, NamedTuple, Optional, Dict, List
from BaseClasses import ItemClassification as IC
from collections.abc import Iterable
from worlds.AutoWorld import World

class ChibiRoboItemData(NamedTuple):
    """
    This class represents the data for an item.

    :param type: The type of the item.
    :param classification: The item's classification (progression, useful, filler).
    :param code: The unique code identifier for the item.
    :param quantity: The number of this item available.
    :param item_id: The ID used to represent the item in-game.
    """

    type: str
    classification: IC
    code: Optional[int]
    quantity: int
    item_id: Optional[int]


class ChibiRoboItem(Item):
    game: str = game_name
    type: Optional[str]

    def __init__(self, name: str, player: int, data: ChibiRoboItemData, classification: Optional[IC] = None) -> None:
        super().__init__(
            name,
            data.classification if classification is None else classification,
            None if data.code is None else ChibiRoboItem.get_apid(data.code),
            player,
        )

        self.type = data.type
        self.item_id = data.item_id
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

    def item_factory(items: str | Iterable[str], world: World) -> Item | list[Item]:
        """
        Create items based on their names.
        Depending on the input, this function can return a single item or a list of items.

        :param items: The name or names of the items to create.
        :param world: The game world.
        :raises KeyError: If an unknown item name is provided.
        :return: A single item or a list of items.
        """
        ret: list[Item] = []
        singleton = False
        if isinstance(items, str):
            items = [items]
            singleton = True
        for item in items:
            if item in ITEM_TABLE:
                ret.append(world.create_item(item))
            else:
                raise KeyError(f"Unknown item {item}")

        return ret[0] if singleton else ret



ITEM_TABLE: dict[str, ChibiRoboItemData] = {
    "Toothbrush Chibi-Gear": ChibiRoboItemData("Item", IC.useful, 0, 1, 0x10),
    "Spoon Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 1, 1, 0x15),
    "Mug Chibi-Gear": ChibiRoboItemData("Item", IC.useful, 2, 1, 0x16),
    "Chibi-Blaster Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 3, 1, 0x83),
    "Squirter Chibi-Gear": ChibiRoboItemData("Item", IC.useful, 4, 1, 0x38),
    "Range Chip": ChibiRoboItemData("Item", IC.useful, 5, 1, 0x36),
    "Alien Ear Chip": ChibiRoboItemData("Item", IC.progression, 6, 1, 0x3e),
    "Charge Chip": ChibiRoboItemData("Item", IC.progression, 7, 1, 0x35),
    "Giga-Battery": ChibiRoboItemData("Item", IC.progression, 8, 1, 0x08),
    "Giga-Charger": ChibiRoboItemData("Item", IC.progression, 9, 1, 0x30),
    "Left Leg": ChibiRoboItemData("Item", IC.progression, 10, 1, 0x6d),
    "Toy Receipt": ChibiRoboItemData("Item", IC.progression, 11, 1, 0x37),
    "Wedding Band": ChibiRoboItemData("Item", IC.progression, 12, 1, 0x7a),
    "C Battery": ChibiRoboItemData("Item", IC.useful, 13, 1, 0x3b),
    "AA Battery": ChibiRoboItemData("Item", IC.useful, 14, 1, 0x3c),
    "D Battery": ChibiRoboItemData("Item", IC.useful, 15, 1, 0x3a),
    "Red Shoe": ChibiRoboItemData("Item", IC.useful, 16, 1, 0x3d),
    "Green Crayon": ChibiRoboItemData("Item", IC.useful, 17, 1, 0x96),
    "Red Crayon": ChibiRoboItemData("Item", IC.useful, 18, 1, 0x93),
    "Purple Crayon": ChibiRoboItemData("Item", IC.useful, 19, 1, 0x97),
    "Space Scramber": ChibiRoboItemData("Item", IC.useful, 20, 1, 0x6b),
    "Chibi-Battery": ChibiRoboItemData("Item", IC.useful, 21, 1, 0x9e),
    "Dinahs Teeth": ChibiRoboItemData("Item", IC.useful, 22, 1, 0x58),
    "Scurvy Splinter": ChibiRoboItemData("Item", IC.useful, 23, 1, 0x72),
    "Red Brick": ChibiRoboItemData("Item", IC.useful, 24, 1, 0x7a),
    "Chibi-Radar Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 25, 1, 0x83),
    "Ticket Stub": ChibiRoboItemData("Item", IC.progression, 26, 1, 0x83),
    "Foyer Waterfall Frog Ring": ChibiRoboItemData("Item", IC.progression, 27, 1, 0x83),
    "Basement Frog Ring": ChibiRoboItemData("Item", IC.progression, 28, 1, 0x83),
    "Backyard Frog Ring": ChibiRoboItemData("Item", IC.progression, 29, 1, 0x83),
    "Jenny's Room Frog Ring": ChibiRoboItemData("Item", IC.progression, 30, 1, 0x83),
    "Living Room Frog Ring (Behind Window)": ChibiRoboItemData("Item", IC.progression, 31, 1, 0x83),
    "Living Room Frog Ring (Corkboard)": ChibiRoboItemData("Item", IC.progression, 32, 1, 0x83),
    "Living Room Frog Ring (Shelf)": ChibiRoboItemData("Item", IC.progression, 33, 1, 0x83),
    "Kitchen Frog Ring (Table)": ChibiRoboItemData("Item", IC.progression, 34, 1, 0x83),
    "Sink Drain Frog Ring": ChibiRoboItemData("Item", IC.progression, 35, 1, 0x83),
    "Green Brick": ChibiRoboItemData("Item", IC.useful, 36, 1, 0x7a),
    "White Brick": ChibiRoboItemData("Item", IC.useful, 37, 1, 0x7a),
    "Yellow Brick": ChibiRoboItemData("Item", IC.useful, 38, 1, 0x7a),
    "Purple Brick": ChibiRoboItemData("Item", IC.useful, 39, 1, 0x7a),
    "Bandage": ChibiRoboItemData("Item", IC.useful, 40, 1, 0x7a),
    "Dog Tags": ChibiRoboItemData("Item", IC.useful, 41, 1, 0x7a),
    "Hot Rod": ChibiRoboItemData("Item", IC.useful, 42, 1, 0x7a),
    "Gunpower": ChibiRoboItemData("Item", IC.useful, 43, 1, 0x7a),
    "Free Rangers Photo": ChibiRoboItemData("Item", IC.useful, 44, 1, 0x7a),
    "Passed-out Frog": ChibiRoboItemData("Item", IC.useful, 45, 1, 0x7a),
    "Yellow Crayon": ChibiRoboItemData("Item", IC.useful, 46, 1, 0x97),
    "Snorkel": ChibiRoboItemData("Item", IC.useful, 47, 1, 0x97),
    "Space Scrambler": ChibiRoboItemData("Item", IC.useful, 48, 1, 0x6b),
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
        "Range Chip",
    },
    "Story Items": {
        "Giga-Charger",
        "Giga-Battery",
        "Charge Chip",
        "Toy Receipt",
        "Alien Ear Chip",
        "Wedding Band",
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
        "Gunpower",
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
}

for basename, substring in _simple_groups:
    if basename not in item_name_groups:
        item_name_groups[basename] = set()
    for itemname in ITEM_TABLE:
        if substring in itemname:
            item_name_groups[basename].add(itemname)
