import logging

from BaseClasses import Region, Entrance, ItemClassification, Location, LocationProgressType
from .locations import ChibiRoboLocation, LOCATION_TABLE, ChibiRoboLocationData
from typing import Dict, List, NamedTuple, Optional

from BaseClasses import MultiWorld, Region, Entrance


class ChibiRoboRegionData(NamedTuple):
    locations: List[str]
    region_exits: Optional[List[str]]

def create_regions(multiworld: MultiWorld, player: int, options):
    chibi_robo_regions: Dict[str, ChibiRoboRegionData] = {
        "Menu": ChibiRoboRegionData([], ["Menu - Living Room" ]),
        "Chibi House": ChibiRoboRegionData([], ["Chibi House - Living Room"]),
        "Living Room": ChibiRoboRegionData([], ["Living Room - Kitchen", "Living Room - Foyer", "Living Room - Backyard", "Living Room - Chibi House", "Living Room - Mother Spider"]),
        "Kitchen": ChibiRoboRegionData([], ["Kitchen - Living Room", "Kitchen - Sink Drain", "Kitchen - Foyer" ]),
        "Sink Drain": ChibiRoboRegionData([], ["Sink Drain - Kitchen"]),
        "Backyard": ChibiRoboRegionData([], ["Backyard - Living Room", "Backyard - UFO" ]),
        "Foyer": ChibiRoboRegionData([], ["Foyer - Living Room", "Foyer - Basement", "Foyer - Jenny's Room", "Foyer - Bedroom", "Foyer - Kitchen" ]),
        "Basement": ChibiRoboRegionData([], ["Basement - Foyer" ]),
        "Jenny's Room": ChibiRoboRegionData([], ["Jenny's Room - Foyer"]),
        "Bedroom": ChibiRoboRegionData([], ["Bedroom - Foyer"]),
        "UFO": ChibiRoboRegionData([], ["UFO - Backyard", "UFO - Bedroom - Past"]),
        "Bedroom - Past": ChibiRoboRegionData([], ["Bedroom - Past - UFO"]),
        "Mother Spider": ChibiRoboRegionData([], ["Mother Spider - Living Room", "Mother Spider - Credits"]),
        "Staff Credits": ChibiRoboRegionData([], ["Staff Credits - Living Room"])
    }

    # Living Room - 37 Locations
    chibi_robo_regions["Living Room"].locations.append("Living Room - Frog Ring (Behind Window)")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Frog Ring (Corkboard)")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Frog Ring (Shelf)")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Wastepaper by Trashbin B")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Candy Wrapper above Trashbin A")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Candy Wrapper above Trashbin B")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Wastepaper by Trashbin A")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Cupholder Wastepaper")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Cookie Crumbs under Table")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Cookie Crumbs by Record Player")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Toothbrush")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Wastepaper by Door to Kitchen")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Fireplace Wastepaper A")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Fireplace Wastepaper B")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Wastepaper on Stack of Books")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Couch Wastepaper B")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Wastepaper by Toothbrush Spawn")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Wastepaper below Cupholder")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Couch Wastepaper A")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Cookie Crumbs under Couch")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Cookie Crumbs on Couch")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Twig A")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Twig B")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Twig C")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Wastepaper above Trashbin A")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Wastepaper above Trashbin B")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Candy Wrapper by Jenny A")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Candy Wrapper by Jenny B")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Couch Candy Wrapper")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Candy Wrapper on Book Stack")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Armchair Candy Wrapper A")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Armchair Candy Wrapper B")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Cupholder Candy Wrapper")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Couch Candy Bag")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Table Cookie Box A")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Table Cookie Box B")
    chibi_robo_regions["Living Room"].locations.append("Living Room - Toy receipt on coach")

    chibi_robo_regions["Living Room"].locations.append("Living Room - Drake Redcrest Suit")

    chibi_robo_regions["Chibi House"].locations.append("Chibi House - Trauma Suit")
    chibi_robo_regions["Chibi House"].locations.append("Chibi House - Ghost Suit")

    # Kitchen - 22 Locations
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Mug Location")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Spoon Location")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Wastepaper by Foyer Door")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Wastepaper under Counter")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Cookie Crumbs by Tao's Bowl")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Cookie Crumbs by Spoon")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Cookie Crumbs on Kitchen Table")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Cookie Crumbs next to Fridge on Counter")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Twig A")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Twig B")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Twig C")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Dog Tags Location")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Bandage Location")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Frog Ring (Table)")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Pink Soda Can")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Purple Soda Can")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Table Candy Wrapper A")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Table Candy Wrapper B")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Table Candy Bag")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Cookie Box by Spoon A")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Cookie Box by Spoon B")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Wastepaper on Shelf by Toaster")
    chibi_robo_regions["Kitchen"].locations.append("Kitchen - Cookie Crumbs under Counter")

    # Drain 1 Location
    chibi_robo_regions["Sink Drain"].locations.append("Sink Drain - Frog Ring")

    # Foyer - 19 Locations
    chibi_robo_regions["Foyer"].locations.append("Foyer - Free Rangers Photo")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Waterfall Frog Ring")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Red Block")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Wastepaper On Stairs")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Candy Wrapper by Entrance")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Candy Wrapper by Jenny Photo A")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Candy Wrapper by Jenny Photo B")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Soda Can on Shelf")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Candy Wrapper by Spaceship Shelf A")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Candy Wrapper by Spaceship Shelf B")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Candy Wrapper by Spaceship Shelf C")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Candy Wrapper on Sofa A")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Candy Wrapper on Sofa B")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Candy Wrapper on Floor by Door")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Upstairs Wastepaper by Parents' Door")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Upstairs Wastepaper by stairs")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Upstairs Cookie Crumbs by stairs")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Upstairs Candy Wrapper by Parents' Door")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Upstairs Candy Wrapper by Jenny's Door A")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Upstairs Candy Wrapper by Jenny's Door B")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Candy Wrapper on Sofa C")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Candy Wrapper on Lower Shelf by Entrance")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Candy Wrapper on Stairs")
    chibi_robo_regions["Foyer"].locations.append("Foyer - Upstairs Soda Can")

    chibi_robo_regions["Foyer"].locations.append("Foyer - Tao Suit")

    # Basement - 15 Locations
    chibi_robo_regions["Basement"].locations.append("Basement - Giga Battery")
    chibi_robo_regions["Basement"].locations.append("Basement - Giga Charger")
    chibi_robo_regions["Basement"].locations.append("Basement - Wine Bottle A")
    chibi_robo_regions["Basement"].locations.append("Basement - Wine Bottle B")
    chibi_robo_regions["Basement"].locations.append("Basement - Wastepaper below Dresser")
    chibi_robo_regions["Basement"].locations.append("Basement - Wastepaper below Stairs")
    chibi_robo_regions["Basement"].locations.append("Basement - Wastepaper on Stairs")
    chibi_robo_regions["Basement"].locations.append("Basement - Wastepaper on Shelf")
    chibi_robo_regions["Basement"].locations.append("Basement - Broken Bottle Bottom")
    chibi_robo_regions["Basement"].locations.append("Basement - Broken Bottle Top")
    chibi_robo_regions["Basement"].locations.append("Basement - Gunpowder")
    chibi_robo_regions["Basement"].locations.append("Basement - Frog Ring")
    chibi_robo_regions["Basement"].locations.append("Basement - Purple Can")
    chibi_robo_regions["Basement"].locations.append("Basement - Cabinet Trash A")
    chibi_robo_regions["Basement"].locations.append("Basement - Trash On Stairs")

    # Backyard - 10 Locations
    chibi_robo_regions["Backyard"].locations.append("Backyard - Twig by Glass Door")
    chibi_robo_regions["Backyard"].locations.append("Backyard - Twig by Fence")
    chibi_robo_regions["Backyard"].locations.append("Backyard - Twig under Tree")
    chibi_robo_regions["Backyard"].locations.append("Backyard - Twig under Awning")
    # chibi_robo_regions["Backyard"].locations.append("Backyard - Scurvy Splinter")
    # chibi_robo_regions["Backyard"].locations.append("Backyard - Weeds A")
    # chibi_robo_regions["Backyard"].locations.append("Backyard - Weeds B")
    # chibi_robo_regions["Backyard"].locations.append("Backyard - Weeds C")
    chibi_robo_regions["Backyard"].locations.append("Backyard - Frog Ring")
    chibi_robo_regions["Backyard"].locations.append("Backyard - White Block")

    chibi_robo_regions["Backyard"].locations.append("Backyard - Frog Suit")

    # Jenny's Room - 43 Locations
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - AA Battery")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - D Battery")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - C Battery")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Wastepaper by Trashcan")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Wastepaper by Piano")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Wastepaper under Dresser")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Wastepaper under Bed A")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Wastepaper under Bed B")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Wastepaper under Bed C")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Wastepaper under Bed D")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Wastepaper by Crayon Box")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Red Shoe")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Frog Ring")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Squirter")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Snorkel")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Cookie Crumbs under Bed A")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Cookie Crumbs under Bed B")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Cookie Crumbs under Bed C")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Cookie Crumbs under Bed D")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Cookie Crumbs by Chair")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Cookie Crumbs on Desk A")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Cookie Crumbs B")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Candy Wrapper below Bed A")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Candy Wrapper below Bed B")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Candy Wrapper below Bed C")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Candy Wrapper on Bed A")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Candy Wrapper on Bed B")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Candy Wrapper by TV")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Candy Wrapper by Crayon Box A")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Candy Wrapper by Crayon Box B")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Candy Bag under Bed")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Candy Bag on Bed")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Cookie Box under Bed A")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Cookie Box under Bed B")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Cookie Box on Desk")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Orange Can")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Purple Can")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Red Crayon")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Yellow Crayon")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Green Crayon")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Purple Crayon")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Green Block")
    chibi_robo_regions["Jenny's Room"].locations.append("Jenny's Room - Wastepaper under Bed E")

    # Bedroom - 17 Locations
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Dinahs Teeth")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Ticket Stub")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Passed Out Frog")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Wastepaper by Bills B")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Wastepaper by Bills A")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Wastepaper under Bed")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Wastepaper under Vanity")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Wastepaper on Vanity")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Wastepaper on Bed")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Wastepaper by Dinahs Place A")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Wastepaper by Dinahs Place B")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Cookie Crumbs on Toybox")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Vanity Candy Wrapper A")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Vanity Candy Wrapper B")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Shelf Candy Wrapper")
    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Vanity Candy Bag")

    chibi_robo_regions["Bedroom"].locations.append("Bedroom - Pajama Suit")

    # Set up the regions correctly.
    for name, data in chibi_robo_regions.items():
        multiworld.regions.append(create_region(multiworld, player, name, data))

    connect_entrances(multiworld, player)


