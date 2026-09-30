import asyncio
import traceback
import dolphin_memory_engine
import time

import Utils
import websockets
import functools
from copy import deepcopy
from typing import List, Any, Iterable, Any, Optional
from NetUtils import decode, encode, JSONtoTextParser, JSONMessagePart, NetworkItem, NetworkPlayer, ClientStatus
from MultiServer import Endpoint
from CommonClient import gui_enabled, ClientCommandProcessor, logger, get_base_parser

tracker_loaded = False
try:
    from worlds.tracker.TrackerClient import TrackerGameContext as SuperContext, TrackerCommandProcessor as SuperCommandProcessor
    tracker_loaded = True
except ModuleNotFoundError:
    from CommonClient import CommonContext as SuperContext, ClientCommandProcessor as SuperCommandProcessor

from .items import LOOKUP_ID_TO_NAME, ITEM_TABLE
from .locations import LOCATION_TABLE, ChibiRoboLocation, ChibiRoboLocationData

DEBUG = True

CONNECTION_REFUSED_GAME_STATUS = (
    "Dolphin failed to connect. Please load a randomized ROM for Chibi Robo. Trying again in 5 seconds..."
)
CONNECTION_REFUSED_SAVE_STATUS = (
    "Dolphin failed to connect. Please load into the save file. Trying again in 5 seconds..."
)
CONNECTION_LOST_STATUS = (
    "Dolphin connection was lost. Please restart your emulator and make sure Chibi Robo is running."
)
CONNECTION_CONNECTED_STATUS = "Dolphin connected successfully."
CONNECTION_INITIAL_STATUS = "Dolphin connection has not been initiated."

# The expected index for the following item that should be received.
# Saves over total times player has recharged that is no longer increased via patcher
EXPECTED_INDEX_ADDR = 0x803686a6

GIVE_ITEM_ARRAY_ADDR = 0x8038f778

CURRENT_INDEX_ADDR = 0

# This address contains the current stage / room ID.
CURR_STAGE_ID_ADDR = 0x8025f847

CURR_GAME_STATE = 0x8025df17

# This address is used to check/set the player's battery
CURR_BATTERY_ADDR = 0x8038f748

# var(1874.d) pending "Pan Drop Trap" count. 0x8036973e (var 1860's confirmed address) +
# (1874-1860)*4 = 0x80369774 - cross-checked against var(1872)'s 0x8036976e + 2*4, same answer.
PAN_DROP_TRAP_VAR_ADDR = 0x80369774

# Script variables: var(N) is the 32-bit word at SCRIPT_VAR_BASE + N*4 (decomp lbl_80367A2C,
# 0x2010 bytes, saved with the game). Write the whole word - the engine only keeps the low
# 16 bits when it reads a var, so writing 2 bytes at the word's start sets the wrong half.
SCRIPT_VAR_BASE = 0x80367a2c

# Door vars each key opens (initialised to 0 in the randomizer's stage05.us sub_576).
KEY_DOOR_VARS = {
    "Living Room - Kitchen Key":  (1870, 1860),  # Living Room -> Kitchen, Kitchen -> Living Room
    "Living Room - Foyer Key":    (1863, 1869),  # Foyer -> Living Room, Living Room -> Foyer
    "Kitchen - Foyer Key":        (1862, 1865),  # Foyer -> Kitchen, Kitchen -> Foyer
    "Foyer - Jenny's Room Key":   (1861, 1866),  # Foyer -> Jenny's Room, Jenny's Room -> Foyer
    "Foyer - Bedroom Key":        (1864, 1868),  # Foyer -> Bedroom, Bedroom -> Foyer
    "Living Room - Backyard Key": (1871, 1873),  # Living Room -> Backyard, Backyard -> Living Room
    "Foyer - Basement Key":       (1872,),       # Foyer -> Basement
}

# Utilibot vars: 0 = not built, 1 = built (what the vanilla scripts set; rooms show the
# utilibot when >= 1), 2 = built and used once (set by the game). The addresses in items.py
# are byte writes that land in the wrong part of the 32-bit var - for Foyer Teleport
# (0x8036852c = top byte of var(704)) the game reads 0, so it never appeared.
UTILIBOT_VARS = {
    "Living Room Ladder": 701,
    "Kitchen Ladder":     702,
    "Foyer Ladder":       703,
    "Foyer Teleport":     704,
    "Living Room Bridge": 705,
    "Kitchen Bridge":     706,
    "Bedroom Bridge":     707,
    "Basement Teleport":  708,
}

GC_GAME_ID_ADDRESS = 0x80000000

MOOLAH_ADDR = 0x8038f752

SCRAP_ADDR = 0X8038f756

HAPPY_POINTS_ADDR = 0x8038f73e

GBA_MESSAGE = 0x80672300

# ---- GBA link cable popups ---------------------------------------------------------------------
# The GBA link patch (randomizer option / apworld option gba_link) puts a mailbox at GBA_MESSAGE.
# Writing a message there makes the game show it as a popup on a GBA plugged into port 2-4; the
# player closes it with A/B on the GameCube controller or A on the GBA. The mailbox holds ONE
# message at a time - the game copies it into its own queue (up to 6) and sets ack = post, usually
# within a frame. Layout (big-endian) is documented in chibi-mini-gba gc/source/messages.h.
GBA_MB_MAGIC = b"CLMB"
GBA_MB_POST = 0x08           # u32, we bump this after filling in the message
GBA_MB_ACK = 0x0C            # u32, game sets = post once it has queued the message
GBA_MB_ICON = 0x10           # u8 icon, u8 reserved, u16 duration in frames (0 = until closed)
GBA_MB_TITLE = 0x14          # 16 bytes, NUL terminated
GBA_MB_TEXT = 0x24           # 96 bytes, NUL terminated, "\n" = line break
GBA_MB_LINK_STATE = 0x84     # u32, 0 = no GBA, 1 = connecting, 2 = linked
GBA_MB_LAST_CLOSED = 0x88    # u32, sequence number of the last popup the player closed
GBA_TITLE_MAX = 15           # characters (+ NUL)
GBA_TEXT_MAX = 95

# Icons available on the GBA (match CL_ICON_* in chibi_link_protocol.h)
GBA_ICON_BATTERY = 0
GBA_ICON_COIN = 1
GBA_ICON_HEART = 2
GBA_ICON_HOUSE = 3
GBA_ICON_CLOCK = 4
GBA_ICON_PLUG = 5

