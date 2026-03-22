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
    "Chibi-Blaster Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 3, 0x83, "cb_cannon_lv_2", 1),
    "Squirter Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 4, 0x38, "item_tyuusyaki", 1),
    "Range Chip": ChibiRoboItemData("Item", IC.progression, 5, 0x06, "item_chip_54", 1),
    "Alien Ear Chip": ChibiRoboItemData("Item", IC.progression, 6, 0x3e, "item_hocyouki", 1),
    "Charge Chip": ChibiRoboItemData("Item", IC.progression, 7, 0x35, "item_chip_53", 1),
    "Giga-Battery": ChibiRoboItemData("Item", IC.progression, 8, 0x08, "item_deka_denchi", 1),
    "Giga-Charger": ChibiRoboItemData("Item", IC.progression, 9, 0x30, "item_chibi_house_denti_2", 1),
    # "Left Leg": ChibiRoboItemData("Item", IC.progression, 10, 0x6d, "item_left_foot", 1),
    "Toy Receipt": ChibiRoboItemData("Item", IC.progression, 11, 0x37,"item_receipt", 1),
    "Wedding Band": ChibiRoboItemData("Item", IC.progression, 12, 0x7a, "item_papa_yubiwa", 1),
    "C Battery": ChibiRoboItemData("Item", IC.useful, 13, 0x3b, "item_denchi_2", 1),
    "AA Battery": ChibiRoboItemData("Item", IC.useful, 14, 0x3c, "item_denchi_3", 1),
    "D Battery": ChibiRoboItemData("Item", IC.useful, 15, 0x3a, "item_denchi_1", 1),
    "Red Shoe": ChibiRoboItemData("Item", IC.useful, 16, 0x3d, "item_peets_kutu", 1),
    "Green Crayon": ChibiRoboItemData("Item", IC.useful, 17, 0x96, "item_kure_4", 1),
    "Red Crayon": ChibiRoboItemData("Item", IC.useful, 18, 0x93, "item_kure_1", 1),
    "Purple Crayon": ChibiRoboItemData("Item", IC.useful, 19, 0x97, "item_kure_5", 1),
    "Chibi-Battery": ChibiRoboItemData("Item", IC.useful, 21, 0x9e, "item_c_denchi", 1),
    "Dinahs Teeth": ChibiRoboItemData("Item", IC.useful, 22, 0x58, "item_rex_tooth", 1),
    "Scurvy Splinter": ChibiRoboItemData("Item", IC.useful, 23, 0x72, "npc_hock_ship_114", 1),
    "Red Brick": ChibiRoboItemData("Item", IC.useful, 24, 0x7a, "item_t_block_6", 1),
    "Chibi-Radar Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 25, 0x83, "cb_radar", 1),
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
    "Purple Brick": ChibiRoboItemData("Item", IC.useful, 39, 0x7a, "item_t_block_2", 1),
    "Bandage": ChibiRoboItemData("Item", IC.useful, 40, 0x67, "item_houtai", 1),
    "Dog Tags": ChibiRoboItemData("Item", IC.useful, 41, 0x65, "item_tug", 1),
    "Hot Rod": ChibiRoboItemData("Item", IC.useful, 42, 0x7b, "item_car_item", 1),
    "Gunpower": ChibiRoboItemData("Item", IC.useful, 43, 0x62, "item_kayaku", 1),
    "Free Rangers Photo": ChibiRoboItemData("Item", IC.useful, 44, 0x7a, "item_army_photo", 1),
    "Passed-out Frog": ChibiRoboItemData("Item", IC.useful, 45, 0x7f, "item_frog", 1),
    "Yellow Crayon": ChibiRoboItemData("Item", IC.useful, 46, 0x97, "item_kure_3", 1),
    "Snorkel": ChibiRoboItemData("Item", IC.useful, 47, 0x63, "item_goggle", 1),
    # "junk_item": ChibiRoboItemData("Junk", IC.useful, 48, 0x12, "item_junk_a", 1),
    "Blue Brick": ChibiRoboItemData("Item", IC.useful, 49, 0x7a, "item_t_block_1", 1),
    "Space Scrambler": ChibiRoboItemData("Item", IC.useful, 50, 0x6b, "item_nwing_item", 1),
    # "Coin C": ChibiRoboItemData("Coin", IC.filler, 51, 0x6b, "coin_c", 1),
    # "Coin S": ChibiRoboItemData("Coin", IC.filler, 81, 0x6b, "coin_s", 1),
    # "Coin G": ChibiRoboItemData("Coin", IC.filler, 88, 0x6b, "coin_g", 1),
    # "Junk A": ChibiRoboItemData("Junk", IC.filler, 92, 0x12, "item_junk_a", 1),
    # "Junk B": ChibiRoboItemData("Junk", IC.filler, 109, 0x12, "item_junk_b", 1),
    # "Junk C": ChibiRoboItemData("Junk", IC.filler, 126, 0x12, "item_junk_c", 1),
    "Wastepaper": ChibiRoboItemData("Item", IC.filler, 143, 0x12, "item_kami_kuzu", 1),
    "Candy Wrapper": ChibiRoboItemData("Item", IC.filler, 165, 0x88, "item_candy_gomi", 1),
    "Candy Bag": ChibiRoboItemData("Item", IC.filler, 173, 0x89, "item_okasi_gomi_1", 1),
    "Cookie Box": ChibiRoboItemData("Item", IC.filler, 178, 0x8a, "item_okasi_gomi_2", 1),
    # "Empty Can": ChibiRoboItemData("Item", IC.filler, 185, 0x6b, "item_okasi_gomi_2", 1),


    #     "Drake Redcrest Suit": ChibiRoboItemData("Item", IC.progression, 235, 0x18, "drake_redcrest_suit"),
    #     "Toa Suit": ChibiRoboItemData("Item", IC.useful, 236, 0x19, "tao_suit"),
    #     "Frog Suit": ChibiRoboItemData("Item", IC.progression, 237, 0x1a, "frog_suit"),
    #     "Trauma Suit": ChibiRoboItemData("Item", IC.useful, 238, 0x1a, "trauma_suit"),
    #     "Ghost Suit": ChibiRoboItemData("Item", IC.useful, 239, 0x22, "ghost_suit"),
    #     "Pajamas Suit": ChibiRoboItemData("Item", IC.useful, 240, 0x1e, "pajamas"),
}

