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
    :param item_id: The ID used to represent the item in-game.
    """

    type: str
    classification: IC
    code: Optional[int]
    item_id: Optional[int]
    object_name: Optional[str]
    qty: Optional[int]
    special: Optional[bool] = False


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

ITEM_TABLE: dict[str, ChibiRoboItemData] = {
    "Toothbrush Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 0, 0x10, "item_brush", 1),
    "Spoon Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 1, 0x15, "item_spoon", 1),
    "Mug Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 2, 0x16, "item_mag_cup", 1),
    "Chibi-Blaster Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 3, 0x80398ef8, "cb_cannon_lv_2", 1, True),
    "Squirter Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 4, 0x38, "item_tyuusyaki", 1),
    "Chibi-Copter Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 72, 0x80398ef2, "archipelago_item", 1, True),
    "Range Chip": ChibiRoboItemData("Item", IC.progression, 5, 0x36, "item_chip_54", 1),
    "Alien Ear Chip": ChibiRoboItemData("Item", IC.progression, 6, 0x3e, "item_hocyouki", 1),
    "Charge Chip": ChibiRoboItemData("Item", IC.progression, 7, 0x35, "item_chip_53", 1),
    "Giga-Battery": ChibiRoboItemData("Item", IC.progression, 8, 0x08, "item_deka_denchi", 1),
    "Giga-Charger": ChibiRoboItemData("Item", IC.progression, 9, 0x30, "item_chibi_house_denti_2", 1),
    "Toy Receipt": ChibiRoboItemData("Item", IC.progression, 11, 0x37,"item_receipt", 1),
    "Wedding Band": ChibiRoboItemData("Item", IC.progression, 12, 0x7c, "item_papa_yubiwa", 1),
    "C Battery": ChibiRoboItemData("Item", IC.useful, 13, 0x3b, "item_denchi_2", 1),
    "AA Battery": ChibiRoboItemData("Item", IC.useful, 14, 0x3c, "item_denchi_3", 1),
    "D Battery": ChibiRoboItemData("Item", IC.useful, 15, 0x3a, "item_denchi_1", 1),
    "Red Shoe": ChibiRoboItemData("Item", IC.progression, 16, 0x3d, "item_peets_kutu", 1),
    "Green Crayon": ChibiRoboItemData("Item", IC.useful, 17, 0x96, "item_kure_4", 1),
    "Red Crayon": ChibiRoboItemData("Item", IC.useful, 18, 0x93, "item_kure_1", 1),
    "Purple Crayon": ChibiRoboItemData("Item", IC.useful, 19, 0x97, "item_kure_5", 1),
    "Chibi-Battery": ChibiRoboItemData("Item", IC.useful, 21, 0x9e, "item_c_denchi", 1),
    "Dinahs Teeth": ChibiRoboItemData("Item", IC.useful, 22, 0x58, "item_rex_tooth", 1),
    # "Scurvy Splinter": ChibiRoboItemData("Item", IC.useful, 23, 0x72, "npc_hock_ship_114", 1),
    "Red Brick": ChibiRoboItemData("Item", IC.useful, 24, 0x7a, "item_t_block_6", 1),
    "Chibi-Radar Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 25, 0x80398f00, "cb_radar", 1, True),
    "Ticket Stub": ChibiRoboItemData("Item", IC.useful, 26, 0x66, "item_ticket", 1),
    "Foyer Waterfall Frog Ring": ChibiRoboItemData("Item", IC.useful, 27, 0x00, "item_frog_ring", 1),
    "Basement Frog Ring": ChibiRoboItemData("Item", IC.useful, 28, 0x00, "item_frog_ring", 1),
    "Backyard Frog Ring": ChibiRoboItemData("Item", IC.useful, 29, 0x00, "item_frog_ring", 1),
    "Jenny's Room Frog Ring": ChibiRoboItemData("Item", IC.useful, 30, 0x00, "item_frog_ring", 1),
    "Living Room Frog Ring (Behind Window)": ChibiRoboItemData("Item", IC.useful, 31, 0x00, "item_frog_ring", 1),
    "Living Room Frog Ring (Corkboard)": ChibiRoboItemData("Item", IC.useful, 32, 0x00, "item_frog_ring", 1),
    "Living Room Frog Ring (Shelf)": ChibiRoboItemData("Item", IC.useful, 33, 0x00, "item_frog_ring", 1),
    "Kitchen Frog Ring (Table)": ChibiRoboItemData("Item", IC.useful, 34, 0x00, "item_frog_ring", 1),
    "Sink Drain Frog Ring": ChibiRoboItemData("Item", IC.useful, 35, 0x00, "item_frog_ring", 1),
    "Green Brick": ChibiRoboItemData("Item", IC.useful, 36, 0x78, "item_t_block_4", 1),
    "White Brick": ChibiRoboItemData("Item", IC.useful, 37, 0x77, "item_t_block_3", 1),
    "Yellow Brick": ChibiRoboItemData("Item", IC.useful, 38, 0x79, "item_t_block_5", 1),
    "Purple Brick": ChibiRoboItemData("Item", IC.useful, 39, 0x76, "item_t_block_2", 1),
    "Bandage": ChibiRoboItemData("Item", IC.useful, 40, 0x67, "item_houtai", 1),
    "Dog Tags": ChibiRoboItemData("Item", IC.useful, 41, 0x65, "item_tug", 1),
    "Hot Rod": ChibiRoboItemData("Item", IC.useful, 42, 0x7b, "item_car_item", 1),
    "Gunpower": ChibiRoboItemData("Item", IC.useful, 43, 0x62, "item_kayaku", 1),
    "Free Rangers Photo": ChibiRoboItemData("Item", IC.useful, 44, 0x6c, "item_army_photo", 1),
    "Passed-out Frog": ChibiRoboItemData("Item", IC.useful, 45, 0x7f, "item_frog", 1),
    "Yellow Crayon": ChibiRoboItemData("Item", IC.useful, 46, 0x97, "item_kure_3", 1),
    "Snorkel": ChibiRoboItemData("Item", IC.useful, 47, 0x63, "item_goggle", 1),
    "Blue Brick": ChibiRoboItemData("Item", IC.useful, 49, 0x75, "item_t_block_1", 1),
    "Space Scrambler": ChibiRoboItemData("Item", IC.useful, 50, 0x6b, "item_nwing_item", 1),
    "Candy Wrapper": ChibiRoboItemData("Item", IC.filler, 51, 0x88, "item_candy_gomi", 1),
    "Candy Bag": ChibiRoboItemData("Item", IC.filler, 52, 0x89, "item_okasi_gomi_1", 1),
    "Cookie Box": ChibiRoboItemData("Item", IC.filler, 53, 0x8a, "item_okasi_gomi_2", 1),
    "Dog Bone": ChibiRoboItemData("Item", IC.progression, 73, 0x0e, "item_snack_bone", 1),

    "Living Room Ladder": ChibiRoboItemData("Item", IC.progression, 64, 0x80368522, "archipelago_item", 1, True),
    "Kitchen Ladder": ChibiRoboItemData("Item", IC.progression, 65, 0x80368526, "archipelago_item", 1, True),
    "Foyer Teleport": ChibiRoboItemData("Item", IC.progression, 66, 0x8036852c, "archipelago_item", 1, True),
    "Foyer Ladder": ChibiRoboItemData("Item", IC.progression, 67, 0x8036852a, "archipelago_item", 1, True),
    "Living Room Bridge": ChibiRoboItemData("Item", IC.progression, 68, 0x80368532, "archipelago_item", 1, True),
    "Kitchen Bridge": ChibiRoboItemData("Item", IC.filler, 69, 0x80368536, "archipelago_item", 1, True),
    "Bedroom Bridge": ChibiRoboItemData("Item", IC.filler, 70, 0x8036853a, "archipelago_item", 1, True),
    "Basement Teleport": ChibiRoboItemData("Item", IC.filler, 71, 0x8036853e, "archipelago_item", 1, True),
    "Battery Charge": ChibiRoboItemData("Item", IC.filler, 74, 0x80367c4e, "archipelago_item", 1, True),
}

FILLER_ITEM_TABLE: dict[str, ChibiRoboItemData] = {
    "Candy Wrapper": ChibiRoboItemData("Item", IC.filler, 54, 0x88, "item_candy_gomi", 1),
    "Candy Bag": ChibiRoboItemData("Item", IC.filler, 55, 0x89, "item_okasi_gomi_1", 1),
    "Cookie Box": ChibiRoboItemData("Item", IC.filler, 56, 0x8a, "item_okasi_gomi_2", 1),
}

CHARGE_ITEM_TABLE: dict[str, ChibiRoboItemData] = {
    "Battery Charge": ChibiRoboItemData("Item", IC.filler, 75, 0x80367c4e, "archipelago_item", 1, True),
}

SUIT_ITEM_TABLE: dict[str, ChibiRoboItemData] = {
    "Drake Redcrest Suit": ChibiRoboItemData("Suit", IC.progression, 57, 0x18, "item_capsule_24", 1),
    "Toa Suit": ChibiRoboItemData("Suit", IC.progression, 58, 0x19, "item_capsule_25", 1),
    "Frog Suit": ChibiRoboItemData("Suit", IC.progression, 59, 0x1a, "item_capsule_26", 1),
    "Super Chibi-Robo Suit": ChibiRoboItemData("Suit", IC.progression, 60, 0x1f, "item_capsule_31", 1),
    "Trauma Suit": ChibiRoboItemData("Suit", IC.progression, 61, 0x20, "item_capsule_32", 1),
    "Ghost Suit": ChibiRoboItemData("Suit", IC.progression, 62, 0x22, "item_cos_obake", 1),
    "Pajamas": ChibiRoboItemData("Suit", IC.progression, 63, 0x1e, "item_capsule_30", 1),
}

ITEM_TABLE_DESC: dict[str, str] = {
    "Toothbrush Chibi-Gear": "You can clean up most any footprint, pawprint, or spilled liquid on the floor. Also, for some strange reason, you can use it to defeat Spydorz.",
    "Spoon Chibi-Gear": "With this, you can dig holes in soft dirt, or dig up buried objects. It also makes a cool piano sound when you hit something solid.",
    "Mug Chibi-Gear": "With this equipped you're invulnerable to attack.",
    "Chibi-Blaster Chibi-Gear": "t can be used to blast stickers of small bears to open new avenues of travel, and can blast certain other types of walls as well",
    "Squirter Chibi-Gear": "With this, you can pick up just about any liquid lying on the ground.",
    "Range Chip": "Using this, you won't have to worry as much about getting too close to your target.",
    "Alien Ear Chip": "You can now understand alien speech.",
    "Charge Chip": "With this purchased, hold down A to charge up a more powerful version of the shot. Some enemies and barriers can only be defeated with this.",
    "Giga-Battery": "Although you'll have to charge it, this is Giga Robo's power source.",
    "Giga-Charger": "Place in the Chibi-House with the Giga-Battery to start filling it up.",
    "Toy Receipt": "After you visit Mom in the Bedroom at night, she'll mention a missing receipt. Give this to her.",
    "Wedding Band": "The number on it is the code for the bottom of Giga-Robo's foot. After reactivating Giga-Robo, give it to Dad for Happy Points.",
    "C Battery": "Used to operate the castle in Jenny's Room.",
    "AA Battery": "Used to operate the castle in Jenny's Room.",
    "D Battery": "Used to operate the castle in Jenny's Room.",
    "Red Shoe": "Show it to Mort, who will tell you to return it to Princess Pitts.",
    "Green Crayon": "A crayon left by Jenny. Put it back in its box.",
    "Red Crayon": "A crayon left by Jenny. Put it back in its box.",
    "Purple Crayon": "A crayon left by Jenny. Put it back in its box.",
    "Chibi-Battery": "If you run out of energy, this will automatically restore 20 units.",
    "Dinahs Teeth": "Give them back to Dinah.",
    "Scurvy Splinter": "Hand it to Plankbeard as part of his sidequest.",
    "Red Brick": "Give all the blocks to Dinah to get the Block Layout.",
    "Chibi-Radar Chibi-Gear": "Use this and you'll pinpoint the location of something hidden. This most often will point to invisible Chibi-Doors.",
    "Ticket Stub": "Give it to Mort the mummy for some Happy Points.",
    "Foyer Waterfall Frog Ring": "Return all ten to Jenny and you'll get the Frog Ring Sticker.",
    "Basement Frog Ring": "Return all ten to Jenny and you'll get the Frog Ring Sticker.",
    "Backyard Frog Ring": "Return all ten to Jenny and you'll get the Frog Ring Sticker.",
    "Jenny's Room Frog Ring": "Return all ten to Jenny and you'll get the Frog Ring Sticker.",
    "Living Room Frog Ring (Behind Window)": "Return all ten to Jenny and you'll get the Frog Ring Sticker.",
    "Living Room Frog Ring (Corkboard)": "Return all ten to Jenny and you'll get the Frog Ring Sticker.",
    "Living Room Frog Ring (Shelf)": "Return all ten to Jenny and you'll get the Frog Ring Sticker.",
    "Kitchen Frog Ring (Table)": "Return all ten to Jenny and you'll get the Frog Ring Sticker.",
    "Sink Drain Frog Ring": "Return all ten to Jenny and you'll get the Frog Ring Sticker.",
    "Green Brick": "Give all the blocks to Dinah to get the Block Layout.",
    "White Brick": "Give all the blocks to Dinah to get the Block Layout.",
    "Yellow Brick": "Give all the blocks to Dinah to get the Block Layout.",
    "Purple Brick": "Give all the blocks to Dinah to get the Block Layout.",
    "Bandage": "Give it to Mort the mummy for some Happy Points.",
    "Dog Tags": "At some point during training with the Free Rangers, you can give these tags to some of the soldiers, and then to Sarge.",
    "Hot Rod": "Play chicken with the hot-rodding Free Ranger and get an S ranking.",
    "Gunpower": "Give it to Drake Redcrest once he runs out of 'pose juice'. It's part of his Sticker quest.",
    "Free Rangers Photo": "Give it to the Sarge for some Happy Points.",
    "Passed-out Frog": "Carry him to Freida in the Backyard.",
    "Yellow Crayon": "A crayon left by Jenny. Put it back in its box.",
    "Snorkel": "Give it to The Great Peekoe when he's in the fishbowl at night after reviving Giga-Robo.",
    "Space Scrambler": "Ride against the Scrambler Free Rangers and get an S ranking.",
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
    ("Bricks", "Brick")
}

for basename, substring in _simple_groups:
    if basename not in item_name_groups:
        item_name_groups[basename] = set()
    for itemname in ITEM_TABLE:
        if substring in itemname:
            item_name_groups[basename].add(itemname)