# Sticker completion flags: name -> (address, 16-bit bitmask).
# A sticker is earned when (read_short(address) & bitmask) == bitmask.
STICKER_FLAGS = {
    "Giga-Robo Sticker":          (0x8036781c, 0x0008),
    "Telly Vision Sticker":       (0x8036789a, 0x0100),
    "Chibi - Door Sticker":       (0x803678ac, 0x2000),
    "Utilibot Sticker":           (0x80367846, 0x0002),
    "Frog Ring Sticker":          (0x803678e6, 0x1000),
    "Frog Sticker":               (0x8036786c, 0x0800),
    "Bluebird Sticker":           (0x803678a0, 0x0800),
    "Mr. Prongs Sticker":         (0x803678a6, 0x0004),
    "Drake Redcrest Sticker":     (0x803678e4, 0x0002),
    "Sophie Sticker":             (0x803678d8, 0x0008),
    "Free Rangers Sticker":       (0x80367892, 0x0100),
    "Captain Plankbeard Sticker": (0x803678d8, 0x0400),
    "The Great Peekoe Sticker":   (0x803678a2, 0x8000),
    "Sunshine Sticker":           (0x803678da, 0x0020),
    "Mort & Princess Sticker":    (0x80367882, 0x8000),
    "Dinah Sticker":              (0x803678a0, 0x2000),
    "Funky Phil Sticker":         (0x803678a0, 0x1000),
    "Queen Spydor Sticker":       (0x8036781c, 0x0002),
    "Hot Rod Sticker":            (0x803678b6, 0x0200),
    "Space Scrambler Sticker":    (0x803678b6, 0x0400),
    "Cooking Sticker":            (0x803678b6, 0x0800),
    "Kid Eggplant Sticker":       (0x803678e6, 0x8000),
    "Primopuel Sticker":          (0x803678e4, 0x0004),
    "Tamagotchi Sticker":         (0x803678e4, 0x0008),
}

class ChibiRoboJSONToTextParser(JSONtoTextParser):
    def _handle_color(self, node: JSONMessagePart):
        return self._handle_text(node)  # No colors for the in-game text


class ChibiRoboCommandProcessor(SuperCommandProcessor):
    def __init__(self, ctx: SuperContext):
        """
        Initialize the command processor with the provided context.

        :param ctx: Context for the client.
        """
        super().__init__(ctx)

    def _cmd_infinite_energy(self) -> None:
        """
        Enable Infinite Energy
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():
            write_short(0x8038f75a, 1)
            return

    def _cmd_gba(self, *text: str) -> None:
        """
        Show a popup message on the linked GBA (needs the GBA link option). Example: /gba Hello!
        """
        if not isinstance(self.ctx, ChibiRoboContext) or not dolphin_memory_engine.is_hooked():
            logger.info("Not connected to Dolphin.")
            return
        if not gba_link_available():
            logger.info("This ISO doesn't have the GBA link patch (gba_link option).")
            return
        if not gba_link_connected():
            logger.info("No GBA is linked right now.")
            return
        queue_gba_message(self.ctx, "Message", " ".join(text) or "Hello from the Archipelago client!")
        logger.info("Sent to the GBA.")

    def _cmd_equip_blaster(self) -> None:
        """
        Equips Blaster
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():
            write_short(0x8038f6c2, 2)
            write_short(0x8038f6c4, 0)
            write_short(0x8038f6c6, 2)
            logger.info("Equipping Blaster")
            return

    def _cmd_equip_radar(self) -> None:
        """
        Equips Radar
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():
            write_short(0x8038f6c2, 3)
            write_short(0x8038f6c4, 0)
            write_short(0x8038f6c6, 3)
            logger.info("Equipping Radar")
            return

    def _cmd_enable_radar(self) -> None:
        """
        Enable Radar
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():
            write_short(0x80398f00, 1)
            logger.info("Enabled Radar")
            return

    def _cmd_enable_copter(self) -> None:
        """
        Enable Copter
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():
            write_short(0x80398ef2, 1)
            logger.info("Enabled Copter")
            return

    def _cmd_enable_blaster(self) -> None:
        """
        Enable Blaster
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():
            write_short(0x80398ef8, 1)
            logger.info("Enabled Blaster")
            return

    def _cmd_enable_living_ladder(self) -> None:
        """
        Enable Blaster
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():
            write_short(0x80368522, 1)
            logger.info("Living Room Ladder Enabled")
            return

    def _cmd_enable_foyer_ladder(self) -> None:
        """
        Enable Blaster
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():
            write_short(0x8036852a, 1)
            logger.info("Foyer Ladder Enabled")
            return

    def _cmd_enable_foyer_teleport(self) -> None:
        """
        Enable Foyer Teleport
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():
            write_short(0x8036852c, 1)
            logger.info("Foyer Teleport Enabled")
            return

    def _cmd_enable_living_bridge(self) -> None:
        """
        Enable Living Room Bridge
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():
            write_short(0x80368532, 1)
            logger.info("Living Room Bridge Enabled")
            return

    def _cmd_enable_kitchen_ladder(self) -> None:
        """
        Enable Kitchen Ladder
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():
            write_short(0x80368526, 1)
            logger.info("Kitchen Ladder Enabled")
            return

    def _cmd_enable_kitchen_bridge(self) -> None:
        """
        Enable Kitchen Bridge
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():
            write_short(0x80368536, 1)
            logger.info("Kitchen Bridge Enabled")
            return

    def _cmd_enable_bedroom_bridge(self) -> None:
        """
        Enable Bedroom Bridge
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():
            write_short(0x8036853a, 1)
            logger.info("Bedroom Bridge Enabled")
            return

    def _cmd_enable_basement_teleport(self) -> None:
        """
        Enable Basement Teleport
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():
            write_short(0x8036853e, 1)
            logger.info("Basement Teleport Enabled")
            return

    def _cmd_increase_giga_charge(self) -> None:
        """
        Increases Giga Charge (Max of 9)
        """
        if isinstance(self.ctx, ChibiRoboContext) and check_ingame():

            cur_charge = read_4byte_short(0x80367c4c)
            if cur_charge < 9000:
                write_4byte_short(0x80367c4c, cur_charge + 1000)
            else:
                logger.info("Giga Battery is at max (9000) charge")

        return

    def _cmd_unlock_kitchen(self) -> None:
        """
        Unlocks Kitchen
        """
        if isinstance(self.ctx, ChibiRoboContext):
            unlock_key_doors("Living Room - Kitchen Key")
            logger.info("Kitchen doors unlocked")
            return

    def _cmd_unlock_foyer(self) -> None:
        """
        Unlocks Foyer
        """
        if isinstance(self.ctx, ChibiRoboContext):
            unlock_key_doors("Living Room - Foyer Key")
            unlock_key_doors("Kitchen - Foyer Key")

            logger.info("Foyer doors unlocked")

            return

    def _cmd_unlock_jenny(self) -> None:
        """
        Unlocks Jenny's Room
        """
        if isinstance(self.ctx, ChibiRoboContext):
            unlock_key_doors("Foyer - Jenny's Room Key")

            logger.info("Jenny doors unlocked")

            return

    def _cmd_unlock_bedroom(self) -> None:
        """
        Unlocks Bedroom
        """
        if isinstance(self.ctx, ChibiRoboContext):
            unlock_key_doors("Foyer - Bedroom Key")

            logger.info("Bedroom doors unlocked")
            return

    def _cmd_unlock_backyard(self) -> None:
        """
        Unlocks Backyard
        """
        if isinstance(self.ctx, ChibiRoboContext):
            unlock_key_doors("Living Room - Backyard Key")

            logger.info("Backyard doors unlocked")
            return

    def _cmd_unlock_basement(self) -> None:
        """
        Unlocks Basement
        """
        if isinstance(self.ctx, ChibiRoboContext):
            unlock_key_doors("Foyer - Basement Key")

            logger.info("Basement door unlocked")
            return

    def _cmd_dolphin(self) -> None:
        """
        Display the current Dolphin emulator connection status.
        """
        if isinstance(self.ctx, ChibiRoboContext):
            logger.info(f"Dolphin Status: {self.ctx.dolphin_status}")
            return

    def _cmd_give_sticker(self, sticker) -> None:
        """
        Gives Sticker Make sure to use the exact name. Example "Telly Vision Sticker"
        """
        if isinstance(self.ctx, ChibiRoboContext):
            give_sticker(sticker)
            return

    def _cmd_remove_sticker(self, sticker) -> None:
        """
        Removes Sticker Make sure to use the exact name. Example "Telly Vision Sticker"
        """
        if isinstance(self.ctx, ChibiRoboContext):
            remove_sticker(sticker)
            return


