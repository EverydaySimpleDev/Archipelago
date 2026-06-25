from .game_id import game_name
from typing import Dict, List

from enum import Enum, Flag, auto
from typing import TYPE_CHECKING, NamedTuple, Optional

from BaseClasses import Location, Region

class ChibiRoboLocationData(NamedTuple):
    """

    :param code: The unique code identifier for the location.
    :param region: The name of the region where the location resides.
    :param stage_id: The ID of the stage where the location resides.
    :param bit: The bit in memory that is associated with the location. This is combined with other location data to
    determine where in memory to determine whether the location has been checked. If the location is a special type,
    this bit is ignored.
    :param address: For certain location types, this variable contains the address of the byte with the check bit for
    that location. Defaults to `None`.
    :param object_id: the object / location in game that will be replaced. Defaults to `None`.
    """

    code: Optional[int]
    region: str
    stage_id: int
    bit: int
    address: Optional[int] = None
    object_id: Optional[int] = None

class ChibiRoboLocation(Location):
    """
    :param player: The ID of the player whose world the location is in.
    :param name: The name of the location.
    :param parent: The location's parent region.
    :param data: The data associated with this location.
    """

    game: str = game_name

    def __init__(self, player: int, name: str, parent: Region, data: ChibiRoboLocationData | None = None):
        address = None if data.code is None else ChibiRoboLocation.get_apid(data.code)
        super().__init__(player, name, address=address, parent=parent)

        self.code = data.code
        self.region = data.region
        self.stage_id = data.stage_id
        self.bit = data.bit
        self.address = self.address
        self.object_id = data.object_id

    @staticmethod
    def get_apid(code: int) -> int:
        """
        Compute the Archipelago ID for the given location code.

        :param code: The unique code for the location.
        :return: The computed Archipelago ID.
        """
        base_id: int = 2326528
        return base_id + code

