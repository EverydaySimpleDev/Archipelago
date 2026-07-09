from typing import Dict, List, Optional, NamedTuple
from BaseClasses import MultiWorld, Region, Entrance
from .locations import FFCCLocation, LOCATION_TABLE, location_groups


class FFCCRegionData(NamedTuple):
    locations:    List[str]
    region_exits: List[str]


def create_regions(multiworld: MultiWorld, player: int, options) -> None:
    dungeon_names = [
        "River Belle Path", "Goblin Wall", "The Mine of Cathuriges",
        "The Mushroom Forest", "Tida", "Moschet Manor", "Mount Kilanda",
        "Daemon's Court", "Selepation Cave", "Veo Lu Sluice", "Lynari Desert",
        "Conall Curach", "Rebena Te Ra", "Mount Vellenge",
    ]

    region_data: Dict[str, FFCCRegionData] = {
        "Menu": FFCCRegionData(location_groups.get("Menu", []), [f"Menu -> {d}" for d in dungeon_names]),
    }
    for name in dungeon_names:
        locs = location_groups.get(name, [])
        region_data[name] = FFCCRegionData(locs, [f"{name} -> Menu"])

    for name, data in region_data.items():
        region = _create_region(multiworld, player, name, data)
        multiworld.regions.append(region)

    connect_entrances(multiworld, player, dungeon_names)


def connect_entrances(multiworld: MultiWorld, player: int,
                      dungeon_names: List[str]) -> None:
    for dungeon in dungeon_names:
        multiworld.get_entrance(f"Menu -> {dungeon}", player).connect(
            multiworld.get_region(dungeon, player)
        )
        multiworld.get_entrance(f"{dungeon} -> Menu", player).connect(
            multiworld.get_region("Menu", player)
        )


def _create_region(multiworld: MultiWorld, player: int,
                   name: str, data: FFCCRegionData) -> Region:
    region = Region(name, player, multiworld)

    for loc_name in data.locations:
        loc_data = LOCATION_TABLE.get(loc_name)
        if loc_data:
            location = FFCCLocation(player, loc_name, region, loc_data)
            region.locations.append(location)

    for exit_name in data.region_exits:
        entrance = Entrance(player, exit_name, region)
        region.exits.append(entrance)

    return region
