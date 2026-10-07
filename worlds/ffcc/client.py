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
from .items import ITEM_TABLE, LOOKUP_ID_TO_NAME, PROGRESSIVE_ARTIFACT_ORDER, PROGRESSIVE_ARTIFACT_NAME, STAGE_KEYS
from .locations import LOCATION_TABLE, FFCCLocationData

# Expected game ID
GAME_ID      = b"GCCE"     # FFCC NTSC-U 4-byte game code
GAME_ID_ADDR = 0x80000000

# Connection status strings
CONNECTION_INITIAL_STATUS   = "Dolphin connection has not been initiated."
CONNECTION_CONNECTED_STATUS = "Dolphin connected successfully."
CONNECTION_REFUSED_STATUS   = "Dolphin refused: wrong game loaded. Please load FFCC NTSC-U."
CONNECTION_LOST_STATUS      = "Dolphin connection was lost. Please restart your emulator and ensure FFCC is running."

# World / dungeon state
ADDR_MAP_ID      = 0x8021de9b   # 1 byte: 0x00-0x0d = dungeon, others = not in dungeon
ADDR_CURRENT_YEAR = 0x8021de93  # 1 byte: current caravan year (1=Year1, 2=Year2, ...)
ADDR_WORLD_MAP   = 0x8021f25a   # 1 byte: 0x01 = on world map
ADDR_PAUSED      = 0x8021f25b   # 1 byte: 0x01 = paused

# Per-dungeon cycle address: map_id 0 → 0x8021deb3, map_id 1 → +4, etc.
ADDR_CYCLE_BASE = 0x8021deb3   # 0x00=Cycle1, 0x01=Cycle2, 0x02=Cycle3

# Player stats
ADDR_MAX_HEARTS = 0x8021f28b   # 1 byte
ADDR_CUR_HEARTS = 0x8021f28d   # 1 byte (1 heart = 2 units; 0 = dead)

# Status effects (2 bytes each; write any nonzero value to apply)
ADDR_FROZEN     = 0x8021f2ae
ADDR_BURNED     = 0x8021f2b0
ADDR_POISONED   = 0x8021f2b2
ADDR_PARALYZED  = 0x8021f2b6
ADDR_SLOWED     = 0x8021f2be

# Inventory / items
ADDR_ITEM_BAG   = 0x8021f33a   # material bag start (2 bytes per slot)
ADDR_ARTIFACT   = 0x8021f3a6   # artifact bag start (2 bytes per slot)
ADDR_GIL        = 0x8021f470   # 4 bytes BE

# Number of 2-byte slots in the material bag (ADDR_ITEM_BAG → ADDR_ARTIFACT).
ITEM_BAG_SLOTS      = (ADDR_ARTIFACT - ADDR_ITEM_BAG) // 2   # = 54
# Number of 2-byte slots in the artifact bag (ADDR_ARTIFACT → ADDR_GIL).
ARTIFACT_BAG_SLOTS  = (ADDR_GIL - ADDR_ARTIFACT) // 2        # = 101
ITEM_SLOT_EMPTY = 0xffff  # sentinel for an empty inventory slot (confirmed via memory view)

# Chalice / bonus / food
ADDR_CHALICE    = 0x8021ef3f   # low byte of the chalice element: 1=Fire,2=Water,4=Wind,8=Earth,16=Unknown
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
ADDR_BONUS      = 0x8021fe14   # 1 byte: 0x01–0x18
ADDR_FOOD_BASE  = 0x8021f629   # 2 bytes × 8 foods (Striped Apple, Cherry Cluster, …)

# Chest bit flags (8 bytes, shared/reused per dungeon, cleared on dungeon exit)
ADDR_CHEST_BASE = 0x80926000

# Trap Setup

ADDR_TRAP_HOOK    = 0x80111a48   # 48 09 82 61 when the randomizer's trap-visuals patch is installed
ADDR_TRAP_PENDING = 0x801a9d28   # u16 per status: 0 freeze, 1 burn, 2 poison, 4 paralysis, 8 slow
TRAP_STATUS_INDEX = {"Frozen Trap": 0, "Burned Trap": 1, "Poisoned Trap": 2,"Paralyzed Trap": 4, "Slowed Trap": 8}
TRAP_TIMER_ADDR   = {"Frozen Trap": ADDR_FROZEN, "Burned Trap": ADDR_BURNED,
                     "Poisoned Trap": ADDR_POISONED,"Paralyzed Trap": ADDR_PARALYZED, "Slowed Trap": ADDR_SLOWED}

# Myrrh / Stages flags
ADDR_MYRRH_COLLECTED = 0x8021ef6d  # 2 bytes: bit n of (byte0 | byte1<<8) = dungeon n cleared
                                   # (event flags 200+n). Confirmed live for River (bit 0) and Goblin Wall (bit 1).
