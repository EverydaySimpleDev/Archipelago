from typing import NamedTuple
from BaseClasses import MultiWorld, Region, Entrance
from .options import FFCCGameOptions
from .locations import (FFCCLocation, FFCCLocationData, LOCATION_TABLE, location_groups, MONSTER_LOCATION_TABLE,
                        MOG_STAMP_NESTS, mog_stamp_location, GROOMING_LOCATIONS, GROOMING_LOCATION_TABLE,
                        ENEMY_LOCATION_TABLE, SHOP_LOCATION_TABLE, monster_location, hunt_list, enemy_is_boss)


# The 13 dungeons with a Myrrh tree (Mount Vellenge has none).
MYRRH_DUNGEONS = [
    "River Belle Path", "Goblin Wall", "The Mine of Cathuriges", "The Mushroom Forest",
    "Tida", "Moschet Manor", "Mount Kilanda", "Daemon's Court", "Selepation Cave",
    "Veo Lu Sluice", "Lynari Desert", "Conall Curach", "Rebena Te Ra",
]


# Every dungeon, Mount Vellenge last.
DUNGEON_NAMES = MYRRH_DUNGEONS + ["Mount Vellenge"]


def myrrh_location(dungeon: str) -> str:
    return f"{dungeon} Myrrh"


class FFCCRegionData(NamedTuple):
    locations:    list[str]
    region_exits: list[str]


def create_regions(multiworld: MultiWorld, player: int, options: FFCCGameOptions) -> None:
    dungeon_names = DUNGEON_NAMES

    # Mog Grooming Only: no locations but the grooming checks (not even the
    # year, cycle and Myrrh events, which only the dungeons give)
    grooming_only = bool(options.mog_grooming_only)
    region_data: dict[str, FFCCRegionData] = {
        "Menu": FFCCRegionData([] if grooming_only else location_groups.get("Menu", []),
                               [f"Menu -> {d}" for d in dungeon_names]),
    }
    for name in dungeon_names:
        locs = [] if grooming_only else location_groups.get(name, [])
        if options.monster_hunt_checks or options.mog_grooming_only:
            # enemies (or the Moogle) are the checks instead of chests
            locs = [loc for loc in locs if not LOCATION_TABLE[loc].chest]
        region_data[name] = FFCCRegionData(locs, [f"{name} -> Menu"])

    for name, data in region_data.items():
        region = _create_region(multiworld, player, name, data, options)
        if name in MYRRH_DUNGEONS and not grooming_only:
            # event: this dungeon's Myrrh tree (holds a "Myrrh Drop")
            region.locations.append(FFCCLocation(player, myrrh_location(name), region))
        if options.victory_goal == options.victory_goal.option_mog_stamps:
            # events: the Moogle Nests (each holds a "Mog Stamp"). A dungeon's
            # nest is in its region, a town's in Menu with its town's rule.
            for nest in MOG_STAMP_NESTS:
                if nest == name or (name == "Menu" and nest not in dungeon_names):
                    region.locations.append(FFCCLocation(player, mog_stamp_location(nest), region))
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
        if name == "Menu":
            # Mog grooming checks: Tipa has a Moogle Nest, so they're in Menu
            from .options import grooming_location_kinds
            kinds = grooming_location_kinds(options)
            for loc_name, (_, kind, _) in GROOMING_LOCATIONS.items():
                if kind in kinds:
                    region.locations.append(FFCCLocation(player, loc_name, region,
                                                         GROOMING_LOCATION_TABLE[loc_name]))
        if name == "Menu" and options.shop_checks:
            # shops are in towns, which aren't regions: each slot's rule asks
            # for its town's world-map area (rules.py)
            for loc_name, loc_data in SHOP_LOCATION_TABLE.items():
                region.locations.append(FFCCLocation(player, loc_name, region, loc_data))
        multiworld.regions.append(region)

    connect_entrances(multiworld, player, dungeon_names)


def connect_entrances(multiworld: MultiWorld, player: int,
                      dungeon_names: list[str]) -> None:
    for dungeon in dungeon_names:
        multiworld.get_entrance(f"Menu -> {dungeon}", player).connect(
            multiworld.get_region(dungeon, player)
        )
        multiworld.get_entrance(f"{dungeon} -> Menu", player).connect(
            multiworld.get_region("Menu", player)
        )


def is_check(loc_data: FFCCLocationData, options: FFCCGameOptions) -> bool:
    """False for a "Cycle N Reached" / "Year N Begins" location whose option
    is off: it is then only an event (no location id), so servers and
    trackers don't list it as a check."""
    if not loc_data.is_event:
        return True
    if loc_data.region == "Menu":
        return bool(options.year_location_checks)
    return bool(options.cycle_location_checks)


def _create_region(multiworld: MultiWorld, player: int,
                   name: str, data: FFCCRegionData, options: FFCCGameOptions) -> Region:
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