class ChibiRoboContext(SuperContext):
    command_processor = ChibiRoboCommandProcessor
    game = "Chibi Robo"
    items_handling: int = 0b111 # Items get sent to us including starting inventory
    # items_handling: int = 0b101 # Items get sent to us including starting inventory but our own items are not sent to us
    len_give_item_array: int = 0x272
    items_received = []
    victory: int
    required_stickers: List[str] = []
    tags = {"AP"}

    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        super().__init__(server_address, password)
        self.dolphin_sync_task: Optional[asyncio.Task[None]] = None
        self.dolphin_status: str = CONNECTION_INITIAL_STATUS
        self.awaiting_rom: bool = False
        self.has_send_death: bool = False

        self.proxy = None
        self.proxy_task = None
        self.gamejsontotext = ChibiRoboJSONToTextParser(self)
        self.autoreconnect_task = None
        self.endpoint = None
        self.room_info = None
        self.connected_msg = None
        self.game_connected = False
        self.awaiting_info = False
        self.full_inventory: List[Any] = []
        self.server_msgs: List[Any] = []

        self.current_stage_name: str = ""
        self.curr_stage_pickup: int = 0
        self.victory: int = 0
        self.required_stickers: List[str] = []
        # (title, text, icon, duration) popups waiting for the GBA mailbox, see queue_gba_message
        self.gba_message_queue: List[Any] = []


    async def server_auth(self, password_requested: bool = True) -> None:
        if password_requested and not self.password:
            await super().server_auth(password_requested)

        await self.get_username()
        await self.send_connect()

    def get_chibi_robo_status(self) -> str:
        if not self.is_proxy_connected():
            return "Not connected to Chibi Robo"

        return "Connected to Chibi Robo"

    async def send_msgs_proxy(self, msgs: Iterable[dict]) -> bool:
        """ `msgs` JSON serializable """
        if not self.endpoint or not self.endpoint.socket.open or self.endpoint.socket.closed:
            return False

        if DEBUG:
            logger.info(f"Outgoing message: {msgs}")

        await self.endpoint.socket.send(msgs)
        return True

    async def disconnect(self, allow_autoreconnect: bool = False) -> None:
        self.auth = None
        self.current_stage_name = ""
        await super().disconnect(allow_autoreconnect)

    async def disconnect_proxy(self):
        if self.endpoint and not self.endpoint.socket.closed:
            await self.endpoint.socket.close()
        if self.proxy_task is not None:
            await self.proxy_task

    def is_connected(self) -> bool:
        return self.server and self.server.socket.open

    def is_proxy_connected(self) -> bool:
        return self.endpoint and self.endpoint.socket.open

    def on_print_json(self, args: dict):
        text = self.gamejsontotext(deepcopy(args["data"]))
        msg = {"cmd": "PrintJSON", "data": [{"text": text}], "type": "Chat"}
        self.server_msgs.append(encode([msg]))

        if self.ui:
            self.ui.print_json(args["data"])
        else:
            text = self.jsontotextparser(args["data"])
            logger.info(text)

    def update_items(self):
        if not self.is_connected():
            return

        self.server_msgs.append(encode([{"cmd": "ReceivedItems", "index": 0, "items": self.full_inventory}]))

    def on_package(self, cmd: str, args: dict):
        super().on_package(cmd, args)
        ctx = self
        if cmd == "Connected":

            json = args
            if "slot_info" in json.keys():
                json["slot_info"] = {}
                ctx.victory = args["slot_data"]["victory_goal"]
                ctx.required_stickers = args["slot_data"].get("_chibi_stickers") or args["slot_data"].get("required_stickers", [])
            if "death_link" + "group_death_link" in args["slot_data"]:
                Utils.async_start(self.update_death_link(bool(args["slot_data"]["death_link"]['group_death_link'])))
            if "players" in json.keys():
                me: NetworkPlayer
                for n in json["players"]:
                    if n.slot == json["slot"] and n.team == json["team"]:
                        me = n
                        break

                json["players"] = [me]
            if DEBUG:
                print(json)
            self.connected_msg = encode([json])
            if self.awaiting_info:
                self.server_msgs.append(self.room_info)
                self.update_items()
                self.awaiting_info = False

        elif cmd == "RoomUpdate":
            json = args
            if "players" in json.keys():
                json["players"] = []

            self.server_msgs.append(encode(json))

        elif cmd == "RoomInfo":
            self.seed_name = args["seed_name"]
            self.room_info = encode([args])
        else:
            if cmd != "PrintJSON":
                self.server_msgs.append(encode([args]))

    def on_deathlink(self, data: dict[str, Any]) -> None:
        """
        Handle a DeathLink event.

        :param data: The data associated with the DeathLink event.
        """
        super().on_deathlink(data)
        _give_death(self)

    def run_gui(self):
        result = super().run_gui()

        if self.ui:
            self.ui.base_title = "Archipelago Chibi Robo Client"

        return result

