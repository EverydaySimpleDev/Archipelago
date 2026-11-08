"""FFCC Archipelago client — connects to Dolphin via dolphin_memory_engine."""

import asyncio
import random
import struct
import time
import traceback
from collections import deque
from contextlib import contextmanager
from typing import Any, Callable, Iterator

import Utils
from CommonClient import (CommonContext, ClientCommandProcessor, gui_enabled, logger, get_base_parser,
                          handle_url_arg, server_loop)
from NetUtils import ClientStatus, NetworkItem

try:
    import dolphin_memory_engine as dme
    DOLPHIN_AVAILABLE = True
except ImportError:  # the apworld's requirements.txt installs it, but just in case
    DOLPHIN_AVAILABLE = False
    logger.warning("dolphin_memory_engine not installed — FFCC client will not function.")

# With Universal Tracker installed, the client is built on its tracker context
# and shows its tracker and map tabs. Without it, it's a plain client.
try:
    from worlds.tracker.TrackerClient import TrackerGameContext as BaseContext
    from worlds.tracker.TrackerClient import TrackerCommandProcessor as BaseCommandProcessor
    tracker_loaded = True
except ModuleNotFoundError:
    BaseContext, BaseCommandProcessor = CommonContext, ClientCommandProcessor
    tracker_loaded = False

from .game_id import game_name
from .items import (ITEM_TABLE, LOOKUP_ID_TO_NAME, PROGRESSIVE_ARTIFACT_ORDER, PROGRESSIVE_ARTIFACT_NAME,
                    GROOMING_TOOLS,
                    STAGE_KEYS, EXTRA_SPELL_RINGS, GIL_AMOUNT)
from .locations import (LOCATION_TABLE, FFCCLocationData, MONSTER_LOCATION_TABLE, MONSTERS, ENEMIES,
                        ENEMY_LOCATION_TABLE, monster_location, hunt_list, SHOP_LOCATIONS, SHOPS,
                        MOG_STAMP_NESTS, MOG_STAMP_BITS, mog_stamp_bit, FFCCLocation, GROOMING_LOCATIONS,
                        LOCATION_NAME_BY_ID, game_gives_item)
from .monster_table import ENEMY_GROUPS
from .bonus import make_bonus_pools, offered_entry, solo_points, item_name, PLAYER_FACTOR
from .bonus_table import BONUS_TABLE
from .equipment_table import PATHS as EQUIPMENT_PATHS, NAMES as EQUIPMENT_NAMES

# Expected game ID
GAME_ID = b"GCCE"     # FFCC NTSC-U 4-byte game code
GAME_ID_ADDR = 0x80000000

# Connection status strings
CONNECTION_INITIAL_STATUS = "Dolphin connection has not been initiated."
CONNECTION_CONNECTED_STATUS = "Dolphin connected successfully."
CONNECTION_REFUSED_STATUS = "Dolphin refused: wrong game loaded. Please load FFCC NTSC-U."
CONNECTION_LOST_STATUS = "Dolphin connection was lost. Please restart your emulator and ensure FFCC is running."

# World / dungeon state
# The stage the game is in:
# 0x00-0x0d = a dungeon, anything else = a town, the world map or an event.
# The game picks the dungeon's cycle with this same index.
ADDR_MAP_ID = 0x8021f255
ADDR_CURRENT_YEAR = 0x8021de93  # 1 byte: current caravan year (1=Year1, 2=Year2, ...)
ADDR_WORLD_MAP = 0x8021f25a   # 1 byte: 0x01 = on world map
ADDR_PAUSED = 0x8021f25b   # 1 byte: 0x01 = paused

# Per-dungeon cycle address: map_id 0 → 0x8021deb3, map_id 1 → +4, etc.
ADDR_CYCLE_BASE = 0x8021deb3   # 0x00=Cycle1, 0x01=Cycle2, 0x02=Cycle3

# Player stats
ADDR_MAX_HEARTS = 0x8021f28b   # 1 byte
ADDR_CUR_HEARTS = 0x8021f28d   # 1 byte (1 heart = 2 units, 0 = dead)

# Status effects (2 bytes each, write any nonzero value to apply)
ADDR_FROZEN = 0x8021f2ae
ADDR_BURNED = 0x8021f2b0
ADDR_POISONED = 0x8021f2b2
ADDR_PARALYZED = 0x8021f2b6
ADDR_SLOWED = 0x8021f2be

CARAVAN_FIRST = 0x8021f270
CARAVAN_SIZE = 0xc30
CARAVAN_MEMBERS = 8            # family characters (the 9th record is Mog)
ADDR_PARTY = 0x8021dea0   # the record each controller plays
ADDR_TOWN_NAME = 0x8021ef28   # 20 bytes the caravan's hometown
CARAVAN_NAME = 0x3ca
CARAVAN_TRIBE = 0x3e0        # u16: 0 Clavat, 1 Lilty, 2 Yuke, 3 Selkie
CARAVAN_GENDER = 0x3e2        # u16: 0 male, 1 female
TRIBE_NAMES = ("Clavat", "Lilty", "Yuke", "Selkie")
_player_offset = 0            # CARAVAN_SIZE * the record player 1 plays

# Inventory / items
#   +0xB4  u16 m_inventoryItemCount   items in the 64 inventory slots
#   +0xB6  m_inventoryItems[164]      slots 0-63 inventory, 64-159 permanent
#                                     artifacts, 160-163 this dungeon's artifacts
#   +0x200 gil
# Permanent artifacts have fixed places: artifact `id` lives in slot
# 64 + (id - 0x9F), and a save only keeps which places are filled, so an
# artifact written anywhere else turns into a different one after a reload.
ADDR_ITEM_COUNT = 0x8021f324   # u16
ADDR_INVENTORY = 0x8021f326   # 64 inventory slots (2 bytes each)
ADDR_ARTIFACT = 0x8021f3a6   # 96 permanent artifact places (2 bytes each)
ADDR_GIL = 0x8021f470   # 4 bytes BE
INVENTORY_SLOTS = 64
ARTIFACT_FIRST_ID = 0x9f
ARTIFACT_SLOTS = 96
ITEM_SLOT_EMPTY = 0xffff  # sentinel for an empty inventory slot
MAX_GIL = 99999999   # Max Gil
STONE_OF_CURE = 0x105   # "Free Cure Magicite"

# Command list (Command Slot Trap)
ADDR_CMD_SLOTS = 0x8021f474
ADDR_CMD_FUSED = 0x8021f484
ADDR_CMD_CURRENT = 0x8021f494
ADDR_CMD_WEAPON = 0x8021f496
ADDR_CMD_COUNT = 0x8021fe1a
FIXED_COMMANDS = 2            # Attack and Defend can't be removed

ADDR_TRIBE = 0x8021f650   # u16: 0 Clavat, 1 Lilty, 2 Yuke, 3 Selkie

# Items delivered so far, kept in the save file (CGameWork m_eventWork[230], a
# value no game script uses, Thanks Decomp Team!) so a reconnect doesn't send everything again and a
# reset without saving re-sends exactly what was lost.
ADDR_ITEMS_DELIVERED = 0x8021f220

# HUD: boxes of text the game draws from a table
# of slots. Item messages use slots 1-3 as lines at the bottom of the screen,
# the newest at the bottom and slot 0 is the play timer's. A slot is 0x60 bytes:
# +0 flags (1 shown, 2 box), +1 font palette, +2 frames left (the game hides
# the slot when it runs out), +4 box x, y, width, height, +0x14 text x, y,
# scale (floats, the screen is 640 x 448), +0x20 border, fill and text
# colours (RGBA), +0x2C the text (zero-terminated).
ADDR_HUD_HOOK = 0x80095ed8
HUD_HOOK_WORD = 0x48113b95          # bl to the HUD code: the ISO has the HUD
ADDR_HUD_SLOTS = 0x801a951c
HUD_SLOT_SIZE = 0x60
HUD_MESSAGE_SLOTS = (1, 2, 3)
HUD_TEXT_MAX = 47                   # what fits in a line's box
HUD_SHOW_SECONDS = 4.0              # how long a message stays up
HUD_BUSY_SECONDS = 2.0              # with more waiting, a line goes after this long
HUD_GAP_SECONDS = 0.8               # between two new lines
HUD_GROOMING_SLOTS = (4, 5)         # in a Moogle Nest: the grooming progress, a tool not found yet

