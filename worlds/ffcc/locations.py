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


# ── Dungeon chest lists, per cycle  ─────────────────────────────────────────
# Each dungeon maps cycle number -> ordered list of physical chest identifiers
# present *in that cycle*. Chest sets are NOT uniform across cycles for most
# dungeons (e.g. The Mushroom Forest only spawns 5 of its 9 chests in Cycle 1);
# using a single flat list for all 3 cycles (the old approach) silently added
# unreachable locations for cycles where a chest doesn't physically exist yet.
#
# Mount Vellenge only has one cycle. Veo Lu Sluice only has two distinct
# cycles in-game (the drained-water state introduced in Cycle 2 persists
# through Years 5-7) — it has no Cycle 3 entry.
#
# Mount Kilanda has three chest pairs that are mutually exclusive (opening
# one permanently prevents the other from ever spawning: 1/8, 2/5, 6/9) —
# each pair is collapsed into a single "a/b" location so AP never expects
# both halves to be independently checkable.
_DUNGEON_CHESTS_BY_CYCLE: dict[str, dict[int, list]] = {
    "River Belle Path": {
        1: [1, 2, 3, 4, 5, 6, 7],
        2: [1, 2, 3, 4, 5, 6, 7],
        3: [1, 2, 3, 4, 5, 6, 7],
    },
    "Goblin Wall": {
        1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14],
        2: list(range(1, 15)),
        3: list(range(1, 15)),
    },
    "The Mine of Cathuriges": {
        1: [1, 2, 3, 4, 5, 12, 13, 14],
        2: list(range(1, 15)),
        3: list(range(1, 15)),
    },
    "The Mushroom Forest": {
        1: [3, 5, 6, 7, 8],
        2: list(range(1, 10)),
        3: list(range(1, 10)),
    },
    "Moschet Manor": {
        1: list(range(1, 8)),
        2: list(range(1, 8)),
        3: list(range(1, 8)),
    },
    "Veo Lu Sluice": {
        1: [1, 2, 3, 4, 5],
        2: list(range(1, 19)),
    },
    "Daemon's Court": {
        1: list(range(1, 11)),
        2: list(range(1, 11)),
        3: list(range(1, 11)),
    },
    "Selepation Cave": {
        1: list(range(1, 11)),
        2: list(range(1, 11)),
        3: list(range(1, 11)),
    },
    "Conall Curach": {
        1: list(range(1, 23)),
        2: list(range(1, 23)),
        3: list(range(1, 23)),
    },
    "Rebena Te Ra": {
        1: list(range(1, 16)),
        2: list(range(1, 16)),
        3: list(range(1, 16)),
    },
    "Mount Vellenge": {
        1: list(range(1, 15)),
    },
    "Lynari Desert": {
        1: list(range(1, 11)),
        2: list(range(1, 11)),
        3: list(range(1, 11)),
    },
    "Tida": {
        1: list(range(1, 14)),
        2: list(range(1, 14)),
        3: list(range(1, 14)),
    },
    "Mount Kilanda": {
        1: ["1/8", "2/5", 3, 4, "6/9", 7],
        2: ["1/8", "2/5", 3, 4, "6/9", 7],
        3: ["1/8", "2/5", 3, 4, "6/9", 7],
    },
}


def _build_location_table() -> dict:
    table = {}
    code = 0
    for dungeon, cycles in _DUNGEON_CHESTS_BY_CYCLE.items():
        for cycle, chests in cycles.items():
            for chest in chests:
                name = f"{dungeon} - Cycle {cycle} - Chest {chest}"
                # "a/b" mutex-pair identifiers store the lower chest number
                # in the numeric `chest` field (used by the patcher output).
                chest_num = int(str(chest).split("/")[0])
                table[name] = FFCCLocationData(code, dungeon, cycle, chest_num)
                code += 1
    # Cycle advancement pseudo-locations — one per dungeon per cycle > 1 that
    # actually exists for that dungeon (Mount Vellenge has none; Veo Lu Sluice
    # only has Cycle 2). chest=0, is_event=True: no physical chest; client
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