LOCATION_TABLE: dict[str, ChibiRoboLocationData] = {

    "Living Room - Frog Ring (Behind Window)": ChibiRoboLocationData(0, "Living Room", 0x07, 1, 0x8037de30, 19),
    "Living Room - Frog Ring (Corkboard)": ChibiRoboLocationData(1, "Living Room", 0x07, 2, 0x8037de30, 20),
    "Living Room - Frog Ring (Shelf)": ChibiRoboLocationData(2, "Living Room", 0x07, 3, 0x8037de30, 21),
    "Living Room - Wastepaper by Trashbin B": ChibiRoboLocationData(17, "Living Room", 0x07, 4, 0x8037de30, 115),
    "Living Room - Candy Wrapper above Trashbin A": ChibiRoboLocationData(18, "Living Room", 0x07, 5, 0x8037de30, 116),
    "Living Room - Wastepaper by Trashbin A": ChibiRoboLocationData(19, "Living Room", 0x07, 7, 0x8037de30, 117),
    "Living Room - Cupholder Wastepaper": ChibiRoboLocationData(20, "Living Room", 0x07, 8, 0x8037de36, 118),
    "Living Room - Cookie Crumbs under Table": ChibiRoboLocationData(21, "Living Room", 0x07, 9, 0x8037de36, 119),
    "Living Room - Cookie Crumbs by Record Player": ChibiRoboLocationData(22, "Living Room", 0x07, 10, 0x8037de36, 120),
    "Living Room - Toothbrush": ChibiRoboLocationData(23, "Living Room", 0x07, 11, 0x8037de36, 133),
    "Living Room - Wastepaper by Door to Kitchen": ChibiRoboLocationData(34, "Living Room", 0x07, 12, 0x8037de36, 257),
    "Living Room - Fireplace Wastepaper A": ChibiRoboLocationData(35, "Living Room", 0x07, 13, 0x8037de36, 258),
    "Living Room - Fireplace Wastepaper B": ChibiRoboLocationData(36, "Living Room", 0x07, 14, 0x8037de36, 259),
    "Living Room - Wastepaper on Stack of Books": ChibiRoboLocationData(37, "Living Room", 0x07, 15, 0x8037de36, 260),
    "Living Room - Couch Wastepaper B": ChibiRoboLocationData(38, "Living Room", 0x07, 0, 0x8037de36, 261),
    "Living Room - Wastepaper by Toothbrush Spawn": ChibiRoboLocationData(41, "Living Room", 0x07, 1, 0x8037de36, 319),
    "Living Room - Wastepaper below Cupholder": ChibiRoboLocationData(42, "Living Room", 0x07, 2, 0x8037de36, 320),
    "Living Room - Couch Wastepaper A": ChibiRoboLocationData(43, "Living Room", 0x07, 3, 0x8037de36, 321),
    "Living Room - Cookie Crumbs under Couch": ChibiRoboLocationData(44, "Living Room", 0x07, 4, 0x8037de36, 322),
    "Living Room - Cookie Crumbs on Couch": ChibiRoboLocationData(45, "Living Room", 0x07, 5, 0x8037de36, 323),
    "Living Room - Twig A": ChibiRoboLocationData(46, "Living Room", 0x07, 6, 0x8037de36, 324),
    "Living Room - Twig B": ChibiRoboLocationData(47, "Living Room", 0x07, 7, 0x8037de36, 325),
    "Living Room - Twig C": ChibiRoboLocationData(48, "Living Room", 0x07, 8, 0x8037de34, 326),
    "Living Room - Wastepaper above Trashbin A": ChibiRoboLocationData(54, "Living Room", 0x07, 9, 0x8037de34, 367),
    "Living Room - Wastepaper above Trashbin B": ChibiRoboLocationData(55, "Living Room", 0x07, 10, 0x8037de34, 368),
    "Living Room - Candy Wrapper above Trashbin B": ChibiRoboLocationData(56, "Living Room", 0x07, 6, 0x8037de30, 437),
    "Living Room - Candy Wrapper by Jenny A": ChibiRoboLocationData(57, "Living Room", 0x07, 11, 0x8037de34, 438),
    "Living Room - Couch Candy Wrapper": ChibiRoboLocationData(58, "Living Room", 0x07, 13, 0x8037de34, 439),
    "Living Room - Candy Wrapper by Jenny B": ChibiRoboLocationData(59, "Living Room", 0x07, 12, 0x8037de34, 440),
    "Living Room - Candy Wrapper on Book Stack": ChibiRoboLocationData(60, "Living Room", 0x07, 14, 0x8037de34, 441),
    "Living Room - Armchair Candy Wrapper B": ChibiRoboLocationData(61, "Living Room", 0x07, 0, 0x8037de34, 442),
    "Living Room - Armchair Candy Wrapper A": ChibiRoboLocationData(62, "Living Room", 0x07, 15, 0x8037de34, 443),
    "Living Room - Cupholder Candy Wrapper": ChibiRoboLocationData(63, "Living Room", 0x07, 1, 0x8037de34, 444),
    "Living Room - Couch Candy Bag": ChibiRoboLocationData(64, "Living Room", 0x07, 2, 0x8037de34, 445),
    "Living Room - Table Cookie Box A": ChibiRoboLocationData(65, "Living Room", 0x07, 3, 0x8037de34, 446),
    "Living Room - Table Cookie Box B": ChibiRoboLocationData(66, "Living Room", 0x07, 4, 0x8037de34, 447),
    "Kitchen - Mug Location": ChibiRoboLocationData(67, "Kitchen", 0x01, 1, 0x8037ddce, 36),
    "Kitchen - Spoon Location": ChibiRoboLocationData(68, "Kitchen", 0x01, 2, 0x8037ddce, 37),
    "Kitchen - Wastepaper by Foyer Door": ChibiRoboLocationData(69, "Kitchen", 0x01, 3, 0x8037ddce, 152),
    "Kitchen - Wastepaper under Counter": ChibiRoboLocationData(70, "Kitchen", 0x01, 4, 0x8037ddce, 153),
    "Kitchen - Cookie Crumbs by Tao's Bowl": ChibiRoboLocationData(71, "Kitchen", 0x01, 5, 0x8037ddce, 155),
    "Kitchen - Cookie Crumbs by Spoon": ChibiRoboLocationData(72, "Kitchen", 0x01, 6, 0x8037ddce, 156),
    "Kitchen - Cookie Crumbs on Kitchen Table": ChibiRoboLocationData(73, "Kitchen", 0x01, 7, 0x8037ddce, 158),
    "Kitchen - Cookie Crumbs next to Fridge on Counter": ChibiRoboLocationData(74, "Kitchen", 0x01, 8, 0x8037ddcc, 159),
    "Kitchen - Twig A": ChibiRoboLocationData(79, "Kitchen", 0x01, 9, 0x8037ddcc, 206),
    "Kitchen - Twig B": ChibiRoboLocationData(80, "Kitchen", 0x01, 10, 0x8037ddcc, 207),
    "Kitchen - Twig C": ChibiRoboLocationData(81, "Kitchen", 0x01, 11, 0x8037ddcc, 208),
    "Kitchen - Dog Tags Location": ChibiRoboLocationData(82, "Kitchen", 0x01, 12, 0x8037ddcc, 227),
    "Kitchen - Bandage Location": ChibiRoboLocationData(83, "Kitchen", 0x01, 13, 0x8037ddcc, 228),
    "Kitchen - Frog Ring (Table)": ChibiRoboLocationData(84, "Kitchen", 0x01, 14, 0x8037ddcc, 240),
    "Kitchen - Pink Soda Can": ChibiRoboLocationData(85, "Kitchen", 0x01, 15, 0x8037ddcc, 304),
    "Kitchen - Purple Soda Can": ChibiRoboLocationData(86, "Kitchen", 0x01, 0, 0x8037ddcc, 305),
    "Kitchen - Table Candy Wrapper A": ChibiRoboLocationData(87, "Kitchen", 0x01, 1, 0x8037ddcc, 306),
    "Kitchen - Table Candy Wrapper B": ChibiRoboLocationData(88, "Kitchen", 0x01, 2, 0x8037ddcc, 307),
    "Kitchen - Table Candy Bag": ChibiRoboLocationData(89, "Kitchen", 0x01, 3, 0x8037ddcc, 308),
    "Kitchen - Cookie Box by Spoon A": ChibiRoboLocationData(90, "Kitchen", 0x01, 4, 0x8037ddcc, 309),
    "Kitchen - Cookie Box by Spoon B": ChibiRoboLocationData(91, "Kitchen", 0x01, 5, 0x8037ddcc, 310),
    "Sink Drain - Frog Ring": ChibiRoboLocationData(105, "Sink Drain", 0x0a, 1, 0x8037de74, 62),
    "Foyer - Free Rangers Photo": ChibiRoboLocationData(107, "Foyer", 0x02, 9, 0x8037dddc, 336),
    "Foyer - Waterfall Frog Ring": ChibiRoboLocationData(108, "Foyer", 0x02, 10, 0x8037dddc, 382),
    "Foyer - Red Block": ChibiRoboLocationData(109, "Foyer", 0x02, 11, 0x8037dddc, 385),
    "Basement - Giga Battery": ChibiRoboLocationData(110, "Basement", 0x03, 1, 0x8037ddec, 6),
    "Basement - Giga Charger": ChibiRoboLocationData(111, "Basement", 0x03, 2, 0x8037ddec, 121),
    "Basement - Wine Bottle A": ChibiRoboLocationData(112, "Basement", 0x03, 3, 0x8037ddec, 14),
    "Basement - Wine Bottle B": ChibiRoboLocationData(113, "Basement", 0x03, 4, 0x8037ddec, 15),
    "Basement - Wastepaper below Dresser": ChibiRoboLocationData(114, "Basement", 0x03, 5, 0x8037ddec, 56),
    "Basement - Wastepaper below Stairs": ChibiRoboLocationData(115, "Basement", 0x03, 6, 0x8037ddec, 57),
    "Basement - Wastepaper on Stairs": ChibiRoboLocationData(116, "Basement", 0x03, 7, 0x8037ddec, 58),
    "Basement - Wastepaper on Shelf": ChibiRoboLocationData(117, "Basement", 0x03, 8, 0x8037ddf2, 59),
    "Basement - Broken Bottle Bottom": ChibiRoboLocationData(118, "Basement", 0x03, 9, 0x8037ddf2, 98),
    "Basement - Broken Bottle Top": ChibiRoboLocationData(119, "Basement", 0x03, 10, 0x8037ddf2, 99),
    "Basement - Gunpowder": ChibiRoboLocationData(120, "Basement", 0x03, 11, 0x8037ddf2, 144),
    "Basement - Frog Ring": ChibiRoboLocationData(121, "Basement", 0x03, 12, 0x8037ddf2, 151),
    "Basement - Purple Can": ChibiRoboLocationData(122, "Basement", 0x03, 13, 0x8037ddf2, 210),
    "Basement - Cabinet Trash A": ChibiRoboLocationData(123, "Basement", 0x03, 14, 0x8037ddf2, 211),
    "Basement - Trash On Stairs": ChibiRoboLocationData(124, "Basement", 0x03, 15, 0x8037ddf2, 212),
    "Backyard - Twig by Glass Door": ChibiRoboLocationData(131, "Backyard", 0x08, 1, 0x8037de56, 106),
    "Backyard - Twig by Fence": ChibiRoboLocationData(132, "Backyard", 0x08, 2, 0x8037de56, 107),
    "Backyard - Twig under Tree": ChibiRoboLocationData(133, "Backyard", 0x08, 3, 0x8037de56, 108),
    "Backyard - Twig under Awning": ChibiRoboLocationData(134, "Backyard", 0x08, 4, 0x8037de56, 109),
    # "Backyard - Scurvy Splinter": ChibiRoboLocationData(135, "Backyard", 0x08, 5, 0x8037de56, 112),
    # "Backyard - Weeds A": ChibiRoboLocationData(136, "Backyard", 0x08, 6, 0x8037de56, 123),
    # "Backyard - Weeds B": ChibiRoboLocationData(137, "Backyard", 0x08, 7, 0x8037de56, 124),
    # "Backyard - Weeds C": ChibiRoboLocationData(138, "Backyard", 0x08, 8, 0x8037de54, 125),
    "Backyard - Frog Ring": ChibiRoboLocationData(139, "Backyard", 0x08, 5, 0x8037de56, 126),
    "Backyard - White Block": ChibiRoboLocationData(145, "Backyard", 0x08, 6, 0x8037de56, 292),
    "Jenny's Room - AA Battery": ChibiRoboLocationData(146, "Jenny's Room", 0x04, 9, 0x8037de02, 104),
    "Jenny's Room - D Battery": ChibiRoboLocationData(152, "Jenny's Room", 0x04, 10, 0x8037de02, 122),
    "Jenny's Room - C Battery": ChibiRoboLocationData(153, "Jenny's Room", 0x04, 11, 0x8037de02, 124),
    "Jenny's Room - Wastepaper by Trashcan": ChibiRoboLocationData(154, "Jenny's Room", 0x04, 12, 0x8037de02, 153),
    "Jenny's Room - Wastepaper by Piano": ChibiRoboLocationData(155, "Jenny's Room", 0x04, 13, 0x8037de02, 154),
    "Jenny's Room - Wastepaper under Dresser": ChibiRoboLocationData(156, "Jenny's Room", 0x04, 14, 0x8037de02, 155),
    "Jenny's Room - Wastepaper under Bed A": ChibiRoboLocationData(157, "Jenny's Room", 0x04, 15, 0x8037de02, 156),
    "Jenny's Room - Wastepaper under Bed B": ChibiRoboLocationData(158, "Jenny's Room", 0x04, 0, 0x8037de02, 157),
    "Jenny's Room - Wastepaper under Bed C": ChibiRoboLocationData(159, "Jenny's Room", 0x04, 1, 0x8037de02, 158),
    "Jenny's Room - Wastepaper under Bed D": ChibiRoboLocationData(160, "Jenny's Room", 0x04, 2, 0x8037de02, 159),
    "Jenny's Room - Wastepaper by Crayon Box": ChibiRoboLocationData(161, "Jenny's Room", 0x04, 3, 0x8037de02, 161),
    "Jenny's Room - Red Shoe": ChibiRoboLocationData(162, "Jenny's Room", 0x04, 4, 0x8037de02, 181),
    "Jenny's Room - Frog Ring": ChibiRoboLocationData(163, "Jenny's Room", 0x04, 5, 0x8037de02, 226),
    "Jenny's Room - Squirter": ChibiRoboLocationData(164, "Jenny's Room", 0x04, 6, 0x8037de02, 236),
    "Jenny's Room - Snorkel": ChibiRoboLocationData(165, "Jenny's Room", 0x04, 7, 0x8037de02, 263),
    "Jenny's Room - Cookie Crumbs under Bed A": ChibiRoboLocationData(166, "Jenny's Room", 0x04, 8, 0x8037de00, 282),
    "Jenny's Room - Cookie Crumbs under Bed B": ChibiRoboLocationData(167, "Jenny's Room", 0x04, 9, 0x8037de00, 283),
    "Jenny's Room - Cookie Crumbs under Bed C": ChibiRoboLocationData(168, "Jenny's Room", 0x04, 10, 0x8037de00, 284),
    "Jenny's Room - Cookie Crumbs under Bed D": ChibiRoboLocationData(169, "Jenny's Room", 0x04, 11, 0x8037de00, 285),
    "Jenny's Room - Cookie Crumbs by Chair": ChibiRoboLocationData(170, "Jenny's Room", 0x04, 12, 0x8037de00, 286),
    "Jenny's Room - Cookie Crumbs on Desk A": ChibiRoboLocationData(171, "Jenny's Room", 0x04, 13, 0x8037de00, 287),
    "Jenny's Room - Cookie Crumbs B": ChibiRoboLocationData(172, "Jenny's Room", 0x04, 14, 0x8037de00, 288),
    "Jenny's Room - Candy Wrapper below Bed A": ChibiRoboLocationData(173, "Jenny's Room", 0x04, 15, 0x8037de00, 289),
    "Jenny's Room - Candy Wrapper below Bed B": ChibiRoboLocationData(174, "Jenny's Room", 0x04, 0, 0x8037de00, 290),
    "Jenny's Room - Candy Wrapper below Bed C": ChibiRoboLocationData(175, "Jenny's Room", 0x04, 1, 0x8037de00, 291),
    "Jenny's Room - Candy Wrapper on Bed A": ChibiRoboLocationData(176, "Jenny's Room", 0x04, 2, 0x8037de00, 292),
    "Jenny's Room - Candy Wrapper on Bed B": ChibiRoboLocationData(177, "Jenny's Room", 0x04, 3, 0x8037de00, 293),
    "Jenny's Room - Candy Wrapper by TV": ChibiRoboLocationData(178, "Jenny's Room", 0x04, 4, 0x8037de00, 294),
    "Jenny's Room - Candy Wrapper by Crayon Box A": ChibiRoboLocationData(179, "Jenny's Room", 0x04, 5, 0x8037de00, 295),
    "Jenny's Room - Candy Wrapper by Crayon Box B": ChibiRoboLocationData(180, "Jenny's Room", 0x04, 6, 0x8037de00, 296),
    "Jenny's Room - Candy Bag under Bed": ChibiRoboLocationData(181, "Jenny's Room", 0x04, 7, 0x8037de00, 297),
    "Jenny's Room - Candy Bag on Bed": ChibiRoboLocationData(182, "Jenny's Room", 0x04, 8, 0x8037de06, 298),
    "Jenny's Room - Cookie Box under Bed A": ChibiRoboLocationData(183, "Jenny's Room", 0x04, 9, 0x8037de06, 299),
    "Jenny's Room - Cookie Box under Bed B": ChibiRoboLocationData(184, "Jenny's Room", 0x04, 10, 0x8037de06, 300),
    "Jenny's Room - Cookie Box on Desk": ChibiRoboLocationData(185, "Jenny's Room", 0x04, 11, 0x8037de06, 301),
    "Jenny's Room - Orange Can": ChibiRoboLocationData(186, "Jenny's Room", 0x04, 12, 0x8037de06, 302),
    "Jenny's Room - Purple Can": ChibiRoboLocationData(187, "Jenny's Room", 0x04, 13, 0x8037de06, 303),
    "Jenny's Room - Red Crayon": ChibiRoboLocationData(188, "Jenny's Room", 0x04, 14, 0x8037de06, 306),
    "Jenny's Room - Yellow Crayon": ChibiRoboLocationData(189, "Jenny's Room", 0x04, 15, 0x8037de06, 307),
    "Jenny's Room - Green Crayon": ChibiRoboLocationData(190, "Jenny's Room", 0x04, 0, 0x8037de06, 308),
    "Jenny's Room - Purple Crayon": ChibiRoboLocationData(191, "Jenny's Room", 0x04, 1, 0x8037de06, 309),
    "Jenny's Room - Green Block": ChibiRoboLocationData(192, "Jenny's Room", 0x04, 2, 0x8037de06, 364),
    "Bedroom - Dinahs Teeth": ChibiRoboLocationData(198, "Bedroom", 0x06, 9, 0x8037de20, 163),
    "Bedroom - Ticket Stub": ChibiRoboLocationData(200, "Bedroom", 0x06, 10, 0x8037de20, 194),
    "Bedroom - Passed Out Frog": ChibiRoboLocationData(201, "Bedroom", 0x06, 11, 0x8037de20, 213),
    "Bedroom - Wastepaper by Bills B": ChibiRoboLocationData(202, "Bedroom", 0x06, 12, 0x8037de20, 281),
    "Bedroom - Wastepaper by Bills A": ChibiRoboLocationData(203, "Bedroom", 0x06, 13, 0x8037de20, 282),
    "Bedroom - Wastepaper under Bed": ChibiRoboLocationData(204, "Bedroom", 0x06, 14, 0x8037de20, 283),
    "Bedroom - Wastepaper under Vanity": ChibiRoboLocationData(205, "Bedroom", 0x06, 15, 0x8037de20, 284),
    "Bedroom - Wastepaper on Vanity": ChibiRoboLocationData(206, "Bedroom", 0x06, 0, 0x8037de20, 285),
    "Bedroom - Wastepaper on Bed": ChibiRoboLocationData(207, "Bedroom", 0x06, 1, 0x8037de20, 286),
    "Bedroom - Wastepaper by Dinahs Place A": ChibiRoboLocationData(208, "Bedroom", 0x06, 2, 0x8037de20, 287),
    "Bedroom - Wastepaper by Dinahs Place B": ChibiRoboLocationData(209, "Bedroom", 0x06, 3, 0x8037de20, 288),
    "Bedroom - Cookie Crumbs on Toybox": ChibiRoboLocationData(210, "Bedroom", 0x06, 4, 0x8037de20, 289),
    "Bedroom - Vanity Candy Wrapper A": ChibiRoboLocationData(211, "Bedroom", 0x06, 5, 0x8037de20, 290),
    "Bedroom - Vanity Candy Wrapper B": ChibiRoboLocationData(212, "Bedroom", 0x06, 6, 0x8037de20, 291),
    "Bedroom - Shelf Candy Wrapper": ChibiRoboLocationData(213, "Bedroom", 0x06, 7, 0x8037de20, 292),
    "Bedroom - Vanity Candy Bag": ChibiRoboLocationData(214, "Bedroom", 0x06, 8, 0x8037de26, 293),

    "Living Room - Drake Redcrest Suit": ChibiRoboLocationData(215, "Living Room", 0x07, 8, 0x803684b2, 447),
    "Backyard - Frog Suit": ChibiRoboLocationData(216, "Backyard", 0x08, 8, 0x803684b6, 293),
    "Chibi House - Trauma Suit": ChibiRoboLocationData(217, "Chibi House", 0x05, 8, 0x803684be, 448),
    "Chibi House - Ghost Suit": ChibiRoboLocationData(218, "Chibi House", 0x05, 8, 0x803684c2, 448),
    "Foyer - Tao Suit": ChibiRoboLocationData(219, "Foyer", 0x02, 8, 0x803684c6, 448),
    "Bedroom - Pajama Suit": ChibiRoboLocationData(220, "Bedroom", 0x06, 8, 0x803684ba, 448),
}

location_groups = {
    "Living Room": [name for (name, data) in LOCATION_TABLE.items() if data[1] == "Living Room"],
    "Kitchen": [name for (name, data) in LOCATION_TABLE.items() if data[1] == "Kitchen"],
    "Foyer": [name for (name, data) in LOCATION_TABLE.items() if data[1] == "Foyer"],
    "Sink Drain": [name for (name, data) in LOCATION_TABLE.items() if data[1] == "Sink Drain"],
    "Basement": [name for (name, data) in LOCATION_TABLE.items() if data[1] == "Basement"],
    "Backyard": [name for (name, data) in LOCATION_TABLE.items() if data[1] == "Backyard"],
    "Jenny's Room": [name for (name, data) in LOCATION_TABLE.items() if data[1] == "Jenny's Room"],
    "Bedroom": [name for (name, data) in LOCATION_TABLE.items() if data[1] == "Bedroom"],
}
