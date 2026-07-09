"""FFCC Archipelago client — connects to Dolphin via dolphin_memory_engine."""

import asyncio
import random
import traceback
from typing import Any, Dict, List, Optional, Set, Tuple

import Utils
from CommonClient import CommonContext, ClientCommandProcessor, gui_enabled, logger, get_base_parser
from NetUtils import ClientStatus

try:
    import dolphin_memory_engine as dme
    DOLPHIN_AVAILABLE = True
except ImportError:
    DOLPHIN_AVAILABLE = False
    logger.warning("dolphin_memory_engine not installed — FFCC client will not function.")

from .game_id import game_name
from .items import ITEM_TABLE, LOOKUP_ID_TO_NAME, PROGRESSIVE_ARTIFACT_ORDER, PROGRESSIVE_ARTIFACT_NAME
from .locations import LOCATION_TABLE, FFCCLocationData

# ── Expected game ID ───────────────────────────────────────────────────────────
GAME_ID      = b"GCCE"     # FFCC NTSC-U 4-byte game code
GAME_ID_ADDR = 0x80000000

# ── Connection status strings ─────────────────────────────────────────────────
CONNECTION_INITIAL_STATUS   = "Dolphin connection has not been initiated."
CONNECTION_CONNECTED_STATUS = "Dolphin connected successfully."
CONNECTION_REFUSED_STATUS   = "Dolphin refused: wrong game loaded. Please load FFCC NTSC-U."
CONNECTION_LOST_STATUS      = "Dolphin connection was lost. Please restart your emulator and ensure FFCC is running."

# ── World / dungeon state ──────────────────────────────────────────────────────
ADDR_MAP_ID      = 0x8021de9b   # 1 byte: 0x00-0x0d = dungeon, others = not in dungeon
ADDR_CURRENT_YEAR = 0x8021de93  # 1 byte: current caravan year (1=Year1, 2=Year2, ...)
ADDR_WORLD_MAP   = 0x8021f25a   # 1 byte: 0x01 = on world map
ADDR_PAUSED      = 0x8021f25b   # 1 byte: 0x01 = paused

# Per-dungeon cycle address: map_id 0 → 0x8021deb3, map_id 1 → +4, etc.
ADDR_CYCLE_BASE = 0x8021deb3   # 0x00=Cycle1, 0x01=Cycle2, 0x02=Cycle3

# ── Player stats ───────────────────────────────────────────────────────────────
ADDR_MAX_HEARTS = 0x8021f28b   # 1 byte
ADDR_CUR_HEARTS = 0x8021f28d   # 1 byte (1 heart = 2 units; 0 = dead)

# ── Status effects (2 bytes each; write any nonzero value to apply) ────────────
ADDR_FROZEN     = 0x8021f2ae
ADDR_BURNED     = 0x8021f2b0
ADDR_POISONED   = 0x8021f2b2
ADDR_PARALYZED  = 0x8021f2b6
ADDR_SLOWED     = 0x8021f2be

# ── Inventory / items ──────────────────────────────────────────────────────────
ADDR_ITEM_BAG   = 0x8021f33a   # material bag start (2 bytes per slot)
ADDR_ARTIFACT   = 0x8021f3a6   # artifact bag start (2 bytes per slot)
ADDR_GIL        = 0x8021f470   # 4 bytes BE

# Number of 2-byte slots in the material bag (ADDR_ITEM_BAG → ADDR_ARTIFACT).
ITEM_BAG_SLOTS      = (ADDR_ARTIFACT - ADDR_ITEM_BAG) // 2   # = 54
# Number of 2-byte slots in the artifact bag (ADDR_ARTIFACT → ADDR_GIL).
ARTIFACT_BAG_SLOTS  = (ADDR_GIL - ADDR_ARTIFACT) // 2        # = 101
ITEM_SLOT_EMPTY = 0xffff  # sentinel for an empty inventory slot (confirmed via memory view)

