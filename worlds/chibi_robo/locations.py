from .game_id import game_name
from typing import Dict, List

from enum import Enum, Flag, auto
from typing import TYPE_CHECKING, NamedTuple, Optional

from BaseClasses import Location, Region

class ChibiRobobLocationData(NamedTuple):
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

    def __init__(self, player: int, name: str, parent: Region, data: ChibiRobobLocationData | None = None):
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

LOCATION_TABLE: dict[str, ChibiRobobLocationData] = {
    "Living Room Frog Ring (Behind Window)": ChibiRobobLocationData(0, "Living Room", 0x7, 0x80000000),
    "Living Room Frog Ring (Corkboard)": ChibiRobobLocationData( 1, "Living Room", 0x7, 0x80000000),
    "Living Room Frog Ring (Shelf)": ChibiRobobLocationData( 2, "Living Room", 0x7, 0x80000000 ),
    "Living Room Table 10M Coin": ChibiRobobLocationData(3, "Living Room", 0x7, 0x80000000),
    "Living Room Under Bookshelf 10M Coin": ChibiRobobLocationData( 4, "Living Room", 0x7, 0x80000000),
    "Living Room Under TV 10M Coin": ChibiRobobLocationData( 5, "Living Room", 0x7, 0x80000000),
    "Living Room Bookshelf 10M Coin A": ChibiRobobLocationData( 6, "Living Room", 0x7, 0x80000000),
    "Living Room Bookshelf 10M Coin B": ChibiRobobLocationData(7, "Living Room", 0x7, 0x80000000),
    "Living Room Armchair 10M Coin": ChibiRobobLocationData( 8, "Living Room", 0x7, 0x80000000),
    "Living Room Under Couch 10M Coin": ChibiRobobLocationData(9, "Living Room", 0x7, 0x80000000),
    "Living Room Couch Backseat 10M Coin A": ChibiRobobLocationData(10, "Living Room", 0x7, 0x80000000),
    "Living Room Couch Backseat 10M Coin B": ChibiRobobLocationData(11, "Living Room", 0x7, 0x80000000),
    "Living Room Couch Backseat 10M Coin C": ChibiRobobLocationData(12, "Living Room", 0x7, 0x80000000),
    "Living Room Cupholder 50M Coin": ChibiRobobLocationData(13, "Living Room", 0x7, 0x80000000),
    "Living Room Plant Shelf 50M A": ChibiRobobLocationData(14, "Living Room", 0x7, 0x80000000),
    "Living Room Plant Shelf 50M B": ChibiRobobLocationData(15, "Living Room", 0x7, 0x80000000),
    "Living Room Plant Leaf 50M Coin": ChibiRobobLocationData(16, "Living Room", 0x7, 0x80000000),
    "Living Room Wastepaper by Trashbin B": ChibiRobobLocationData(17, "Living Room", 0x7, 0x80000000),
    "Living Room Candy Wrapper above Trashbin A": ChibiRobobLocationData(18, "Living Room", 0x7, 0x80000000),
    "Living Room Wastepaper by Trashbin A": ChibiRobobLocationData(19, "Living Room", 0x7, 0x80000000),
    "Living Room Cupholder Wastepaper": ChibiRobobLocationData(20, "Living Room", 0x7, 0x80000000),
    "Living Room Cookie Crumbs under Table": ChibiRobobLocationData(21, "Living Room", 0x7, 0x80000000),
    "Living Room Cookie Crumbs by Record Player": ChibiRobobLocationData(22, "Living Room", 0x7, 0x80000000),
    "Living Room Toothbrush": ChibiRobobLocationData(23, "Living Room", 0x7, 0x80000000),
    "Living Room Armchair Happy Block": ChibiRobobLocationData(24, "Living Room", 0x7, 0x80000000),
    "Living Room Bookshelf Happy Block (Lower)": ChibiRobobLocationData(25, "Living Room", 0x7, 0x80000000),
    "Living Room Top of Record Player Shelving Happy Block": ChibiRobobLocationData(26, "Living Room", 0x7, 0x80000000),
    "Living Room Bookshelf Happy Block (Upper)": ChibiRobobLocationData(27, "Living Room", 0x7, 0x80000000),
    "Living Room Plant Shelf Happy Block (Lower)": ChibiRobobLocationData(28, "Living Room", 0x7, 0x80000000),
    "Living Room Grandfather Clock Shelving Happy Block": ChibiRobobLocationData(29, "Living Room", 0x7, 0x80000000),
    "Living Room Happy Block above Chibi-House": ChibiRobobLocationData(30, "Living Room", 0x7, 0x80000000),
    "Living Room Plant Shelf Happy Block (Upper)": ChibiRobobLocationData(31, "Living Room", 0x7, 0x80000000),
    "Living Room Happy Block above Fireplace": ChibiRobobLocationData(32, "Living Room", 0x7, 0x80000000),
    "Living Room Happy Block by Record Player": ChibiRobobLocationData(33, "Living Room", 0x7, 0x80000000),
    "Living Room Wastepaper by Door to Kitchen": ChibiRobobLocationData(34, "Living Room", 0x7, 0x80000000),
    "Living Room Fireplace Wastepaper A": ChibiRobobLocationData(35, "Living Room", 0x7, 0x80000000),
    "Living Room Fireplace Wastepaper B": ChibiRobobLocationData(36, "Living Room", 0x7, 0x80000000),
    "Living Room Wastepaper on Stack of Books": ChibiRobobLocationData(37, "Living Room", 0x7, 0x80000000),
    "Living Room Couch Wastepaper B": ChibiRobobLocationData(38, "Living Room", 0x7, 0x80000000),
    "Living Room Armchair 50M Coin": ChibiRobobLocationData(39, "Living Room", 0x7, 0x80000000),
    "Living Room Lamp 50M Coin": ChibiRobobLocationData(40, "Living Room", 0x7, 0x80000000),
    "Living Room Wastepaper by Toothbrush Spawn": ChibiRobobLocationData(41, "Living Room", 0x7, 0x80000000),
    "Living Room Wastepaper below Cupholder": ChibiRobobLocationData(42, "Living Room", 0x7, 0x80000000),
    "Living Room Couch Wastepaper A": ChibiRobobLocationData(43, "Living Room", 0x7, 0x80000000),
    "Living Room Cookie Crumbs under Couch": ChibiRobobLocationData(44, "Living Room", 0x7, 0x80000000),
    "Living Room Cookie Crumbs on Couch": ChibiRobobLocationData(45, "Living Room", 0x7, 0x80000000),
    "Living Room Twig A": ChibiRobobLocationData( 46, "Living Room", 0x7, 0x80000000),
    "Living Room Twig B": ChibiRobobLocationData( 47, "Living Room", 0x7, 0x80000000),
    "Living Room Twig C": ChibiRobobLocationData(48, "Living Room", 0x7, 0x80000000),
    "Living Room 50M Coin on top of Chibi-House": ChibiRobobLocationData(49, "Living Room", 0x7, 0x80000000),
    "Living Room Couch 10M Coin (Below Left Armrest)": ChibiRobobLocationData(50, "Living Room", 0x7, 0x80000000),
    "Living Room 10M Coin behind Grandfather Clock Shelving C": ChibiRobobLocationData(51, "Living Room", 0x7, 0x80000000),
    "Living Room 10M Coin behind Grandfather Clock Shelving B": ChibiRobobLocationData( 52, "Living Room", 0x7, 0x80000000),
    "Living Room 10M Coin behind Grandfather Clock Shelving A": ChibiRobobLocationData(53, "Living Room", 0x7, 0x80000000),
    "Living Room Wastepaper above Trashbin B": ChibiRobobLocationData(54, "Living Room", 0x7, 0x80000000),
    "Living Room Wastepaper above Trashbin A": ChibiRobobLocationData(55, "Living Room", 0x7, 0x80000000),
    "Living Room Candy Wrapper above Trashbin B": ChibiRobobLocationData(56, "Living Room", 0x7, 0x80000000),
    "Living Room Candy Wrapper by Jenny A": ChibiRobobLocationData(57, "Living Room", 0x7, 0x80000000),
    "Living Room Couch Candy Wrapper": ChibiRobobLocationData(58, "Living Room", 0x7, 0x80000000),
    "Living Room Candy Wrapper by Jenny B": ChibiRobobLocationData(59, "Living Room", 0x7, 0x80000000),
    "Living Room Candy Wrapper on Book Stack": ChibiRobobLocationData(60, "Living Room", 0x7, 0x80000000),
    "Living Room Armchair Candy Wrapper B": ChibiRobobLocationData( 61, "Living Room", 0x7, 0x80000000),
    "Living Room Armchair Candy Wrapper A": ChibiRobobLocationData(62, "Living Room", 0x7, 0x80000000),
    "Living Room Cupholder Candy Wrapper": ChibiRobobLocationData(63, "Living Room", 0x7, 0x80000000),
    "Living Room Couch Candy Bag": ChibiRobobLocationData(64, "Living Room", 0x7, 0x80000000),
    "Living Room Table Cookie Box A": ChibiRobobLocationData(65, "Living Room", 0x7, 0x80000000),
    "Living Room Table Cookie Box B": ChibiRobobLocationData(66, "Living Room", 0x7, 0x80000000),
    "Kitchen Mug Location": ChibiRobobLocationData(67, "Kitchen", 0x1, 0x80000000),
    "Kitchen Spoon Location": ChibiRobobLocationData(68, "Kitchen", 0x1, 0x80000000),
    "Kitchen Wastepaper by Foyer Door": ChibiRobobLocationData(69, "Kitchen", 0x1, 0x80000000 ),
    "Kitchen Wastepaper under Counter": ChibiRobobLocationData(70, "Kitchen", 0x1, 0x80000000),
    "Kitchen Cookie Crumbs by Tao's Bowl": ChibiRobobLocationData(71, "Kitchen", 0x1, 0x80000000),
    "Kitchen Cookie Crumbs by Spoon": ChibiRobobLocationData( 72, "Kitchen", 0x1, 0x80000000),
    "Kitchen Cookie Crumbs on Kitchen Table": ChibiRobobLocationData(73, "Kitchen", 0x1, 0x80000000),
    "Kitchen Cookie Crumbs next to Fridge on Counter": ChibiRobobLocationData(74, "Kitchen", 0x1, 0x80000000),
    "Kitchen Table Happy Block": ChibiRobobLocationData(75, "Kitchen", 0x1, 0x80000000),
    "Kitchen Cabinet Happy Block": ChibiRobobLocationData(76, "Kitchen", 0x1, 0x80000000),
    "Kitchen Happy Block above Bandage": ChibiRobobLocationData( 77, "Kitchen", 0x1, 0x80000000),
    "Kitchen Happy Block by Bridge-Only Chibi-Door": ChibiRobobLocationData(78, "Kitchen", 0x1, 0x80000000),
    "Kitchen Twig A": ChibiRobobLocationData(79, "Kitchen", 0x1, 0x80000000),
    "Kitchen Twig B": ChibiRobobLocationData(80, "Kitchen", 0x1, 0x80000000),
    "Kitchen Twig C": ChibiRobobLocationData(81, "Kitchen", 0x1, 0x80000000),
    "Kitchen Dog Tags Location": ChibiRobobLocationData(82, "Kitchen", 0x1, 0x80000000),
    "Kitchen Bandage Location": ChibiRobobLocationData(83, "Kitchen", 0x1, 0x80000000),
    "Kitchen Frog Ring (Table)": ChibiRobobLocationData( 84, "Kitchen", 0x1, 0x80000000),
    "Kitchen Pink Soda Can": ChibiRobobLocationData(85, "Kitchen", 0x1, 0x80000000),
    "Kitchen Purple Soda Can": ChibiRobobLocationData( 86, "Kitchen", 0x1, 0x80000000),
    "Kitchen Table Candy Wrapper A": ChibiRobobLocationData(87, "Kitchen", 0x1, 0x80000000),
    "Kitchen Table Candy Wrapper B": ChibiRobobLocationData(88, "Kitchen", 0x1, 0x80000000),
    "Kitchen Table Candy Bag": ChibiRobobLocationData(89, "Kitchen", 0x1, 0x80000000),
    "Kitchen Cookie Box by Spoon A": ChibiRobobLocationData(90, "Kitchen", 0x1, 0x80000000),
    "Kitchen Cookie Box by Spoon B": ChibiRobobLocationData(91, "Kitchen", 0x1, 0x80000000),
    "Kitchen High Cupboard 10M Coin": ChibiRobobLocationData(92, "Kitchen", 0x1, 0x80000000),
    "Kitchen 10M Coin by Stove": ChibiRobobLocationData(93, "Kitchen", 0x1, 0x80000000),
    "Kitchen 10M Coin by Sink": ChibiRobobLocationData(94, "Kitchen", 0x1, 0x80000000),
    "Kitchen 10M behind Bottles": ChibiRobobLocationData(95, "Kitchen", 0x1, 0x80000000),
    "Sink Drain Middle Row 100M Coin C": ChibiRobobLocationData(96, "Sink Drain", 0x1, 0x80000000),
    "Sink Drain Middle Row 100M Coin B": ChibiRobobLocationData(97, "Sink Drain", 0x1, 0x80000000),
    "Sink Drain Middle Row 100M Coin A": ChibiRobobLocationData(98, "Sink Drain", 0x1, 0x80000000),
    "Sink Drain Middle Row 10M Coin C": ChibiRobobLocationData(99, "Sink Drain", 0x1, 0x80000000),
    "Sink Drain Middle Row 10M Coin B": ChibiRobobLocationData(100, "Sink Drain", 0x1, 0x80000000),
    "Sink Drain Middle Row 10M Coin A": ChibiRobobLocationData(101, "Sink Drain", 0x1, 0x80000000),
    "Sink Drain Top Row 100M Coin": ChibiRobobLocationData(102, "Sink Drain", 0x1, 0x80000000),
    "Sink Drain Top Row 10M Coin B": ChibiRobobLocationData(103, "Sink Drain", 0x1, 0x80000000),
    "Sink Drain Top Row 10M Coin A": ChibiRobobLocationData( 104, "Sink Drain", 0x1, 0x80000000),
    "Sink Drain Frog Ring": ChibiRobobLocationData( 105, "Sink Drain", 0x1, 0x80000000),
    "Foyer Top of Stairs 10M Coin": ChibiRobobLocationData(106, "Foyer", 0x1, 0x80000000),
    "Foyer Free Rangers Photo": ChibiRobobLocationData( 107, "Foyer", 0x1, 0x80000000),
    "Foyer Waterfall Frog Ring": ChibiRobobLocationData(108, "Foyer", 0x1, 0x80000000),
    "Foyer Red Block": ChibiRobobLocationData(109, "Foyer", 0x1, 0x80000000),
    "Basement Giga-Battery": ChibiRobobLocationData(110, "Basement", 0x1, 0x80000000),
    "Basement Giga-Charger": ChibiRobobLocationData(111, "Basement", 0x1, 0x80000000),
    "Basement Wine Bottle A": ChibiRobobLocationData(112, "Basement", 0x1, 0x80000000),
    "Basement Wine Bottle B": ChibiRobobLocationData(113, "Basement", 0x1, 0x80000000),
    "Basement Wastepaper below Dresser": ChibiRobobLocationData(114, "Basement", 0x1, 0x80000000),
    "Basement Wastepaper below Stairs": ChibiRobobLocationData(115, "Basement", 0x1, 0x80000000),
    "Basement Wastepaper on Stairs": ChibiRobobLocationData(116, "Basement", 0x1, 0x80000000),
    "Basement Wastepaper on Shelf": ChibiRobobLocationData(117, "Basement", 0x1, 0x80000000),
    "Basement Broken Bottle Bottom": ChibiRobobLocationData(118, "Basement", 0x1, 0x80000000),
    "Basement Broken Bottle Top": ChibiRobobLocationData(119, "Basement", 0x1, 0x80000000),
    "Basement Gunpowder": ChibiRobobLocationData(120, "Basement", 0x1, 0x80000000),
    "Basement Frog Ring": ChibiRobobLocationData(121, "Basement", 0x1, 0x80000000),
    "Basement Purple Can": ChibiRobobLocationData(122, "Basement", 0x1, 0x80000000),
    "Basement Cabinet Trash A": ChibiRobobLocationData(123, "Basement", 0x1, 0x80000000),
    "Basement Cabinet Trash B": ChibiRobobLocationData(124, "Basement", 0x1, 0x80000000),
    "Basement Shelf Happy Block B": ChibiRobobLocationData(125, "Basement", 0x1, 0x80000000),
    "Basement Shelf Happy Block A": ChibiRobobLocationData(126, "Basement", 0x1, 0x80000000),
    "Basement Rafters Happy Block B": ChibiRobobLocationData(127, "Basement", 0x1, 0x80000000),
    "Basement Rafters Happy Block A": ChibiRobobLocationData(128, "Basement", 0x1, 0x80000000),
    "Basement Stairs Happy Block": ChibiRobobLocationData(129, "Basement", 0x1, 0x80000000),
    "Basement Swing 10M Coin": ChibiRobobLocationData(130, "Basement", 0x1, 0x80000000),
    "Backyard Twig by Glass Door": ChibiRobobLocationData(131, "Backyard", 0x1, 0x80000000),
    "Backyard Twig by Fence": ChibiRobobLocationData(132, "Backyard", 0x1, 0x80000000),
    "Backyard Twig under Tree": ChibiRobobLocationData(133, "Backyard", 0x1, 0x80000000),
    "Backyard Twig under Awning": ChibiRobobLocationData(134, "Backyard", 0x1, 0x80000000),
    "Backyard Scurvy Splinter": ChibiRobobLocationData(135, "Backyard", 0x1, 0x80000000),
    "Backyard Weeds A": ChibiRobobLocationData(136, "Backyard", 0x1, 0x80000000),
    "Backyard Weeds B": ChibiRobobLocationData(137, "Backyard", 0x1, 0x80000000),
    "Backyard Weeds C": ChibiRobobLocationData(138, "Backyard", 0x1, 0x80000000),
    "Backyard Frog Ring": ChibiRobobLocationData(139, "Backyard", 0x1, 0x80000000),
    "Backyard Right Awning Happy Block C": ChibiRobobLocationData(140, "Backyard", 0x1, 0x80000000),
    "Backyard Right Awning Happy Block B": ChibiRobobLocationData(141, "Backyard", 0x1, 0x80000000),
    "Backyard Left Awning Happy Block": ChibiRobobLocationData(142, "Backyard", 0x1, 0x80000000),
    "Backyard Tree Happy Block": ChibiRobobLocationData(143, "Backyard", 0x1, 0x80000000),
    "Backyard Right Awning Happy Block A": ChibiRobobLocationData(144, "Backyard", 0x1, 0x80000000),
    "Backyard White Block": ChibiRobobLocationData(145, "Backyard", 0x1, 0x80000000),
    "Jenny's Room AA Battery": ChibiRobobLocationData(146, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Happy Block by TV": ChibiRobobLocationData(147, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Happy Block on Train Shelf B": ChibiRobobLocationData(148, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Happy Block on Chair": ChibiRobobLocationData(149, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Happy Block on Bookshelf": ChibiRobobLocationData(150, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Happy Block on Train Shelf A": ChibiRobobLocationData(151, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room D Battery": ChibiRobobLocationData(152, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room C Battery": ChibiRobobLocationData(153, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Wastepaper by Trashcan": ChibiRobobLocationData(154, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Wastepaper by Piano": ChibiRobobLocationData(155, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Wastepaper under Dresser": ChibiRobobLocationData(156, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Wastepaper under Bed A": ChibiRobobLocationData(157, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Wastepaper under Bed B": ChibiRobobLocationData(158, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Wastepaper under Bed C": ChibiRobobLocationData(159, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Wastepaper under Bed D": ChibiRobobLocationData(160, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Wastepaper by Crayon Box": ChibiRobobLocationData(161, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Red Shoe": ChibiRobobLocationData(162, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Frog Ring": ChibiRobobLocationData(163, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Squirter": ChibiRobobLocationData(164, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Snorkel": ChibiRobobLocationData(165, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Cookie Crumbs under Bed A": ChibiRobobLocationData(166, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Cookie Crumbs under Bed B": ChibiRobobLocationData(167, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Cookie Crumbs under Bed C": ChibiRobobLocationData(168, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Cookie Crumbs under Bed D": ChibiRobobLocationData(169, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Cookie Crumbs by Chair": ChibiRobobLocationData(170, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Cookie Crumbs on Desk A": ChibiRobobLocationData(171, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Cookie Crumbs B": ChibiRobobLocationData(172, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Candy Wrapper below Bed A": ChibiRobobLocationData(173, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Candy Wrapper below Bed B": ChibiRobobLocationData(174, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Candy Wrapper below Bed C": ChibiRobobLocationData(175, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Candy Wrapper on Bed A": ChibiRobobLocationData(176, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Candy Wrapper on Bed B": ChibiRobobLocationData(177, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Candy Wrapper by TV": ChibiRobobLocationData(178, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Candy Wrapper by Crayon Box A": ChibiRobobLocationData(179, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Candy Wrapper by Crayon Box B": ChibiRobobLocationData(180, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Candy Bag under Bed": ChibiRobobLocationData(181, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Candy Bag on Bed": ChibiRobobLocationData(182, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Cookie Box under Bed A": ChibiRobobLocationData(183, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Cookie Box under Bed B": ChibiRobobLocationData(184, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Cookie Box on Desk": ChibiRobobLocationData(185, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Orange Can": ChibiRobobLocationData(186, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Purple Can": ChibiRobobLocationData(187, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Red Crayon": ChibiRobobLocationData(188, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Yellow Crayon": ChibiRobobLocationData(189, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Green Crayon": ChibiRobobLocationData(190, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Purple Crayon": ChibiRobobLocationData(191, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Green Block": ChibiRobobLocationData(192, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Stool 10M Coin": ChibiRobobLocationData(193, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Bed Railing 10M Coin B": ChibiRobobLocationData(194, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Bed Railing 10M Coin A": ChibiRobobLocationData(195, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room Slide 10M Coin": ChibiRobobLocationData(196, "Jenny's Room", 0x1, 0x80000000),
    "Jenny's Room 10M Coin under Castle": ChibiRobobLocationData(197, "Jenny's Room", 0x1, 0x80000000),
    "Bedroom Dinahs Teeth": ChibiRobobLocationData(198, "Bedroom", 0x1, 0x80000000),
    "Bedroom Left Leg in Suitcase": ChibiRobobLocationData(199, "Bedroom", 0x1, 0x80000000),
    "Bedroom Ticket Stub": ChibiRobobLocationData(200, "Bedroom", 0x1, 0x80000000),
    "Bedroom Passed-Out Frog": ChibiRobobLocationData(201, "Bedroom", 0x1, 0x80000000),
    "Bedroom Wastepaper by Bills B": ChibiRobobLocationData(202, "Bedroom", 0x1, 0x80000000),
    "Bedroom Wastepaper by Bills A": ChibiRobobLocationData(203, "Bedroom", 0x1, 0x80000000),
    "Bedroom Wastepaper under Bed": ChibiRobobLocationData(204, "Bedroom", 0x1, 0x80000000),
    "Bedroom Wastepaper under Vanity": ChibiRobobLocationData(205, "Bedroom", 0x1, 0x80000000),
    "Bedroom Wastepaper on Vanity": ChibiRobobLocationData(206, "Bedroom", 0x1, 0x80000000),
    "Bedroom Wastepaper on Bed": ChibiRobobLocationData(207, "Bedroom", 0x1, 0x80000000),
    "Bedroom Wastepaper by Dinahs Place A": ChibiRobobLocationData(208, "Bedroom", 0x1, 0x80000000),
    "Bedroom Wastepaper by Dinahs Place B": ChibiRobobLocationData(209, "Bedroom", 0x1, 0x80000000),
    "Bedroom Cookie Crumbs on Toybox": ChibiRobobLocationData(210, "Bedroom", 0x1, 0x80000000),
    "Bedroom Vanity Candy Wrapper A": ChibiRobobLocationData(211, "Bedroom", 0x1, 0x80000000),
    "Bedroom Vanity Candy Wrapper B": ChibiRobobLocationData(212, "Bedroom", 0x1, 0x80000000),
    "Bedroom Shelf Candy Wrapper": ChibiRobobLocationData(213, "Bedroom", 0x1, 0x80000000),
    "Bedroom Vanity Candy Bag": ChibiRobobLocationData(214, "Bedroom", 0x1, 0x80000000),
    "Bedroom Happy Block by Ticket Stub (Lower Shelf)": ChibiRobobLocationData(215, "Bedroom", 0x1, 0x80000000),
    "Bedroom Happy Block by Ticket Stub (Higher Shelf)": ChibiRobobLocationData(216, "Bedroom", 0x1, 0x80000000),
    "Bedroom Vanity Stool 10M Coin": ChibiRobobLocationData(217, "Bedroom", 0x1, 0x80000000),
    "Bedroom 10M Coin by Dinahs Place": ChibiRobobLocationData(218, "Bedroom", 0x1, 0x80000000),
    "Bedroom 10M Coin under Bed": ChibiRobobLocationData(219, "Bedroom", 0x1, 0x80000000),
    "Bedroom 10M Coin on Nightstand": ChibiRobobLocationData(220, "Bedroom", 0x1, 0x80000000),
    "Bedroom 10M Coin on Shelf": ChibiRobobLocationData(221, "Bedroom", 0x1, 0x80000000),
    "Chibi House Pink Flower Seed": ChibiRobobLocationData(222, "Chibi House", 0x1, 0x80000000),
    "Chibi House Blue Flower Seed": ChibiRobobLocationData(223, "Chibi House", 0x1, 0x80000000),
    "Chibi House White Flower Seed": ChibiRobobLocationData(224, "Chibi House", 0x1, 0x80000000),
    "Chibi House Nectar Flower Seed": ChibiRobobLocationData(225, "Chibi House", 0x1, 0x80000000),
    "Chibi House Charge Chip": ChibiRobobLocationData(226, "Chibi House", 0x1, 0x80000000),
    "Chibi House Chibi-Battery": ChibiRobobLocationData(227, "Chibi House", 0x1, 0x80000000),
    "Chibi House Chibi-Blaster": ChibiRobobLocationData(228, "Chibi House", 0x1, 0x80000000),
    "Chibi House Range Chip": ChibiRobobLocationData(229, "Chibi House", 0x1, 0x80000000),
    "Chibi House Chibi-Radar": ChibiRobobLocationData(230, "Chibi House", 0x1, 0x80000000),
    "Chibi House Alien Ear Chip": ChibiRobobLocationData(231, "Chibi House", 0x1, 0x80000000),
    "Chibi House Hot Rod": ChibiRobobLocationData(232, "Chibi House", 0x1, 0x80000000),
    "Chibi House Space Scrambler": ChibiRobobLocationData(233, "Chibi House", 0x1, 0x80000000)
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
