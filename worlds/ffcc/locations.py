from typing import NamedTuple, Optional, Tuple
from BaseClasses import Location, Region
from .game_id import game_name

class FFCCLocationData(NamedTuple):
    code:        int           # AP code (AP id = get_apid(code)), fixed in chest_table.py
    region:      str           # dungeon name (must match regions.py), "Menu" for the Year locations
    cycle:       int           # 1, 2, or 3 (the year, for "Year N Begins")
    chest:       int           # chest number in the game's order (0 = not a chest)
    flags:       Tuple[int, ...] = ()   # the chest's "opened" flags (see chest_table.py)
    is_event:    bool = False  # True for "Cycle N Reached" / "Year N Begins" (no chest)

class FFCCLocation(Location):
    game: str = game_name

    def __init__(self, player: int, name: str, parent: Region,
                 data: Optional[FFCCLocationData] = None):
        address = None if data is None or data.code is None else FFCCLocation.get_apid(data.code)
        super().__init__(player, name, address=address, parent=parent)
        if data:
            self.code        = data.code
            self.region      = data.region
            self.cycle       = data.cycle
            self.chest       = data.chest
            self.flags       = data.flags

    @staticmethod
    def get_apid(code: int) -> int:
        return 2326528 + code


# Chests are numbered in the game's own order and know their
# chest-opened flags, and the client and the patcher use the same numbers, so a
# location always means the same physical chest. "Cycle N Reached" and
# "Year N Begins" are event checks with no chest.
from .chest_table import LOCATIONS

LOCATION_TABLE: dict[str, FFCCLocationData] = {
    name: FFCCLocationData(code, region, cycle, chest, flags, is_event=chest == 0)
    for name, (code, region, cycle, chest, flags) in LOCATIONS.items()
}

# Groupings for tracker / hint purposes
location_groups: dict[str, list] = {}
for _name, _data in LOCATION_TABLE.items():
    location_groups.setdefault(_data.region, []).append(_name)
    location_groups.setdefault(f"Cycle {_data.cycle}", []).append(_name)


# The Monster Hunt: one location per enemy type ("Monster Hunt - <enemy>"),
# checked when the first enemy of that type is defeated.
from .monster_table import MONSTERS, ENEMIES

MONSTER_HUNT_PREFIX = "Monster Hunt - "

def monster_location(enemy: str) -> str:
    return MONSTER_HUNT_PREFIX + enemy

def hunt_list(include_bosses: bool) -> list:
    """The enemy types of the hunt, in the table's order."""
    return [enemy for enemy, row in MONSTERS.items() if include_bosses or not row[1]]

MONSTER_LOCATION_TABLE: dict[str, FFCCLocationData] = {
    monster_location(enemy): FFCCLocationData(row[0], "Menu", 0, 0)
    for enemy, row in MONSTERS.items()
}
location_groups["Monster Hunt"] = list(MONSTER_LOCATION_TABLE)
location_groups["Monster Hunt Bosses"] = [monster_location(e) for e, row in MONSTERS.items() if row[1]]

# "Every Enemy": one location per enemy, named "<dungeon> - <enemy> <n>" (or
# "<dungeon> - <boss>"), in its dungeon's region. `cycle` is the first cycle
# it appears in.
ENEMY_LOCATION_TABLE: dict[str, FFCCLocationData] = {
    name: FFCCLocationData(row[0], row[1], 1 if row[1] == "Mount Vellenge" else min(row[7]), 0)
    for name, row in ENEMIES.items()
}

def enemy_is_boss(name: str) -> bool:
    return MONSTERS[ENEMIES[name][2]][1]


for _name, _data in ENEMY_LOCATION_TABLE.items():
    location_groups.setdefault(_data.region + " Enemies", []).append(_name)
location_groups["Every Enemy"] = list(ENEMY_LOCATION_TABLE)


# "Shop Checks": one location per shop slot ("Alfitaria Food Shop - Slot 2"),
# checked by its first purchase.
from .shop_table import LOCATIONS as SHOP_LOCATIONS, SHOPS

SHOP_LOCATION_TABLE: dict[str, FFCCLocationData] = {
    name: FFCCLocationData(row[0], "Menu", 0, 0) for name, row in SHOP_LOCATIONS.items()
}
for _name, _row in SHOP_LOCATIONS.items():
    location_groups.setdefault(SHOPS[_row[1]][0], []).append(_name)
location_groups["Shops"] = list(SHOP_LOCATION_TABLE)
