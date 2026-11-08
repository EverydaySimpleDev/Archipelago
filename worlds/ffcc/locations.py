from typing import NamedTuple
from BaseClasses import Location, Region
from .game_id import game_name
from .chest_table import LOCATIONS
from .monster_table import MONSTERS, ENEMIES
from .shop_table import LOCATIONS as SHOP_LOCATIONS, SHOPS


class FFCCLocationData(NamedTuple):
    code:        int           # AP code (AP id = get_apid(code)), fixed in chest_table.py
    region:      str           # dungeon name (must match regions.py), "Menu" for the Year locations
    cycle:       int           # 1, 2, or 3 (the year, for "Year N Begins")
    chest:       int           # chest number in the game's order (0 = not a chest)
    flags:       tuple[int, ...] = ()   # the chest's "opened" flags (see chest_table.py)
    is_event:    bool = False  # True for "Cycle N Reached" / "Year N Begins" (no chest)


class FFCCLocation(Location):
    game: str = game_name

    def __init__(self, player: int, name: str, parent: Region,
                 data: FFCCLocationData | None = None) -> None:
        address = None if data is None or data.code is None else FFCCLocation.get_apid(data.code)
        super().__init__(player, name, address=address, parent=parent)
        if data:
            self.code = data.code
            self.region = data.region
            self.cycle = data.cycle
            self.chest = data.chest
            self.flags = data.flags

    @staticmethod
    def get_apid(code: int) -> int:
        return 2326528 + code


# Chests are numbered in the game's own order and know their
# chest-opened flags, and the client and the patcher use the same numbers, so a
# location always means the same physical chest. "Cycle N Reached" and
# "Year N Begins" are event checks with no chest.

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

SHOP_LOCATION_TABLE: dict[str, FFCCLocationData] = {
    name: FFCCLocationData(row[0], "Menu", 0, 0) for name, row in SHOP_LOCATIONS.items()
}
for _name, _row in SHOP_LOCATIONS.items():
    location_groups.setdefault(SHOPS[_row[1]][0], []).append(_name)
location_groups["Shops"] = list(SHOP_LOCATION_TABLE)

# Mog Stamps: one Moogle Nest per stamp, each a bit in the 4 bytes at
# 0x8021EF56 (the client reads them). nest -> (byte, bit). A dungeon's nest
# has the dungeon's name. With the Mog Stamps goal each nest is an event
# location ("Mog Stamp - Tida") holding a "Mog Stamp".
MOG_STAMP_NESTS = {
    "Marr's Pass": (0, 4), "Tipa": (0, 5), "The Fields of Fum": (0, 6), "Alfitaria": (0, 7),
    "Shella": (1, 0), "West Jegon River": (1, 1), "River Belle Path": (1, 2), "Leuda": (1, 3),
    "Port Tipa": (1, 4), "The Mushroom Forest": (1, 5), "Daemon's Court": (1, 6), "Mount Kilanda": (1, 7),
    "Veo Lu Sluice": (2, 0), "Selepation Cave": (2, 1), "Goblin Wall": (2, 2), "Lynari Desert": (2, 3),
    "Conall Curach": (2, 4), "The Mine of Cathuriges": (2, 5), "Tida": (2, 6), "Moschet Manor": (2, 7),
    "Rebena Te Ra": (3, 0), "Mount Vellenge": (3, 1), "Mag Mell": (3, 2),
}


def mog_stamp_bit(nest: str) -> int:
    """The nest's bit in the 4 stamp bytes read as one big-endian number."""
    byte, bit = MOG_STAMP_NESTS[nest]
    return 1 << (8 * (3 - byte) + bit)


def mog_stamp_location(nest: str) -> str:
    return f"Mog Stamp - {nest}"


MOG_STAMP_BITS = sum(map(mog_stamp_bit, MOG_STAMP_NESTS))    # 0xF0FFFF07

# Mog grooming checks (option Mog Grooming Checks), done in any Moogle Nest.
# The radars: the colour a Moogle's fur shows most (by the game's own
# pattern score) sets the GBA radar: red the Monster Radar, green the Score
# Radar, blue the Treasure Radar. The milestones: how much of the fur is dyed
# (in any colours) or cut. name -> (code, kind, value)
GROOMING_LOCATIONS = {
    "Mog Radar - Red (Monster Radar)":   (3200, "radar", 1),
    "Mog Radar - Green (Score Radar)":   (3201, "radar", 2),
    "Mog Radar - Blue (Treasure Radar)": (3202, "radar", 3),
    "Mog Grooming - Dyed 25%":           (3203, "dyed", 25),
    "Mog Grooming - Dyed 50%":           (3204, "dyed", 50),
    "Mog Grooming - Dyed 75%":           (3205, "dyed", 75),
    "Mog Grooming - Cut 25%":            (3206, "cut", 25),
    "Mog Grooming - Cut 50%":            (3207, "cut", 50),
    "Mog Grooming - Cut 75%":            (3208, "cut", 75),
}
GROOMING_RADAR_DYE = {1: "Red Dye", 2: "Green Dye", 3: "Blue Dye"}
GROOMING_LOCATION_TABLE = {
    name: FFCCLocationData(code, "Menu", 1, 0)
    for name, (code, _, _) in GROOMING_LOCATIONS.items()
}
for _name, (_, _kind, _) in GROOMING_LOCATIONS.items():
    location_groups.setdefault("Mog Grooming", []).append(_name)

# Items the game itself gives the player. The patcher puts this player's own
# items into their chests and shops when the game can hold them, and the game
# hands them over when the chest is opened or the item is bought. The client
# must not give those again. The world and the client both use these rules.
SHOP_ITEM_TYPES = ("Food", "Material", "Recipe", "Phoenix Down")
LOCATION_NAME_BY_ID = {
    FFCCLocation.get_apid(data.code): name
    for name, data in {**LOCATION_TABLE, **SHOP_LOCATION_TABLE}.items()
    if data.code is not None
}


def chest_holds_item(item_name: str, location_name: str) -> bool:
    """True if the patcher puts this player's own item in the chest itself: an
    item with an in-game ID, in a real chest, and not an artifact (see
    items.ARTIFACT_TYPES)."""
    from .items import ITEM_TABLE, ARTIFACT_TYPES
    loc_data = LOCATION_TABLE.get(location_name)
    if loc_data is None or loc_data.is_event or not loc_data.chest:
        return False
    item_data = ITEM_TABLE.get(item_name)
    return item_data is not None and item_data.item_id is not None and item_data.type not in ARTIFACT_TYPES


def shop_sells_item(item_name: str, location_name: str) -> bool:
    """True if this shop slot sells this player's own item itself (food,
    materials, recipes and Phoenix Downs), so buying it gives the item."""
    from .items import ITEM_TABLE
    if location_name not in SHOP_LOCATION_TABLE:
        return False
    item_data = ITEM_TABLE.get(item_name)
    return item_data is not None and item_data.item_id is not None and item_data.type in SHOP_ITEM_TYPES


def game_gives_item(item_name: str, location_name: str) -> bool:
    """True if the game gives this player's own item at this location itself."""
    return chest_holds_item(item_name, location_name) or shop_sells_item(item_name, location_name)
