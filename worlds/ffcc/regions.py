import logging

from BaseClasses import Region, Entrance, ItemClassification, Location, LocationProgressType
from .locations import FFCCLocation, LOCATION_TABLE, FFCCLocationData
from typing import Dict, List, NamedTuple, Optional

from BaseClasses import MultiWorld, Region, Entrance


class ChibiRoboRegionData(NamedTuple):
    locations: List[str]
    region_exits: Optional[List[str]]

def create_regions(multiworld: MultiWorld, player: int, options):
    FFCC_regions: Dict[str, ChibiRoboRegionData] = {
        "Menu": ChibiRoboRegionData([], ["Menu - Living Room" ]),
    }

    FFCC_regions["Living Room"].locations.append("Living Room - Frog Ring (Behind Window)")

    # Set up the regions correctly.
    for name, data in FFCC_regions.items():
        multiworld.regions.append(create_region(multiworld, player, name, data))

    connect_entrances(multiworld, player)


def connect_entrances(multiworld: MultiWorld, player: int):

    multiworld.get_entrance("Menu - Living Room", player).connect(multiworld.get_region("Living Room", player))



def create_region(multiworld: MultiWorld, player: int, name: str, data: ChibiRoboRegionData):
    region = Region(name, player, multiworld)

    for loc_name in data.locations:
        loc_data = LOCATION_TABLE[loc_name]
        location = FFCCLocation(player, loc_name, region, loc_data)
        region.locations.append(location)

    for exit in data.region_exits:
        entrance = Entrance(player, exit, region)
        region.exits.append(entrance)

    return region

