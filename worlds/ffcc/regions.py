from typing import Dict, List, Optional, NamedTuple
from BaseClasses import MultiWorld, Region, Entrance
from .locations import (FFCCLocation, LOCATION_TABLE, location_groups, MONSTER_LOCATION_TABLE,
                        ENEMY_LOCATION_TABLE, SHOP_LOCATION_TABLE, monster_location, hunt_list, enemy_is_boss)


# The 13 dungeons with a Myrrh tree (Mount Vellenge has none).
MYRRH_DUNGEONS = [
    "River Belle Path", "Goblin Wall", "The Mine of Cathuriges", "The Mushroom Forest",
    "Tida", "Moschet Manor", "Mount Kilanda", "Daemon's Court", "Selepation Cave",
    "Veo Lu Sluice", "Lynari Desert", "Conall Curach", "Rebena Te Ra",
]


def myrrh_location(dungeon: str) -> str:
    return f"{dungeon} Myrrh"


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
        if options.monster_hunt_checks:
            # enemies are the checks instead of chests
            locs = [loc for loc in locs if not LOCATION_TABLE[loc].chest]
        region_data[name] = FFCCRegionData(locs, [f"{name} -> Menu"])

    for name, data in region_data.items():
        region = _create_region(multiworld, player, name, data, options)
        if name in MYRRH_DUNGEONS:
            # event: this dungeon's Myrrh tree (holds a "Myrrh Drop")
            region.locations.append(FFCCLocation(player, myrrh_location(name), region))
        hunt = options.monster_hunt_checks
        if name == "Menu" and hunt == hunt.option_enemy_types:
            # an enemy type can be found in several dungeons, so its location
            # sits in Menu and its rule asks for any of them (rules.py)
            for enemy in hunt_list(bool(options.monster_hunt_bosses)):
                loc_name = monster_location(enemy)
                region.locations.append(FFCCLocation(player, loc_name, region, MONSTER_LOCATION_TABLE[loc_name]))
        if hunt == hunt.option_every_enemy:
            for loc_name, loc_data in ENEMY_LOCATION_TABLE.items():
                if loc_data.region == name and (options.monster_hunt_bosses or not enemy_is_boss(loc_name)):
                    region.locations.append(FFCCLocation(player, loc_name, region, loc_data))
        if name == "Menu" and options.shop_checks:
            # shops are in towns, which aren't regions: each slot's rule asks
            # for its town's world-map area (rules.py)
            for loc_name, loc_data in SHOP_LOCATION_TABLE.items():
                region.locations.append(FFCCLocation(player, loc_name, region, loc_data))
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


def is_check(loc_data, options) -> bool:
    """False for a "Cycle N Reached" / "Year N Begins" location whose option
    is off: it is then only an event (no location id), so servers and
    trackers don't list it as a check."""
    if not loc_data.is_event:
        return True
    if loc_data.region == "Menu":
        return bool(options.year_location_checks)
    return bool(options.cycle_location_checks)


def _create_region(multiworld: MultiWorld, player: int,
                   name: str, data: FFCCRegionData, options) -> Region:
    region = Region(name, player, multiworld)

    for loc_name in data.locations:
        loc_data = LOCATION_TABLE.get(loc_name)
        if loc_data:
            if is_check(loc_data, options):
                location = FFCCLocation(player, loc_name, region, loc_data)
            else:
                location = FFCCLocation(player, loc_name, region)
            region.locations.append(location)

    for exit_name in data.region_exits:
        entrance = Entrance(player, exit_name, region)
        region.exits.append(entrance)

    return region