def read_short(console_address: int) -> int:
    """
    Read a 2-byte short from Dolphin memory.

    :param console_address: Address to read from.
    :return: The value read from memory.
    """
    return int.from_bytes(dolphin_memory_engine.read_bytes(console_address, 2), byteorder="big")

def read_4byte_short(console_address: int) -> int:
    """
    Read a 4-byte short from Dolphin memory.

    :param console_address: Address to read from.
    :return: The value read from memory.
    """
    return int.from_bytes(dolphin_memory_engine.read_bytes(console_address, 4), byteorder="big")

def write_short(console_address: int, value: int) -> None:
    """
    Write a 2-byte short to Dolphin memory.

    :param console_address: Address to write to.
    :param value: Value to write.
    """
    dolphin_memory_engine.write_bytes(console_address, value.to_bytes(2, byteorder="big"))

def write_4byte_short(console_address: int, value: int) -> None:
    """
    Write a 4-byte short to Dolphin memory.

    :param console_address: Address to write to.
    :param value: Value to write.
    """
    dolphin_memory_engine.write_bytes(console_address, value.to_bytes(4, byteorder="big"))

def write_8byte_short(console_address: int, value: int) -> None:
    """
    Write a 4-byte short to Dolphin memory.

    :param console_address: Address to write to.
    :param value: Value to write.
    """
    dolphin_memory_engine.write_bytes(console_address, value.to_bytes(8, byteorder="big"))

def read_string(console_address: int, strlen: int) -> str:
    """
    Read a string from Dolphin memory.

    :param console_address: Address to start reading from.
    :param strlen: Length of the string to read.
    :return: The string.
    """

    return dolphin_memory_engine.read_bytes(console_address, strlen).split(b"\0", 1)[0].decode()

def _give_death(ctx: ChibiRoboContext) -> None:
    """
    Trigger the player's death in-game by setting their current health to zero.

    :param ctx: The client context.
    """
    if (
        ctx.slot is not None
        and dolphin_memory_engine.is_hooked()
        and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS
        and check_ingame()
    ):
        ctx.has_send_death = True
        write_short(CURR_BATTERY_ADDR, 0)

async def check_death(ctx: ChibiRoboContext) -> None:
    """
    Check if the player is currently dead in-game.
    If DeathLink is on, notify the server of the player's death.

    :return: `True` if the player is dead, otherwise `False`.
    """
    if ctx.slot is not None and check_ingame():
        cur_battery = read_short(CURR_BATTERY_ADDR)
        if cur_battery <= 0:
            if not ctx.has_send_death and time.time() >= ctx.last_death_link + 3:
                ctx.has_send_death = True
                await ctx.send_death(ctx.player_names[ctx.slot] + " ran out of battery.")
        else:
            ctx.has_send_death = False

def script_var_addr(var: int) -> int:
    """Address of script variable var(N) (a 32-bit word)."""
    return SCRIPT_VAR_BASE + var * 4


def unlock_key_doors(item_name: str) -> None:
    """Set every door var opened by `item_name` (one of KEY_DOOR_VARS) to 1."""
    for var in KEY_DOOR_VARS[item_name]:
        if read_4byte_short(script_var_addr(var)) != 1:
            write_4byte_short(script_var_addr(var), 1)


def sync_key_doors(ctx: ChibiRoboContext) -> None:
    """
    Re-open the doors for every key the player has received. Door state lives in script vars,
    and stage05's sub_576 (first Chibi-House load after the party) resets them all to 0 - so a
    key given before that point (start inventory, or items sent while the player was still in the
    intro) was wiped, and give_items() never gives it again because the expected index already
    moved past it. Deriving the vars from the received items every pass makes that self-healing,
    and also repairs saves where var(1873) got the old wrong-half write. A door's open/closed
    model is set when its room loads, so the player may need to re-enter the room once.
    """
    if dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 1) == b"\x0e":
        return
    received = {LOOKUP_ID_TO_NAME.get(item.item) for item in ctx.items_received}
    for item_name in KEY_DOOR_VARS:
        if item_name in received:
            unlock_key_doors(item_name)
    for item_name in UTILIBOT_VARS:
        if item_name in received:
            build_utilibot(item_name)


def build_utilibot(item_name: str) -> None:
    """
    Make the utilibot `item_name` (one of UTILIBOT_VARS) built. Only writes when the game would
    read it as not built (low 16 bits 0), so a used one (2) - or an old-client value like 256,
    which already counts as built - is left alone, while the old Foyer Teleport write
    (0x01000000, read as 0) gets repaired.
    """
    addr = script_var_addr(UTILIBOT_VARS[item_name])
    if read_4byte_short(addr) & 0xFFFF == 0:
        write_4byte_short(addr, 1)