# Mog grooming. In a Moogle Nest the Moogle's fur is a 64 x 64
# texture at ADDR_MOG_FUR: a u16 per texel, 3 bits of length (7 = full) and
# 4 bits each of red, green and blue (white = not dyed), in 4 x 4 tiles. The
# tool held is a u32 after it (0 red dye, 1 blue dye, 2 green dye, 3 wash,
# 4 scissors). With the Grooming Tools option the patcher only lets a tool
# work if its bit is set in the byte at ADDR_GROOMING_TOOLS.
ADDR_MOG_FUR = 0x802e68a4
MOG_FUR_TEXELS = 64 * 64
ADDR_MOG_TOOL = ADDR_MOG_FUR + 0x2000
ADDR_GROOMING_TOOLS = 0x801a92ac
ADDR_GROOMING_HOOK = 0x800dfdf4
# Byte offsets of the texels on the Moogle: the fur is a disc (radius 32
# around the centre). The corners of the texture aren't on the model, so they
# can't be groomed and don't count.
MOG_FUR_ON_MODEL = [2 * ((x // 4) * 16 + (y // 4) * 256 + x % 4 + (y % 4) * 4)
                    for y in range(64) for x in range(64)
                    if (x - 31.5) ** 2 + (y - 31.5) ** 2 <= 32 ** 2]
GROOMING_HOOK_WORD = 0x480c94bd
# The GBA radar the Moogle's fur gives:
# 0 the map, 1 Monster (red fur), 2 Score (green), 3 Treasure (blue). The game
# sets it on every grooming stroke and keeps it in the save.
ADDR_MOG_RADAR = 0x8021f25d

# "Hide Collected Chests": each dungeon's chest mask for its current cycle
# The patched dungeon scripts add the mask to the chests' "opened"
# bits as an area loads, so those chests don't appear
ADDR_EVENT_WORK = 0x8021f054
CHEST_MASK_SLOT = 180

# Live monsters: 64 records of 0x110 bytes. In each, +0x10 is the
# monster id (the same number as in the dungeon scripts' SPAWN records,
# +0x1A max HP and +0x1C HP. When a monster dies its HP
# drops to 0 and stays there until the next area reuses the record.
ADDR_MONSTER_WORK = 0x80226020
MONSTER_WORK_SIZE = 0x110
MONSTER_SLOTS = 64
MONSTER_ID = 0x10
MONSTER_MAX_HP = 0x1A
MONSTER_HP = 0x1C

# Monsters that never reach 0 HP: at 1 HP the Lamia Queen (Moschet Manor)
# gives up and flees across the room instead, so dropping to 1 HP is her defeat.
FLEES_AT_1_HP = {112}

# monster id -> enemy type of the Monster Hunt
MONSTER_BY_ID: dict[int, str] = {monster_id: enemy for enemy, row in MONSTERS.items() for monster_id in row[2]}

# "Every Enemy": a monster's object (the record's +0x0C) keeps where it
# spawned at +0x168 (3 floats), the same spot as its row in ENEMIES, so a
# monster that dies is told apart from the others of its type by that spot.
MONSTER_SPAWN = 0x168
MONSTER_HOME = 0x6F8
SPAWN_TOLERANCE = 0.05
HUNT_EVERY_ENEMY = 2
# dungeon -> [(monster id, (x, y, z), AP ids)] for normal enemies: one AP id,
# or a switch group's (ENEMY_GROUPS) - only some of its spots spawn per
# visit, so a kill on any of them is its first AP id still unchecked.
# (dungeon, enemy type) -> AP id for bosses (any piece of the fight counts)
# dungeon -> [(monster id, AP ids)] for ambush groups (a spot of None): the
# map script moves them onto the player, so a kill of that id no spot
# matches counts as their first AP id still unchecked.
ENEMY_SPOTS: dict[str, list[tuple[int, tuple[float, float, float], list[int]]]] = {}
BOSS_SPOTS: dict[tuple[str, str], int] = {}
AMBUSH_IDS: dict[str, list[tuple[int, list[int]]]] = {}
_GROUPED = {name for _, members, _ in ENEMY_GROUPS for name, _ in members}
for _name, _row in ENEMIES.items():
    _ap_id = 2326528 + _row[0]
    if MONSTERS[_row[2]][1]:
        BOSS_SPOTS[(_row[1], _row[2])] = _ap_id
    elif _name not in _GROUPED:
        ENEMY_SPOTS.setdefault(_row[1], []).append((_row[3], _row[6], [_ap_id]))
for _dungeon, _members, _spots in ENEMY_GROUPS:
    _ap_ids = [2326528 + code for _, code in _members]
    for _monster_id, _spot in _spots:
        if _spot is None:
            AMBUSH_IDS.setdefault(_dungeon, []).append((_monster_id, _ap_ids))
        else:
            ENEMY_SPOTS.setdefault(_dungeon, []).append((_monster_id, _spot, _ap_ids))

# in-game item id -> item name
ITEM_NAME_BY_ID: dict[int, str] = {d.item_id: n for n, d in ITEM_TABLE.items() if d.item_id is not None}

# Shop Checks. While a shop is open, player 1's caravan record holds
# its list (count, then up to 16 item ids) and the shop menu.
ADDR_GIL = 0x8021f470    # u32, player 1
ADDR_SHOP_COUNT = 0x8021fe54    # s16
ADDR_SHOP_MENU = 0x802e99f8    # pointer to the shop menu
SHOP_MENU_SUB = 0x10
SHOP_MENU_CURSOR = 0x28
SHOP_CONFIRM = 2
# file name of the town's script
ADDR_SCRIPT_FILE = 0x8029977e
SHOP_TOWN_BY_SCRIPT = {"weap": "Marr's Pass", "cast": "Alfitaria",
                       "magi": "Shella", "farm": "Fields of Fum", "thie": "Leuda"}
# Towns where received items are delivered too (dropped once no shop is open)
TOWN_SCRIPTS = {"vill", *SHOP_TOWN_BY_SCRIPT}
# (town, slots) -> shop key. A town's shops have different lengths.
SHOP_BY_TOWN = {(row[1], row[4]): key for key, row in SHOPS.items()}
# (shop key, slot from 1) -> AP id
SHOP_SLOT_IDS = {(row[1], row[2]): 2326528 + row[0] for row in SHOP_LOCATIONS.values()}

# Mog Stamps: one bit per Moogle Nest in these 4 bytes.
# Bit 3 of the last byte is the stamp card, not a stamp.
# A new stamp sends a hint (Mog Stamp Hints), and all of them are the Mog
# Stamps goal.
ADDR_MOG_STAMPS = 0x8021ef56
MOG_STAMPS = {mog_stamp_bit(nest): nest for nest in MOG_STAMP_NESTS}   # bit -> nest
MOG_STAMP_COUNT = len(MOG_STAMPS)
HINT_PRIORITY = 30          # NetUtils.HintStatus.HINT_PRIORITY

# Item types the client adds to the permanent artifact places. Everything else
# (Spell Rings included, which are used from the command list) goes in the bag.
PERMANENT_ARTIFACT_TYPES = ("Artifact", "Stage Key")
EXTRA_RING_IDS = {iid for _, iid in EXTRA_SPELL_RINGS}

# Chalice / bonus / food
ADDR_CHALICE = 0x8021ef3f   # low byte of the chalice element: 1=Fire,2=Water,4=Wind,8=Earth,16=Unknown
CHALICE_ELEMENTS = {"fire": 0x01, "water": 0x02, "wind": 0x04, "earth": 0x08, "unknown": 0x10}
ADDR_CHALICE_FILL = 0x8021de97  # 1 byte: Myrrh drops in the chalice this year (0-3, 3 = full)

# Myrrh tree state, one byte per dungeon at ADDR_MYRRH_TREE + 4 * n (n = the
# dungeon's order below): 100 = has Myrrh, 0 = just harvested, 25/50/75 = regrowing.
ADDR_MYRRH_TREE = 0x8021deef
MYRRH_TREE_READY = 100
MYRRH_TREE_DUNGEONS = [
    "River Belle Path", "Goblin Wall", "The Mine of Cathuriges", "The Mushroom Forest",
    "Tida", "Moschet Manor", "Mount Kilanda", "Daemon's Court", "Selepation Cave",
    "Veo Lu Sluice", "Lynari Desert", "Conall Curach", "Rebena Te Ra",
]
ADDR_BONUS = 0x8021fe14   # 1 byte: 0x01–0x18
# Bonus counters for this dungeon:
#   enemies defeated, items picked up, times knocked out,
#   points earned for the bonus, points left for the bonus.
# Bonus points = earned + left (0-100). score = bonus points + enemies + items - knock-outs (0-999).
ADDR_BONUS_COUNTERS = 0x8021fe34
# The bonus screen at the end of a dungeon: a pointer to its data. In that data, +0x12 holds the
# 4 bonus-pool items offered (shorts) and +0x3C player 1's pick (int, -1 until
# chosen, and the screen closes about a second after the pick).
ADDR_BONUS_SCREEN = 0x8032de88
BONUS_OFFERED = 0x12
BONUS_PICKED = 0x3c
BONUS_NAMES = {
    0x01: "Open treasure chests", 0x02: "Pick up items", 0x03: "Use items",
    0x04: "Pick up magicite", 0x06: "Pick up money",
    0x07: "Defeat enemies with focus attacks", 0x08: "Defeat enemies with spells",
    0x09: "Defeat enemies with spell fusion", 0x0a: "Dodge attacks", 0x0b: "Inflict damage",
    0x0c: "Avoid damage", 0x0d: "Take physical damage", 0x0e: "Eat lots of food",
    0x0f: "Don't use physical attacks", 0x10: "Don't use focus attacks", 0x11: "Don't cast spells",
    0x12: "Don't heal yourself", 0x13: "Don't heal allies", 0x14: "Don't pick anything up",
    0x15: "Dodge thrown rocks", 0x16: "Take magical damage", 0x17: "Defeat flying enemies",
    0x18: "Finish as quickly as possible",
}
ADDR_FOOD_BASE = 0x8021f628   # u16 × 8 food preferences (caravan +0x3B8), about 0-100 each

# Chest bit flags (8 bytes, shared/reused per dungeon, cleared on dungeon exit)
ADDR_CHEST_BASE = 0x80926000

# Trap Setup
ADDR_TRAP_HOOK = 0x80111a48
# The hook word at ADDR_TRAP_HOOK: the trap-visuals patch alone, or with the
# item-drop code ("Items Dropped At Your Feet") in front of it.
TRAP_HOOK_WORDS = (bytes.fromhex("48098261"), bytes.fromhex("48098339"))
ITEM_DROP_HOOK = bytes.fromhex("48098339")
# Item id the patched game puts on the ground in front of player 1 (u16, the
# game clears it once the item is there).
ADDR_ITEM_DROP = 0x801a9d78
# Weapons, armor and other equipment (ids 0x01-0x9E) can't be dropped.
LAST_EQUIPMENT_ID = 0x9e

ADDR_KEEP_ARTIFACTS = 0x800a14e0
KEEP_ARTIFACTS_CODE = bytes.fromhex("38c4ffa1")

ADDR_HOOK_PLAYER = 0x801a9cb0
HOOK_FOLLOWS_PARTY = bytes.fromhex("3d608023816ba440")
HOOK_ALL_PLAYERS = bytes.fromhex("280c00034d810020")
ADDR_TRAP_PENDING = 0x801a9d28   # u16 per status: 0 freeze, 1 burn, 2 poison, 4 paralysis, 8 slow
TRAP_PENDING_STRIDE = 18         # each controller's table
TRAP_STATUS_INDEX = {"Frozen Trap": 0, "Burned Trap": 1, "Poisoned Trap": 2, "Paralyzed Trap": 4, "Slowed Trap": 8}
TRAP_TIMER_ADDR = {"Frozen Trap": ADDR_FROZEN, "Burned Trap": ADDR_BURNED,
                   "Poisoned Trap": ADDR_POISONED, "Paralyzed Trap": ADDR_PARALYZED, "Slowed Trap": ADDR_SLOWED}

# Myrrh / Stages flags
ADDR_MYRRH_COLLECTED = 0x8021ef6d  # 2 bytes: bit n of (byte0 | byte1<<8) = dungeon n cleared
# (event flags 200+n), e.g. bit 0 = River Belle Path, bit 1 = Goblin Wall.
MYRRH_DUNGEONS = 13                # River Belle Path (0), Rebena Te Ra (12), Mount Vellenge has no tree
ALL_MYRRH_MASK = (1 << MYRRH_DUNGEONS) - 1

# Credits Victory Setup
ADDR_SCRIPT_NAME_ID = 0x80299780   # chars 3-6 of the loaded stage script's name
ENDING_IDS = (0x34345F32, 0x34345F33)  # "44_2" = ending (ff44_2), "44_3" = credits (ff44_3)

# Map ID → dungeon name
MAP_ID_TO_DUNGEON: dict[int, str] = {
    0x00: "River Belle Path",
    0x01: "Goblin Wall",
    0x02: "The Mine of Cathuriges",
    0x03: "The Mushroom Forest",
    0x04: "Tida",
    0x05: "Moschet Manor",
    0x06: "Mount Kilanda",
    0x07: "Daemon's Court",
    0x08: "Selepation Cave",
    0x09: "Veo Lu Sluice",
    0x0a: "Lynari Desert",
    0x0b: "Conall Curach",
    0x0c: "Rebena Te Ra",
    0x0d: "Mount Vellenge",
}

#  Chest flags per dungeon
# each chest's "opened" flag(s). Flag n = bit n of the big-endian u32 words at
# ADDR_CHEST_BASE: byte 4*(n//32) + 3 - (n%32)//8, bit n%8. The same table
# numbers the AP locations and drives the patcher, so a flag always reports
# the chest the item was put in.


def _flag_pos(n: int) -> tuple[int, int]:
    return 4 * (n // 32) + 3 - (n % 32) // 8, n % 8


# dungeon -> {(byte, bit): (chest, cycles it is a location in)}
CHEST_FLAGS: dict[str, dict[tuple[int, int], tuple[int, tuple[int, ...]]]] = {}
for _data in LOCATION_TABLE.values():
    for _flag in _data.flags:
        _chest, _cycles = CHEST_FLAGS.setdefault(_data.region, {}).get(_flag_pos(_flag), (_data.chest, ()))
        CHEST_FLAGS[_data.region][_flag_pos(_flag)] = (_chest, tuple(sorted(set(_cycles) | {_data.cycle})))


def _chest_location(dungeon: str, cycle: int, chest: int) -> str:
    return f"{dungeon} - Cycle {cycle} - Chest {chest}"

# Helpers


def _relocate(addr: int) -> int:
    """An address in the first character's record, moved to the record of
    the character on player 1. Other addresses are unchanged."""
    if CARAVAN_FIRST <= addr < CARAVAN_FIRST + CARAVAN_SIZE:
        return addr + _player_offset
    return addr


def _read_byte(addr: int) -> int:
    return dme.read_bytes(_relocate(addr), 1)[0]


def _read_short(addr: int) -> int:
    return int.from_bytes(dme.read_bytes(_relocate(addr), 2), "big")


def _read_int(addr: int) -> int:
    return int.from_bytes(dme.read_bytes(_relocate(addr), 4), "big")


def _write_byte(addr: int, val: int) -> None:
    dme.write_bytes(_relocate(addr), val.to_bytes(1, "big"))


def _write_short(addr: int, val: int) -> None:
    dme.write_bytes(_relocate(addr), val.to_bytes(2, "big"))


def _write_int(addr: int, val: int) -> None:
    dme.write_bytes(_relocate(addr), val.to_bytes(4, "big"))


def _party() -> list[int]:
    """The record index each controller is playing (-1 = nobody)."""
    return list(struct.unpack(">4i", dme.read_bytes(ADDR_PARTY, 16)))


def _character(record: int) -> dict:
    """Name, tribe and gender of one of the save's characters."""
    base = CARAVAN_FIRST + CARAVAN_SIZE * record
    raw = dme.read_bytes(base + CARAVAN_NAME, 18).split(b"\0")[0]
    tribe, gender = struct.unpack(">HH", dme.read_bytes(base + CARAVAN_TRIBE, 4))
    return {"name": raw.decode("shift_jis", "replace"),
            "tribe": TRIBE_NAMES[tribe] if tribe < len(TRIBE_NAMES) else "?",
            "gender": "female" if gender else "male"}


EMPTY_CHARACTER = "（なまえなし）"   # the name the game gives an unused slot ("no name")


def _town_name() -> str:
    return dme.read_bytes(ADDR_TOWN_NAME, 20).split(b"\0")[0].decode("shift_jis", "replace")


def _players() -> list[int]:
    """The records of the family characters being played."""
    out = []
    for record in _party():
        if 0 <= record < CARAVAN_MEMBERS and record not in out:
            out.append(record)
    return out


@contextmanager
def _as_player(record: int) -> Iterator[None]:
    """Read and write the per-character addresses of `record`."""
    global _player_offset
    saved = _player_offset
    _player_offset = CARAVAN_SIZE * record
    try:
        yield
    finally:
        _player_offset = saved


def _for_each_player(ctx: "FFCCContext", give: Callable[[], bool]) -> bool:
    """Call give() as every player who hasn't had this item yet.
    True once all of them have it. False to try the rest
    again later (give() returned False, e.g. a full bag)."""
    for record in _players():
        if record in ctx.given_to:
            continue
        with _as_player(record):
            if give():
                ctx.given_to.add(record)
    return all(record in ctx.given_to for record in _players())


def _update_player(ctx: "FFCCContext") -> None:
    """Follow the character on player 1. Kept as it
    was while no character is chosen."""
    global _player_offset
    record = _party()[0]
    if not 0 <= record < CARAVAN_MEMBERS:
        return
    _player_offset = CARAVAN_SIZE * record
    if record != ctx.player_record:
        ctx.player_record = record
        who = _character(record)
        logger.info(f"FFCC: Playing as {who["name"]} ({who["tribe"]}, {who["gender"]}) "
                    f"of {_town_name()}. Items go to this character.")


def _read_game_id() -> bytes:
    return dme.read_bytes(GAME_ID_ADDR, 4)


def _is_in_dungeon() -> bool:
    # 0x01 = world map. Towns also read 0x00, so check the stage index too
    return _read_byte(ADDR_WORLD_MAP) == 0x00 and _get_map_id() in MAP_ID_TO_DUNGEON


def _is_in_town() -> bool:
    return (_read_byte(ADDR_WORLD_MAP) == 0x00 and _get_map_id() not in MAP_ID_TO_DUNGEON
            and dme.read_bytes(ADDR_SCRIPT_FILE, 4).decode("ascii", "replace") in TOWN_SCRIPTS)


def _get_map_id() -> int:
    return _read_byte(ADDR_MAP_ID)


def _get_dungeon_cycle(map_id: int) -> int:
    raw = _read_byte(ADDR_CYCLE_BASE + map_id * 4)
    return raw + 1  # game stores 0/1/2, we want 1/2/3


def _read_chest_flags() -> bytes:
    return dme.read_bytes(ADDR_CHEST_BASE, 8)


def _get_bit(data: bytes, byte_offset: int, bit_index: int) -> bool:
    if byte_offset >= len(data):
        return False
    return bool((data[byte_offset] >> bit_index) & 1)


def _add_bag_item(item_id: int) -> bool:
    """Put an item in the first empty inventory slot and count it but False if the inventory is full."""
    count = _read_short(ADDR_ITEM_COUNT)
    if count >= INVENTORY_SLOTS:
        return False
    for i in range(INVENTORY_SLOTS):
        addr = ADDR_INVENTORY + i * 2
        if _read_short(addr) == ITEM_SLOT_EMPTY:
            _write_short(addr, item_id)
            _write_short(ADDR_ITEM_COUNT, count + 1)
            return True
    return False


AP_ITEM_ID = 0x162   # the "AP Item" shops sell for other players' items


def _remove_ap_items() -> int:
    """Take every AP Item out of the bag (bought in a shop, the check is
    already sent). Returns how many were removed."""
    slots = dme.read_bytes(_relocate(ADDR_INVENTORY), INVENTORY_SLOTS * 2)
    found = [i for i in range(INVENTORY_SLOTS)
             if int.from_bytes(slots[2 * i:2 * i + 2], "big") == AP_ITEM_ID]
    for i in found:
        _write_short(ADDR_INVENTORY + 2 * i, ITEM_SLOT_EMPTY)
    if found:
        _write_short(ADDR_ITEM_COUNT, max(0, _read_short(ADDR_ITEM_COUNT) - len(found)))
    return len(found)


def _hooks_reach_player() -> bool:
    """True if the item-drop and trap-visuals hooks act for the character
    being played: a patch that follows the party table, or (with an older
    patch) the save's first character."""
    return _player_offset == 0 or dme.read_bytes(ADDR_HOOK_PLAYER, 8) in (HOOK_FOLLOWS_PARTY, HOOK_ALL_PLAYERS)


def _drops_on(ctx: "FFCCContext") -> bool:
    """True if received items go on the ground: the seed's "Items Dropped At
    Your Feet" option and a game patched for it."""
    return (ctx.items_dropped_at_your_feet and dme.read_bytes(ADDR_TRAP_HOOK, 4) == ITEM_DROP_HOOK
            and _hooks_reach_player())


def _drop_or_bag(ctx: "FFCCContext", item_id: int, label: str) -> bool:
    """Give an item: on the ground in front of the player with "Items Dropped
    At Your Feet", otherwise in the bag. Returns True once it is given, False
    to try again later (the bag is full, or the game hasn't dropped the
    previous item yet)."""
    if not _drops_on(ctx) or not _can_drop(item_id):
        if _add_bag_item(item_id):
            return True
        for record in _players()[1:]:          # player 1's bag is full: the next player with room
            with _as_player(record):
                if _add_bag_item(item_id):
                    logger.info(f"FFCC: {label} went to {_character(record)["name"]}'s bag.")
                    return True
        logger.warning("FFCC: Item bag is full - cannot deliver item, will retry.")
        return False
    return _drop_item(ctx, item_id, label)


def _can_drop(item_id: int) -> bool:
    """False for equipment (ids up to LAST_EQUIPMENT_ID): it can't be an item
    on the ground, and the game hangs trying to drop one."""
    return item_id > LAST_EQUIPMENT_ID


def _artifact_drops_on(ctx: "FFCCContext") -> bool:
    """True if received artifacts go on the ground: "Items Dropped At Your
    Feet" and "Keep Picked-Up Artifacts" in the seed and the game patched for
    both, so picking one up keeps it."""
    return (ctx.keep_picked_up_artifacts and _drops_on(ctx)
            and dme.read_bytes(ADDR_KEEP_ARTIFACTS, 4) == KEEP_ARTIFACTS_CODE)


def _drop_or_give_artifact(ctx: "FFCCContext", artifact_id: int, label: str) -> bool:
    """Give an artifact: at the player's feet when _artifact_drops_on,
    otherwise straight into the artifact list."""
    if _artifact_drops_on(ctx):
        return _drop_item(ctx, artifact_id, label)
    return _give_artifact(artifact_id)


def _drop_item(ctx: "FFCCContext", item_id: int, label: str) -> bool:
    """Drop an item in front of the player. One item is dropped at a time:
    it is written to ADDR_ITEM_DROP and counts as given (True) once the game
    has cleared that. False until then."""
    if ctx.in_town and ctx.dropping is None and _read_int(ADDR_SHOP_MENU) != 0:
        return False    # in a shop: it drops once the menu is closed
    waiting = _read_short(ADDR_ITEM_DROP)
    if ctx.dropping == item_id and waiting == 0:
        ctx.dropping = None
        ctx.last_dropped = (item_id, label)
        logger.info(f"FFCC: {label} dropped at your feet.")
        return True
    if waiting == item_id and ctx.dropping is None:
        ctx.dropping = item_id        # written before a reconnect
    if waiting == 0 and ctx.dropping is None:
        _write_short(ADDR_ITEM_DROP, item_id)
        ctx.dropping = item_id
    return False


def _give_equipment(ctx: "FFCCContext", item_name: str) -> bool:
    """Put the next weapon, armor or tribal piece for the player's tribe in
    the bag, to equip from the menu. Returns False to try again later (bag
    full)."""
    paths = EQUIPMENT_PATHS[item_name]
    tribe = _read_short(ADDR_TRIBE)
    if tribe >= len(paths):
        logger.warning(f"FFCC: Unknown tribe {tribe} - {item_name} skipped.")
        return True
    path = paths[tribe]

    # The Nth copy received gives the Nth piece of the path (this copy is the
    # item at ctx.received_index, still being delivered).
    copies = sum(1 for net_item in ctx.items_received[:ctx.received_index + 1]
                 if LOOKUP_ID_TO_NAME.get(net_item.item) == item_name)
    if copies > len(path):
        logger.info(f"FFCC: {item_name}: you already have the best one for your tribe.")
        return True
    piece = path[copies - 1]
    piece_name = EQUIPMENT_NAMES.get(piece, hex(piece))

    # Always the bag: equipment can't be an item on the ground (the game hangs
    # trying to drop one), so it is never dropped at the player's feet.
    if not _add_bag_item(piece):
        logger.warning("FFCC: Item bag is full - cannot deliver item, will retry.")
        return False
    logger.info(f"FFCC: {item_name}: {piece_name} put in your bag. Equip it from the menu.")
    return True


def _artifact_addr(artifact_id: int) -> int | None:
    """Address of an artifact's fixed place, or None if it isn't an artifact ID."""
    place = artifact_id - ARTIFACT_FIRST_ID
    return ADDR_ARTIFACT + place * 2 if 0 <= place < ARTIFACT_SLOTS else None

# Command processor


class FFCCCommandProcessor(BaseCommandProcessor):
    def _cmd_dolphin(self) -> None:
        """Show Dolphin connection status."""
        if isinstance(self.ctx, FFCCContext):
            logger.info(f"Dolphin status: {self.ctx.dolphin_status}")

    def _cmd_party(self) -> bool:
        """Show the save's characters and who each controller is playing.
        Items, traps and DeathLink go to the character on player 1."""
        if not dme.is_hooked():
            logger.info("Dolphin isn't connected.")
            return False
        party = _party()
        logger.info(f"Caravan of {_town_name()}:")
        for record in range(CARAVAN_MEMBERS):
            who = _character(record)
            if who["name"] == EMPTY_CHARACTER:
                continue
            ports = [str(port + 1) for port, r in enumerate(party) if r == record]
            playing = f"  <- controller {", ".join(ports)}" if ports else ""
            logger.info(f"  {record + 1}. {who["name"]} ({who["tribe"]}, {who["gender"]}){playing}")
        return True

    def _cmd_element(self, element: str = "") -> bool:
        """Set the chalice element: /element fire|water|wind|earth|unknown.
        Without a name, shows the current element. Unknown crosses every
        Miasma Stream, so only use it if you are stuck."""
        if not dme.is_hooked():
            logger.info("Dolphin isn't connected.")
            return False
        names = {v: k.capitalize() for k, v in CHALICE_ELEMENTS.items()}
        if not element:
            current = _read_byte(ADDR_CHALICE)
            logger.info(f"Chalice element: {names.get(current, f'none ({current})')}")
            return True
        value = CHALICE_ELEMENTS.get("unknown" if element.lower() == "holy" else element.lower())
        if value is None:
            logger.info(f"Unknown element {element!r}. Use one of: {", ".join(CHALICE_ELEMENTS)}")
            return False
        _write_byte(ADDR_CHALICE, value)
        logger.info(f"Chalice element set to {names[value]}.")
        return True

    def _cmd_stagekeys(self, mode: str = "") -> bool:
        """Turn the stage-key locks off or back on: /stagekeys off|on.
        "off" puts every dungeon's key in your artifact bag so all dungeons
        open (handy if you're stuck, dungeons may then be out of logic).
        "on" takes back the keys you haven't received from the multiworld.
        Without on/off, shows which keys you have."""
        if not isinstance(self.ctx, FFCCContext) or not dme.is_hooked():
            logger.info("Dolphin isn't connected.")
            return False
        received = _received_stage_keys(self.ctx)
        in_bag = _stage_keys_in_bag()
        mode = mode.lower()
        if mode == "off":
            added = 0
            for name, key_id in STAGE_KEYS:
                if key_id not in in_bag:
                    _give_artifact(key_id)
                    added += 1
            logger.info(f"Stage keys off: {added} key(s) added, every dungeon is open. "
                        f"Use /stagekeys on to undo.")
            return True
        if mode == "on":
            removed = _remove_stage_keys(keep=received)
            logger.info(f"Stage keys on: {removed} key(s) you haven't received were taken back.")
            return True
        if mode:
            logger.info("Use /stagekeys off or /stagekeys on.")
            return False
        extra = in_bag - received
        logger.info(f"Stage keys received: {len(received)}/{len(STAGE_KEYS)}"
                    + (f" - locks are off ({len(extra)} extra key(s) in your bag)" if extra else ""))
        for name, key_id in STAGE_KEYS:
            if key_id in received:
                logger.info(f"  {name}")
        missing = [name for name, key_id in STAGE_KEYS if key_id not in received]
        if missing:
            logger.info("Still to find: " + ", ".join(missing))
        return True

    def _cmd_tree(self, *name: str) -> bool:
        """Show every dungeon's Myrrh tree, or restore one so its Myrrh can be
        collected again: /tree river (any unique part of the dungeon name)."""
        if not dme.is_hooked():
            logger.info("Dolphin isn't connected.")
            return False
        query = " ".join(name).lower().strip()
        if not query:
            for n, dungeon in enumerate(MYRRH_TREE_DUNGEONS):
                state = _read_byte(ADDR_MYRRH_TREE + 4 * n)
                text = "ready" if state >= MYRRH_TREE_READY else f"regrowing ({state}%)"
                logger.info(f"{dungeon}: {text}")
            return True
        matches = [n for n, d in enumerate(MYRRH_TREE_DUNGEONS) if query in d.lower()]
        if len(matches) != 1:
            logger.info(f"Name one dungeon: {", ".join(MYRRH_TREE_DUNGEONS)}")
            return False
        n = matches[0]
        _write_byte(ADDR_MYRRH_TREE + 4 * n, MYRRH_TREE_READY)
        logger.info(f"{MYRRH_TREE_DUNGEONS[n]}'s Myrrh tree is ready again.")
        return True

    def _cmd_cycle(self, *args: str) -> bool:
        """Show every dungeon's cycle, or set one: /cycle river 2 (any unique
        part of the dungeon name, then 1-3). The new cycle applies the next
        time the dungeon is entered."""
        if not dme.is_hooked():
            logger.info("Dolphin isn't connected.")
            return False
        if not args:
            for n, dungeon in enumerate(MYRRH_TREE_DUNGEONS):
                logger.info(f"{dungeon}: cycle {min(_read_byte(ADDR_CYCLE_BASE + 4 * n), 2) + 1}")
            return True
        if len(args) < 2 or args[-1] not in ("1", "2", "3"):
            logger.info("Usage: /cycle <dungeon> <1-3>, e.g. /cycle river 2")
            return False
        query = " ".join(args[:-1]).lower().strip()
        matches = [n for n, d in enumerate(MYRRH_TREE_DUNGEONS) if query in d.lower()]
        if len(matches) != 1:
            logger.info(f"Name one dungeon: {", ".join(MYRRH_TREE_DUNGEONS)}")
            return False
        n, cycle = matches[0], int(args[-1])
        # the game keeps a 4-byte value per dungeon: 0/1/2 = cycle 1/2/3
        dme.write_bytes(ADDR_CYCLE_BASE - 3 + 4 * n, (cycle - 1).to_bytes(4, "big"))
        if _is_in_dungeon() and _get_map_id() == n:
            logger.info(f"{MYRRH_TREE_DUNGEONS[n]} is now on cycle {cycle}. "
                        f"Make sure to reload the overworld map before entering.")
        else:
            logger.info(f"{MYRRH_TREE_DUNGEONS[n]} is now on cycle {cycle}.")
        return True

    def _cmd_status(self) -> bool:
        """Show the year, where you are, the chalice element, Myrrh trees
        collected and the stage keys you have."""
        if not isinstance(self.ctx, FFCCContext) or not dme.is_hooked():
            logger.info("Dolphin isn't connected.")
            return False
        ctx = self.ctx
        names = {v: k.capitalize() for k, v in CHALICE_ELEMENTS.items()}
        logger.info(f"Year: {_read_byte(ADDR_CURRENT_YEAR)}")
        if _is_in_dungeon():
            dungeon = MAP_ID_TO_DUNGEON.get(_get_map_id(), "a dungeon")
            logger.info(f"In {dungeon} (cycle {ctx.current_cycle})")
        else:
            logger.info("On the world map or in a town")
        element = _read_byte(ADDR_CHALICE)
        logger.info(f"Chalice element: {names.get(element, f'none ({element})')}")
        logger.info(f"Myrrh in the chalice this year: {_read_byte(ADDR_CHALICE_FILL)}/3")
        if ctx.slot is not None:
            trees = ctx.stored_data.get(_myrrh_key(ctx)) or 0
            trees |= _read_myrrh_mask()
            logger.info(f"Myrrh trees collected: {bin(trees).count("1")}/{MYRRH_DUNGEONS}")
        keys = sorted({LOOKUP_ID_TO_NAME.get(i.item, "") for i in ctx.items_received
                       if ITEM_TABLE.get(LOOKUP_ID_TO_NAME.get(i.item, "")) is not None
                       and ITEM_TABLE[LOOKUP_ID_TO_NAME[i.item]].type == "Stage Key"})
        logger.info("Stage keys: " + (", ".join(keys) if keys else "none yet"))
        return True

    def _cmd_bonus(self) -> bool:
        """Show this dungeon's bonus condition and the score earned so far
        (what the bonus screen will show when the dungeon is cleared)."""
        if not isinstance(self.ctx, FFCCContext) or not dme.is_hooked():
            logger.info("Dolphin isn't connected.")
            return False
        if not _is_in_dungeon():
            logger.info("The bonus only counts inside a dungeon.")
            return False
        bonus = _read_byte(ADDR_BONUS)
        enemies, items, knocked_out, bonus_points, score = _bonus_score()
        logger.info(f"Bonus: {BONUS_NAMES.get(bonus, f'bonus {bonus}')}")
        logger.info(f"Bonus points: {bonus_points}/100")
        logger.info(f"Enemies defeated: {enemies}, items picked up: {items}, times knocked out: {knocked_out}")
        logger.info(f"Score so far: {score}")
        dungeon = MAP_ID_TO_DUNGEON.get(_get_map_id())
        if dungeon in BONUS_TABLE and isinstance(self.ctx, FFCCContext):
            cycle = min(_read_byte(ADDR_CYCLE_BASE + 4 * _get_map_id()), 2) + 1
            thresholds = BONUS_TABLE[dungeon][0]
            entries = self.ctx.bonus_pools.get(dungeon, [])
            picked = ((self.ctx.stored_data.get(_bonus_key(self.ctx)) or {}).get(dungeon) or {}).get("picked", [])
            reached = max((t for t in range(4) if score * PLAYER_FACTOR[0] >= thresholds[t]), default=0)
            logger.info(f"{dungeon} bonus rewards, Cycle {cycle} (points needed solo; * = collected):")
            for tier in range(4):
                entry = entries[offered_entry(cycle, tier)]
                names = ", ".join(item_name(v) + ("*" if v in picked else "") for v in entry)
                here = "  <- your score" if tier == reached else ""
                logger.info(f"  Tier {tier + 1}: {solo_points(thresholds[tier])}+ points: {names}{here}")
        return True

    def _cmd_resend(self, *name: str) -> bool:
        """Give a received item again, at your feet with "Items Dropped At
        Your Feet" (otherwise in your bag): /resend for the last item dropped,
        or /resend <item name> for any item you have received (Progressive
        Equipment gives your latest piece). Only works inside a dungeon."""
        if not isinstance(self.ctx, FFCCContext) or self.ctx.slot is None or not dme.is_hooked():
            logger.info("Connect to the server and Dolphin first.")
            return False
        ctx = self.ctx
        if not (_is_in_dungeon() or _is_in_town()):
            logger.info("Items can only be given inside a dungeon or a town.")
            return False
        wanted = " ".join(name).strip().lower()
        if not wanted:
            if ctx.last_dropped is None:
                logger.info("No item has been dropped yet. Use /resend <item name>.")
                return False
            item_id, label = ctx.last_dropped
        else:
            received = [LOOKUP_ID_TO_NAME.get(i.item, "") for i in ctx.items_received]
            match = next((n for n in received if n.lower() == wanted), None)
            if match is None:
                logger.info(f"You haven't received an item called {" ".join(name)!r}.")
                return False
            data = ITEM_TABLE[match]
            if data.type == "Progressive Equipment":
                paths = EQUIPMENT_PATHS[match]
                tribe = _read_short(ADDR_TRIBE)
                copies = min(received.count(match), len(paths[tribe]))
                item_id = paths[tribe][copies - 1]
                label = EQUIPMENT_NAMES.get(item_id, match)
            elif (data.item_id is None or data.type == "Trap" or data.type == "Stage Key"
                  or (data.type == "Artifact" and not _artifact_drops_on(ctx))):
                logger.info(f"{match} can't be resent.")
                return False
            else:
                item_id, label = data.item_id, match
        if _drops_on(ctx) and _can_drop(item_id):
            if _read_short(ADDR_ITEM_DROP) != 0:
                logger.info("Another item is still waiting to be dropped. Try again in a moment.")
                return False
            _write_short(ADDR_ITEM_DROP, item_id)
            ctx.last_dropped = (item_id, label)
            logger.info(f"FFCC: {label} will be dropped at your feet.")
        elif _add_bag_item(item_id):
            logger.info(f"FFCC: {label} put in your bag.")
        else:
            logger.info("Your bag is full.")
            return False
        return True

    def _cmd_deathlink(self, mode: str = "") -> bool:
        """Turn DeathLink on or off for this slot: /deathlink on, /deathlink
        off, or /deathlink to see it. The choice is kept on the server, so it
        lasts through reconnects. /deathlink default goes back to the seed's
        setting."""
        if not isinstance(self.ctx, FFCCContext) or self.ctx.slot is None:
            logger.info("Connect to the server first.")
            return False
        ctx = self.ctx
        mode = mode.lower()
        if mode not in ("", "on", "off", "default"):
            logger.info("Use /deathlink on, /deathlink off or /deathlink default.")
            return False
        if mode:
            on = ctx.death_link_seed if mode == "default" else mode == "on"
            value = None if mode == "default" else on
            Utils.async_start(ctx.update_death_link(on))
            Utils.async_start(ctx.send_msgs([{"cmd": "Set", "key": _deathlink_key(ctx), "default": None,
                                              "operations": [{"operation": "replace", "value": value}]}]))
        else:
            on = "DeathLink" in ctx.tags
        logger.info(f"DeathLink is {"on" if on else "off"}"
                    + (" (the seed's setting)." if mode in ("", "default") and on == ctx.death_link_seed
                       else "."))
        return True

    def _cmd_regrow(self) -> bool:
        """Grow the Moogle's fur back to full length (its colours stay). Use it in
        a Moogle Nest."""
        if not dme.is_hooked():
            logger.info("Dolphin isn't connected.")
            return False
        if not _in_moogle_nest():
            logger.info("Go into a Moogle Nest first.")
            return False
        fur = bytearray(dme.read_bytes(ADDR_MOG_FUR, 2 * MOG_FUR_TEXELS))
        for i in range(0, len(fur), 2):
            fur[i] |= 0x70                    # the length bits: full
        dme.write_bytes(ADDR_MOG_FUR, bytes(fur))
        logger.info("The Moogle's fur has grown back. It shows on your next stroke with a grooming tool.")
        return True

    def _cmd_hunt(self) -> bool:
        """Show the Monster Hunt: how many enemy types are defeated and the
        ones still to find, by the dungeon they appear in most."""
        if not isinstance(self.ctx, FFCCContext) or self.ctx.slot is None:
            logger.info("Connect to the server first.")
            return False
        ctx = self.ctx
        wanted = hunt_list(ctx.monster_hunt_bosses)
        done = _defeated(ctx)
        logger.info(f"Monster Hunt: {sum(1 for e in wanted if e in done)}/{len(wanted)} enemy types defeated")
        left: dict[str, list[str]] = {}
        for enemy in wanted:
            if enemy not in done:
                left.setdefault(MONSTERS[enemy][3], []).append(enemy)
        for dungeon, enemies in left.items():
            logger.info(f"  {dungeon}: {", ".join(enemies)}")
        return True


class FFCCContext(BaseContext):
    command_processor = FFCCCommandProcessor
    game = game_name
    items_handling = 0b111  # full remote items
    victory: int

    def __init__(self, server_address: str | None, password: str | None) -> None:
        super().__init__(server_address, password)
        self.tags = {"AP"}
        self.items_handling = 0b111
        self.dolphin_status:   str = CONNECTION_INITIAL_STATUS
        self.dolphin_sync_task: asyncio.Task | None = None

        # Game state
        self.current_dungeon:  str | None = None
        self.reported_stage:   str | None = None  # last stage sent for PopTracker's auto tab
        self.reported_cycles:  dict[str, int] | None = None  # last cycles sent for PopTracker
        self.current_cycle:    int = 1
        self.current_year:     int | None = None
        self.prev_chest_flags: bytes = bytes(8)
        self.received_index:   int = 0  # items processed so far
        self.victory: int = 0

        # Settings loaded from slot_data
        self.progressive_artifacts: bool = False
        self.magicite_needs_ring:   bool = False
        self.monster_hunt_checks:   int = 0     # 0 off, 1 enemy types, 2 every enemy
        self.items_dropped_at_your_feet: bool = False
        self.keep_picked_up_artifacts:  bool = False
        self.free_cure_magicite:    bool = False
        self.cure_pending:          bool = False  # a Stone of Cure is owed for this dungeon visit
        self.player_record: int | None = None  # the save's character player 1 plays
        self.given_to:      set[int] = set()      # players who have the item being delivered
        self.cure_given:    set[int] = set()      # players who have this visit's Stone of Cure
        self.dead_players:  set[int] = set()      # players whose death was already sent
        self.synced:        tuple | None = None  # last party/items the artifact sync saw
        self.dropping:              int | None = None              # item id waiting to be dropped
        self.last_dropped:          tuple[int, str] | None = None  # (item id, name), for /resend
        self.monster_hunt_bosses:   bool = True
        self.monster_hp:            dict[int, tuple[int, int, int]] = {}  # slot -> (owner, id, HP) last seen
        self.group_spots_done:      set[tuple] = set()  # switch-group spots credited this dungeon visit
        self.in_town:               bool = False
        self.shop_checks:           bool = False
        self.stamp_hints:           list[list[int]] = []   # [player, location] of own progression items
        self.stamps_seen:           int | None = None   # Mog Stamps last reported (Mog Stamps goal)
        self.stamps_reported:       int = 0                # Mog Stamps put in data storage (trackers)
        self.shop_gil:              int | None = None   # gil last seen with a shop open
        self.shop_buying:           int | None = None   # slot on the yes/no screen
        self.hide_collected_chests: bool = False
        self.bonus_pools:           dict[str, list[list[int]]] = make_bonus_pools()
        self.bonus_recorded:        tuple[str, int, int] | None = None  # last pick sent
        self.reported_live:         dict[str, Any] | None = None        # last live score sent
        self.progressive_count:     int = 0   # how many progressive arts received
        self.artifact_order:        list[int] = list(PROGRESSIVE_ARTIFACT_ORDER)
        self.include_traps:         bool = True
        self.trap_weights:          dict[str, int] = {}
        self.death_link_enabled:    bool = False
        self.death_link_seed:       bool = False   # the seed's DeathLink option

        # AP location IDs where the hybrid patcher wrote the real item into the chest.
        # The game engine gives those items on pickup, so we skip the memory-write
        # when ReceivedItems delivers them to avoid a double-give.
        self.physical_chest_ap_ids: set[int] = set()

        # Mog grooming (the Mog Grooming goal and the Grooming Tools option)
        self.grooming_tools:        bool = False
        self.grooming_goal:         int = 0     # 0 dye, 1 trim, 2 both
        self.grooming_percent:      int = 50
        self.grooming_shown:        tuple[str, str] | None = None   # the grooming lines on screen
        self.grooming_checks:       bool = False   # the seed has Mog grooming checks
        self.grooming_reported:     tuple[int, int] | None = None

        # item messages on the game's screen (the HUD)
        self.item_messages:         bool = True
        self.hud_queue:             deque[str] = deque()
        self.hud_lines:             list[tuple[str, float, float]] = []   # (text, shown at, hide at), newest first
        self.hud_last_line:         float = 0.0

    async def server_auth(self, password_requested: bool = True) -> None:
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict) -> None:
        if cmd == "Connected":
            slot_data = args.get("slot_data", {})
            self.reported_stage = None
            self.reported_cycles = None
            self.progressive_artifacts = bool(slot_data.get("progressive_artifacts", False))
            self.magicite_needs_ring = bool(slot_data.get("magicite_needs_ring", False))
            self.hide_collected_chests = bool(slot_data.get("hide_collected_chests", False))
            self.monster_hunt_checks = int(slot_data.get("monster_hunt_checks", 0))
            self.items_dropped_at_your_feet = bool(slot_data.get("items_dropped_at_your_feet", False))
            self.keep_picked_up_artifacts = bool(slot_data.get("keep_picked_up_artifacts", False))
            self.free_cure_magicite = bool(slot_data.get("free_cure_magicite", False))
            self.dropping = None
            self.monster_hunt_bosses = bool(slot_data.get("monster_hunt_bosses", True))
            self.monster_hp = {}
            self.shop_checks = bool(slot_data.get("shop_checks", False))
            self.stamp_hints = slot_data.get("stamp_hints") or []
            self.stamps_reported = 0
            if self.stamp_hints:
                self.set_notify(_stamps_key(self))
            self.shop_gil = self.shop_buying = None
            self.set_notify(_hunt_key(self))
            # seeds from before the bonus pools were decided by the world use the vanilla ones
            self.bonus_pools = slot_data.get("bonus_pools") or make_bonus_pools()
            self.bonus_recorded = None
            self.reported_live = None
            self.set_notify(_bonus_key(self))
            # seeds from before the Progressive Artifact Order option use the game order
            self.artifact_order = slot_data.get("progressive_artifact_order") or list(PROGRESSIVE_ARTIFACT_ORDER)
            self.include_traps = bool(slot_data.get("include_traps", True))
            self.trap_weights = {
                "Frozen Trap":          slot_data.get("frozen_trap_weight", 2),
                "Burned Trap":          slot_data.get("burned_trap_weight", 2),
                "Slowed Trap":          slot_data.get("slowed_trap_weight", 2),
                "Poisoned Trap":        slot_data.get("poisoned_trap_weight", 1),
                "Chalice Element Trap": slot_data.get("chalice_element_trap_weight", 1),
                "Bonus Set Trap":       slot_data.get("bonus_set_trap_weight", 1),
                "Food Preference Trap": slot_data.get("food_preference_trap_weight", 1),
            }
            self.set_notify(_myrrh_key(self))
            if slot_data.get("victory_goal"):
                self.victory = args["slot_data"]["victory_goal"]
            # DeathLink follows the seed, unless the player switched it with
            # /deathlink (kept in data storage, applied once it arrives)
            self.death_link_seed = bool(slot_data.get("death_link"))
            Utils.async_start(self.update_death_link(self.death_link_seed))
            self.set_notify(_deathlink_key(self))
            # seeds from before the client worked this out send the list
            self.physical_chest_ap_ids = set(slot_data.get("physical_chest_ap_ids", []))
            self.item_messages = bool(slot_data.get("item_messages", True))
            self.grooming_tools = bool(slot_data.get("grooming_tools", False))
            self.grooming_goal = int(slot_data.get("mog_grooming_goal", 0))
            self.grooming_percent = min(int(slot_data.get("mog_grooming_percent", 50)), 95)
            self.grooming_checks = bool(slot_data.get("mog_grooming_checks", 0))
            self.grooming_shown = None
            self.grooming_reported = None
            self.hud_queue.clear()
            if self.physical_chest_ap_ids:
                logger.debug(f"FFCC: Hybrid patch active — {len(self.physical_chest_ap_ids)} "
                             f"chest(s) contain real items, client will skip those on receive.")
        super().on_package(cmd, args)
        if cmd in ("Retrieved", "SetReply") and self.slot is not None:
            values = args.get("keys", {}) if cmd == "Retrieved" else {args.get("key"): args.get("value")}
            choice = values.get(_deathlink_key(self))
            if isinstance(choice, bool):
                Utils.async_start(self.update_death_link(choice))

    def on_print_json(self, args: dict) -> None:
        super().on_print_json(args)
        # an item of ours found that belongs to someone else: say who it went to
        if args.get("type") != "ItemSend" or self.slot is None:
            return
        item, receiving = args.get("item"), args.get("receiving")
        if item is None or receiving is None:
            return
        if hasattr(item, "item"):
            item_id, sender = item.item, item.player
        elif isinstance(item, dict):
            item_id, sender = item.get("item"), item.get("player")
        else:
            item_id, sender = item[0], item[2]
        if sender == self.slot and receiving != self.slot:
            name = self.item_names.lookup_in_slot(item_id, receiving)
            _hud_message(self, f"Sent {name} to {self.player_names.get(receiving, receiving)}")

    def on_deathlink(self, data: dict) -> None:
        super().on_deathlink(data)
        if dme.is_hooked() and _is_in_dungeon():
            logger.info("DeathLink received - the whole party falls.")
            for record in _players():
                with _as_player(record):
                    _write_byte(ADDR_CUR_HEARTS, 0)
                self.dead_players.add(record)     # not sent back as a death of our own

    def make_gui(self) -> type:
        ui = super().make_gui()
        ui.base_title = "Archipelago FFCC Client"
        return ui


# Item giving

def _give_item(ctx: FFCCContext, item_name: str) -> bool:
    """Write an item to game memory. Returns True on success."""
    if not dme.is_hooked() or not (_is_in_dungeon() or _is_in_town()):
        return False

    data = ITEM_TABLE.get(item_name)
    if not data:
        logger.warning(f"Unknown item: {item_name!r}")
        return True  # skip unknown items

    if data.type == "Trap":
        _apply_trap(ctx, item_name)
        return True

    if item_name == PROGRESSIVE_ARTIFACT_NAME:
        if ctx.progressive_count < len(ctx.artifact_order):
            art_id = ctx.artifact_order[ctx.progressive_count]
            if not _drop_or_give_artifact(ctx, art_id, ITEM_NAME_BY_ID.get(art_id, item_name)):
                return False  # not dropped yet, try again next tick
            ctx.progressive_count += 1
        return True

    if data.type == "Progressive Equipment":
        return _for_each_player(ctx, lambda: _give_equipment(ctx, item_name))

    if data.type == "Gil":
        _add_gil(GIL_AMOUNT[item_name])
        return True

    if data.item_id is None:
        return True

    if data.type == "Artifact":
        return _drop_or_give_artifact(ctx, data.item_id, item_name)
    if data.type in PERMANENT_ARTIFACT_TYPES:
        return _give_artifact(data.item_id)     # stage keys always go straight to the list

    # Spell Rings go in every player's bag
    if data.type == "Spell Ring":
        return _for_each_player(ctx, lambda: _give_spell_ring(ctx, data.item_id))

    # Materials, Food, Recipes, Magicite, Phoenix Down: in the bag, or on the
    # ground with "Items Dropped At Your Feet"
    return _drop_or_bag(ctx, data.item_id, item_name)


def _received_stage_keys(ctx: "FFCCContext") -> set[int]:
    """In-game IDs of the stage keys received from the multiworld."""
    ids = {ITEM_TABLE[name].item_id for name, _ in STAGE_KEYS}
    out = set()
    for net_item in ctx.items_received:
        data = ITEM_TABLE.get(LOOKUP_ID_TO_NAME.get(net_item.item, ""))
        if data is not None and data.item_id in ids:
            out.add(data.item_id)
    return out


def _stage_keys_in_bag() -> set[int]:
    """In-game IDs of the stage keys the caravan has."""
    return {key_id for _, key_id in STAGE_KEYS if _read_short(_artifact_addr(key_id)) == key_id}


def _remove_stage_keys(keep: set[int]) -> int:
    """Take away the stage keys not in `keep`."""
    removed = 0
    for key_id in _stage_keys_in_bag() - keep:
        _write_short(_artifact_addr(key_id), ITEM_SLOT_EMPTY)
        removed += 1
    return removed


def _give_spell_ring(ctx: "FFCCContext", ring_id: int) -> bool:
    """Put a Spell Ring in the current player's bag. With
    "Magicite Needs Its Ring" the game checks the permanent artifact list for
    the ring, so the game's own rings also take their artifact place. False
    while the bag is full."""
    if ctx.magicite_needs_ring and ring_id not in EXTRA_RING_IDS:
        _give_artifact(ring_id)
    if not _add_bag_item(ring_id):
        logger.warning(f"FFCC: {_character(_player_offset // CARAVAN_SIZE)["name"]}'s bag is full - "
                       "the ring waits until there is room.")
        return False
    return True


def _add_gil(amount: int) -> None:
    """Add gil to player 1's character, up to the game's limit."""
    gil = min(_read_int(ADDR_GIL) + amount, MAX_GIL)
    _write_int(ADDR_GIL, gil)
    logger.info(f"FFCC: {amount} gil added ({gil} gil now).")


def _received_artifacts(ctx: "FFCCContext") -> list[int]:
    """The artifact places player 1 has from the multiworld so far:
    artifacts, Progressive Artifacts, stage keys and (with "Magicite Needs
    Its Ring") the game's own Spell Rings."""
    out = list(ctx.artifact_order[:ctx.progressive_count])
    for net_item in ctx.items_received[:ctx.received_index]:
        data = ITEM_TABLE.get(LOOKUP_ID_TO_NAME.get(net_item.item, ""))
        if data is None or data.item_id is None:
            continue
        if data.type in PERMANENT_ARTIFACT_TYPES or (
                data.type == "Spell Ring" and ctx.magicite_needs_ring and data.item_id not in EXTRA_RING_IDS):
            out.append(data.item_id)
    return out


def _sync_party(ctx: "FFCCContext") -> None:
    """Give the other players everything player 1 got that every player
    should have: the artifact places of _received_artifacts and the Spell
    Rings (in the bag, if there is room). Writing a place twice does nothing,
    so this also catches up a player who joins later. Runs when the party or
    the delivered items change."""
    players = _players()
    state = (tuple(players), ctx.received_index, ctx.progressive_count)
    if len(players) < 2 or state == ctx.synced:
        ctx.synced = state
        return
    ctx.synced = state
    places = _received_artifacts(ctx)
    rings = {ITEM_TABLE[name].item_id for name in (LOOKUP_ID_TO_NAME.get(i.item, "")
                                                   for i in ctx.items_received[:ctx.received_index])
             if name in ITEM_TABLE and ITEM_TABLE[name].type == "Spell Ring"}
    for record in players[1:]:
        with _as_player(record):
            for artifact_id in places:
                _give_artifact(artifact_id)
            bag = {_read_short(ADDR_INVENTORY + 2 * i) for i in range(INVENTORY_SLOTS)}
            for ring_id in rings - bag:
                _add_bag_item(ring_id)


def _give_artifact(artifact_id: int) -> bool:
    """Give a permanent artifact by filling its set place"""
    addr = _artifact_addr(artifact_id)
    if addr is None:
        logger.warning(f"FFCC: 0x{artifact_id:x} is not an artifact - skipped.")
        return True
    _write_short(addr, artifact_id)
    return True


def _apply_trap(ctx: FFCCContext, trap_name: str) -> None:
    """Apply a trap effect to a random player (the chalice is the caravan's,
    so that trap hits everyone)."""
    players = _players() or [ctx.player_record or 0]
    target = random.choice(players)
    if len(players) > 1 and trap_name != "Chalice Element Trap":
        logger.info(f"FFCC: {trap_name} hits {_character(target)["name"]}.")
    with _as_player(target):
        _apply_trap_to(trap_name, _visuals_table(target))


def _visuals_table(record: int) -> int | None:
    """Address of the trap-visuals pending table that serves this player, or
    None if the game's patch doesn't serve them (the status is then set
    directly, without its particles and sound)."""
    if dme.read_bytes(ADDR_TRAP_HOOK, 4) not in TRAP_HOOK_WORDS:
        return None
    party = _party()
    if record not in party:
        return None
    controller = party.index(record)
    if dme.read_bytes(ADDR_HOOK_PLAYER, 8) == HOOK_ALL_PLAYERS:
        return ADDR_TRAP_PENDING + TRAP_PENDING_STRIDE * controller
    if controller == 0 and _hooks_reach_player():
        return ADDR_TRAP_PENDING
    return None


def _apply_trap_to(trap_name: str, table: int | None) -> None:
    """Apply a trap to the current player (see _as_player). A status trap
    goes through `table` (_visuals_table) when there is one."""
    if trap_name in TRAP_STATUS_INDEX:
        _apply_status_trap(trap_name, table)
    elif trap_name == "Chalice Element Trap":
        elements = [0x01, 0x02, 0x04, 0x08]  # Fire, Water, Wind, Earth (never the Unknown element)
        current = _read_byte(ADDR_CHALICE)
        choices = [e for e in elements if e != current] or elements
        _write_byte(ADDR_CHALICE, random.choice(choices))
    elif trap_name == "Bonus Set Trap":
        # Randomize bonus set (0x01–0x18 = 24 possible bonuses)
        _write_byte(ADDR_BONUS, random.randint(1, 0x18))
    elif trap_name == "Food Preference Trap":
        # Scramble all 8 food favorite values (2 bytes each, 0x00–0x64)
        for i in range(8):
            _write_short(ADDR_FOOD_BASE + i * 2, random.randint(0, 0x64))
    elif trap_name == "Command Slot Trap":
        _clear_command_slot()


def _clear_command_slot() -> None:
    """Take one random command (not Attack or Defend) off player 1's command
    list, the way the game does it. A fused spell the command was part of comes apart"""
    count = min(_read_short(ADDR_CMD_COUNT), 8)
    slots = [_read_short(ADDR_CMD_SLOTS + 2 * i) for i in range(8)]
    used = [i for i in range(FIXED_COMMANDS, count) if slots[i] != 0xffff]
    if not used:
        logger.debug("FFCC: Command Slot Trap - no command to take away.")
        return
    index = random.choice(used)
    fused = [_read_short(ADDR_CMD_FUSED + 2 * i) for i in range(8)]
    if fused[index] != 0:
        start = index
        while start > FIXED_COMMANDS and fused[start] == 0xffff:
            start -= 1
        end = start + 1
        while end < 8 and fused[end] == 0xffff:
            end += 1
        for i in range(start, end):
            _write_short(ADDR_CMD_FUSED + 2 * i, 0)
    _write_short(ADDR_CMD_SLOTS + 2 * index, 0xffff)
    for addr in (ADDR_CMD_CURRENT, ADDR_CMD_WEAPON):
        if _read_short(addr) == index:
            _write_short(addr, 0)
    logger.debug(f"FFCC: Command Slot Trap - command {index + 1} was taken off your command list.")

# Chest detection


def _find_new_chest_locations(dungeon: str, cycle: int,
                              prev: bytes, curr: bytes) -> list[str]:
    """Return AP location names for chest bits that flipped 0→1."""
    flags = CHEST_FLAGS.get(dungeon, {})
    found = []
    for byte_off in range(8):
        for bit_idx in range(8):
            if _get_bit(prev, byte_off, bit_idx) or not _get_bit(curr, byte_off, bit_idx):
                continue
            hit = flags.get((byte_off, bit_idx))
            if hit is None:
                # gil-only chests and anything not in the table
                logger.debug(f"FFCC: Unmapped chest flag byte={byte_off}, bit={bit_idx} in {dungeon!r}")
                continue
            chest, cycles = hit
            loc_name = _chest_location(dungeon, cycle, chest)
            logger.debug(f"FFCC: Chest flag (byte={byte_off}, bit={bit_idx}) → {loc_name!r}")
            if cycle in cycles and loc_name in LOCATION_TABLE and loc_name not in found:
                found.append(loc_name)
    return found

# Death detection


def _deliver_items(ctx: FFCCContext) -> None:
    """Give the received items this save doesn't have yet, in order."""
    # Start after the ones this save already has (the count is stored in the
    # save itself).
    if ctx.items_received:
        delivered = _read_short(ADDR_ITEMS_DELIVERED)
        if delivered > len(ctx.items_received):
            delivered = 0      # a save from a different seed
        if delivered != ctx.received_index:
            ctx.received_index = delivered
            ctx.progressive_count = sum(
                1 for i in ctx.items_received[:delivered]
                if LOOKUP_ID_TO_NAME.get(i.item) == PROGRESSIVE_ARTIFACT_NAME)
        for idx in range(ctx.received_index, len(ctx.items_received)):
            network_item = ctx.items_received[idx]
            item_name = LOOKUP_ID_TO_NAME.get(network_item.item)

            # The game gave this one itself (the patcher put it in its chest or
            # shop), so it isn't given again.
            if _given_by_the_game(ctx, network_item):
                logger.debug(f"FFCC: {item_name or "?"} already given by chest — skipping write")
            elif item_name:
                if not _give_item(ctx, item_name):
                    break  # try again next tick
                item_data = ITEM_TABLE.get(item_name)
                if not item_data or item_data.type != "Placeholder":
                    logger.debug(f"FFCC: Received {item_name}")
                    if network_item.player == ctx.slot:
                        _hud_message(ctx, f"Found {item_name}")
                    else:
                        _hud_message(ctx, f"Received {item_name} from "
                                     f"{ctx.player_names.get(network_item.player, network_item.player)}")
            ctx.given_to = set()
            ctx.received_index = idx + 1
            _write_short(ADDR_ITEMS_DELIVERED, ctx.received_index)
    _sync_party(ctx)


def _given_by_the_game(ctx: "FFCCContext", network_item: NetworkItem) -> bool:
    """True if the game gave this received item itself: one of this player's
    own items that the patcher put in its chest or shop
    (locations.game_gives_item)."""
    if network_item.location in ctx.physical_chest_ap_ids:
        return True
    if network_item.player != ctx.slot:
        return False
    location = LOCATION_NAME_BY_ID.get(network_item.location)
    item_name = LOOKUP_ID_TO_NAME.get(network_item.item)
    return location is not None and item_name is not None and game_gives_item(item_name, location)


def _hud_message(ctx: "FFCCContext", text: str) -> None:
    """Queue a line for the game's screen (shown by _update_hud)."""
    if ctx.item_messages:
        ctx.hud_queue.append(text)


def _hud_installed() -> bool:
    return int.from_bytes(dme.read_bytes(ADDR_HUD_HOOK, 4), "big") == HUD_HOOK_WORD


def _hud_line(text: str, line: int, frames: int) -> bytes:
    """One message slot: a box across the bottom of the screen, `line` lines
    up from the bottom (0 = the bottom line)."""
    text = text.encode("ascii", "replace")
    if len(text) > HUD_TEXT_MAX:
        text = text[:HUD_TEXT_MAX - 3] + b"..."
    y = 372.0 - 34.0 * line
    slot = bytearray(HUD_SLOT_SIZE)
    slot[0], slot[1] = 1 | 2, 0x15                         # shown with a box, in white text
    slot[2:4] = min(frames, 0xFFFF).to_bytes(2, "big")
    slot[4:0x20] = struct.pack(">7f", 80.0, y, 480.0, 30.0, 94.0, y + 5.0, 0.8)
    slot[0x20:0x2C] = bytes((200, 210, 230, 200, 20, 30, 45, 190, 255, 255, 255, 255))
    slot[0x2C:0x2C + len(text)] = text
    return bytes(slot)


def _update_hud(ctx: "FFCCContext") -> None:
    """Show the queued messages as lines at the bottom of the screen, newest
    at the bottom, each for HUD_SHOW_SECONDS. With more waiting, a new line
    pushes the oldest out once it has been up HUD_BUSY_SECONDS, so a burst of
    items goes by quickly but every one is shown."""
    if not ctx.hud_queue and not ctx.hud_lines:
        return
    if not _hud_installed():                 # an ISO without the HUD
        ctx.hud_queue.clear()
        ctx.hud_lines = []
        return
    now = time.monotonic()
    lines = [line for line in ctx.hud_lines if line[2] > now]
    changed = len(lines) != len(ctx.hud_lines)
    if ctx.hud_queue and now - ctx.hud_last_line >= HUD_GAP_SECONDS:
        if len(lines) == len(HUD_MESSAGE_SLOTS) and now - lines[-1][1] >= HUD_BUSY_SECONDS:
            lines.pop()
        if len(lines) < len(HUD_MESSAGE_SLOTS):
            lines.insert(0, (ctx.hud_queue.popleft(), now, now + HUD_SHOW_SECONDS))
            ctx.hud_last_line = now
            changed = True
    ctx.hud_lines = lines
    if not changed:
        return
    for line, slot in enumerate(HUD_MESSAGE_SLOTS):
        at = ADDR_HUD_SLOTS + HUD_SLOT_SIZE * slot
        if line < len(lines):
            text, _, hide_at = lines[line]
            # the game hides it by itself too, in case the client goes away
            dme.write_bytes(at, _hud_line(text, line, int((hide_at - now) * 30) + 15))
        else:
            dme.write_bytes(at, bytes(4))       # hidden


def _in_moogle_nest() -> bool:
    return dme.read_bytes(ADDR_SCRIPT_FILE, 5) == b"mog_0"


def _grooming_colours() -> tuple[int, int, int, int, int]:
    """(% of the Moogle's fur dyed, % of it red, green, blue, % cut shorter
    than full length), of the fur on the model (MOG_FUR_ON_MODEL). A dyed
    spot's colour is its strongest channel. The dyes are red 15,4,4, green
    4,15,4 and blue 4,8,15, and strokes blend and shade them. A spot with two
    equal strongest channels counts as dyed, but not as any one colour."""
    fur = dme.read_bytes(ADDR_MOG_FUR, 2 * MOG_FUR_TEXELS)
    dyed = cut = 0
    colours = [0, 0, 0]
    for i in MOG_FUR_ON_MODEL:
        texel = (fur[i] << 8) | fur[i + 1]
        if (texel >> 12) & 7 < 7:
            cut += 1
        if texel & 0xFFF == 0xFFF:
            continue
        dyed += 1
        rgb = ((texel >> 8) & 0xF, (texel >> 4) & 0xF, texel & 0xF)
        strongest = max(rgb)
        if rgb.count(strongest) == 1:
            colours[rgb.index(strongest)] += 1

    def pct(n: int) -> int:
        return n * 100 // len(MOG_FUR_ON_MODEL)

    return pct(dyed), pct(colours[0]), pct(colours[1]), pct(colours[2]), pct(cut)


def _grooming() -> tuple[int, int]:
    """(% of the Moogle's fur dyed, % cut shorter than full length)."""
    dyed, _, _, _, cut = _grooming_colours()
    return dyed, cut


def _grooming_goal_met(ctx: "FFCCContext", dyed: int, cut: int) -> bool:
    need = ctx.grooming_percent
    return ((ctx.grooming_goal == 1 or dyed >= need) and (ctx.grooming_goal == 0 or cut >= need))


def _grooming_tools_owned(ctx: "FFCCContext") -> int:
    """The patcher's tools byte: a bit per grooming tool received (all of
    them without the Grooming Tools option)."""
    if not ctx.grooming_tools:
        return 0x1F
    owned = 0
    for net_item in ctx.items_received:
        for name, _, number in GROOMING_TOOLS:
            if LOOKUP_ID_TO_NAME.get(net_item.item) == name:
                owned |= 1 << number
    return owned


def _update_grooming(ctx: "FFCCContext") -> None:
    """Keep the tools byte up to date and, in a Moogle Nest, show how far the
    grooming has got (with the Mog Grooming goal or the Grooming Tools
    option): the goal's progress, then how much of each colour, or the tool
    held if it hasn't been found yet."""
    locked = int.from_bytes(dme.read_bytes(ADDR_GROOMING_HOOK, 4), "big") == GROOMING_HOOK_WORD
    owned = _grooming_tools_owned(ctx)
    if locked and _read_byte(ADDR_GROOMING_TOOLS) != owned:
        _write_byte(ADDR_GROOMING_TOOLS, owned)
    progress = second = ""
    if _in_moogle_nest() and (ctx.victory == 4 or ctx.grooming_checks or (locked and ctx.grooming_tools)):
        dyed, red, green, blue, cut = _grooming_colours()
        second = f"Red {red}%  Green {green}%  Blue {blue}%"
        if ctx.victory == 4:
            need = ctx.grooming_percent
            parts = [f"Dyed {dyed}%/{need}%" if ctx.grooming_goal != 1 else "",
                     f"Cut {cut}%/{need}%" if ctx.grooming_goal != 0 else ""]
            progress = "  ".join(p for p in parts if p)
            if (dyed, cut) != ctx.grooming_reported:
                ctx.grooming_reported = (dyed, cut)
                logger.debug(f"FFCC: Mog grooming: {dyed}% dyed, {cut}% cut")
        tool = _read_int(ADDR_MOG_TOOL)
        if locked and 0 <= tool < len(GROOMING_TOOLS) and not owned & (1 << tool):
            second = f"Need the {GROOMING_TOOLS[tool][0]}"     # instead of the colours
        if not progress:
            progress, second = second, ""
    if (progress, second) == ctx.grooming_shown or not _hud_installed():
        return
    ctx.grooming_shown = (progress, second)
    # top centre, between the hearts and the play timer
    for line, (slot_no, text) in enumerate(zip(HUD_GROOMING_SLOTS, (progress, second))):
        at = ADDR_HUD_SLOTS + HUD_SLOT_SIZE * slot_no
        if text:
            slot = bytearray(_hud_line(text, 0, 0))
            y = 18.0 + 34.0 * line
            slot[4:0x1C] = struct.pack(">6f", 180.0, y, 320.0, 30.0, 194.0, y + 5.0)
            dme.write_bytes(at, bytes(slot))
        else:
            dme.write_bytes(at, bytes(4))


async def _check_grooming(ctx: "FFCCContext") -> None:
    """Mog grooming checks: a radar once the fur has turned it on (anywhere in
    the game, the save keeps it), the dye and cut milestones in a Moogle Nest."""
    if not ctx.grooming_checks or not 1 <= _read_byte(ADDR_CURRENT_YEAR) <= 99:
        return
    radar = _read_byte(ADDR_MOG_RADAR)
    dyed = cut = None
    if _in_moogle_nest():
        dyed, _, _, _, cut = _grooming_colours()
    found = []
    for name, (code, kind, value) in GROOMING_LOCATIONS.items():
        ap_id = FFCCLocation.get_apid(code)
        if ap_id not in ctx.missing_locations:
            continue
        if ((kind == "radar" and radar == value)
                or (kind == "dyed" and dyed is not None and dyed >= value)
                or (kind == "cut" and cut is not None and cut >= value)):
            found.append(ap_id)
            logger.info(f"FFCC: {name}!")
    if found:
        await ctx.send_msgs([{"cmd": "LocationChecks", "locations": found}])


def _give_cure(ctx: FFCCContext) -> bool:
    """Free Cure Magicite: a Stone of Cure for every player (player 1's
    at their feet with "Items Dropped At Your Feet"). True once all have one."""
    players = _players() or [ctx.player_record or 0]
    for record in players:
        if record in ctx.cure_given:
            continue
        if record == players[0]:
            given = _drop_or_bag(ctx, STONE_OF_CURE, "Stone of Cure")
        else:
            with _as_player(record):
                given = _add_bag_item(STONE_OF_CURE)
        if given:
            ctx.cure_given.add(record)
    return all(record in ctx.cure_given for record in players)


async def _check_death(ctx: FFCCContext) -> None:
    """Send a death when any player runs out of hearts (once per death)."""
    if not ctx.slot or not _is_in_dungeon():
        return
    for record in _players():
        with _as_player(record):
            hearts = _read_byte(ADDR_CUR_HEARTS)
        if hearts != 0:
            ctx.dead_players.discard(record)
        elif record not in ctx.dead_players:
            ctx.dead_players.add(record)
            await ctx.send_death(f"{_character(record)["name"]} ({ctx.player_names[ctx.slot]}) "
                                 "ran out of hearts.")

# Main sync loop


async def dolphin_sync_task(ctx: FFCCContext) -> None:
    logger.info("FFCC: Starting Dolphin connector. Use /dolphin for status.")
    while not ctx.exit_event.is_set():
        await asyncio.sleep(0.1)
        try:
            if dme.is_hooked() and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                # Connected — run game logic
                if ctx.slot is None:
                    continue

                _update_player(ctx)
                in_dungeon = _is_in_dungeon()
                await _report_cycles(ctx)
                await _watch_bonus(ctx)
                _update_grooming(ctx)
                _update_hud(ctx)
                _write_chest_masks(ctx)
                await _report_live_score(ctx, in_dungeon)
                if ctx.shop_checks and not in_dungeon:
                    await _watch_shop(ctx)
                    if ctx.shop_gil is None and _remove_ap_items():   # once the shop is closed
                        logger.debug("FFCC: removed a bought AP Item from the bag")
                if ctx.stamp_hints:
                    await _watch_stamps(ctx)
                await _report_stamps(ctx)
                await _check_grooming(ctx)

                # Year advancement - monitor on world map and in dungeon.
                # Year advances when the caravan returns home after filling the chalice,
                # which happens on the world map. We check every tick so we don't miss it.
                year = _read_byte(ADDR_CURRENT_YEAR)
                if year != ctx.current_year:
                    old_year = ctx.current_year
                    ctx.current_year = year
                    if old_year is not None and year > old_year:
                        from .locations import FFCCLocation
                        for y in range(old_year + 1, year + 1):
                            year_loc_name = f"Year {y} Begins"
                            year_loc_data = LOCATION_TABLE.get(year_loc_name)
                            if year_loc_data:
                                ap_id = FFCCLocation.get_apid(year_loc_data.code)
                                if ap_id in ctx.missing_locations:
                                    await ctx.send_msgs([{"cmd": "LocationChecks",
                                                          "locations": [ap_id]}])
                                    logger.debug(f"FFCC: Year advancement — Year {y} has begun")
                # Check victory
                if not ctx.finished_game:
                    await _check_victory(ctx)

                ctx.in_town = not in_dungeon and _is_in_town()
                if ctx.in_town:
                    _deliver_items(ctx)
                if not in_dungeon:
                    ctx.current_dungeon = None
                    ctx.prev_chest_flags = bytes(8)
                    ctx.monster_hp = {}
                    ctx.group_spots_done = set()
                    ctx.cure_pending = False
                    await _report_stage(ctx, "")
                    continue

                map_id = _get_map_id()
                dungeon = MAP_ID_TO_DUNGEON.get(map_id)
                if dungeon is None:
                    continue
                await _report_stage(ctx, dungeon)
                await _watch_kills(ctx, dungeon)

                cycle = _get_dungeon_cycle(map_id)
                if dungeon == "Mount Vellenge":
                    cycle = 1  # single-cycle dungeon

                just_entered = (dungeon != ctx.current_dungeon or cycle != ctx.current_cycle)
                if just_entered:
                    # "Free Cure Magicite": one Stone of Cure per visit, given
                    # when the caravan comes in from outside (not on a cycle
                    # change inside the dungeon)
                    if ctx.free_cure_magicite and ctx.current_dungeon is None:
                        ctx.cure_pending = True
                        ctx.cure_given = set()
                    ctx.current_dungeon = dungeon
                    ctx.current_cycle = cycle
                    ctx.prev_chest_flags = bytes(8)
                    logger.debug(f"FFCC: Entered {dungeon} — Cycle {cycle}")
                    if cycle >= 2:
                        cycle_loc_name = f"{dungeon} - Cycle {cycle} Reached"
                        cycle_loc_data = LOCATION_TABLE.get(cycle_loc_name)
                        if cycle_loc_data:
                            ap_id = 2326528 + cycle_loc_data.code
                            if ap_id in ctx.missing_locations:
                                await ctx.send_msgs([{"cmd": "LocationChecks", "locations": [ap_id]}])
                                logger.debug(f"FFCC: Cycle advancement — {cycle_loc_name}")

                # Check for newly opened chests
                curr_flags = _read_chest_flags()
                new_locs = _find_new_chest_locations(dungeon, cycle,
                                                     ctx.prev_chest_flags, curr_flags)
                ctx.prev_chest_flags = curr_flags

                if new_locs:
                    ap_ids = []
                    for loc_name in new_locs:
                        loc_data = LOCATION_TABLE.get(loc_name)
                        if loc_data:
                            from .locations import FFCCLocation
                            ap_id = FFCCLocation.get_apid(loc_data.code)
                            if ap_id not in ctx.checked_locations:
                                ap_ids.append(ap_id)
                                logger.debug(f"FFCC: Chest opened — {loc_name}")
                    if ap_ids:
                        await ctx.send_msgs([{"cmd": "LocationChecks", "locations": ap_ids}])

                if ctx.cure_pending and _give_cure(ctx):
                    ctx.cure_pending = False
                    logger.debug("FFCC: Free Cure Magicite - here's a Stone of Cure for this dungeon.")
                _deliver_items(ctx)

                # DeathLink
                if "DeathLink" in ctx.tags:
                    await _check_death(ctx)

            else:
                # Not connected - attempt to connect / reconnect
                if ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                    logger.info("FFCC: Connection to Dolphin lost, reconnecting...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                    ctx.current_dungeon = None
                    ctx.current_year = None
                    ctx.prev_chest_flags = bytes(8)
                    await ctx.disconnect()

                dme.hook()
                if not dme.is_hooked():
                    logger.info("FFCC: Failed to connect to Dolphin, trying again in 5 seconds...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                    await ctx.disconnect()
                    await asyncio.sleep(5)
                    continue

                # Verify game ID — retry a few times in case the game is still loading
                game_id = None
                for _attempt in range(5):
                    try:
                        game_id = _read_game_id()
                        if game_id == GAME_ID:
                            break
                    except Exception:
                        game_id = None
                    await asyncio.sleep(1)
                if game_id != GAME_ID:
                    logger.warning(
                        f"FFCC: Wrong game loaded (read {game_id!r}, expected {GAME_ID!r}). "
                        f"Please load FFCC NTSC-U in Dolphin."
                    )
                    ctx.dolphin_status = CONNECTION_REFUSED_STATUS
                    dme.un_hook()
                    await asyncio.sleep(5)
                    continue

                logger.info(CONNECTION_CONNECTED_STATUS)
                ctx.dolphin_status = CONNECTION_CONNECTED_STATUS
                ctx.prev_chest_flags = bytes(8)
                ctx.current_dungeon = None
                ctx.current_year = None

        except Exception:
            logger.error(f"FFCC dolphin sync error:\n{traceback.format_exc()}")
            if dme.is_hooked():
                dme.un_hook()
            ctx.dolphin_status = CONNECTION_LOST_STATUS
            ctx.current_dungeon = None
            ctx.current_year = None
            ctx.prev_chest_flags = bytes(8)
            await ctx.disconnect()
            await asyncio.sleep(5)


async def _check_victory(ctx: FFCCContext) -> None:
    """Send goal completion when victory goal is finished"""
    if ctx.victory == 0:  # collect all 13 Myrrh drops
        key = _myrrh_key(ctx)
        stored = ctx.stored_data.get(key) or 0
        mask = _read_myrrh_mask()
        if mask & ~stored:
            # Bits reset each year, so remember every dungeon ever seen on the server.
            await ctx.send_msgs([{"cmd": "Set", "key": key, "default": 0, "want_reply": True,
                                  "operations": [{"operation": "or", "value": mask}]}])
            stored |= mask
            ctx.stored_data[key] = stored
            logger.info(f"FFCC: Myrrh trees harvested: {bin(stored).count("1")}/{MYRRH_DUNGEONS}")

        if stored & ALL_MYRRH_MASK == ALL_MYRRH_MASK:
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True
            logger.info("FFCC: Goal complete — congratulations!")

    elif ctx.victory == 1:  # defeat the final boss (Mount Vellenge) and enter credits / end screen
        if _read_int(ADDR_SCRIPT_NAME_ID) in ENDING_IDS:
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True
            logger.info("FFCC: Goal complete — congratulations!")

    elif ctx.victory == 2:  # Monster Hunt: one of every enemy type of the hunt
        done = _defeated(ctx)
        if all(enemy in done for enemy in hunt_list(ctx.monster_hunt_bosses)):
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True
            logger.info("FFCC: Goal complete — every enemy type defeated, congratulations!")

    elif ctx.victory == 4:  # Mog Grooming: a Moogle dyed or trimmed enough
        if _in_moogle_nest():
            dyed, cut = _grooming()
            if _grooming_goal_met(ctx, dyed, cut):
                await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                ctx.finished_game = True
                done = " and ".join(part for part, kind in ((f"{dyed}% dyed", 1), (f"{cut}% cut", 0))
                                    if ctx.grooming_goal != kind)
                logger.info(f"FFCC: Goal complete — the Moogle is {done}, congratulations!")

    elif ctx.victory == 3:  # Mog Stamps: every stamp on the card
        stamps = int.from_bytes(dme.read_bytes(ADDR_MOG_STAMPS, 4), "big") & MOG_STAMP_BITS
        if stamps != ctx.stamps_seen:
            new = [name for bit, name in MOG_STAMPS.items()
                   if stamps & bit and ctx.stamps_seen is not None and not ctx.stamps_seen & bit]
            missing = [name for bit, name in MOG_STAMPS.items() if not stamps & bit]
            ctx.stamps_seen = stamps
            logger.info(f"FFCC: Mog Stamps: {MOG_STAMP_COUNT - len(missing)}/{MOG_STAMP_COUNT}"
                        + (f" (new: {", ".join(new)})" if new else ""))
            if 0 < len(missing) <= 5:
                logger.info(f"FFCC: Mog Stamps still to get: {", ".join(missing)}")
        if stamps == MOG_STAMP_BITS:
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True
            logger.info("FFCC: Goal complete — every Mog Stamp collected, congratulations!")


def _hunt_key(ctx: "FFCCContext") -> str:
    return f"ffcc_hunt_{ctx.team}_{ctx.slot}"


def _defeated(ctx: "FFCCContext") -> set[str]:
    """Enemy types defeated so far: the ones in data storage (kept even
    without Monster Hunt Checks) and the checked Monster Hunt locations."""
    done = set((ctx.stored_data.get(_hunt_key(ctx)) or {}).keys())
    for enemy in MONSTERS:
        data = MONSTER_LOCATION_TABLE[monster_location(enemy)]
        if 2326528 + data.code in ctx.checked_locations:
            done.add(enemy)
    return done


def _enemy_location(dungeon: str, owner: int, monster_id: int) -> tuple[tuple | None, list[int]]:
    """The "Every Enemy" AP ids the monster that just died can check, and
    its spot: a boss by its type, any other enemy by the spot it spawned at
    (a switch group's spot gives the whole group's ids). No ids for monsters
    that no spawn record places (ones a boss summons during its fight)."""
    enemy = MONSTER_BY_ID[monster_id]
    if MONSTERS[enemy][1]:
        ap_id = BOSS_SPOTS.get((dungeon, enemy))
        return None, [ap_id] if ap_id is not None else []
    if not 0x80000000 <= owner < 0x81800000:
        return None, []
    for offset in (MONSTER_SPAWN, MONSTER_HOME):
        pos = struct.unpack(">3f", dme.read_bytes(owner + offset, 12))
        for spot_id, spot, ap_ids in ENEMY_SPOTS.get(dungeon, []):
            if spot_id == monster_id and all(abs(a - b) <= SPAWN_TOLERANCE for a, b in zip(pos, spot)):
                return (dungeon, spot_id, spot), ap_ids
    for ambush_id, ap_ids in AMBUSH_IDS.get(dungeon, []):
        if ambush_id == monster_id:
            # no spot to go by: the monster object is this visit's ambusher
            return (dungeon, monster_id, owner), ap_ids
    return None, []


async def _watch_kills(ctx: "FFCCContext", dungeon: str) -> None:
    """Find monsters that just died (HP went from above 0 to 0) and record
    their enemy type in the server's data storage (ffcc_hunt_<team>_<slot> =
    {enemy: true}, for the goal and the trackers) and send the Monster Hunt
    check: the enemy type's (Enemy Types) or the enemy's own (Every Enemy).
    A record that changes owner or id is a new monster, so its HP is only
    compared once it has been seen."""
    raw = dme.read_bytes(ADDR_MONSTER_WORK, MONSTER_WORK_SIZE * MONSTER_SLOTS)
    killed = []
    for slot in range(MONSTER_SLOTS):
        base = MONSTER_WORK_SIZE * slot
        owner = struct.unpack_from(">I", raw, base + 0x0C)[0]
        monster_id = struct.unpack_from(">i", raw, base + MONSTER_ID)[0]
        max_hp, hp = struct.unpack_from(">2H", raw, base + MONSTER_MAX_HP)
        seen = ctx.monster_hp.get(slot)
        ctx.monster_hp[slot] = (owner, monster_id, hp)
        if seen is None or seen[:2] != (owner, monster_id) or max_hp == 0:
            continue
        if monster_id in FLEES_AT_1_HP:
            down = seen[2] > 1 and hp <= 1
        else:
            down = seen[2] > 0 and hp == 0
        if down and monster_id in MONSTER_BY_ID:
            killed.append((owner, monster_id))
    if not killed:
        return

    ap_ids = []
    if ctx.monster_hunt_checks == HUNT_EVERY_ENEMY:
        for owner, monster_id in killed:
            spot, candidates = _enemy_location(dungeon, owner, monster_id)
            if len(candidates) > 1:
                # a group spot counts once per dungeon visit: re-entering an
                # area kills the dead again (setRepop), which would use up
                # the group's next check
                if spot in ctx.group_spots_done:
                    continue
                ctx.group_spots_done.add(spot)
            ap_ids += [next((i for i in candidates if i in ctx.missing_locations and i not in ap_ids), None)]
        ap_ids = [i for i in ap_ids if i is not None]

    done = _defeated(ctx)
    new = [enemy for enemy in dict.fromkeys(MONSTER_BY_ID[m] for _, m in killed) if enemy not in done]
    # kills are always recorded, but only announced when the hunt is in play
    announce = logger.info if ctx.monster_hunt_checks or ctx.victory == 2 else logger.debug
    for enemy in new:
        announce(f"FFCC: Monster Hunt: defeated the first {enemy}")
    if new:
        ctx.stored_data[_hunt_key(ctx)] = dict(ctx.stored_data.get(_hunt_key(ctx)) or {}, **{e: True for e in new})
        await ctx.send_msgs([{"cmd": "Set", "key": _hunt_key(ctx), "default": {},
                              "operations": [{"operation": "update", "value": {e: True for e in new}}]}])
        if ctx.monster_hunt_checks and ctx.monster_hunt_checks != HUNT_EVERY_ENEMY:
            ap_ids += [i for i in (2326528 + MONSTER_LOCATION_TABLE[monster_location(e)].code for e in new)
                       if i in ctx.missing_locations]
    if ap_ids:
        await ctx.send_msgs([{"cmd": "LocationChecks", "locations": ap_ids}])


def _shop_town() -> str | None:
    name = dme.read_bytes(ADDR_SCRIPT_FILE, 4).decode("ascii", "replace")
    return SHOP_TOWN_BY_SCRIPT.get(name)


async def _watch_shop(ctx: "FFCCContext") -> None:
    """Send a shop slot's check when something is bought from it: the slot
    on the yes/no screen, then a drop in gil with the shop still open."""
    count = struct.unpack(">h", dme.read_bytes(_relocate(ADDR_SHOP_COUNT), 2))[0]
    menu = _read_int(ADDR_SHOP_MENU)
    if not 0 < count <= 16 or not 0x80000000 <= menu < 0x81800000:
        ctx.shop_gil = ctx.shop_buying = None
        return
    gil = _read_int(ADDR_GIL)
    if _read_int(menu + SHOP_MENU_SUB) == SHOP_CONFIRM:
        ctx.shop_buying = _read_int(menu + SHOP_MENU_CURSOR)
    bought = ctx.shop_buying if ctx.shop_gil is not None and gil < ctx.shop_gil else None
    ctx.shop_gil = gil
    if bought is None or not 0 <= bought < count:
        return
    ctx.shop_buying = None
    shop = SHOP_BY_TOWN.get((_shop_town(), count))
    ap_id = SHOP_SLOT_IDS.get((shop, bought + 1))
    if ap_id is not None and ap_id in ctx.missing_locations:
        logger.debug(f"FFCC: bought slot {bought + 1} of {SHOPS[shop][0]}")
        await ctx.send_msgs([{"cmd": "LocationChecks", "locations": [ap_id]}])


def _deathlink_key(ctx: "FFCCContext") -> str:
    return f"ffcc_deathlink_{ctx.team}_{ctx.slot}"


def _stamps_key(ctx: "FFCCContext") -> str:
    return f"ffcc_stamps_{ctx.team}_{ctx.slot}"


def _mog_stamps_key(ctx: "FFCCContext") -> str:
    return f"ffcc_mog_stamps_{ctx.team}_{ctx.slot}"


async def _report_stamps(ctx: "FFCCContext") -> None:
    """Put the save's Mog Stamps in the server's data storage for the
    trackers: ffcc_mog_stamps_<team>_<slot> = the 4 stamp bytes read as one
    big-endian number (bits as in MOG_STAMP_NESTS). Stamps are only added
    (a bitwise or), so a reload or reconnect never takes one away."""
    if not 1 <= _read_byte(ADDR_CURRENT_YEAR) <= 99:
        return
    stamps = int.from_bytes(dme.read_bytes(ADDR_MOG_STAMPS, 4), "big") & MOG_STAMP_BITS
    if not stamps & ~ctx.stamps_reported:
        return
    ctx.stamps_reported |= stamps
    await ctx.send_msgs([{"cmd": "Set", "key": _mog_stamps_key(ctx), "default": 0, "want_reply": False,
                          "operations": [{"operation": "or", "value": stamps}]}])


async def _watch_stamps(ctx: "FFCCContext") -> None:
    """Send a hint for every Mog Stamp the save has that hasn't given one
    yet. The server's data storage keeps {"stamps": stamps that gave a hint,
    "hinted": [[player, location], ...]}, so a reloaded save or a
    reconnect doesn't hint again."""
    key = _stamps_key(ctx)
    if key not in ctx.stored_data or not 1 <= _read_byte(ADDR_CURRENT_YEAR) <= 99:
        return
    stored = ctx.stored_data[key] or {}
    used = int(stored.get("stamps", 0))
    stamps = int.from_bytes(dme.read_bytes(ADDR_MOG_STAMPS, 4), "big") & MOG_STAMP_BITS
    new = bin(stamps & ~used).count("1")
    if not new:
        return
    hinted = [tuple(h) for h in stored.get("hinted", [])]
    found = {(item.player, item.location) for item in ctx.items_received}
    targets = [tuple(t) for t in ctx.stamp_hints if tuple(t) not in found and tuple(t) not in hinted]
    for player, location in targets[:new]:
        # Priority: they're all progression items, and it gives the hint the
        # PopTracker pack's yellow highlight
        await ctx.send_msgs([{"cmd": "CreateHints", "player": player, "locations": [location],
                              "status": HINT_PRIORITY}])
        hinted.append((player, location))
    logger.info(f"FFCC: Mog Stamp! {min(new, len(targets))} hint(s) sent." if targets
                else "FFCC: Mog Stamp! Every progression item is already found or hinted.")
    value = {"stamps": used | stamps, "hinted": [list(h) for h in hinted]}
    ctx.stored_data[key] = value
    await ctx.send_msgs([{"cmd": "Set", "key": key, "default": {},
                          "operations": [{"operation": "replace", "value": value}]}])


def _read_myrrh_mask() -> int:
    raw = dme.read_bytes(ADDR_MYRRH_COLLECTED, 2)
    return (raw[0] | (raw[1] << 8)) & ALL_MYRRH_MASK


def _myrrh_key(ctx: "FFCCContext") -> str:
    return f"ffcc_myrrh_{ctx.team}_{ctx.slot}"


def _stage_key(ctx: "FFCCContext") -> str:
    return f"ffcc_stage_{ctx.team}_{ctx.slot}"


async def _report_stage(ctx: "FFCCContext", stage: str) -> None:
    """Put the dungeon the player is in ("" when outside one) in the
    server's data storage, where the PopTracker pack reads it to open
    that dungeon's map tab."""
    if ctx.slot is None or stage == ctx.reported_stage:
        return
    ctx.reported_stage = stage
    await ctx.send_msgs([{"cmd": "Set", "key": _stage_key(ctx), "default": "",
                          "operations": [{"operation": "replace", "value": stage}]}])


def _bonus_score() -> tuple[int, int, int, int, int]:
    """(enemies defeated, items picked up, times knocked out, bonus points,
    score) for the dungeon being played, the way the bonus screen adds them."""
    enemies, items, knocked_out, earned, left = struct.unpack(">5H", dme.read_bytes(_relocate(ADDR_BONUS_COUNTERS), 10))
    bonus_points = max(0, min(100, earned + left))
    score = max(0, min(999, bonus_points + enemies + items - knocked_out))
    return enemies, items, knocked_out, bonus_points, score


def _live_key(ctx: "FFCCContext") -> str:
    return f"ffcc_bonus_live_{ctx.team}_{ctx.slot}"


async def _report_live_score(ctx: "FFCCContext", in_dungeon: bool) -> None:
    """Put the current run's bonus score in data storage for the trackers:
    {"dungeon", "cycle", "score"}, or {} outside a dungeon. Sent only when it
    changes."""
    live = {}
    if in_dungeon:
        dungeon = MAP_ID_TO_DUNGEON.get(_get_map_id())
        if dungeon in BONUS_TABLE:
            cycle = min(_read_byte(ADDR_CYCLE_BASE + 4 * _get_map_id()), 2) + 1
            live = {"dungeon": dungeon, "cycle": cycle, "score": _bonus_score()[4]}
    if live == ctx.reported_live:
        return
    ctx.reported_live = live
    await ctx.send_msgs([{"cmd": "Set", "key": _live_key(ctx), "default": {},
                          "operations": [{"operation": "replace", "value": live}]}])

# (dungeon, cycle) -> [(AP id, chest flags)] for every chest location
CHEST_LOCATIONS: dict[tuple[str, int], list[tuple[int, tuple[int, ...]]]] = {}
for _data in LOCATION_TABLE.values():
    if _data.chest and _data.flags:
        CHEST_LOCATIONS.setdefault((_data.region, _data.cycle), []).append(
            (2326528 + _data.code, _data.flags))


def _write_chest_masks(ctx: "FFCCContext") -> None:
    """With "Hide Collected Chests", give every dungeon the mask of the chests
    whose check for its current cycle is done. Only differing masks are
    written, and nothing before a save is loaded (year 0)."""
    if not ctx.hide_collected_chests or not 1 <= _read_byte(ADDR_CURRENT_YEAR) <= 99:
        return
    raw = dme.read_bytes(ADDR_CYCLE_BASE, 4 * len(MAP_ID_TO_DUNGEON))
    masks = {}
    for map_id, dungeon in MAP_ID_TO_DUNGEON.items():
        cycle = 1 if dungeon == "Mount Vellenge" else min(raw[4 * map_id], 2) + 1
        mask = 0
        for ap_id, flags in CHEST_LOCATIONS.get((dungeon, cycle), []):
            if ap_id in ctx.checked_locations:
                for flag in flags:
                    mask |= 1 << flag
        masks[map_id] = mask

    start = ADDR_EVENT_WORK + 2 * CHEST_MASK_SLOT
    current = dme.read_bytes(start, 6 * len(masks))
    for map_id, mask in masks.items():
        # three u16: flags 0-15, 16-31, 32-47
        wanted = struct.pack(">3H", mask & 0xFFFF, (mask >> 16) & 0xFFFF, (mask >> 32) & 0xFFFF)
        if current[6 * map_id:6 * map_id + 6] != wanted:
            dme.write_bytes(start + 6 * map_id, wanted)


def _bonus_key(ctx: "FFCCContext") -> str:
    return f"ffcc_bonus_{ctx.team}_{ctx.slot}"


def _bonus_tier(ctx: "FFCCContext", dungeon: str, cycle: int, offered: list[int]) -> int | None:
    """The tier (0-3) whose entry the bonus screen is offering, or None."""
    entries = ctx.bonus_pools.get(dungeon, [])
    for tier in range(3, -1, -1):
        entry = offered_entry(cycle, tier)
        if entry < len(entries) and list(entries[entry]) == offered:
            return tier
    return None


async def _watch_bonus(ctx: "FFCCContext") -> None:
    """While the bonus screen is open, record the tier reached and the item
    picked in the server's data storage, as {dungeon: {"tiers": {cycle: best
    tier}, "picked": [item ids]}} for the trackers."""
    if ctx.slot is None:
        return
    ptr = _read_int(ADDR_BONUS_SCREEN)
    if not 0x80000000 <= ptr < 0x81800000:
        return
    dungeon = MAP_ID_TO_DUNGEON.get(_get_map_id())
    if dungeon not in ctx.bonus_pools:
        return
    data = dme.read_bytes(ptr, BONUS_PICKED + 4)
    offered = [v for v in struct.unpack(">4h", data[BONUS_OFFERED:BONUS_OFFERED + 8])]
    picked = struct.unpack(">i", data[BONUS_PICKED:BONUS_PICKED + 4])[0]
    cycle = min(_read_byte(ADDR_CYCLE_BASE + 4 * _get_map_id()), 2) + 1
    tier = _bonus_tier(ctx, dungeon, cycle, offered)
    stored = (ctx.stored_data.get(_bonus_key(ctx)) or {}).get(dungeon) or {}
    record = {"tiers": dict(stored.get("tiers", {})), "picked": list(stored.get("picked", []))}
    changed = False
    if tier is not None and record["tiers"].get(str(cycle), -1) < tier:
        record["tiers"][str(cycle)] = tier
        changed = True
    if picked in offered and picked not in record["picked"] and ctx.bonus_recorded != (dungeon, ptr, picked):
        record["picked"].append(picked)
        ctx.bonus_recorded = (dungeon, ptr, picked)
        logger.info(f"FFCC: Bonus: {item_name(picked)} from {dungeon} (Cycle {cycle}, tier {tier})")
        changed = True
    if changed:
        await ctx.send_msgs([{"cmd": "Set", "key": _bonus_key(ctx), "default": {},
                              "operations": [{"operation": "update", "value": {dungeon: record}}]}])


def _cycles_key(ctx: "FFCCContext") -> str:
    return f"ffcc_cycles_{ctx.team}_{ctx.slot}"


async def _report_cycles(ctx: "FFCCContext") -> None:
    """Put every dungeon's current cycle ({dungeon: 1-3}) and the year
    ("Year": n) in the server's data storage, where the PopTracker pack reads
    them to set its cycle and year trackers. Nothing is sent before a save is
    loaded (year 0)."""
    year = _read_byte(ADDR_CURRENT_YEAR)
    if ctx.slot is None or not 1 <= year <= 99:
        return
    raw = dme.read_bytes(ADDR_CYCLE_BASE, 4 * len(MAP_ID_TO_DUNGEON))
    cycles = {dungeon: min(raw[4 * map_id], 2) + 1 for map_id, dungeon in MAP_ID_TO_DUNGEON.items()
              if dungeon != "Mount Vellenge"}
    cycles["Year"] = year
    if cycles == ctx.reported_cycles:
        return
    ctx.reported_cycles = cycles
    await ctx.send_msgs([{"cmd": "Set", "key": _cycles_key(ctx), "default": {},
                          "operations": [{"operation": "replace", "value": cycles}]}])

STATUS_TRAP_FRAMES = 0x012c   # 300 frames = ~5 s


def _apply_status_trap(trap_name: str, table: int | None, frames: int = STATUS_TRAP_FRAMES) -> None:
    """Give the current player a status: through the trap-visuals table (the
    game applies it, with particles and sound), or straight into the timer."""
    if table is not None:
        _write_short(table + 2 * TRAP_STATUS_INDEX[trap_name], frames)
    else:
        _write_short(TRAP_TIMER_ADDR[trap_name], frames)


def read_ffcc_connection(path: str) -> tuple[str | None, str | None]:
    """(server address, slot name) from a .apffcc (or older .ffcc) file. The
    server is only there when the file was downloaded from a room."""
    import json
    import zipfile
    try:
        with zipfile.ZipFile(path) as ffcc:
            manifest = json.loads(ffcc.read("archipelago.json"))
        return manifest.get("server") or None, manifest.get("player_name") or None
    except (OSError, KeyError, ValueError, zipfile.BadZipFile):
        logger.warning(f"Could not read the connection info from {path}")
        return None, None


def launch(*launch_args: str) -> None:
    async def main() -> None:
        parser = get_base_parser()
        parser.add_argument("ffcc_file", default="", nargs="?",
                            help="A .apffcc file (connects to its room) or an archipelago:// URL")
        parser.add_argument("--name", default=None, help="Slot name to connect as")
        args = parser.parse_args(launch_args)

        server, name = args.connect, args.name
        if args.ffcc_file.startswith("archipelago://"):
            args.url = args.ffcc_file
            args = handle_url_arg(args, parser)
            server, name = args.connect, args.name
        elif args.ffcc_file:
            file_server, file_name = read_ffcc_connection(args.ffcc_file)
            server, name = server or file_server, name or file_name

        ctx = FFCCContext(server, args.password)
        ctx.username = name

        if tracker_loaded:
            ctx.run_generator()
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        if server:
            ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")
        ctx.dolphin_sync_task = asyncio.create_task(dolphin_sync_task(ctx), name="DolphinSync")
        await asyncio.gather(
            ctx.dolphin_sync_task,
            ctx.exit_event.wait(),
        )

    Utils.init_logging("FFCCClient")
    import colorama
    colorama.just_fix_windows_console()
    asyncio.run(main())
    colorama.deinit()