# ── Chalice / bonus / food ─────────────────────────────────────────────────────
ADDR_CHALICE    = 0x8021ef3e   # 1 byte: bit0=Fire,bit1=Water,bit2=Wind,bit3=Earth,bit4=Holy
ADDR_BONUS      = 0x8021fe14   # 1 byte: 0x01–0x18
ADDR_FOOD_BASE  = 0x8021f629   # 2 bytes × 8 foods (Striped Apple, Cherry Cluster, …)

# ── Chest bit flags (8 bytes, shared/reused per dungeon, cleared on dungeon exit) ─
ADDR_CHEST_BASE = 0x80926000

# ── Map ID → dungeon name ──────────────────────────────────────────────────────
MAP_ID_TO_DUNGEON: Dict[int, str] = {
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

# ── Chest bit flag positions per dungeon ───────────────────────────────────────
# List of (byte_offset, bit_index) relative to ADDR_CHEST_BASE.
# Order matches game8 chest number order for that dungeon.
# NOTE: mapping is tentative — requires in-game testing to verify.
# Dungeon flag-bit counts may not equal game8 chest counts; only the first
# min(len(flags), len(chests)) pairs are used for AP location detection.
DUNGEON_FLAG_BITS: Dict[str, List[Tuple[int, int]]] = {
    "River Belle Path":       [(3,1),(3,3),(3,4),(3,6),(3,7),(3,5),(2,0)],  # re-verified in-game 2026-07-08 (previous order was wrong: 2/3/4/5/6 checks fired mismatched)
    "Goblin Wall":            [(1,0),(2,1),(2,2),(2,3),(2,6),(2,7),(3,0),(3,1),(3,2),(3,3),(3,4)],
    "The Mine of Cathuriges": [(1,4),(1,5),(1,6),(2,1),(2,2),(2,3),(2,4),(2,5),(2,6),(3,1),(3,2),(3,3),(3,4),(3,5)],
    "The Mushroom Forest":    [(2,1),(3,1),(3,2),(3,3),(3,4)],
    "Tida":                   [(1,0),(2,3),(2,4),(2,5),(2,7),(3,0),(3,2),(3,3),(3,4),(3,5),(3,6),(3,7)],
    "Moschet Manor":          [(0,0),(1,3),(2,1),(2,6),(3,0),(3,1),(3,4)],
    "Mount Kilanda":          [(2,2),(2,3),(2,4),(3,0),(3,1),(3,2),(3,3),(3,4),(3,5)],
    "Daemon's Court":         [(2,0),(2,1),(3,0),(3,1),(3,2),(3,3),(3,4),(3,5),(3,6),(3,7)],
    "Selepation Cave":        [(2,2),(2,3),(2,4),(3,0),(3,1),(3,2),(3,3),(3,4),(3,5),(3,6)],
    "Veo Lu Sluice":          [(2,0),(2,1),(2,2),(2,3),(2,4),(3,0),(3,1),(3,2),(3,3),(3,4),(3,5),(3,6),(3,7)],
    "Lynari Desert":          [(1,4),(1,5),(2,0),(2,1),(3,2),(3,3),(3,4),(3,5),(3,6),(3,7)],
    "Conall Curach":          [(0,7),(1,0),(1,1),(1,2),(1,3),(1,4),(1,5),
                               (2,3),(2,4),(2,5),(2,6),(2,7),
                               (3,1),(3,4),(3,5),(3,6),(3,7),
                               (7,0),(7,1),(7,2),(7,3),(7,4)],
    "Rebena Te Ra":           [(0,6),(0,7),(1,4),(2,1),(2,2),(2,3),(2,4),
                               (3,0),(3,1),(3,2),(7,0),(7,1),(7,2),(7,3),(7,4)],
    "Mount Vellenge":         [(0,1),(0,2),(1,4),(1,6),(1,7),(2,0),
                               (3,1),(3,2),(3,3),(3,4),(3,5),(3,6),(3,7)],
}

# game8 chest numbers per dungeon, per cycle (same identifiers as
# locations._DUNGEON_CHESTS_BY_CYCLE — must be kept in sync with that table,
# since these are used to reconstruct the exact AP location name strings).
# Chest sets are NOT uniform across cycles for most dungeons; Mount Vellenge
# has only one cycle and Veo Lu Sluice only has two.
# NOTE: flag-bit order below is still tentative/unverified for every dungeon
# except River Belle Path — expanding a dungeon's chest count here does not
# mean the extra chests have verified flag-bit positions yet (see
# DUNGEON_FLAG_BITS' `min(len(flags), len(chests))` truncation below).
DUNGEON_CHESTS: Dict[str, Dict[int, List]] = {
    "River Belle Path": {  # re-verified 2026-07-08 against DUNGEON_FLAG_BITS above
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

# Precompute: (dungeon, cycle, chest_index) → AP location name for fast lookup
_BIT_INDEX_TO_LOCATION: Dict[Tuple[str, int, int], str] = {}
for _dungeon, _cycles in DUNGEON_CHESTS.items():
    for _cycle, _chests in _cycles.items():
        for _idx, _chest in enumerate(_chests):
            _loc_name = f"{_dungeon} - Cycle {_cycle} - Chest {_chest}"
            _BIT_INDEX_TO_LOCATION[(_dungeon, _cycle, _idx)] = _loc_name

# ── Helpers ────────────────────────────────────────────────────────────────────

def _read_byte(addr: int) -> int:
    return dme.read_bytes(addr, 1)[0]

def _read_short(addr: int) -> int:
    return int.from_bytes(dme.read_bytes(addr, 2), "big")

def _read_int(addr: int) -> int:
    return int.from_bytes(dme.read_bytes(addr, 4), "big")

def _write_byte(addr: int, val: int) -> None:
    dme.write_bytes(addr, val.to_bytes(1, "big"))

def _write_short(addr: int, val: int) -> None:
    dme.write_bytes(addr, val.to_bytes(2, "big"))

def _read_game_id() -> bytes:
    return dme.read_bytes(GAME_ID_ADDR, 4)

def _is_in_dungeon() -> bool:
    on_map = _read_byte(ADDR_WORLD_MAP)
    return on_map == 0x00  # 0x01 = world map, 0x00 = in dungeon

def _get_map_id() -> int:
    return _read_byte(ADDR_MAP_ID)

def _get_dungeon_cycle(map_id: int) -> int:
    raw = _read_byte(ADDR_CYCLE_BASE + map_id * 4)
    return raw + 1  # game stores 0/1/2; we want 1/2/3

def _read_chest_flags() -> bytes:
    return dme.read_bytes(ADDR_CHEST_BASE, 8)

def _force_chest_flag(byte_offset: int, bit_index: int) -> None:
    addr = ADDR_CHEST_BASE + byte_offset
    current = _read_byte(addr)
    _write_byte(addr, current | (1 << bit_index))

def _get_bit(data: bytes, byte_offset: int, bit_index: int) -> bool:
    if byte_offset >= len(data):
        return False
    return bool((data[byte_offset] >> bit_index) & 1)

def _find_free_item_slot() -> Optional[int]:
    """Return the address of the first empty (0xffff) material bag slot, or None if full."""
    for i in range(ITEM_BAG_SLOTS):
        addr = ADDR_ITEM_BAG + i * 2
        if _read_short(addr) == ITEM_SLOT_EMPTY:
            return addr
    return None

def _find_free_artifact_slot() -> Optional[int]:
    """Return the address of the first empty (0xffff) artifact bag slot, or None if full."""
    for i in range(ARTIFACT_BAG_SLOTS):
        addr = ADDR_ARTIFACT + i * 2
        if _read_short(addr) == ITEM_SLOT_EMPTY:
            return addr
    return None

# ── Command processor ──────────────────────────────────────────────────────────

class FFCCCommandProcessor(ClientCommandProcessor):
    def _cmd_dolphin(self) -> None:
        """Show Dolphin connection status."""
        if isinstance(self.ctx, FFCCContext):
            logger.info(f"Dolphin status: {self.ctx.dolphin_status}")


# ── Client context ─────────────────────────────────────────────────────────────

class FFCCContext(CommonContext):
    command_processor = FFCCCommandProcessor
    game              = game_name
    items_handling    = 0b111  # full remote items

    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        super().__init__(server_address, password)
        self.dolphin_status:   str = CONNECTION_INITIAL_STATUS
        self.dolphin_sync_task: Optional[asyncio.Task] = None
        self.has_sent_death:   bool = False

        # Game state
        self.current_dungeon:  Optional[str] = None
        self.current_cycle:    int = 1
        self.current_year:     Optional[int] = None
        self.prev_chest_flags: bytes = bytes(8)
        self.received_index:   int = 0  # items processed so far

        # Settings loaded from slot_data
        self.progressive_artifacts: bool = False
        self.progressive_count:     int = 0   # how many progressive arts received
        self.include_traps:         bool = True
        self.trap_weights:          Dict[str, int] = {}
        self.death_link_enabled:    bool = False

        # AP location IDs where the hybrid patcher wrote the real item into the chest.
        # The game engine gives those items on pickup, so we skip the memory-write
        # when ReceivedItems delivers them to avoid a double-give.
        self.physical_chest_ap_ids: Set[int] = set()

    async def server_auth(self, password_requested: bool = True) -> None:
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict) -> None:
        if cmd == "Connected":
            slot_data = args.get("slot_data", {})
            self.progressive_artifacts = bool(slot_data.get("progressive_artifacts", False))
            self.include_traps         = bool(slot_data.get("include_traps", True))
            self.trap_weights = {
                "Frozen Trap":          slot_data.get("frozen_trap_weight", 2),
                "Burned Trap":          slot_data.get("burned_trap_weight", 2),
                "Slowed Trap":          slot_data.get("slowed_trap_weight", 2),
                "Poisoned Trap":        slot_data.get("poisoned_trap_weight", 1),
                "Chalice Element Trap": slot_data.get("chalice_element_trap_weight", 1),
                "Bonus Set Trap":       slot_data.get("bonus_set_trap_weight", 1),
                "Food Preference Trap": slot_data.get("food_preference_trap_weight", 1),
            }
            if slot_data.get("death_link"):
                Utils.async_start(self.update_death_link(True))
            self.physical_chest_ap_ids = set(slot_data.get("physical_chest_ap_ids", []))
            if self.physical_chest_ap_ids:
                logger.info(f"FFCC: Hybrid patch active — {len(self.physical_chest_ap_ids)} "
                            f"chest(s) contain real items; client will skip those on receive.")
        super().on_package(cmd, args)

    def on_deathlink(self, data: dict) -> None:
        super().on_deathlink(data)
        if dme.is_hooked() and _is_in_dungeon():
            logger.info("DeathLink received — killing player.")
            _write_byte(ADDR_CUR_HEARTS, 0)

    def run_gui(self):
        from kvui import GameManager

        class FFCCManager(GameManager):
            logging_pairs = [("Client", "Archipelago")]
            base_title    = "Archipelago FFCC Client"

        self.ui = FFCCManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")


# ── Item giving ────────────────────────────────────────────────────────────────

def _give_item(ctx: FFCCContext, item_name: str) -> bool:
    """Write an item to game memory. Returns True on success."""
    if not dme.is_hooked() or not _is_in_dungeon():
        return False

    data = ITEM_TABLE.get(item_name)
    if not data:
        logger.warning(f"Unknown item: {item_name!r}")
        return True  # skip unknown items

    if data.type == "Trap":
        _apply_trap(ctx, item_name)
        return True

    if item_name == PROGRESSIVE_ARTIFACT_NAME:
        if ctx.progressive_count < len(PROGRESSIVE_ARTIFACT_ORDER):
            art_id = PROGRESSIVE_ARTIFACT_ORDER[ctx.progressive_count]
            if not _give_artifact(art_id):
                return False  # bag full, retry next tick
            ctx.progressive_count += 1
        return True

    if data.item_id is None:
        return True

    if data.type == "Artifact":
        return _give_artifact(data.item_id)  # False if bag full → retry

    # Materials, Food, Recipes, Magicite, Phoenix Down — find a free bag slot.
    # Empty slots are 0xffff; never overwrite an occupied slot.
    addr = _find_free_item_slot()
    if addr is None:
        logger.warning("FFCC: Item bag is full — cannot deliver item, will retry.")
        return False  # retry on next tick
    _write_short(addr, data.item_id)
    return True


def _give_artifact(artifact_id: int) -> bool:
    """Write an artifact item ID into the first empty artifact bag slot.
    Returns False if the bag is full (caller should retry next tick)."""
    addr = _find_free_artifact_slot()
    if addr is None:
        logger.warning("FFCC: Artifact bag is full — cannot deliver artifact, will retry.")
        return False
    _write_short(addr, artifact_id)
    return True


def _apply_trap(ctx: FFCCContext, trap_name: str) -> None:
    """Apply a trap effect to the player."""
    if trap_name == "Frozen Trap":
        _write_short(ADDR_FROZEN, 0x012c)       # ~3 seconds of frozen
    elif trap_name == "Burned Trap":
        _write_short(ADDR_BURNED, 0x012c)
    elif trap_name == "Slowed Trap":
        _write_short(ADDR_SLOWED, 0x012c)
    elif trap_name == "Poisoned Trap":
        _write_short(ADDR_POISONED, 0x012c)
    elif trap_name == "Chalice Element Trap":
        elements = [0x01, 0x02, 0x04, 0x08, 0x10]  # Fire,Water,Wind,Earth,Holy
        current  = _read_byte(ADDR_CHALICE)
        choices  = [e for e in elements if e != current] or elements
        _write_byte(ADDR_CHALICE, random.choice(choices))
    elif trap_name == "Bonus Set Trap":
        # Randomize bonus set (0x01–0x18 = 24 possible bonuses)
        _write_byte(ADDR_BONUS, random.randint(1, 0x18))
    elif trap_name == "Food Preference Trap":
        # Scramble all 8 food favorite values (2 bytes each, 0x00–0x64)
        for i in range(8):
            _write_short(ADDR_FOOD_BASE + i * 2, random.randint(0, 0x64))


# ── Chest detection ────────────────────────────────────────────────────────────

def _find_new_chest_locations(dungeon: str, cycle: int,
                               prev: bytes, curr: bytes) -> List[str]:
    """Return AP location names for chest bits that flipped 0→1."""
    flags  = DUNGEON_FLAG_BITS.get(dungeon, [])
    chests = DUNGEON_CHESTS.get(dungeon, {}).get(cycle, [])
    count  = min(len(flags), len(chests))
    found  = []
    known  = set(flags)
    for idx in range(count):
        byte_off, bit_idx = flags[idx]
        was_set = _get_bit(prev, byte_off, bit_idx)
        now_set = _get_bit(curr, byte_off, bit_idx)
        if not was_set and now_set:
            loc_name = _BIT_INDEX_TO_LOCATION.get((dungeon, cycle, idx))
            # Debug line: lets us verify that each flag bit matches the right chest.
            # Enable DEBUG logging to see this (e.g. run client with --loglevel debug).
            logger.info(f"FFCC: Chest flag (byte={byte_off}, bit={bit_idx}) → {loc_name!r}")
            if loc_name and loc_name in LOCATION_TABLE:
                found.append(loc_name)
    # Catch any bit flips not yet in our mapping — helps during verification runs.
    for byte_off in range(8):
        for bit_idx in range(8):
            if (byte_off, bit_idx) not in known:
                if not _get_bit(prev, byte_off, bit_idx) and _get_bit(curr, byte_off, bit_idx):
                    logger.info(f"FFCC: Unmapped chest flag bit flipped: "
                                 f"byte={byte_off}, bit={bit_idx} in {dungeon!r}")
    return found


def _restore_sent_chest_bits(dungeon: str, cycle: int,
                              checked_locs: Set[int]) -> None:
    """Force chest bits for already-checked locations so chests appear open on re-entry."""
    flags  = DUNGEON_FLAG_BITS.get(dungeon, [])
    chests = DUNGEON_CHESTS.get(dungeon, {}).get(cycle, [])
    count  = min(len(flags), len(chests))
    for idx in range(count):
        loc_name = _BIT_INDEX_TO_LOCATION.get((dungeon, cycle, idx))
        if not loc_name:
            continue
        loc_data = LOCATION_TABLE.get(loc_name)
        if not loc_data:
            continue
        ap_id = FFCCLocationData.code  # we need the apid, not raw code
        from .locations import FFCCLocation
        ap_id = FFCCLocation.get_apid(loc_data.code)
        if ap_id in checked_locs:
            byte_off, bit_idx = flags[idx]
            _force_chest_flag(byte_off, bit_idx)


# ── Death detection ────────────────────────────────────────────────────────────

async def _check_death(ctx: FFCCContext) -> None:
    if not ctx.slot or not _is_in_dungeon():
        return
    cur_hearts = _read_byte(ADDR_CUR_HEARTS)
    if cur_hearts == 0:
        if not ctx.has_sent_death:
            ctx.has_sent_death = True
            await ctx.send_death(f"{ctx.player_names[ctx.slot]} ran out of hearts.")
    else:
        ctx.has_sent_death = False


# ── Main sync loop ─────────────────────────────────────────────────────────────

async def dolphin_sync_task(ctx: FFCCContext) -> None:
    logger.info("FFCC: Starting Dolphin connector. Use /dolphin for status.")
    while not ctx.exit_event.is_set():
        await asyncio.sleep(0.1)
        try:
            if dme.is_hooked() and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                # ── Connected — run game logic ────────────────────────────────
                if ctx.slot is None:
                    continue

                in_dungeon = _is_in_dungeon()

                # Year advancement — monitor on world map and in dungeon.
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
                                if ap_id not in ctx.checked_locations:
                                    await ctx.send_msgs([{"cmd": "LocationChecks",
                                                          "locations": [ap_id]}])
                                    logger.info(f"FFCC: Year advancement — Year {y} has begun")

                if not in_dungeon:
                    ctx.current_dungeon  = None
                    ctx.prev_chest_flags = bytes(8)
                    continue

                map_id  = _get_map_id()
                dungeon = MAP_ID_TO_DUNGEON.get(map_id)
                if dungeon is None:
                    continue

                cycle = _get_dungeon_cycle(map_id)
                if dungeon == "Mount Vellenge":
                    cycle = 1  # single-cycle dungeon
                elif dungeon == "Veo Lu Sluice":
                    cycle = min(cycle, 2)  # only 2 distinct cycles; drained state persists after

                just_entered = (dungeon != ctx.current_dungeon or cycle != ctx.current_cycle)
                if just_entered:
                    ctx.current_dungeon  = dungeon
                    ctx.current_cycle    = cycle
                    ctx.prev_chest_flags = bytes(8)
                    _restore_sent_chest_bits(dungeon, cycle, ctx.checked_locations)
                    logger.info(f"FFCC: Entered {dungeon} — Cycle {cycle}")
                    if cycle >= 2:
                        cycle_loc_name = f"{dungeon} - Cycle {cycle} Reached"
                        cycle_loc_data = LOCATION_TABLE.get(cycle_loc_name)
                        if cycle_loc_data:
                            ap_id = 2326528 + cycle_loc_data.code
                            if ap_id not in ctx.checked_locations:
                                await ctx.send_msgs([{"cmd": "LocationChecks", "locations": [ap_id]}])
                                logger.info(f"FFCC: Cycle advancement — {cycle_loc_name}")

                # ── Check for newly opened chests ─────────────────────────────
                curr_flags = _read_chest_flags()
                new_locs   = _find_new_chest_locations(dungeon, cycle,
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
                                logger.info(f"FFCC: Chest opened — {loc_name}")
                    if ap_ids:
                        await ctx.send_msgs([{"cmd": "LocationChecks", "locations": ap_ids}])

                # ── Process received items ────────────────────────────────────
                if ctx.items_received:
                    for idx in range(ctx.received_index, len(ctx.items_received)):
                        network_item = ctx.items_received[idx]

                        # Hybrid patch: item was physically placed in the chest and
                        # given by the game engine on pickup — skip the memory-write.
                        if network_item.location in ctx.physical_chest_ap_ids:
                            ctx.received_index = idx + 1
                            item_name = LOOKUP_ID_TO_NAME.get(network_item.item, "?")
                            logger.info(f"FFCC: {item_name} already given by chest — skipping write")
                            continue

                        item_name = LOOKUP_ID_TO_NAME.get(network_item.item)
                        if item_name:
                            if _give_item(ctx, item_name):
                                ctx.received_index = idx + 1
                                item_data = ITEM_TABLE.get(item_name)
                                if not item_data or item_data.type != "Placeholder":
                                    logger.info(f"FFCC: Received {item_name}")
                            else:
                                break  # try again next tick

                # ── DeathLink ─────────────────────────────────────────────────
                if "DeathLink" in ctx.tags:
                    await _check_death(ctx)

                # ── Victory check ─────────────────────────────────────────────
                if not ctx.finished_game:
                    await _check_victory(ctx)

            else:
                # ── Not connected — attempt to connect / reconnect ────────────
                if ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                    logger.info("FFCC: Connection to Dolphin lost, reconnecting...")
                    ctx.dolphin_status   = CONNECTION_LOST_STATUS
                    ctx.current_dungeon  = None
                    ctx.current_year     = None
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
                ctx.dolphin_status   = CONNECTION_CONNECTED_STATUS
                ctx.prev_chest_flags = bytes(8)
                ctx.current_dungeon  = None
                ctx.current_year     = None

        except Exception:
            logger.error(f"FFCC dolphin sync error:\n{traceback.format_exc()}")
            if dme.is_hooked():
                dme.un_hook()
            ctx.dolphin_status   = CONNECTION_LOST_STATUS
            ctx.current_dungeon  = None
            ctx.current_year     = None
            ctx.prev_chest_flags = bytes(8)
            await ctx.disconnect()
            await asyncio.sleep(5)


async def _check_victory(ctx: FFCCContext) -> None:
    """Send goal completion when all Mount Vellenge locations are checked."""
    mv_locs = [
        name for name, data in LOCATION_TABLE.items()
        if data.region == "Mount Vellenge"
    ]
    from .locations import FFCCLocation
    mv_ap_ids = {FFCCLocation.get_apid(LOCATION_TABLE[n].code) for n in mv_locs}
    if mv_ap_ids and mv_ap_ids.issubset(ctx.checked_locations):
        await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
        ctx.finished_game = True
        logger.info("FFCC: Goal complete — congratulations!")


# ── Entry point ────────────────────────────────────────────────────────────────

def launch(*launch_args: str) -> None:
    async def main() -> None:
        parser = get_base_parser()
        args   = parser.parse_args(launch_args)
        ctx    = FFCCContext(args.connect, args.password)

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

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