def _give_item(ctx: ChibiRoboContext, item_name: str, player: int) -> bool:
    """
    Give an item to the player in-game.

    :param ctx: The client context.
    :param item_name: Name of the item to give.
    :return: Whether the item was successfully given.
    """

    if not check_ingame() or dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 1) == b"\x0e":
        return False

    item_id = ITEM_TABLE[item_name].item_id
    is_special = ITEM_TABLE[item_name].special
    IC = ITEM_TABLE[item_name].classification

    # Loop through the item array, placing the item in an empty slot.
    for idx in range(ctx.len_give_item_array):

        item_slot = dolphin_memory_engine.read_bytes(GIVE_ITEM_ARRAY_ADDR + idx, 2)
        current_item = dolphin_memory_engine.read_byte((GIVE_ITEM_ARRAY_ADDR + idx) + 1)

        if item_name.__contains__("Sticker"):
            give_sticker(item_name)
            return True

        if item_name == "Giga Battery Charge":
            # Make sure the giga battery doesn't go over 9000 otherwise player can't pick up the maxed battery
            cur_charge = read_4byte_short(0x80367c4c)
            if cur_charge < 9000:
                write_4byte_short(0x80367c4c, cur_charge + 1000)
                return True
            else:
                return True

        elif item_name == "Max Battery Increase":

            cur_max = read_short(0x8038f74c)
            write_short(0x8038f74c, cur_max + 20)

            return True

        elif item_name in KEY_DOOR_VARS:

            # sync_key_doors() keeps re-applying this afterwards, see its docstring.
            unlock_key_doors(item_name)

            return True

        elif item_name in UTILIBOT_VARS:

            # sync_key_doors() keeps re-applying this afterwards, like the keys.
            build_utilibot(item_name)

            return True

        elif item_name == "Pan Drop Trap":

            if player != ctx.slot:
                # Self-found Pan Drop Traps already play the animation instantly at pickup via
                # Form1.cs's injected .interact code (see project_pan_drop_trap memory) - only
                # queue here for traps found by OTHER players and delivered to us asynchronously.
                # Matches this function's existing convention for self-found items (see the
                # `ctx.slot == player` check below, for the same reason).
                cur_pending = read_4byte_short(PAN_DROP_TRAP_VAR_ADDR)
                write_4byte_short(PAN_DROP_TRAP_VAR_ADDR, cur_pending + 1)
                # logger.info(f"Pan Drop Trap: pending count {cur_pending} -> {cur_pending + 1} (addr {hex(PAN_DROP_TRAP_VAR_ADDR)}, stage {stage_hex_to_name()})")

            return True


        if is_special:
            dolphin_memory_engine.write_byte(item_id, 1)
            return True

        if ctx.slot == player:
            return True

        if item_slot == b'\xff\xff':

            dolphin_memory_engine.write_byte((GIVE_ITEM_ARRAY_ADDR + idx), 0x00)
            dolphin_memory_engine.write_byte((GIVE_ITEM_ARRAY_ADDR + idx) + 1, item_id)
            dolphin_memory_engine.write_byte((GIVE_ITEM_ARRAY_ADDR + idx) + 3, 1)
            return True

        elif item_slot == b'\x00\x00' and current_item == item_id: # Extra check to make sure frog rings are stacking correctly

            current_item_qty = dolphin_memory_engine.read_byte((GIVE_ITEM_ARRAY_ADDR + idx) + 3) +1
            dolphin_memory_engine.write_byte((GIVE_ITEM_ARRAY_ADDR + idx) + 3, current_item_qty)
            return True

        elif current_item == item_id and IC == 0:

            # logger.info(hex(item_id))
            # logger.info(hex(current_item))
            # logger.info("Same Item: " + item_name)

            current_item_qty = dolphin_memory_engine.read_byte((GIVE_ITEM_ARRAY_ADDR + idx) + 3) +1
            dolphin_memory_engine.write_byte((GIVE_ITEM_ARRAY_ADDR + idx) + 3, current_item_qty)
            return True

    # If unable to place the item in the array, return `False`.
    return False


def gba_link_available() -> bool:
    """
    `True` if this ISO has the GBA link patch. Without it GBA_MESSAGE is ordinary game heap, so
    nothing may be written there.
    """
    try:
        return dolphin_memory_engine.read_bytes(GBA_MESSAGE, 4) == GBA_MB_MAGIC
    except RuntimeError:
        return False


def gba_link_connected() -> bool:
    """`True` if the patch is present and a GBA is currently linked and running the program."""
    return gba_link_available() and read_4byte_short(GBA_MESSAGE + GBA_MB_LINK_STATE) == 2


def _gba_text(text: str, max_len: int) -> bytes:
    # The GBA font is plain ASCII: swap common typographic characters, drop anything else.
    replacements = {"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-",
                    "…": "...", "é": "e", "è": "e", "à": "a", "ö": "o", "ü": "u"}
    text = "".join(replacements.get(c, c) for c in text)
    data = text.encode("ascii", errors="ignore")
    data = bytes(b for b in data if b == 0x0A or 0x20 <= b < 0x7F)
    return data[:max_len].ljust(max_len + 1, b"\0")


def send_gba_message(title: str, text: str, icon: int = GBA_ICON_PLUG, duration: int = 0,
                     require_link: bool = True) -> bool:
    """
    Show any popup message on the player's GBA.

    :param title: Title line, up to 15 characters.
    :param text: Message body, up to 95 characters, word-wrapped by the GBA ("\\n" forces a break).
    :param icon: One of the GBA_ICON_* constants.
    :param duration: Frames (60 per second) until it closes by itself; 0 = until the player closes it.
    :param require_link: Only send while a GBA is linked (otherwise messages would pile up in the game).
    :return: `True` if the game accepted it. `False` means try again later: the ISO has no GBA
             patch, no GBA is linked, or the previous message hasn't been picked up yet.
    """
    if not gba_link_available():
        return False
    if require_link and read_4byte_short(GBA_MESSAGE + GBA_MB_LINK_STATE) != 2:
        return False

    post = read_4byte_short(GBA_MESSAGE + GBA_MB_POST)
    ack = read_4byte_short(GBA_MESSAGE + GBA_MB_ACK)
    if post != ack:
        return False  # the game hasn't copied the last message yet (or its queue is full)

    dolphin_memory_engine.write_bytes(GBA_MESSAGE + GBA_MB_ICON,
                                      bytes([icon & 0xFF, 0]) + (duration & 0xFFFF).to_bytes(2, "big"))
    dolphin_memory_engine.write_bytes(GBA_MESSAGE + GBA_MB_TITLE, _gba_text(title, GBA_TITLE_MAX))
    dolphin_memory_engine.write_bytes(GBA_MESSAGE + GBA_MB_TEXT, _gba_text(text, GBA_TEXT_MAX))
    # Bump `post` last: that's what tells the game a complete message is waiting.
    write_4byte_short(GBA_MESSAGE + GBA_MB_POST, (ack + 1) & 0xFFFFFFFF)
    return True


def _gba_item_icon(item_name: str) -> int:
    name = item_name.lower()
    if "moolah" in name or "coin" in name:
        return GBA_ICON_COIN
    if "happy" in name or "sticker" in name:
        return GBA_ICON_HEART
    if "battery" in name or "charge" in name:
        return GBA_ICON_BATTERY
    return GBA_ICON_PLUG


def _gba_item_text(item_name: str, from_player: Optional[str]) -> str:
    if from_player:
        return f"Received {item_name} from {from_player}!"
    return f"You found your {item_name}!"


def send_gba_item_message(item_name: str, from_player: Optional[str] = None) -> bool:
    """
    Show a "received item" popup on the player's GBA right away.

    :param item_name: Name of the item received.
    :param from_player: Name of the player who found it, or `None` if the player found it themselves.
    :return: Same as `send_gba_message` (`False` = not sent, try again later).
    """
    return send_gba_message("Archipelago", _gba_item_text(item_name, from_player), _gba_item_icon(item_name))


