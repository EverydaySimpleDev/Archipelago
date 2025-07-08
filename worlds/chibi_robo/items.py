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
    "Toothbrush Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 0, 0x10, "item_brush"),
    "Spoon Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 1, 0x15, "item_spoon"),
    "Mug Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 2, 0x16, "item_mag_cup"),
    "Chibi-Blaster Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 3, 0x83, "cb_cannon_lv_2"),
    "Squirter Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 4, 0x38, "item_tyuusyaki"),
    "Range Chip": ChibiRoboItemData("Item", IC.progression, 5, 0x06, "item_chip_54"),
    "Alien Ear Chip": ChibiRoboItemData("Item", IC.progression, 6, 0x3e, "item_hocyouki"),
    "Charge Chip": ChibiRoboItemData("Item", IC.progression, 7, 0x35, "item_chip_53"),
    "Giga-Battery": ChibiRoboItemData("Item", IC.progression, 8, 0x08, "item_deka_denchi"),
    "Giga-Charger": ChibiRoboItemData("Item", IC.progression, 9, 0x30, "item_chibi_house_denti_2"),
    "Left Leg": ChibiRoboItemData("Item", IC.progression, 10, 0x6d, "item_left_foot"),
    "Toy Receipt": ChibiRoboItemData("Item", IC.progression, 11, 0x37,"item_receipt"),
    "Wedding Band": ChibiRoboItemData("Item", IC.progression, 12, 0x7a, "item_papa_yubiwa"),
    "C Battery": ChibiRoboItemData("Item", IC.useful, 13, 0x3b, "item_denchi_2"),
    "AA Battery": ChibiRoboItemData("Item", IC.useful, 14, 0x3c, "item_denchi_3"),
    "D Battery": ChibiRoboItemData("Item", IC.useful, 15, 0x3a, "item_denchi_1"),
    "Red Shoe": ChibiRoboItemData("Item", IC.useful, 16, 0x3d, "item_peets_kutu"),
    "Green Crayon": ChibiRoboItemData("Item", IC.useful, 17, 0x96, "item_kure_4"),
    "Red Crayon": ChibiRoboItemData("Item", IC.useful, 18, 0x93, "item_kure_1"),
    "Purple Crayon": ChibiRoboItemData("Item", IC.useful, 19, 0x97, "item_kure_5"),
    "Space Scramber": ChibiRoboItemData("Item", IC.useful, 20, 0x6b, "item_nwing_item"),
    "Chibi-Battery": ChibiRoboItemData("Item", IC.useful, 21, 0x9e, "item_c_denchi"),
    "Dinahs Teeth": ChibiRoboItemData("Item", IC.useful, 22, 0x58, "item_rex_tooth"),
    "Scurvy Splinter": ChibiRoboItemData("Item", IC.useful, 23, 0x72, "npc_hock_ship_114"),
    "Red Brick": ChibiRoboItemData("Item", IC.useful, 24, 0x7a, "item_t_block_6"),
    "Chibi-Radar Chibi-Gear": ChibiRoboItemData("Item", IC.progression, 25, 0x83, "cb_radar"),
    "Ticket Stub": ChibiRoboItemData("Item", IC.progression, 26, 0x66, "item_ticket"),
    "Foyer Waterfall Frog Ring": ChibiRoboItemData("Item", IC.progression, 27, 0x00, "item_frog_ring"),
    "Basement Frog Ring": ChibiRoboItemData("Item", IC.progression, 28, 0x00, "item_frog_ring"),
    "Backyard Frog Ring": ChibiRoboItemData("Item", IC.progression, 29, 0x00, "item_frog_ring"),
    "Jenny's Room Frog Ring": ChibiRoboItemData("Item", IC.progression, 30, 0x00, "item_frog_ring"),
    "Living Room Frog Ring (Behind Window)": ChibiRoboItemData("Item", IC.useful, 31, 0x00, "item_frog_ring"),
    "Living Room Frog Ring (Corkboard)": ChibiRoboItemData("Item", IC.useful, 32, 0x00, "item_frog_ring"),
    "Living Room Frog Ring (Shelf)": ChibiRoboItemData("Item", IC.useful, 33, 0x00, "item_frog_ring"),
    "Kitchen Frog Ring (Table)": ChibiRoboItemData("Item", IC.useful, 34, 0x00, "item_frog_ring"),
    "Sink Drain Frog Ring": ChibiRoboItemData("Item", IC.useful, 35, 0x00, "item_frog_ring"),
    "Green Brick": ChibiRoboItemData("Item", IC.useful, 36, 0x78, "item_t_block_4"),
    "White Brick": ChibiRoboItemData("Item", IC.useful, 37, 0x77, "item_t_block_3"),
    "Yellow Brick": ChibiRoboItemData("Item", IC.useful, 38, 0x79, "item_t_block_5"),
    "Purple Brick": ChibiRoboItemData("Item", IC.useful, 39, 0x7a, "item_t_block_2"),
    "Bandage": ChibiRoboItemData("Item", IC.useful, 40, 0x67, "item_houtai"),
    "Dog Tags": ChibiRoboItemData("Item", IC.useful, 41, 0x65, "item_tug"),
    "Hot Rod": ChibiRoboItemData("Item", IC.useful, 42, 0x7b, "item_car_item"),
    "Gunpower": ChibiRoboItemData("Item", IC.useful, 43, 0x62, "item_kayaku"),
    "Free Rangers Photo": ChibiRoboItemData("Item", IC.useful, 44, 0x7a, "item_army_photo"),
    "Passed-out Frog": ChibiRoboItemData("Item", IC.useful, 45, 0x7f, "item_frog"),
    "Yellow Crayon": ChibiRoboItemData("Item", IC.useful, 46, 0x97, "item_kure_3"),
    "Snorkel": ChibiRoboItemData("Item", IC.useful, 47, 0x63, "item_goggle"),
    "junk_item": ChibiRoboItemData("Item", IC.useful, 48, 0x12, "item_junk_a"),
    "Coin C 1": ChibiRoboItemData("Item", IC.filler, 49, 0x6b, "coin_c"),
    "Coin C 2": ChibiRoboItemData("Item", IC.filler, 50, 0x6b, "coin_c"),
    "Coin C 3": ChibiRoboItemData("Item", IC.filler, 51, 0x6b, "coin_c"),
    "Coin C 4": ChibiRoboItemData("Item", IC.filler, 52, 0x6b, "coin_c"),
    "Coin C 5": ChibiRoboItemData("Item", IC.filler, 53, 0x6b, "coin_c"),
    "Coin C 6": ChibiRoboItemData("Item", IC.filler, 54, 0x6b, "coin_c"),
    "Coin C 7": ChibiRoboItemData("Item", IC.filler, 55, 0x6b, "coin_c"),
    "Coin C 8": ChibiRoboItemData("Item", IC.filler, 56, 0x6b, "coin_c"),
    "Coin C 9": ChibiRoboItemData("Item", IC.filler, 57, 0x6b, "coin_c"),
    "Coin C 10": ChibiRoboItemData("Item", IC.filler, 58, 0x6b, "coin_c"),
    "Coin C 11": ChibiRoboItemData("Item", IC.filler, 59, 0x6b, "coin_c"),
    "Coin C 12": ChibiRoboItemData("Item", IC.filler, 60, 0x6b, "coin_c"),
    "Coin C 13": ChibiRoboItemData("Item", IC.filler, 61, 0x6b, "coin_c"),
    "Coin C 14": ChibiRoboItemData("Item", IC.filler, 62, 0x6b, "coin_c"),
    "Coin C 15": ChibiRoboItemData("Item", IC.filler, 63, 0x6b, "coin_c"),
    "Coin C 16": ChibiRoboItemData("Item", IC.filler, 64, 0x6b, "coin_c"),
    "Coin C 17": ChibiRoboItemData("Item", IC.filler, 65, 0x6b, "coin_c"),
    "Coin C 18": ChibiRoboItemData("Item", IC.filler, 66, 0x6b, "coin_c"),
    "Coin C 19": ChibiRoboItemData("Item", IC.filler, 67, 0x6b, "coin_c"),
    "Coin C 20": ChibiRoboItemData("Item", IC.filler, 68, 0x6b, "coin_c"),
    "Coin C 21": ChibiRoboItemData("Item", IC.filler, 69, 0x6b, "coin_c"),
    "Coin C 22": ChibiRoboItemData("Item", IC.filler, 70, 0x6b, "coin_c"),
    "Coin C 23": ChibiRoboItemData("Item", IC.filler, 71, 0x6b, "coin_c"),
    "Coin C 24": ChibiRoboItemData("Item", IC.filler, 72, 0x6b, "coin_c"),
    "Coin C 25": ChibiRoboItemData("Item", IC.filler, 73, 0x6b, "coin_c"),
    "Coin C 26": ChibiRoboItemData("Item", IC.filler, 74, 0x6b, "coin_c"),
    "Coin C 27": ChibiRoboItemData("Item", IC.filler, 75, 0x6b, "coin_c"),
    "Coin C 28": ChibiRoboItemData("Item", IC.filler, 76, 0x6b, "coin_c"),
    "Coin C 29": ChibiRoboItemData("Item", IC.filler, 77, 0x6b, "coin_c"),
    "Coin C 30": ChibiRoboItemData("Item", IC.filler, 78, 0x6b, "coin_c"),
    "Coin S 1": ChibiRoboItemData("Item", IC.filler, 79, 0x6b, "coin_s"),
    "Coin S 2": ChibiRoboItemData("Item", IC.filler, 80, 0x6b, "coin_s"),
    "Coin S 3": ChibiRoboItemData("Item", IC.filler, 81, 0x6b, "coin_s"),
    "Coin S 4": ChibiRoboItemData("Item", IC.filler, 82, 0x6b, "coin_s"),
    "Coin S 5": ChibiRoboItemData("Item", IC.filler, 83, 0x6b, "coin_s"),
    "Coin S 6": ChibiRoboItemData("Item", IC.filler, 84, 0x6b, "coin_s"),
    "Coin S 7": ChibiRoboItemData("Item", IC.filler, 85, 0x6b, "coin_s"),
    "Coin G 1": ChibiRoboItemData("Item", IC.filler, 86, 0x6b, "coin_g"),
    "Coin G 2": ChibiRoboItemData("Item", IC.filler, 87, 0x6b, "coin_g"),
    "Coin G 3": ChibiRoboItemData("Item", IC.filler, 88, 0x6b, "coin_g"),
    "Coin G 4": ChibiRoboItemData("Item", IC.filler, 89, 0x6b, "coin_g"),
    "Junk A 1": ChibiRoboItemData("Item", IC.filler, 90, 0x12, "item_junk_a"),
    "Junk A 2": ChibiRoboItemData("Item", IC.filler, 91, 0x12, "item_junk_a"),
    "Junk A 3": ChibiRoboItemData("Item", IC.filler, 92, 0x12, "item_junk_a"),
    "Junk A 4": ChibiRoboItemData("Item", IC.filler, 93, 0x6b, "item_junk_a"),
    "Junk A 5": ChibiRoboItemData("Item", IC.filler, 94, 0x12, "item_junk_a"),
    "Junk A 6": ChibiRoboItemData("Item", IC.filler, 95, 0x12, "item_junk_a"),
    "Junk A 7": ChibiRoboItemData("Item", IC.filler, 96, 0x12, "item_junk_a"),
    "Junk A 8": ChibiRoboItemData("Item", IC.filler, 97, 0x12, "item_junk_a"),
    "Junk A 9": ChibiRoboItemData("Item", IC.filler, 98, 0x12, "item_junk_a"),
    "Junk A 10": ChibiRoboItemData("Item", IC.filler, 99, 0x12, "item_junk_a"),
    "Junk A 11": ChibiRoboItemData("Item", IC.filler, 100, 0x12, "item_junk_a"),
    "Junk A 12": ChibiRoboItemData("Item", IC.filler, 101, 0x12, "item_junk_a"),
    "Junk A 13": ChibiRoboItemData("Item", IC.filler, 102, 0x12, "item_junk_a"),
    "Junk A 14": ChibiRoboItemData("Item", IC.filler, 103, 0x12, "item_junk_a"),
    "Junk A 15": ChibiRoboItemData("Item", IC.filler, 104, 0x12, "item_junk_a"),
    "Junk A 16": ChibiRoboItemData("Item", IC.filler, 105, 0x12, "item_junk_a"),
    "Junk A 17": ChibiRoboItemData("Item", IC.filler, 106, 0x12, "item_junk_a"),
    "Junk B 1": ChibiRoboItemData("Item", IC.filler, 107, 0x12, "item_junk_b"),
    "Junk B 2": ChibiRoboItemData("Item", IC.filler, 108, 0x12, "item_junk_b"),
    "Junk B 3": ChibiRoboItemData("Item", IC.filler, 109, 0x12, "item_junk_b"),
    "Junk B 4": ChibiRoboItemData("Item", IC.filler, 110, 0x12, "item_junk_b"),
    "Junk B 5": ChibiRoboItemData("Item", IC.filler, 111, 0x12, "item_junk_b"),
    "Junk B 6": ChibiRoboItemData("Item", IC.filler, 112, 0x12, "item_junk_b"),
    "Junk B 7": ChibiRoboItemData("Item", IC.filler, 113, 0x12, "item_junk_b"),
    "Junk B 8": ChibiRoboItemData("Item", IC.filler, 114, 0x12, "item_junk_b"),
    "Junk B 9": ChibiRoboItemData("Item", IC.filler, 115, 0x12, "item_junk_b"),
    "Junk B 10": ChibiRoboItemData("Item", IC.filler, 116, 0x12, "item_junk_b"),
    "Junk B 11": ChibiRoboItemData("Item", IC.filler, 117, 0x12, "item_junk_b"),
    "Junk B 12": ChibiRoboItemData("Item", IC.filler, 118, 0x12, "item_junk_b"),
    "Junk B 13": ChibiRoboItemData("Item", IC.filler, 119, 0x12, "item_junk_b"),
    "Junk B 14": ChibiRoboItemData("Item", IC.filler, 120, 0x12, "item_junk_b"),
    "Junk B 15": ChibiRoboItemData("Item", IC.filler, 121, 0x12, "item_junk_b"),
    "Junk B 16": ChibiRoboItemData("Item", IC.filler, 122, 0x12, "item_junk_b"),
    "Junk B 17": ChibiRoboItemData("Item", IC.filler, 123, 0x12, "item_junk_b"),
    "Junk C 1": ChibiRoboItemData("Item", IC.filler, 124, 0x12, "item_junk_c"),
    "Junk C 2": ChibiRoboItemData("Item", IC.filler, 125, 0x12, "item_junk_c"),
    "Junk C 3": ChibiRoboItemData("Item", IC.filler, 126, 0x12, "item_junk_c"),
    "Junk C 4": ChibiRoboItemData("Item", IC.filler, 127, 0x12, "item_junk_c"),
    "Junk C 5": ChibiRoboItemData("Item", IC.filler, 128, 0x12, "item_junk_c"),
    "Junk C 6": ChibiRoboItemData("Item", IC.filler, 129, 0x12, "item_junk_c"),
    "Junk C 7": ChibiRoboItemData("Item", IC.filler, 130, 0x12, "item_junk_c"),
    "Junk C 8": ChibiRoboItemData("Item", IC.filler, 131, 0x12, "item_junk_c"),
    "Junk C 9": ChibiRoboItemData("Item", IC.filler, 132, 0x12, "item_junk_c"),
    "Junk C 10": ChibiRoboItemData("Item", IC.filler, 133, 0x12, "item_junk_c"),
    "Junk C 11": ChibiRoboItemData("Item", IC.filler, 134, 0x12, "item_junk_c"),
    "Junk C 12": ChibiRoboItemData("Item", IC.filler, 135, 0x12, "item_junk_c"),
    "Junk C 13": ChibiRoboItemData("Item", IC.filler, 136, 0x12, "item_junk_c"),
    "Junk C 14": ChibiRoboItemData("Item", IC.filler, 137, 0x12, "item_junk_c"),
    "Junk C 15": ChibiRoboItemData("Item", IC.filler, 138, 0x12, "item_junk_c"),
    "Junk C 16": ChibiRoboItemData("Item", IC.filler, 139, 0x12, "item_junk_c"),
    "Junk C 17": ChibiRoboItemData("Item", IC.filler, 140, 0x12, "item_junk_c"),
    "Wastepaper 1": ChibiRoboItemData("Item", IC.filler, 141, 0x12, "item_kami_kuzu"),
    "Wastepaper 2": ChibiRoboItemData("Item", IC.filler, 142, 0x12, "item_kami_kuzu"),
    "Wastepaper 3": ChibiRoboItemData("Item", IC.filler, 143, 0x12, "item_kami_kuzu"),
    "Wastepaper 4": ChibiRoboItemData("Item", IC.filler, 144, 0x12, "item_kami_kuzu"),
    "Wastepaper 5": ChibiRoboItemData("Item", IC.filler, 145, 0x12, "item_kami_kuzu"),
    "Wastepaper 6": ChibiRoboItemData("Item", IC.filler, 146, 0x12, "item_kami_kuzu"),
    "Wastepaper 7": ChibiRoboItemData("Item", IC.filler, 147, 0x12, "item_kami_kuzu"),
    "Wastepaper 8": ChibiRoboItemData("Item", IC.filler, 148, 0x12, "item_kami_kuzu"),
    "Wastepaper 9": ChibiRoboItemData("Item", IC.filler, 149, 0x12, "item_kami_kuzu"),
    "Wastepaper 10": ChibiRoboItemData("Item", IC.filler, 150, 0x12, "item_kami_kuzu"),
    "Wastepaper 11": ChibiRoboItemData("Item", IC.filler, 151, 0x12, "item_kami_kuzu"),
    "Wastepaper 12": ChibiRoboItemData("Item", IC.filler, 152, 0x12, "item_kami_kuzu"),
    "Wastepaper 13": ChibiRoboItemData("Item", IC.filler, 153, 0x12, "item_kami_kuzu"),
    "Wastepaper 14": ChibiRoboItemData("Item", IC.filler, 154, 0x12, "item_kami_kuzu"),
    "Wastepaper 15": ChibiRoboItemData("Item", IC.filler, 155, 0x12, "item_kami_kuzu"),
    "Wastepaper 16": ChibiRoboItemData("Item", IC.filler, 156, 0x12, "item_kami_kuzu"),
    "Wastepaper 17": ChibiRoboItemData("Item", IC.filler, 157, 0x12, "item_kami_kuzu"),
    "Wastepaper 18": ChibiRoboItemData("Item", IC.filler, 158, 0x12, "item_kami_kuzu"),
    "Wastepaper 19": ChibiRoboItemData("Item", IC.filler, 159, 0x12, "item_kami_kuzu"),
    "Wastepaper 20": ChibiRoboItemData("Item", IC.filler, 160, 0x12, "item_kami_kuzu"),
    "Wastepaper 21": ChibiRoboItemData("Item", IC.filler, 161, 0x12, "item_kami_kuzu"),
    "Wastepaper 22": ChibiRoboItemData("Item", IC.filler, 162, 0x12, "item_kami_kuzu"),
    "Candy Wrapper 1": ChibiRoboItemData("Item", IC.filler, 163, 0x88, "item_candy_gomi"),
    "Candy Wrapper 2": ChibiRoboItemData("Item", IC.filler, 164, 0x88, "item_candy_gomi"),
    "Candy Wrapper 3": ChibiRoboItemData("Item", IC.filler, 165, 0x88, "item_candy_gomi"),
    "Candy Wrapper 4": ChibiRoboItemData("Item", IC.filler, 166, 0x88, "item_candy_gomi"),
    "Candy Wrapper 5": ChibiRoboItemData("Item", IC.filler, 167, 0x88, "item_candy_gomi"),
    "Candy Wrapper 6": ChibiRoboItemData("Item", IC.filler, 168, 0x88, "item_candy_gomi"),
    "Candy Wrapper 7": ChibiRoboItemData("Item", IC.filler, 169, 0x88, "item_candy_gomi"),
    "Candy Wrapper 8": ChibiRoboItemData("Item", IC.filler, 170, 0x88, "item_candy_gomi"),
    # "Candy Wrapper 9": ChibiRoboItemData("Item", IC.filler, 171, 0x88, "item_candy_gomi"),
    # "Candy Wrapper 10": ChibiRoboItemData("Item", IC.filler, 172, 0x88, "item_candy_gomi"),
    # "Candy Wrapper 11": ChibiRoboItemData("Item", IC.filler, 173, 0x88, "item_candy_gomi"),
    # "Candy Wrapper 12": ChibiRoboItemData("Item", IC.filler, 174, 0x88, "item_candy_gomi"),
    # "Candy Wrapper 13": ChibiRoboItemData("Item", IC.filler, 175, 0x88, "item_candy_gomi"),
    # "Candy Wrapper 14": ChibiRoboItemData("Item", IC.filler, 176, 0x88, "item_candy_gomi"),
    # "Candy Wrapper 15": ChibiRoboItemData("Item", IC.filler, 177, 0x88, "item_candy_gomi"),
    # "Candy Wrapper 16": ChibiRoboItemData("Item", IC.filler, 178, 0x88, "item_candy_gomi"),
    # "Candy Wrapper 17": ChibiRoboItemData("Item", IC.filler, 179, 0x88, "item_candy_gomi"),
    # "Candy Wrapper 18": ChibiRoboItemData("Item", IC.filler, 180, 0x88, "item_candy_gomi"),
    # "Candy Wrapper 19": ChibiRoboItemData("Item", IC.filler, 181, 0x88, "item_candy_gomi"),
    # "Candy Wrapper 20": ChibiRoboItemData("Item", IC.filler, 182, 0x88, "item_candy_gomi"),
    # "Candy Wrapper 21": ChibiRoboItemData("Item", IC.filler, 183, 0x88, "item_candy_gomi"),
    # "Candy Wrapper 22": ChibiRoboItemData("Item", IC.filler, 184, 0x88, "item_candy_gomi"),
    "Candy Bag 1": ChibiRoboItemData("Item", IC.filler, 185, 0x89, "item_okasi_gomi_1"),
    "Candy Bag 2": ChibiRoboItemData("Item", IC.filler, 186, 0x89, "item_okasi_gomi_1"),
    "Candy Bag 3": ChibiRoboItemData("Item", IC.filler, 187, 0x89, "item_okasi_gomi_1"),
    "Candy Bag 4": ChibiRoboItemData("Item", IC.filler, 188, 0x89, "item_okasi_gomi_1"),
    "Candy Bag 5": ChibiRoboItemData("Item", IC.filler, 189, 0x89, "item_okasi_gomi_1"),
    "Cookie Box 1": ChibiRoboItemData("Item", IC.filler, 190, 0x8a, "item_okasi_gomi_2"),
    "Cookie Box 2": ChibiRoboItemData("Item", IC.filler, 191, 0x8a, "item_okasi_gomi_2"),
    "Cookie Box 3": ChibiRoboItemData("Item", IC.filler, 192, 0x8a, "item_okasi_gomi_2"),
    "Cookie Box 4": ChibiRoboItemData("Item", IC.filler, 193, 0x8a, "item_okasi_gomi_2"),
    "Cookie Box 5": ChibiRoboItemData("Item", IC.filler, 194, 0x8a, "item_okasi_gomi_2"),
    "Cookie Box 6": ChibiRoboItemData("Item", IC.filler, 195, 0x8a, "item_okasi_gomi_2"),
    "Cookie Box 7": ChibiRoboItemData("Item", IC.filler, 196, 0x8a, "item_okasi_gomi_2"),
    "Empty Can 1": ChibiRoboItemData("Item", IC.filler, 197, 0x6b, "item_okasi_gomi_2"),
    "Empty Can 2": ChibiRoboItemData("Item", IC.filler, 198, 0x6b, "item_okasi_gomi_2"),
    "Empty Can 3": ChibiRoboItemData("Item", IC.filler, 199, 0x6b, "item_okasi_gomi_2"),
    "Coin G 6": ChibiRoboItemData("Item", IC.filler, 211, 0x6b, "coin_g"),
    "Coin G 7": ChibiRoboItemData("Item", IC.filler, 212, 0x6b, "coin_g"),
    "Coin G 8": ChibiRoboItemData("Item", IC.filler, 213, 0x6b, "coin_g"),
    "Coin G 9": ChibiRoboItemData("Item", IC.filler, 214, 0x6b, "coin_g"),
    "Coin G 10": ChibiRoboItemData("Item", IC.filler, 215, 0x6b, "coin_g"),
    "Coin G 11": ChibiRoboItemData("Item", IC.filler, 216, 0x6b, "coin_g"),
    "Coin G 12": ChibiRoboItemData("Item", IC.filler, 217, 0x6b, "coin_g"),
    "Coin G 13": ChibiRoboItemData("Item", IC.filler, 218, 0x6b, "coin_g"),
    "Coin G 14": ChibiRoboItemData("Item", IC.filler, 219, 0x6b, "coin_g"),
    "Coin G 15": ChibiRoboItemData("Item", IC.filler, 220, 0x6b, "coin_g"),
    "Coin G 16": ChibiRoboItemData("Item", IC.filler, 221, 0x6b, "coin_g"),
    "Coin G 17": ChibiRoboItemData("Item", IC.filler, 222, 0x6b, "coin_g"),
    "Coin G 18": ChibiRoboItemData("Item", IC.filler, 223, 0x6b, "coin_g"),
    "Coin G 19": ChibiRoboItemData("Item", IC.filler, 224, 0x6b, "coin_g"),
    "Coin G 20": ChibiRoboItemData("Item", IC.filler, 225, 0x6b, "coin_g"),
    "Coin G 21": ChibiRoboItemData("Item", IC.filler, 226, 0x6b, "coin_g"),
    "Coin G 22": ChibiRoboItemData("Item", IC.filler, 227, 0x6b, "coin_g"),
    "Coin G 23": ChibiRoboItemData("Item", IC.filler, 228, 0x6b, "coin_g"),
    "Coin G 24": ChibiRoboItemData("Item", IC.filler, 229, 0x6b, "coin_g"),
    "Coin G 25": ChibiRoboItemData("Item", IC.filler, 230, 0x6b, "coin_g"),
    "Coin G 26": ChibiRoboItemData("Item", IC.filler, 231, 0x6b, "coin_g"),
    "Coin G 27": ChibiRoboItemData("Item", IC.filler, 232, 0x6b, "coin_g"),
    "Blue Brick": ChibiRoboItemData("Item", IC.useful, 233, 0x7a, "item_t_block_1"),
    "Space Scrambler": ChibiRoboItemData("Item", IC.useful, 234, 0x6b, "item_nwing_item"),
    "Coin G 28": ChibiRoboItemData("Item", IC.filler, 235, 0x6b, "coin_g"),
    "Coin G 29": ChibiRoboItemData("Item", IC.filler, 236, 0x6b, "coin_g"),
    "Coin G 30": ChibiRoboItemData("Item", IC.filler, 237, 0x6b, "coin_g"),
    "Coin G 31": ChibiRoboItemData("Item", IC.filler, 238, 0x6b, "coin_g"),
    "Coin G 32": ChibiRoboItemData("Item", IC.filler, 239, 0x6b, "coin_g"),
    "Coin G 33": ChibiRoboItemData("Item", IC.filler, 240, 0x6b, "coin_g"),
    "Coin G 34": ChibiRoboItemData("Item", IC.filler, 241, 0x6b, "coin_g"),
    "Coin G 35": ChibiRoboItemData("Item", IC.filler, 242, 0x6b, "coin_g"),
    "Coin G 36": ChibiRoboItemData("Item", IC.filler, 243, 0x6b, "coin_g"),
    "Coin G 37": ChibiRoboItemData("Item", IC.filler, 244, 0x6b, "coin_g"),
    "Coin G 38": ChibiRoboItemData("Item", IC.filler, 245, 0x6b, "coin_g"),

    #     "Drake Redcrest Suit": ChibiRoboItemData("Item", IC.progression, 235, 0x18, "drake_redcrest_suit"),
    #     "Toa Suit": ChibiRoboItemData("Item", IC.useful, 236, 0x19, "tao_suit"),
    #     "Frog Suit": ChibiRoboItemData("Item", IC.progression, 237, 0x1a, "frog_suit"),
    #     "Trauma Suit": ChibiRoboItemData("Item", IC.useful, 238, 0x1a, "trauma_suit"),
    #     "Ghost Suit": ChibiRoboItemData("Item", IC.useful, 239, 0x22, "ghost_suit"),
    #     "Pajamas Suit": ChibiRoboItemData("Item", IC.useful, 240, 0x1e, "pajamas"),
}

filler_item_names = ["Coin S 1", "Coin C 1", "Coin G 1" ]

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
