from BaseClasses import Region, Entrance, ItemClassification, Location, LocationProgressType
from .locations import ChibiRoboLocation, LOCATION_TABLE, ChibiRobobLocationData
from typing import Dict, List, NamedTuple, Optional

from BaseClasses import MultiWorld, Region, Entrance


class ChibiRoboRegionData(NamedTuple):
    locations: List[str]
    region_exits: Optional[List[str]]

def create_regions(multiworld: MultiWorld, player: int, options):
    regions: Dict[str, ChibiRoboRegionData] = {
        "Menu": ChibiRoboRegionData([], ["Menu - Living Room" ]),
        "Living Room": ChibiRoboRegionData([], ["Living Room - Kitchen", "Living Room - Foyer", "Living Room - Backyard", "Living Room - Chibi House"]),
        "Chibi House": ChibiRoboRegionData([], ["Chibi House - Living Room" ]),
        "Kitchen": ChibiRoboRegionData([], ["Kitchen - Living Room", "Kitchen - Sink Drain", "Kitchen - Foyer" ]),
        "Sink Drain": ChibiRoboRegionData([], ["Sink Drain - Kitchen"]),
        "Backyard": ChibiRoboRegionData([], ["Backyard - Living Room", "UFO" ]),
        "Foyer": ChibiRoboRegionData([], ["Foyer - Living Room", "Foyer - Basement", "Foyer - Jenny's Room", "Foyer - Bedroom", "Foyer - Kitchen" ]),
        "Basement": ChibiRoboRegionData([], ["Basement - Foyer" ]),
        "Jenny's Room": ChibiRoboRegionData([], ["Jenny's Room - Foyer"]),
        "Bedroom": ChibiRoboRegionData([], ["Bedroom - Foyer"]),
        "UFO": ChibiRoboRegionData([], ["UFO - Backyard", "UFO - Bedroom - Past"]),
        "Bedroom - Past": ChibiRoboRegionData([], ["Bedroom - Past - UFO"]),
        "Mother Spider": ChibiRoboRegionData([], ["Mother Spider - Living Room"]),
    }

    # Set up the regions correctly.
    for name, data in regions.items():
        multiworld.regions.append(create_region(multiworld, player, name, data))

def connect_entrances(multiworld: MultiWorld, player: int):
    multiworld.get_entrance("Menu - Living Room", player).connect(multiworld.get_region("Menu", player))
    multiworld.get_entrance("Living Room - Kitchen", player).connect(multiworld.get_region("Living Room", player))
    multiworld.get_entrance("Living Room - Foyer", player).connect(multiworld.get_region("Living Room", player))
    multiworld.get_entrance("Living Room - Backyard", player).connect(multiworld.get_region("Living Room", player))
    multiworld.get_entrance("Living Room - Chibi House", player).connect(multiworld.get_region("Living Room", player))
    multiworld.get_entrance("Chibi House - Living Room", player).connect(multiworld.get_region("Chibi House", player))
    multiworld.get_entrance("Kitchen - Living Room", player).connect(multiworld.get_region("Kitchen", player))
    multiworld.get_entrance("Kitchen - Foyer", player).connect(multiworld.get_region("Kitchen", player))
    multiworld.get_entrance("Kitchen - Sink Drain", player).connect(multiworld.get_region("Kitchen", player))
    multiworld.get_entrance("Sink Drain - Kitchen", player).connect(multiworld.get_region("Sink Drain", player))
    multiworld.get_entrance("Backyard - Living Room", player).connect(multiworld.get_region("Backyard", player))
    multiworld.get_entrance("UFO", player).connect(multiworld.get_region("Backyard", player))
    multiworld.get_entrance("Foyer - Living Room", player).connect(multiworld.get_region("Foyer", player))
    multiworld.get_entrance("Foyer - Basement", player).connect(multiworld.get_region("Foyer", player))
    multiworld.get_entrance("Foyer - Jenny's Room", player).connect(multiworld.get_region("Foyer", player))
    multiworld.get_entrance("Foyer - Bedroom", player).connect(multiworld.get_region("Foyer", player))
    multiworld.get_entrance("Foyer - Kitchen", player).connect(multiworld.get_region("Foyer", player))
    multiworld.get_entrance("Basement - Foyer", player).connect(multiworld.get_region("Basement", player))
    multiworld.get_entrance("Jenny's Room - Foyer", player).connect(multiworld.get_region("Jenny's Room", player))
    multiworld.get_entrance("Bedroom - Foyer", player).connect(multiworld.get_region("Bedroom", player))
    multiworld.get_entrance("UFO - Backyard", player).connect(multiworld.get_region("UFO", player))
    multiworld.get_entrance("UFO - Bedroom - Past", player).connect(multiworld.get_region("UFO", player))
    multiworld.get_entrance("Bedroom - Past - UFO", player).connect(multiworld.get_region("Bedroom - Past", player))
    multiworld.get_entrance("Mother Spider - Living Room", player).connect(multiworld.get_region("Mother Spider", player))

def create_region(multiworld: MultiWorld, player: int, name: str, data: ChibiRoboRegionData):
    region = Region(name, player, multiworld)
    if data.locations:
        for loc_name in data.locations:
            loc_data = LOCATION_TABLE.get(loc_name)
            location = ChibiRoboLocation(player, loc_name, region, ChibiRobobLocationData( 999, "Unknown", 0x7, 0x80000000))
            region.locations.append(location)

    if data.region_exits:
        for exit in data.region_exits:
            entrance = Entrance(player, exit, region)
            region.exits.append(entrance)

    return region