def connect_entrances(multiworld: MultiWorld, player: int):

    multiworld.get_entrance("Menu - Living Room", player).connect(multiworld.get_region("Living Room", player))
    multiworld.get_entrance("Chibi House - Living Room", player).connect(multiworld.get_region("Living Room", player))
    multiworld.get_entrance("Kitchen - Living Room", player).connect(multiworld.get_region("Living Room", player))
    multiworld.get_entrance("Backyard - Living Room", player).connect(multiworld.get_region("Living Room", player))
    multiworld.get_entrance("Foyer - Living Room", player).connect(multiworld.get_region("Living Room", player))
    multiworld.get_entrance("Mother Spider - Living Room", player).connect(multiworld.get_region("Living Room", player))

    multiworld.get_entrance("Living Room - Chibi House", player).connect(multiworld.get_region("Chibi House", player))

    multiworld.get_entrance("Living Room - Kitchen", player).connect(multiworld.get_region("Kitchen", player))
    multiworld.get_entrance("Sink Drain - Kitchen", player).connect(multiworld.get_region("Kitchen", player))
    multiworld.get_entrance("Foyer - Kitchen", player).connect(multiworld.get_region("Kitchen", player))

    multiworld.get_entrance("Living Room - Foyer", player).connect(multiworld.get_region("Foyer", player))
    multiworld.get_entrance("Kitchen - Foyer", player).connect(multiworld.get_region("Foyer", player))

    multiworld.get_entrance("Living Room - Backyard", player).connect(multiworld.get_region("Backyard", player))
    multiworld.get_entrance("UFO - Backyard", player).connect(multiworld.get_region("Backyard", player))

    multiworld.get_entrance("Backyard - UFO", player).connect(multiworld.get_region("UFO", player))
    multiworld.get_entrance("Bedroom - Past - UFO", player).connect(multiworld.get_region("UFO", player))

    multiworld.get_entrance("Kitchen - Sink Drain", player).connect(multiworld.get_region("Sink Drain", player))

    multiworld.get_entrance("Foyer - Basement", player).connect(multiworld.get_region("Basement", player))
    multiworld.get_entrance("Foyer - Jenny's Room", player).connect(multiworld.get_region("Jenny's Room", player))
    multiworld.get_entrance("Foyer - Bedroom", player).connect(multiworld.get_region("Bedroom", player))

    multiworld.get_entrance("Basement - Foyer", player).connect(multiworld.get_region("Foyer", player))
    multiworld.get_entrance("Jenny's Room - Foyer", player).connect(multiworld.get_region("Foyer", player))
    multiworld.get_entrance("Bedroom - Foyer", player).connect(multiworld.get_region("Foyer", player))

    multiworld.get_entrance("UFO - Bedroom - Past", player).connect(multiworld.get_region("Bedroom - Past", player))

    multiworld.get_entrance("Living Room - Mother Spider", player).connect(multiworld.get_region("Mother Spider", player))

    multiworld.get_entrance("Mother Spider - Credits", player).connect(multiworld.get_region("Staff Credits", player))

    multiworld.get_entrance("Staff Credits - Living Room", player).connect(multiworld.get_region("Living Room", player))


def create_region(multiworld: MultiWorld, player: int, name: str, data: ChibiRoboRegionData):
    region = Region(name, player, multiworld)

    for loc_name in data.locations:
        loc_data = LOCATION_TABLE[loc_name]
        location = ChibiRoboLocation(player, loc_name, region, loc_data)
        region.locations.append(location)

    for exit in data.region_exits:
        entrance = Entrance(player, exit, region)
        region.exits.append(entrance)

    return region

