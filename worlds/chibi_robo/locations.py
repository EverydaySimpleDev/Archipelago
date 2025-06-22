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
    """

    code: Optional[int]
    region: str
    stage_id: int
    bit: int
    address: Optional[int] = None

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

    "Living Room - Frog Ring (Behind Window)": ChibiRoboLocationData(0, "Living Room", 7, 0x80000000),
    "Living Room - Frog Ring (Corkboard)": ChibiRoboLocationData(1, "Living Room", 7, 0x80000000),
    "Living Room - Frog Ring (Shelf)": ChibiRoboLocationData(2, "Living Room", 7, 0x80000000),
    "Living Room - Table 10M Coin": ChibiRoboLocationData(3, "Living Room", 7, 0x80000000),
    "Living Room - Under Bookshelf 10M Coin": ChibiRoboLocationData(4, "Living Room", 7, 0x80000000),
    "Living Room - Under TV 10M Coin": ChibiRoboLocationData(5, "Living Room", 7, 0x80000000),
    "Living Room - Bookshelf 10M Coin A": ChibiRoboLocationData(6, "Living Room", 7, 0x80000000),
    "Living Room - Bookshelf 10M Coin B": ChibiRoboLocationData(7, "Living Room", 7, 0x80000000),
    "Living Room - Armchair 10M Coin": ChibiRoboLocationData(8, "Living Room", 7, 0x80000000),
    "Living Room - Under Couch 10M Coin": ChibiRoboLocationData(9, "Living Room", 7, 0x80000000),
    "Living Room - Couch Backseat 10M Coin A": ChibiRoboLocationData(10, "Living Room", 7, 0x80000000),
    "Living Room - Couch Backseat 10M Coin B": ChibiRoboLocationData(11, "Living Room", 7, 0x80000000),
    "Living Room - Couch Backseat 10M Coin C": ChibiRoboLocationData(12, "Living Room", 7, 0x80000000),
    "Living Room - Cupholder 50M Coin": ChibiRoboLocationData(13, "Living Room", 7, 0x80000000),
    "Living Room - Plant Shelf 50M A": ChibiRoboLocationData(14, "Living Room", 7, 0x80000000),
    "Living Room - Plant Shelf 50M B": ChibiRoboLocationData(15, "Living Room", 7, 0x80000000),
    "Living Room - Plant Leaf 50M Coin": ChibiRoboLocationData(16, "Living Room", 7, 0x80000000),
    "Living Room - Wastepaper by Trashbin B": ChibiRoboLocationData(17, "Living Room", 7, 0x80000000),
    "Living Room - Candy Wrapper above Trashbin A": ChibiRoboLocationData(18, "Living Room", 7, 0x80000000),
    "Living Room - Wastepaper by Trashbin A": ChibiRoboLocationData(19, "Living Room", 7, 0x80000000),
    "Living Room - Cupholder Wastepaper": ChibiRoboLocationData(20, "Living Room", 7, 0x80000000),
    "Living Room - Cookie Crumbs under Table": ChibiRoboLocationData(21, "Living Room", 7, 0x80000000),
    "Living Room - Cookie Crumbs by Record Player": ChibiRoboLocationData(22, "Living Room", 7, 0x80000000),
    "Living Room - Toothbrush": ChibiRoboLocationData(23, "Living Room", 7, 0x80000000),
    "Living Room - Armchair Happy Block": ChibiRoboLocationData(24, "Living Room", 7, 0x80000000),
    "Living Room - Bookshelf Happy Block (Lower)": ChibiRoboLocationData(25, "Living Room", 7, 0x80000000),
    "Living Room - Top of Record Player Shelving Happy Block": ChibiRoboLocationData(26, "Living Room", 7, 0x80000000),
    "Living Room - Bookshelf Happy Block (Upper)": ChibiRoboLocationData(27, "Living Room", 7, 0x80000000),
    "Living Room - Plant Shelf Happy Block (Lower)": ChibiRoboLocationData(28, "Living Room", 7, 0x80000000),
    "Living Room - Grandfather Clock Shelving Happy Block": ChibiRoboLocationData(29, "Living Room", 7, 0x80000000),
    "Living Room - Happy Block above Chibi House": ChibiRoboLocationData(30, "Living Room", 7, 0x80000000),
    "Living Room - Plant Shelf Happy Block (Upper)": ChibiRoboLocationData(31, "Living Room", 7, 0x80000000),
    "Living Room - Happy Block above Fireplace": ChibiRoboLocationData(32, "Living Room", 7, 0x80000000),
    "Living Room - Happy Block by Record Player": ChibiRoboLocationData(33, "Living Room", 7, 0x80000000),
    "Living Room - Wastepaper by Door to Kitchen": ChibiRoboLocationData(34, "Living Room", 7, 0x80000000),
    "Living Room - Fireplace Wastepaper A": ChibiRoboLocationData(35, "Living Room", 7, 0x80000000),
    "Living Room - Fireplace Wastepaper B": ChibiRoboLocationData(36, "Living Room", 7, 0x80000000),
    "Living Room - Wastepaper on Stack of Books": ChibiRoboLocationData(37, "Living Room", 7, 0x80000000),
    "Living Room - Couch Wastepaper B": ChibiRoboLocationData(38, "Living Room", 7, 0x80000000),
    "Living Room - Armchair 50M Coin": ChibiRoboLocationData(39, "Living Room", 7, 0x80000000),
    "Living Room - Lamp 50M Coin": ChibiRoboLocationData(40, "Living Room", 7, 0x80000000),
    "Living Room - Wastepaper by Toothbrush Spawn": ChibiRoboLocationData(41, "Living Room", 7, 0x80000000),
    "Living Room - Wastepaper below Cupholder": ChibiRoboLocationData(42, "Living Room", 7, 0x80000000),
    "Living Room - Couch Wastepaper A": ChibiRoboLocationData(43, "Living Room", 7, 0x80000000),
    "Living Room - Cookie Crumbs under Couch": ChibiRoboLocationData(44, "Living Room", 7, 0x80000000),
    "Living Room - Cookie Crumbs on Couch": ChibiRoboLocationData(45, "Living Room", 7, 0x80000000),
    "Living Room - Twig A": ChibiRoboLocationData(46, "Living Room", 7, 0x80000000),
    "Living Room - Twig B": ChibiRoboLocationData(47, "Living Room", 7, 0x80000000),
    "Living Room - Twig C": ChibiRoboLocationData(48, "Living Room", 7, 0x80000000),
    "Living Room - 50M Coin on top of Chibi House": ChibiRoboLocationData(49, "Living Room", 7, 0x80000000),
    "Living Room - Couch 10M Coin (Below Left Armrest)": ChibiRoboLocationData(50, "Living Room", 7, 0x80000000),
    "Living Room - 10M Coin behind Grandfather Clock Shelving A": ChibiRoboLocationData(51, "Living Room", 7, 0x80000000),
    "Living Room - 10M Coin behind Grandfather Clock Shelving B": ChibiRoboLocationData(52, "Living Room", 7, 0x80000000),
    "Living Room - 10M Coin behind Grandfather Clock Shelving C": ChibiRoboLocationData(53, "Living Room", 7, 0x80000000),
    "Living Room - Wastepaper above Trashbin A": ChibiRoboLocationData(54, "Living Room", 7, 0x80000000),
    "Living Room - Wastepaper above Trashbin B": ChibiRoboLocationData(55, "Living Room", 7, 0x80000000),
    "Living Room - Candy Wrapper above Trashbin B": ChibiRoboLocationData(56, "Living Room", 7, 0x80000000),
    "Living Room - Candy Wrapper by Jenny A": ChibiRoboLocationData(57, "Living Room", 7, 0x80000000),
    "Living Room - Couch Candy Wrapper": ChibiRoboLocationData(58, "Living Room", 7, 0x80000000),
    "Living Room - Candy Wrapper by Jenny B": ChibiRoboLocationData(59, "Living Room", 7, 0x80000000),
    "Living Room - Candy Wrapper on Book Stack": ChibiRoboLocationData(60, "Living Room", 7, 0x80000000),
    "Living Room - Armchair Candy Wrapper B": ChibiRoboLocationData(61, "Living Room", 7, 0x80000000),
    "Living Room - Armchair Candy Wrapper A": ChibiRoboLocationData(62, "Living Room", 7, 0x80000000),
    "Living Room - Cupholder Candy Wrapper": ChibiRoboLocationData(63, "Living Room", 7, 0x80000000),
    "Living Room - Couch Candy Bag": ChibiRoboLocationData(64, "Living Room", 7, 0x80000000),
    "Living Room - Table Cookie Box A": ChibiRoboLocationData(65, "Living Room", 7, 0x80000000),
    "Living Room - Table Cookie Box B": ChibiRoboLocationData(66, "Living Room", 7, 0x80000000),
    "Kitchen - Mug Location": ChibiRoboLocationData(67, "Kitchen", 1, 0x80000000),
    "Kitchen - Spoon Location": ChibiRoboLocationData(68, "Kitchen", 1, 0x80000000),
    "Kitchen - Wastepaper by Foyer Door": ChibiRoboLocationData(69, "Kitchen", 1, 0x80000000),
    "Kitchen - Wastepaper under Counter": ChibiRoboLocationData(70, "Kitchen", 1, 0x80000000),
    "Kitchen - Cookie Crumbs by Tao's Bowl": ChibiRoboLocationData(71, "Kitchen", 1, 0x80000000),
    "Kitchen - Cookie Crumbs by Spoon": ChibiRoboLocationData(72, "Kitchen", 1, 0x80000000),
    "Kitchen - Cookie Crumbs on Kitchen Table": ChibiRoboLocationData(73, "Kitchen", 1, 0x80000000),
    "Kitchen - Cookie Crumbs next to Fridge on Counter": ChibiRoboLocationData(74, "Kitchen", 1, 0x80000000),
    "Kitchen - Table Happy Block": ChibiRoboLocationData(75, "Kitchen", 1, 0x80000000),
    "Kitchen - Cabinet Happy Block": ChibiRoboLocationData(76, "Kitchen", 1, 0x80000000),
    "Kitchen - Happy Block above Bandage": ChibiRoboLocationData(77, "Kitchen", 1, 0x80000000),
    "Kitchen - Happy Block by Bridge Only Chibi Door": ChibiRoboLocationData(78, "Kitchen", 1, 0x80000000),
    "Kitchen - Twig A": ChibiRoboLocationData(79, "Kitchen", 1, 0x80000000),
    "Kitchen - Twig B": ChibiRoboLocationData(80, "Kitchen", 1, 0x80000000),
    "Kitchen - Twig C": ChibiRoboLocationData(81, "Kitchen", 1, 0x80000000),
    "Kitchen - Dog Tags Location": ChibiRoboLocationData(82, "Kitchen", 1, 0x80000000),
    "Kitchen - Bandage Location": ChibiRoboLocationData(83, "Kitchen", 1, 0x80000000),
    "Kitchen - Frog Ring (Table)": ChibiRoboLocationData(84, "Kitchen", 1, 0x80000000),
    "Kitchen - Pink Soda Can": ChibiRoboLocationData(85, "Kitchen", 1, 0x80000000),
    "Kitchen - Purple Soda Can": ChibiRoboLocationData(86, "Kitchen", 1, 0x80000000),
    "Kitchen - Table Candy Wrapper A": ChibiRoboLocationData(87, "Kitchen", 1, 0x80000000),
    "Kitchen - Table Candy Wrapper B": ChibiRoboLocationData(88, "Kitchen", 1, 0x80000000),
    "Kitchen - Table Candy Bag": ChibiRoboLocationData(89, "Kitchen", 1, 0x80000000),
    "Kitchen - Cookie Box by Spoon A": ChibiRoboLocationData(90, "Kitchen", 1, 0x80000000),
    "Kitchen - Cookie Box by Spoon B": ChibiRoboLocationData(91, "Kitchen", 1, 0x80000000),
    "Kitchen - High Cupboard 10M Coin": ChibiRoboLocationData(92, "Kitchen", 1, 0x80000000),
    "Kitchen - 10M Coin by Stove": ChibiRoboLocationData(93, "Kitchen", 1, 0x80000000),
    "Kitchen - 10M Coin by Sink": ChibiRoboLocationData(94, "Kitchen", 1, 0x80000000),
    "Kitchen - 10M behind Bottles": ChibiRoboLocationData(95, "Kitchen", 1, 0x80000000),
    "Sink Drain - Middle Row 100M Coin C": ChibiRoboLocationData(96, "Sink Drain", 11, 0x80000000),
    "Sink Drain - Middle Row 100M Coin B": ChibiRoboLocationData(97, "Sink Drain", 11, 0x80000000),
    "Sink Drain - Middle Row 100M Coin A": ChibiRoboLocationData(98, "Sink Drain", 11, 0x80000000),
    "Sink Drain - Middle Row 10M Coin C": ChibiRoboLocationData(99, "Sink Drain", 11, 0x80000000),
    "Sink Drain - Middle Row 10M Coin B": ChibiRoboLocationData(100, "Sink Drain", 11, 0x80000000),
    "Sink Drain - Middle Row 10M Coin A": ChibiRoboLocationData(101, "Sink Drain", 11, 0x80000000),
    "Sink Drain - Top Row 100M Coin": ChibiRoboLocationData(102, "Sink Drain", 11, 0x80000000),
    "Sink Drain - Top Row 10M Coin B": ChibiRoboLocationData(103, "Sink Drain", 11, 0x80000000),
    "Sink Drain - Top Row 10M Coin A": ChibiRoboLocationData(104, "Sink Drain", 11, 0x80000000),
    "Sink Drain - Frog Ring": ChibiRoboLocationData(105, "Sink Drain", 11, 0x80000000),
    "Foyer - Top of Stairs 10M Coin": ChibiRoboLocationData(106, "Foyer", 2, 0x80000000),
    "Foyer - Free Rangers Photo": ChibiRoboLocationData(107, "Foyer", 2, 0x80000000),
    "Foyer - Waterfall Frog Ring": ChibiRoboLocationData(108, "Foyer", 2, 0x80000000),
    "Foyer - Red Block": ChibiRoboLocationData(109, "Foyer", 2, 0x80000000),
    "Basement - Giga Battery": ChibiRoboLocationData(110, "Basement", 3, 0x80000000),
    "Basement - Giga Charger": ChibiRoboLocationData(111, "Basement", 3, 0x80000000),
    "Basement - Wine Bottle A": ChibiRoboLocationData(112, "Basement", 3, 0x80000000),
    "Basement - Wine Bottle B": ChibiRoboLocationData(113, "Basement", 3, 0x80000000),
    "Basement - Wastepaper below Dresser": ChibiRoboLocationData(114, "Basement", 3, 0x80000000),
    "Basement - Wastepaper below Stairs": ChibiRoboLocationData(115, "Basement", 3, 0x80000000),
    "Basement - Wastepaper on Stairs": ChibiRoboLocationData(116, "Basement", 3, 0x80000000),
    "Basement - Wastepaper on Shelf": ChibiRoboLocationData(117, "Basement", 3, 0x80000000),
    "Basement - Broken Bottle Bottom": ChibiRoboLocationData(118, "Basement", 3, 0x80000000),
    "Basement - Broken Bottle Top": ChibiRoboLocationData(119, "Basement", 3, 0x80000000),
    "Basement - Gunpowder": ChibiRoboLocationData(120, "Basement", 3, 0x80000000),
    "Basement - Frog Ring": ChibiRoboLocationData(121, "Basement", 3, 0x80000000),
    "Basement - Purple Can": ChibiRoboLocationData(122, "Basement", 3, 0x80000000),
    "Basement - Cabinet Trash A": ChibiRoboLocationData(123, "Basement", 3, 0x80000000),
    "Basement - Cabinet Trash B": ChibiRoboLocationData(124, "Basement", 3, 0x80000000),
    "Basement - Shelf Happy Block B": ChibiRoboLocationData(125, "Basement", 3, 0x80000000),
    "Basement - Shelf Happy Block A": ChibiRoboLocationData(126, "Basement", 3, 0x80000000),
    "Basement - Rafters Happy Block B": ChibiRoboLocationData(127, "Basement", 3, 0x80000000),
    "Basement - Rafters Happy Block A": ChibiRoboLocationData(128, "Basement", 3, 0x80000000),
    "Basement - Stairs Happy Block": ChibiRoboLocationData(129, "Basement", 3, 0x80000000),
    "Basement - Swing 10M Coin": ChibiRoboLocationData(130, "Basement", 3, 0x80000000),
    "Backyard - Twig by Glass Door": ChibiRoboLocationData(131, "Backyard", 9, 0x80000000),
    "Backyard - Twig by Fence": ChibiRoboLocationData(132, "Backyard", 9, 0x80000000),
    "Backyard - Twig under Tree": ChibiRoboLocationData(133, "Backyard", 9, 0x80000000),
    "Backyard - Twig under Awning": ChibiRoboLocationData(134, "Backyard", 9, 0x80000000),
    "Backyard - Scurvy Splinter": ChibiRoboLocationData(135, "Backyard", 9, 0x80000000),
    "Backyard - Weeds A": ChibiRoboLocationData(136, "Backyard", 9, 0x80000000),
    "Backyard - Weeds B": ChibiRoboLocationData(137, "Backyard", 9, 0x80000000),
    "Backyard - Weeds C": ChibiRoboLocationData(138, "Backyard", 9, 0x80000000),
    "Backyard - Frog Ring": ChibiRoboLocationData(139, "Backyard", 9, 0x80000000),
    "Backyard - Right Awning Happy Block C": ChibiRoboLocationData(140, "Backyard", 9, 0x80000000),
    "Backyard - Right Awning Happy Block B": ChibiRoboLocationData(141, "Backyard", 9, 0x80000000),
    "Backyard - Left Awning Happy Block": ChibiRoboLocationData(142, "Backyard", 9, 0x80000000),
    "Backyard - Tree Happy Block": ChibiRoboLocationData(143, "Backyard", 9, 0x80000000),
    "Backyard - Right Awning Happy Block A": ChibiRoboLocationData(144, "Backyard", 9, 0x80000000),
    "Backyard - White Block": ChibiRoboLocationData(145, "Backyard", 9, 0x80000000),
    "Jenny's Room - AA Battery": ChibiRoboLocationData(146, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Happy Block by TV": ChibiRoboLocationData(147, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Happy Block on Train Shelf B": ChibiRoboLocationData(148, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Happy Block on Chair": ChibiRoboLocationData(149, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Happy Block on Bookshelf": ChibiRoboLocationData(150, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Happy Block on Train Shelf A": ChibiRoboLocationData(151, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - D Battery": ChibiRoboLocationData(152, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - C Battery": ChibiRoboLocationData(153, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Wastepaper by Trashcan": ChibiRoboLocationData(154, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Wastepaper by Piano": ChibiRoboLocationData(155, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Wastepaper under Dresser": ChibiRoboLocationData(156, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Wastepaper under Bed A": ChibiRoboLocationData(157, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Wastepaper under Bed B": ChibiRoboLocationData(158, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Wastepaper under Bed C": ChibiRoboLocationData(159, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Wastepaper under Bed D": ChibiRoboLocationData(160, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Wastepaper by Crayon Box": ChibiRoboLocationData(161, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Red Shoe": ChibiRoboLocationData(162, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Frog Ring": ChibiRoboLocationData(163, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Squirter": ChibiRoboLocationData(164, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Snorkel": ChibiRoboLocationData(165, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Cookie Crumbs under Bed A": ChibiRoboLocationData(166, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Cookie Crumbs under Bed B": ChibiRoboLocationData(167, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Cookie Crumbs under Bed C": ChibiRoboLocationData(168, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Cookie Crumbs under Bed D": ChibiRoboLocationData(169, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Cookie Crumbs by Chair": ChibiRoboLocationData(170, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Cookie Crumbs on Desk A": ChibiRoboLocationData(171, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Cookie Crumbs B": ChibiRoboLocationData(172, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Candy Wrapper below Bed A": ChibiRoboLocationData(173, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Candy Wrapper below Bed B": ChibiRoboLocationData(174, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Candy Wrapper below Bed C": ChibiRoboLocationData(175, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Candy Wrapper on Bed A": ChibiRoboLocationData(176, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Candy Wrapper on Bed B": ChibiRoboLocationData(177, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Candy Wrapper by TV": ChibiRoboLocationData(178, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Candy Wrapper by Crayon Box A": ChibiRoboLocationData(179, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Candy Wrapper by Crayon Box B": ChibiRoboLocationData(180, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Candy Bag under Bed": ChibiRoboLocationData(181, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Candy Bag on Bed": ChibiRoboLocationData(182, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Cookie Box under Bed A": ChibiRoboLocationData(183, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Cookie Box under Bed B": ChibiRoboLocationData(184, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Cookie Box on Desk": ChibiRoboLocationData(185, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Orange Can": ChibiRoboLocationData(186, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Purple Can": ChibiRoboLocationData(187, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Red Crayon": ChibiRoboLocationData(188, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Yellow Crayon": ChibiRoboLocationData(189, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Green Crayon": ChibiRoboLocationData(190, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Purple Crayon": ChibiRoboLocationData(191, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Green Block": ChibiRoboLocationData(192, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Stool 10M Coin": ChibiRoboLocationData(193, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Bed Railing 10M Coin B": ChibiRoboLocationData(194, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Bed Railing 10M Coin A": ChibiRoboLocationData(195, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - Slide 10M Coin": ChibiRoboLocationData(196, "Jenny's Room", 4, 0x80000000),
    "Jenny's Room - 10M Coin under Castle": ChibiRoboLocationData(197, "Jenny's Room", 4, 0x80000000),
    "Bedroom - Dinahs Teeth": ChibiRoboLocationData(198, "Bedroom", 6, 0x80000000),
    "Bedroom - Left Leg in Suitcase": ChibiRoboLocationData(199, "Bedroom", 6, 0x80000000),
    "Bedroom - Ticket Stub": ChibiRoboLocationData(200, "Bedroom", 6, 0x80000000),
    "Bedroom - Passed Out Frog": ChibiRoboLocationData(201, "Bedroom", 6, 0x80000000),
    "Bedroom - Wastepaper by Bills B": ChibiRoboLocationData(202, "Bedroom", 6, 0x80000000),
    "Bedroom - Wastepaper by Bills A": ChibiRoboLocationData(203, "Bedroom", 6, 0x80000000),
    "Bedroom - Wastepaper under Bed": ChibiRoboLocationData(204, "Bedroom", 6, 0x80000000),
    "Bedroom - Wastepaper under Vanity": ChibiRoboLocationData(205, "Bedroom", 6, 0x80000000),
    "Bedroom - Wastepaper on Vanity": ChibiRoboLocationData(206, "Bedroom", 6, 0x80000000),
    "Bedroom - Wastepaper on Bed": ChibiRoboLocationData(207, "Bedroom", 6, 0x80000000),
    "Bedroom - Wastepaper by Dinahs Place A": ChibiRoboLocationData(208, "Bedroom", 6, 0x80000000),
    "Bedroom - Wastepaper by Dinahs Place B": ChibiRoboLocationData(209, "Bedroom", 6, 0x80000000),
    "Bedroom - Cookie Crumbs on Toybox": ChibiRoboLocationData(210, "Bedroom", 6, 0x80000000),
    "Bedroom - Vanity Candy Wrapper A": ChibiRoboLocationData(211, "Bedroom", 6, 0x80000000),
    "Bedroom - Vanity Candy Wrapper B": ChibiRoboLocationData(212, "Bedroom", 6, 0x80000000),
    "Bedroom - Shelf Candy Wrapper": ChibiRoboLocationData(213, "Bedroom", 6, 0x80000000),
    "Bedroom - Vanity Candy Bag": ChibiRoboLocationData(214, "Bedroom", 6, 0x80000000),
    "Bedroom - Happy Block by Ticket Stub (Lower Shelf)": ChibiRoboLocationData(215, "Bedroom", 6, 0x80000000),
    "Bedroom - Happy Block by Ticket Stub (Higher Shelf)": ChibiRoboLocationData(216, "Bedroom", 6, 0x80000000),
    "Bedroom - Vanity Stool 10M Coin": ChibiRoboLocationData(217, "Bedroom", 6, 0x80000000),
    "Bedroom - 10M Coin by Dinahs Place": ChibiRoboLocationData(218, "Bedroom", 6, 0x80000000),
    "Bedroom - 10M Coin under Bed": ChibiRoboLocationData(219, "Bedroom", 6, 0x80000000),
    "Bedroom - 10M Coin on Nightstand": ChibiRoboLocationData(220, "Bedroom", 6, 0x80000000),
    "Bedroom - 10M Coin on Shelf": ChibiRoboLocationData(221, "Bedroom", 6, 0x80000000),
    "Chibi House - Pink Flower Seed": ChibiRoboLocationData(222, "Chibi House", 5, 0x80000000),
    "Chibi House - Blue Flower Seed": ChibiRoboLocationData(223, "Chibi House", 5, 0x80000000),
    "Chibi House - White Flower Seed": ChibiRoboLocationData(224, "Chibi House", 5, 0x80000000),
    "Chibi House - Nectar Flower Seed": ChibiRoboLocationData(225, "Chibi House", 5, 0x80000000),
    "Chibi House - Charge Chip": ChibiRoboLocationData(226, "Chibi House", 5, 0x80000000),
    "Chibi House - Chibi Battery": ChibiRoboLocationData(227, "Chibi House", 5, 0x80000000),
    "Chibi House - Chibi Blaster": ChibiRoboLocationData(228, "Chibi House", 5, 0x80000000),
    "Chibi House - Range Chip": ChibiRoboLocationData(229, "Chibi House", 5, 0x80000000),
    "Chibi House - Chibi Radar": ChibiRoboLocationData(230, "Chibi House", 5, 0x80000000),
    "Chibi House - Alien Ear Chip": ChibiRoboLocationData(231, "Chibi House", 5, 0x80000000),
    "Chibi House - Hot Rod": ChibiRoboLocationData(232, "Chibi House", 5, 0x80000000),
    "Chibi House - Space Scrambler": ChibiRoboLocationData(233, "Chibi House", 5, 0x80000000)
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
    "Chibi House": [name for (name, data) in LOCATION_TABLE.items() if data[1] == "Chibi House"]
}