def queue_gba_message(ctx: "ChibiRoboContext", title: str, text: str, icon: int = GBA_ICON_PLUG,
                      duration: int = 0) -> None:
    """
    Queue any popup for the GBA. Queued messages go out one at a time from `flush_gba_messages`
    (called by the Dolphin sync loop), so a burst of items can't overwrite the mailbox. Nothing is
    queued if the ISO has no GBA patch or no GBA is linked.
    """
    if not gba_link_connected():
        return
    if len(ctx.gba_message_queue) < 32:
        ctx.gba_message_queue.append((title, text, icon, duration))


def queue_gba_item_message(ctx: "ChibiRoboContext", item_name: str, sending_player: int) -> None:
    """Queue a "received item" popup; `sending_player` is the slot number of whoever found it."""
    from_player = None
    if sending_player != ctx.slot:
        from_player = ctx.player_names.get(sending_player, f"Player {sending_player}")
    queue_gba_message(ctx, "Archipelago", _gba_item_text(item_name, from_player), _gba_item_icon(item_name))


def flush_gba_messages(ctx: "ChibiRoboContext") -> None:
    """Send the next queued GBA popup if the mailbox is free. Call once per sync-loop pass."""
    if not ctx.gba_message_queue:
        return
    if not gba_link_connected():
        ctx.gba_message_queue.clear()  # GBA unplugged: drop them rather than show stale popups later
        return
    title, text, icon, duration = ctx.gba_message_queue[0]
    if send_gba_message(title, text, icon, duration):
        ctx.gba_message_queue.pop(0)

def check_ingame() -> bool:
    """
    Check if the player is currently in-game.

    :return: `True` if the player is in-game, otherwise `False`.
    """

    # logger.info(dolphin_memory_engine.read_bytes(CURR_GAME_STATE, 1))

    # there is a timing gap between the is_hooked and this read_bytes that can cause a client crash
    # try catch to retry if client has that crash happen instead of just crashing
    try:
        return dolphin_memory_engine.read_bytes(CURR_GAME_STATE, 1) not in [b"", b'\x00', b'\x40', b'\x07']
    except RuntimeError:
        return False


def change_max_items() -> None:
    dolphin_memory_engine.write_byte(0x800D1273, 99)
    dolphin_memory_engine.write_byte(0x800D1773, 99)
    dolphin_memory_engine.write_byte(0x800DCD07, 99)
    dolphin_memory_engine.write_byte(0x800DCD0F, 99)
    dolphin_memory_engine.write_byte(0x800DCD13, 246)

async def give_items(ctx: ChibiRoboContext) -> None:
    """
    Give the player all outstanding items they have yet to receive.

    :param ctx: client context.

    """

    if check_ingame() and dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 1) != b"\x0e":
        expected_idx = read_short(EXPECTED_INDEX_ADDR)

        # Check if there are new items.
        received_items = ctx.items_received
        # logger.info(f"give_items: expected_idx={expected_idx}, total received={len(received_items)}")
        if len(received_items) <= expected_idx:
            # There are no new items.
            return

        # Loop through items to give.
        for idx, item in enumerate(received_items[expected_idx:], start=expected_idx):

            received_player = received_items[idx][2]

            item_name = LOOKUP_ID_TO_NAME.get(item.item)
            if item_name is None:
                # Unmapped item id - a raw LOOKUP_ID_TO_NAME[item.item] here would raise KeyError,
                # which propagates uncaught out of this function and gets treated as a Dolphin
                # connection failure by dolphin_sync_task (disconnect + reconnect loop), silently
                # stalling every item queued after this one forever. Log and stop this pass instead
                # so expected_idx doesn't advance past a name we don't understand.
                # logger.info(f"give_items: item id {item.item} at idx {idx} has no ITEM_TABLE/LOOKUP_ID_TO_NAME entry - not giving it, stopping this pass")
                return

            # logger.info(f"give_items: giving '{item_name}' (item id {item.item}, idx {idx})")

            # Attempt to give the item and increment the expected index.
            while not _give_item(ctx, item_name, received_player):
                await asyncio.sleep(0.01)

            # Increment the expected index.
            write_short(EXPECTED_INDEX_ADDR, idx + 1)

            # Popup on the GBA, if the GBA link patch is in this ISO and a GBA is linked.
            queue_gba_item_message(ctx, item_name, received_player)

async def check_locations(ctx: ChibiRoboContext) -> None:
    """
    Iterate through all locations and check whether the player has checked each location.

    Update the server with all newly checked locations since the last update. If the player has completed the goal,
    notify the server.

    :param ctx: The client context.
    """
    # We check which locations are currently checked on the current stage.
    curr_stage_id = stage_hex_to_id()
    ctx.curr_stage_pickup = read_4byte_short(EXPECTED_INDEX_ADDR)
    if not ctx.finished_game:
        goal_reached = False

        if ctx.victory == 1:  # Activate Giga-Robo
            goal_reached = read_4byte_short(0x803684ae) == 65536
        elif ctx.victory == 2:  # Collect all required stickers
            required = ctx.required_stickers
            goal_reached = bool(required) and all(
                is_sticker_complete(name) for name in required
            )
        elif ctx.victory == 3:  # DIVORCE
            goal_reached = read_4byte_short(0x803684ca) == 65536
            
        else:  # Credits (victory == 0)
            goal_reached = curr_stage_id == 9

        if goal_reached:
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True
            logger.info("Congratulations, you have completed the game!")
            send_gba_message("Archipelago", "I hope you had fun playing!", GBA_ICON_HEART)

    for location, data in LOCATION_TABLE.items():

        checked = check_location(ctx, curr_stage_id, location, data)

        if checked:
            ctx.locations_checked.add(ChibiRoboLocation.get_apid(data.code))

    locations_checked = ctx.locations_checked.difference(ctx.checked_locations)
    if locations_checked:
        await ctx.send_msgs([{"cmd": "LocationChecks", "locations": locations_checked}])

def is_sticker_complete(name: str) -> bool:
    """Return True if the named sticker's completion bit is set in memory."""
    flag = STICKER_FLAGS.get(name)
    if flag is None:
        # Unknown name (e.g. an option/table name mismatch) can never be satisfied,
        # so a typo fails safe instead of granting an early victory.
        return False
    address, mask = flag
    return (read_short(address) & mask) == mask

def give_sticker(name: str) -> bool:

    flag = STICKER_FLAGS.get(name)
    if flag is None:
        logger.info(f"Unknown sticker {name}")
        return False

    address, mask = flag

    modify_memory_bitmask(address, mask, operation="SET")

    return True

def remove_sticker(name: str) -> bool:

    flag = STICKER_FLAGS.get(name)
    if flag is None:
        logger.info(f"Unknown sticker {name}")
        return False

    address, mask = flag

    modify_memory_bitmask(address, mask, operation="CLEAR")

    return True