MYRRH_DUNGEONS = 13                # River Belle Path (0) .. Rebena Te Ra (12); Mount Vellenge has no tree
ALL_MYRRH_MASK = (1 << MYRRH_DUNGEONS) - 1

# Credits Victory Setup

ADDR_SCRIPT_NAME_ID = 0x80299780   # chars 3-6 of the loaded stage script's name
ENDING_IDS = (0x34345F32, 0x34345F33)  # "44_2" = ending (ff44_2), "44_3" = credits (ff44_3)

# Map ID → dungeon name
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

#  Chest flags per dungeon
# From chest_table.py (generated from the game files): each chest's
# "opened" flag(s). Flag n = bit n of the big-endian u32 words at
# ADDR_CHEST_BASE: byte 4*(n//32) + 3 - (n%32)//8, bit n%8. The same table
# numbers the AP locations and drives the patcher, so a flag always reports
# the chest the item was put in.
from .chest_table import CHESTS


def _flag_pos(n: int) -> Tuple[int, int]:
    return 4 * (n // 32) + 3 - (n % 32) // 8, n % 8

# dungeon -> {(byte, bit): (chest, cycles)}
CHEST_FLAGS: Dict[str, Dict[Tuple[int, int], Tuple[int, Tuple[int, ...]]]] = {
    dungeon: {_flag_pos(f): (chest, cycles) for chest, cycles, flags in rows for f in flags}
    for dungeon, rows in CHESTS.items()
}


def _chest_location(dungeon: str, cycle: int, chest: int) -> str:
    return f"{dungeon} - Cycle {cycle} - Chest {chest}"

# Helpers

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

# Command processor

class FFCCCommandProcessor(ClientCommandProcessor):
    def _cmd_dolphin(self) -> None:
        """Show Dolphin connection status."""
        if isinstance(self.ctx, FFCCContext):
            logger.info(f"Dolphin status: {self.ctx.dolphin_status}")

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
            logger.info(f"Unknown element {element!r}. Use one of: {', '.join(CHALICE_ELEMENTS)}")
            return False
        _write_byte(ADDR_CHALICE, value)
        logger.info(f"Chalice element set to {names[value]}.")
        return True

    def _cmd_stagekeys(self, mode: str = "") -> bool:
        """Turn the stage-key locks off or back on: /stagekeys off|on.
        "off" puts every dungeon's key in your artifact bag so all dungeons
        open (handy if you're stuck; dungeons may then be out of logic).
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
                    if not _give_artifact(key_id):
                        logger.info("Your artifact bag is full - free a slot and try again.")
                        return False
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
            logger.info(f"Name one dungeon: {', '.join(MYRRH_TREE_DUNGEONS)}")
            return False
        n = matches[0]
        _write_byte(ADDR_MYRRH_TREE + 4 * n, MYRRH_TREE_READY)
        logger.info(f"{MYRRH_TREE_DUNGEONS[n]}'s Myrrh tree is ready again.")
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
            logger.info(f"Myrrh trees collected: {bin(trees).count('1')}/{MYRRH_DUNGEONS}")
        keys = sorted({LOOKUP_ID_TO_NAME.get(i.item, "") for i in ctx.items_received
                       if ITEM_TABLE.get(LOOKUP_ID_TO_NAME.get(i.item, "")) is not None
                       and ITEM_TABLE[LOOKUP_ID_TO_NAME[i.item]].type == "Stage Key"})
        logger.info("Stage keys: " + (", ".join(keys) if keys else "none yet"))
        return True

class FFCCContext(CommonContext):
    command_processor = FFCCCommandProcessor
    game              = game_name
    items_handling    = 0b111  # full remote items
    victory: int

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
        self.victory: int = 0

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
            self.set_notify(_myrrh_key(self))
            if slot_data.get("victory_goal"):
                self.victory = args["slot_data"]["victory_goal"]
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


# Item giving

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

    if data.type in ("Artifact", "Stage Key"):
        return _give_artifact(data.item_id)  # False if bag full → retry

    # Materials, Food, Recipes, Magicite, Phoenix Down — find a free bag slot.
    # Empty slots are 0xffff; never overwrite an occupied slot.
    addr = _find_free_item_slot()
    if addr is None:
        logger.warning("FFCC: Item bag is full — cannot deliver item, will retry.")
        return False  # retry on next tick
    _write_short(addr, data.item_id)
    return True


def _received_stage_keys(ctx: "FFCCContext") -> Set[int]:
    """In-game IDs of the stage keys received from the multiworld."""
    ids = {ITEM_TABLE[name].item_id for name, _ in STAGE_KEYS}
    out = set()
    for net_item in ctx.items_received:
        data = ITEM_TABLE.get(LOOKUP_ID_TO_NAME.get(net_item.item, ""))
        if data is not None and data.item_id in ids:
            out.add(data.item_id)
    return out


def _stage_keys_in_bag() -> Set[int]:
    """In-game IDs of the stage keys currently in the artifact bag."""
    ids = {key_id for _, key_id in STAGE_KEYS}
    return {v for v in (_read_short(ADDR_ARTIFACT + i * 2) for i in range(ARTIFACT_BAG_SLOTS)) if v in ids}


def _remove_stage_keys(keep: Set[int]) -> int:
    """Empty the artifact bag slots holding stage keys not in `keep`."""
    ids = {key_id for _, key_id in STAGE_KEYS}
    removed = 0
    for i in range(ARTIFACT_BAG_SLOTS):
        addr = ADDR_ARTIFACT + i * 2
        v = _read_short(addr)
        if v in ids and v not in keep:
            _write_short(addr, ITEM_SLOT_EMPTY)
            removed += 1
    return removed


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
    if trap_name in TRAP_STATUS_INDEX:
        _apply_status_trap(trap_name)
    elif trap_name == "Chalice Element Trap":
        elements = [0x01, 0x02, 0x04, 0x08]  # Fire, Water, Wind, Earth (never the Unknown element)
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


# Chest detection

def _find_new_chest_locations(dungeon: str, cycle: int,
                               prev: bytes, curr: bytes) -> List[str]:
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
                logger.info(f"FFCC: Unmapped chest flag byte={byte_off}, bit={bit_idx} in {dungeon!r}")
                continue
            chest, cycles = hit
            loc_name = _chest_location(dungeon, cycle, chest)
            logger.info(f"FFCC: Chest flag (byte={byte_off}, bit={bit_idx}) → {loc_name!r}")
            if cycle in cycles and loc_name in LOCATION_TABLE and loc_name not in found:
                found.append(loc_name)
    return found


def _restore_sent_chest_bits(dungeon: str, cycle: int,
                              checked_locs: Set[int]) -> None:
    """Force chest bits for already-checked locations so chests appear open on re-entry."""
    from .locations import FFCCLocation
    for (byte_off, bit_idx), (chest, cycles) in CHEST_FLAGS.get(dungeon, {}).items():
        loc_data = LOCATION_TABLE.get(_chest_location(dungeon, cycle, chest))
        if loc_data and FFCCLocation.get_apid(loc_data.code) in checked_locs:
            _force_chest_flag(byte_off, bit_idx)


# Death detection

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

                in_dungeon = _is_in_dungeon()

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
                                if ap_id not in ctx.checked_locations:
                                    await ctx.send_msgs([{"cmd": "LocationChecks",
                                                          "locations": [ap_id]}])
                                    logger.info(f"FFCC: Year advancement — Year {y} has begun")
                # Check victory
                if not ctx.finished_game:
                    await _check_victory(ctx)

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

                # Check for newly opened chests
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

                # Process received items
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

                # DeathLink
                if "DeathLink" in ctx.tags:
                    await _check_death(ctx)

            else:
                # Not connected - attempt to connect / reconnect
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
    """Send goal completion when victory goal is finished"""
    if ctx.victory == 0:  # collect all 13 Myrrh drops
        key    = _myrrh_key(ctx)
        stored = ctx.stored_data.get(key) or 0
        mask   = _read_myrrh_mask()
        if mask & ~stored:
            # Bits reset each year, so remember every dungeon ever seen on the server.
            await ctx.send_msgs([{"cmd": "Set", "key": key, "default": 0, "want_reply": True,
                                  "operations": [{"operation": "or", "value": mask}]}])
            stored |= mask
            ctx.stored_data[key] = stored
            logger.info(f"FFCC: Myrrh trees harvested: {bin(stored).count('1')}/{MYRRH_DUNGEONS}")

        if stored & ALL_MYRRH_MASK == ALL_MYRRH_MASK:
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True
            logger.info("FFCC: Goal complete — congratulations!")

    elif ctx.victory == 1:  # defeat the final boss (Mount Vellenge) and enter credits / end screen
        if _read_int(ADDR_SCRIPT_NAME_ID) in ENDING_IDS:
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True
            logger.info("FFCC: Goal complete — congratulations!")

def _read_myrrh_mask() -> int:
    raw = dme.read_bytes(ADDR_MYRRH_COLLECTED, 2)
    return (raw[0] | (raw[1] << 8)) & ALL_MYRRH_MASK

def _myrrh_key(ctx: "FFCCContext") -> str:
    return f"ffcc_myrrh_{ctx.team}_{ctx.slot}"

def _apply_status_trap(trap_name: str, frames: int = 0x012c) -> None:   # 300 frames = ~5 s
    if dme.read_bytes(ADDR_TRAP_HOOK, 4) == bytes.fromhex("48098261"):
        _write_short(ADDR_TRAP_PENDING + 2 * TRAP_STATUS_INDEX[trap_name], frames)  # game applies it + visual
    else:
        _write_short(TRAP_TIMER_ADDR[trap_name], frames)                            # unpatched ISO: no visual

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