FILLER_ITEM_TABLE: dict[str, ChibiRoboItemData] = {

    # "Coin C": ChibiRoboItemData("Coin", IC.filler, 51, 0x6b, "coin_c", 29),
    # "Coin S": ChibiRoboItemData("Coin", IC.filler, 81, 0x6b, "coin_s", 6),
    # "Coin G": ChibiRoboItemData("Coin", IC.filler, 88, 0x6b, "coin_g", 3),
    # "Junk A": ChibiRoboItemData("Junk", IC.filler, 92, 0x12, "item_junk_a", 14),
    # "Junk B": ChibiRoboItemData("Junk", IC.filler, 109, 0x12, "item_junk_b", 14),
    # "Junk C": ChibiRoboItemData("Junk", IC.filler, 126, 0x12, "item_junk_c", 9),
    "Wastepaper": ChibiRoboItemData("Item", IC.filler, 143, 0x12, "item_kami_kuzu", 1),
    "Candy Wrapper": ChibiRoboItemData("Item", IC.filler, 165, 0x88, "item_candy_gomi", 1),
    "Candy Bag": ChibiRoboItemData("Item", IC.filler, 173, 0x89, "item_okasi_gomi_1", 1),
    "Cookie Box": ChibiRoboItemData("Item", IC.filler, 178, 0x8a, "item_okasi_gomi_2", 1),
    # "Empty Can": ChibiRoboItemData("Item", IC.filler, 185, 0x6b, "item_okasi_gomi_2", 1),
    # "Dust 1": ChibiRoboItemData("Dust", IC.filler, 188, 0x6b, "yogore_h_s", 10),
    # "Dust 2": ChibiRoboItemData("Dust", IC.filler, 189, 0x6b, "yogore_h_k", 10),
    # "Dust 3": ChibiRoboItemData("Dust", IC.filler, 190, 0x6b, "yogore_hun", 10),
    # "Dust 4": ChibiRoboItemData("Dust", IC.filler, 191, 0x6b, "yogore_shimi", 10),
    # "Dust 5": ChibiRoboItemData("Dust", IC.filler, 192, 0x6b, "yogore_30k", 10),
    # "Dust 6": ChibiRoboItemData("Dust", IC.filler, 193, 0x6b, "yogore_50k", 10),
    # "Dust 7": ChibiRoboItemData("Dust", IC.filler, 194, 0x6b, "yogore_kureyon_k", 10),

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
    # "Left Leg": "Slap it on Giga-Robo.",
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

    #     "Drake Redcrest Suit": "This will let anyone know you're a fighter for justice. Drake and Sophie in particular react to this.",
    #     "Tao Suit": " A bark, which will scare lots of people. Further, while wearing this, you can talk to Tao.",
    #     "Frog Suit": "you can talk to any frog, the Bluebird, and Jenny with it.",
    #     "Trauma Suit": "You'll collapse on the ground as if out of power. Wait a few seconds and Telly will automatically take you back to the Chibi-House with no time spent.",
    #     "Ghost Suit": "You'll give a big scare to anyone nearby. The ladies tend to freak out more severely than the guys do, like Princess Pitts and Sophie. Also, if you use this near normal Spydorz, they'll all blow up.",
    #     "Pajamas Suit": "You'll lie down to sleep and will automatically go to the next half-day.",
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
    ("Coins", "Coin"),
    ("Junk", "Junk")
}

for basename, substring in _simple_groups:
    if basename not in item_name_groups:
        item_name_groups[basename] = set()
    for itemname in ITEM_TABLE:
        if substring in itemname:
            item_name_groups[basename].add(itemname)