def modify_memory_bitmask(address, mask, operation="SET"):
    """
    Modifies specific bits at a memory address using a bitmask.

    Operations:
      "SET"   : Turn target bits ON (Bitwise OR)
      "CLEAR" : Turn target bits OFF (Bitwise AND with inverted mask)
      "FLIP"  : Toggle target bits (Bitwise XOR)
    """

    # 1. Read the current 4-byte unsigned integer value from RAM
    current_value = read_short(address)

    # 2. Apply the bitmask logic based on your objective
    if operation.upper() == "SET":
        new_value = current_value | mask
    elif operation.upper() == "CLEAR":
        new_value = current_value & ~mask
    elif operation.upper() == "FLIP":
        new_value = current_value ^ mask
    else:
        raise ValueError("Invalid operation. Use 'SET', 'CLEAR', or 'FLIP'.")

    # 3. Write the modified value back to Dolphin memory
    write_short(address, new_value)
    print(f"Address {hex(address)} updated: {bin(current_value)} -> {bin(new_value)}")


def check_location(ctx: ChibiRoboContext, curr_stage_id: int, name: str, data: ChibiRoboLocationData) -> bool:
    """
    Check that the player has checked a given location.
    This function handles locations that only require checking that a particular bit is set.

    The check looks at the saved data for the stage at which the location is located and the data for the current stage.
    In the latter case, this data includes data that has not yet been written to the saved data.

    :param ctx: The client context.
    :param curr_stage_id: The current stage at which the player is.
    :param data: The data associated with the location.
    :raises NotImplementedError: If a location with an unknown type is provided.
    """
    checked = False

    # If the location is in the current stage, check the bitfields for the current stage as well.
    if not checked and curr_stage_id == data.stage_id:

        if data.address:

            location_addr = hex(data.address)

            location_value = dolphin_memory_engine.read_bytes(int( location_addr, 16), 4)

            checked = bool( (int.from_bytes(location_value, byteorder='little') >> data.bit) & 1)

    return checked

def stage_hex_to_name() -> str:
    stage_value = dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 1)

    if stage_value == b"\x0e":
        return "Menu"
    elif stage_value == b"\x01":
        return "Kitchen"
    elif stage_value == b"\x02":
        return "Foyer"
    elif stage_value == b"\x03":
        return "Basement"
    elif stage_value == b"\x04":
        return "Jenny's Room"
    elif stage_value == b"\x05":
        return "Chibi House"
    elif stage_value == b"\x06":
        return "Bedroom"
    elif stage_value == b"\x07":
        return "Living Room"
    elif stage_value == b"\x08" or stage_value == b"\t":
        return "Backyard"
    elif stage_value == b"\x0a":
        return "Staff Credits"
    elif stage_value == b"\x0b":
        return "Sink Drain"
    elif stage_value == b"\x0e":
        return "Living Room (Birthday)"
    elif stage_value == b"\x10":
        return "UFO"
    elif stage_value == b"\x12":
        return "Bedroom (Past)"
    elif stage_value == b"\x16":
        return "Mother Spider Boss"
    elif stage_value == b"\x0a":
        return "Ending Credits"

    return "Could Not Find Room / Stage Name"

def stage_hex_to_id() -> int:

    stage_value = dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 1)

    if  stage_value == b"\x0e":
        return 0 # 'Menu'
    elif stage_value == b"\x01":
        return 1 # "Kitchen"
    elif stage_value == b"\x02":
        return 2 #"Foyer"
    elif stage_value == b"\x03":
        return 3 #"Basement"
    elif stage_value == b"\x04":
        return 4 #"Jenny's Room"
    elif stage_value == b"\x05":
        return 5 #"Chibi House"
    elif stage_value == b"\x06":
        return 6 #"Bedroom"
    elif stage_value == b"\x07":
        return 7 #"Living Room"
    elif stage_value == b"\x08" or stage_value == b"\t":
        return 8 #"Backyard"
    elif stage_value == b"\x0a":
        return 9 #"Staff Credits"
    elif stage_value == b"\x0b":
        return 10 #"Sink Drain"
    elif stage_value == b"\x0e":
        return 11 #"Living Room (Birthday)"
    elif stage_value == b"\x10":
        return 12 #"UFO"
    elif stage_value == b"\x12":
        return 13 #"Bedroom (Past)"
    elif stage_value == b"\x16":
        return 14 #"Mother Spider Boss"
    elif stage_value == b"\x0a":
        return 15 #"Ending Credits"

    return -1 #"Could Not Find Room / Stage Name"

async def check_current_stage_changed(ctx: ChibiRoboContext) -> None:
    """
    Check if the player has moved to a new stage.
    If so, update all trackers with the new stage name.
    If the stage has never been visited, additionally update the server.

    :param ctx: client context.
    """

    new_stage_name = stage_hex_to_name()

    current_stage_name = ctx.current_stage_name

    if new_stage_name != current_stage_name:
        # logger.info(current_stage_name + ' -> ' + new_stage_name)
        ctx.current_stage_name = new_stage_name
        # Send a Bounced message containing the new stage name to all trackers connected to the current slot.
        data_to_send = {"chibi_robo_stage_name": new_stage_name}
        message = {
            "cmd": "Bounce",
            "slots": [ctx.slot],
            "data": data_to_send,
        }
        await ctx.send_msgs([message])

        # Write stage ID to DataStorage so UT can auto-tab to the correct map.
        if ctx.slot is not None:
            team = ctx.team if hasattr(ctx, "team") and ctx.team is not None else 1
            await ctx.send_msgs([{
                "cmd": "Set",
                "key": f"chibi_robo_stage_{ctx.slot}_{team}",
                "default": -1,
                "want_reply": False,
                "operations": [{"operation": "replace", "value": stage_hex_to_id()}],
            }])

async def check_alive() -> bool:
    """
    Check if the player is currently alive in-game.

    :return: `True` if the player is alive, otherwise `False`.
    """
    cur_health = read_short(CURR_BATTERY_ADDR)

    # logger.info(cur_health)

    return cur_health > 0


