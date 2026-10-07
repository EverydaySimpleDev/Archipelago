from typing import NamedTuple, Optional
from BaseClasses import Location, Region
from .game_id import game_name

class FFCCLocationData(NamedTuple):
    code:        int           # sequential AP code for get_apid
    region:      str           # dungeon name (must match regions.py)
    cycle:       int           # 1, 2, or 3
    chest:       int           # chest number (used by patcher; 0 = no physical chest)
    # Chest bit flag in memory: (byte_offset, bit_index) relative to 0x80926000
    # None = not yet mapped; requires in-game testing to confirm
    flag_byte:   Optional[int] = None
    flag_bit:    Optional[int] = None
    is_event:    bool = False  # True for cycle-advancement pseudo-locations (no physical chest)

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
            self.chest = data.chest
            self.flag_byte   = data.flag_byte
            self.flag_bit    = data.flag_bit

    @staticmethod
    def get_apid(code: int) -> int:
        return 2326528 + code


# Dungeon chest lists, per cycle
# Built from chest_table.py, which chestflags.py generates from the
# game files: chests are numbered in the game's own order,
# each knows the cycles it appears in and its chest-opened flag(s). The client
# and the patcher use the same table, so a location always means the same
# physical chest.
#
# Mount Vellenge is only played once, so it only gets Cycle 1 locations.
from .chest_table import CHESTS

_SINGLE_CYCLE = {"Mount Vellenge"}

_DUNGEON_CHESTS_BY_CYCLE: dict[str, dict[int, list]] = {}
for _dungeon, _rows in CHESTS.items():
    _by_cycle: dict[int, list] = {}
    for _chest, _cycles, _flags in _rows:
        for _cycle in _cycles:
            if _dungeon in _SINGLE_CYCLE and _cycle != 1:
                continue
            _by_cycle.setdefault(_cycle, []).append(_chest)
    _DUNGEON_CHESTS_BY_CYCLE[_dungeon] = dict(sorted(_by_cycle.items()))


def _build_location_table() -> dict:
    table = {}
    code = 0
    for dungeon, cycles in _DUNGEON_CHESTS_BY_CYCLE.items():
        for cycle, chests in cycles.items():
            for chest in chests:
                name = f"{dungeon} - Cycle {cycle} - Chest {chest}"
                table[name] = FFCCLocationData(code, dungeon, cycle, chest)
                code += 1
    # Cycle advancement pseudo-locations - one per dungeon per cycle > 1 that
    # actually exists for that dungeon (Mount Vellenge has none). chest=0, is_event=True: no physical chest; client
    # sends these as LocationChecks when just_entered fires with cycle >= 2.
    # Items placed here are bonus filler.
    for dungeon, cycles in _DUNGEON_CHESTS_BY_CYCLE.items():
        for cycle in sorted(cycles):
            if cycle == 1:
                continue
            name = f"{dungeon} - Cycle {cycle} Reached"
            table[name] = FFCCLocationData(code, dungeon, cycle, 0, is_event=True)
            code += 1
    # Year advancement pseudo-locations — one per year from Year 2 to Year 10.
    # region="Menu" distinguishes these from cycle locations in __init__.py logic.
    # cycle field stores the year number; chest=0, is_event=True.
    for year in range(2, 11):
        name = f"Year {year} Begins"
        table[name] = FFCCLocationData(code, "Menu", year, 0, is_event=True)
        code += 1
    return table


LOCATION_TABLE: dict[str, FFCCLocationData] = _build_location_table()

# Groupings for tracker / hint purposes
location_groups: dict[str, list] = {}
for _name, _data in LOCATION_TABLE.items():
    location_groups.setdefault(_data.region, []).append(_name)
    location_groups.setdefault(f"Cycle {_data.cycle}", []).append(_name)