async def dolphin_sync_task(ctx: ChibiRoboContext) -> None:
    """
    The task loop for managing the connection to Dolphin.

    While connected, read the emulator's memory to look for any relevant changes made by the player in the game.

    :param ctx: The client context.
    """
    logger.info("Starting Dolphin connector. Use /dolphin for status information.")
    sleep_time = 0.0
    while not ctx.exit_event.is_set():
        if sleep_time > 0.0:
            try:
                # ctx.watcher_event gets set when receiving ReceivedItems or LocationInfo, or when shutting down.
                await asyncio.wait_for(ctx.watcher_event.wait(), sleep_time)
            except asyncio.TimeoutError:
                pass
            sleep_time = 0.0
        ctx.watcher_event.clear()

        try:
            if dolphin_memory_engine.is_hooked() and ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                if not check_ingame():
                    # Do NOT reset GIVE_ITEM_ARRAY_ADDR here. check_ingame() also returns false
                    # during a completely normal level/room transition (a brief loading state),
                    # not just at boot/menu - 0xFF is the "empty slot" marker read elsewhere
                    # (`if item_slot == b'\xff\xff':`), so filling the whole array with it wiped
                    # every currently-held item on every single level change. Just skip processing
                    # this iteration; give_items() safely resumes from expected_idx once back
                    # in-game, with nothing needing to be pre-emptively cleared.
                    sleep_time = 0.1
                    continue
                if ctx.slot is not None:
                    if "DeathLink" + "group_death_link" in ctx.tags:
                        await check_death(ctx)

                    # change_max_items()
                    await give_items(ctx)
                    sync_key_doors(ctx)
                    flush_gba_messages(ctx)
                    await check_locations(ctx)
                    await check_current_stage_changed(ctx)
                else:
                    if ctx.awaiting_rom:
                        await ctx.server_auth()
                sleep_time = 0.1
            else:
                if ctx.dolphin_status == CONNECTION_CONNECTED_STATUS:
                    logger.info("Connection to Dolphin lost, reconnecting...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                logger.info("Attempting to connect to Dolphin...")
                dolphin_memory_engine.hook()
                if dolphin_memory_engine.is_hooked():

                    if dolphin_memory_engine.read_bytes(0x80000000, 6) != b"GGTE01":
                        ctx.dolphin_status = CONNECTION_REFUSED_GAME_STATUS
                        dolphin_memory_engine.un_hook()
                        sleep_time = 5
                    else:
                        logger.info(CONNECTION_CONNECTED_STATUS)
                        ctx.dolphin_status = CONNECTION_CONNECTED_STATUS
                        ctx.locations_checked = set()

                else:
                    logger.info(ctx.dolphin_status)
                    logger.info("Connection to Dolphin failed, attempting again in 5 seconds...")
                    ctx.dolphin_status = CONNECTION_LOST_STATUS
                    # reset_item_flag()
                    await ctx.disconnect()
                    sleep_time = 5
                    continue
        except Exception:
            dolphin_memory_engine.un_hook()
            logger.info("Connection to Dolphin failed, attempting again in 5 seconds...")
            logger.error(traceback.format_exc())
            ctx.dolphin_status = CONNECTION_LOST_STATUS
            # reset_item_flag()
            await ctx.disconnect()
            sleep_time = 5
            continue

async def proxy(websocket, path: str = "/", ctx: ChibiRoboContext = None):
    ctx.endpoint = Endpoint(websocket)
    try:
        await on_client_connected(ctx)

        if ctx.is_proxy_connected():
            async for data in websocket:
                if DEBUG:
                    logger.info(f"Incoming message: {data}")

                for msg in decode(data):
                    if msg["cmd"] == "Connect":
                        # Proxy is connecting, make sure it is valid
                        if msg["game"] != "Chibi Robo":
                            logger.info("Aborting proxy connection: game is not Chibi Robo")
                            await ctx.disconnect_proxy()
                            break

                        if ctx.seed_name:
                            seed_name = msg.get("seed_name", "")
                            if seed_name != "" and seed_name != ctx.seed_name:
                                logger.info("Aborting proxy connection: seed mismatch from save file")
                                logger.info(f"Expected: {ctx.seed_name}, got: {seed_name}")
                                text = encode([{"cmd": "PrintJSON",
                                                "data": [{"text": "Connection aborted - save file to seed mismatch"}]}])
                                await ctx.send_msgs_proxy(text)
                                await ctx.disconnect_proxy()
                                break

                        if ctx.auth:
                            name = msg.get("name", "")
                            if name != "" and name != ctx.auth:
                                logger.info("Aborting proxy connection: player name mismatch from save file")
                                logger.info(f"Expected: {ctx.auth}, got: {name}")
                                text = encode([{"cmd": "PrintJSON",
                                                "data": [{"text": "Connection aborted - player name mismatch"}]}])
                                await ctx.send_msgs_proxy(text)
                                await ctx.disconnect_proxy()
                                break

                        if ctx.connected_msg and ctx.is_connected():
                            await ctx.send_msgs_proxy(ctx.connected_msg)
                            ctx.update_items()
                        continue

                    if not ctx.is_proxy_connected():
                        break

                    await ctx.send_msgs([msg])

    except Exception as e:
        if not isinstance(e, websockets.WebSocketException):
            logger.exception(e)
    finally:
        await ctx.disconnect_proxy()


async def on_client_connected(ctx: ChibiRoboContext):
    if ctx.room_info and ctx.is_connected():
        await ctx.send_msgs_proxy(ctx.room_info)
    else:
        ctx.awaiting_info = True


async def proxy_loop(ctx: ChibiRoboContext):
    try:
        while not ctx.exit_event.is_set():
            if len(ctx.server_msgs) > 0:
                for msg in ctx.server_msgs:
                    await ctx.send_msgs_proxy(msg)

                ctx.server_msgs.clear()
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.exception(e)
        logger.info("Aborting ChibiRobo Proxy Client due to errors")


def launch(*launch_args: str):
    async def main() -> None:
        parser = get_base_parser()
        args = parser.parse_args(launch_args)

        ctx = ChibiRoboContext(args.connect, args.password)
        logger.info("Starting Chibi Robo proxy server")
        ctx.proxy = websockets.serve(functools.partial(proxy, ctx=ctx),
                                     host="localhost", port=11311, ping_timeout=999999, ping_interval=999999)
        ctx.proxy_task = asyncio.create_task(proxy_loop(ctx), name="ProxyLoop")

        if tracker_loaded:
            ctx.run_generator()
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        ctx.dolphin_sync_task = asyncio.create_task(dolphin_sync_task(ctx), name="DolphinSync")
        ctx.watcher_event.set()
        ctx.server_address = None
        await ctx.shutdown()

        if ctx.dolphin_sync_task:
            await ctx.dolphin_sync_task

        await ctx.proxy
        await ctx.proxy_task
        await ctx.exit_event.wait()

    Utils.init_logging("ChibiRoboClient")
    # options = Utils.get_options()

    import colorama
    colorama.just_fix_windows_console()
    asyncio.run(main())
    colorama.deinit()
