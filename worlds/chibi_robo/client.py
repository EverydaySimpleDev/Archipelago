import asyncio
import traceback
import dolphin_memory_engine
import numpy as np

import NetUtils
import Utils
import websockets
import functools
from copy import deepcopy
from typing import List, Any, Iterable, Any, Optional
from NetUtils import decode, encode, JSONtoTextParser, JSONMessagePart, NetworkItem, NetworkPlayer, ClientStatus
from MultiServer import Endpoint
from CommonClient import CommonContext, gui_enabled, ClientCommandProcessor, logger, get_base_parser
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
EXPECTED_INDEX_ADDR = 0x80396576

CURRENT_INDEX_ADDR = 0

# This address contains the current stage / room ID.
CURR_STAGE_ID_ADDR = 0x8026644C

# This address is used to check/set the player's battery
CURR_BATTERY_ADDR = 0x8396558

GC_GAME_ID_ADDRESS = 0x80000000

MOOLAH_ADDR = 0x80396550

SCRAP_ADDR = 0X80396554

HAPPY_POINTS_ADDR = 0x8039653C

class ChibiRoboJSONToTextParser(JSONtoTextParser):
    def _handle_color(self, node: JSONMessagePart):
        return self._handle_text(node)  # No colors for the in-game text


class ChibiRoboCommandProcessor(ClientCommandProcessor):
    def __init__(self, ctx: CommonContext):
        """
        Initialize the command processor with the provided context.

        :param ctx: Context for the client.
        """
        super().__init__(ctx)

    def _cmd_debug(self) -> None:
        """
        Debug Messages
        """
        if isinstance(self.ctx, ChibiRoboContext):
            # logger.info(f"{self.ctx.item_names["Chibi Robo"]}")
            # logger.info(f"{self.ctx.location_names["Chibi Robo"]}")
            return

    def _cmd_dolphin(self) -> None:
        """
        Display the current Dolphin emulator connection status.
        """
        if isinstance(self.ctx, ChibiRoboContext):
            logger.info(f"Dolphin Status: {self.ctx.dolphin_status}")


class ChibiRoboContext(CommonContext):
    command_processor = ChibiRoboCommandProcessor
    game = "Chibi Robo"

    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        super().__init__(server_address, password)
        self.dolphin_sync_task: Optional[asyncio.Task[None]] = None
        self.dolphin_status: str = CONNECTION_INITIAL_STATUS
        self.awaiting_rom: bool = False
        self.has_send_death: bool = False
        self.send_index: int = 0

        self.proxy = None
        self.proxy_task = None
        self.gamejsontotext = ChibiRoboJSONToTextParser(self)
        self.autoreconnect_task = None
        self.endpoint = None
        self.items_handling = 0b111
        self.room_info = None
        self.connected_msg = None
        self.game_connected = False
        self.awaiting_info = False
        self.full_inventory: List[Any] = []
        self.server_msgs: List[Any] = []

        self.current_stage_name: str = ""
        self.curr_stage_pickup: int


    async def server_auth(self, password_requested: bool = True) -> None:
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        # if not self.auth:
        #     if self.awaiting_rom:
        #         return
        #     self.awaiting_rom = True
        #     logger.info("Awaiting connection to Dolphin to get player information.")
        #     return
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
        reset_item_flag()
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
        ctx = ChibiRoboContext
        if cmd == "Connected":

            json = args
            if "slot_info" in json.keys():
                json["slot_info"] = {}
            if "players" in json.keys():
                me: NetworkPlayer
                for n in json["players"]:
                    if n.slot == json["slot"] and n.team == json["team"]:
                        me = n
                        break

                # Only put our player info in there as we actually need it
                json["players"] = [me]
            if DEBUG:
                print(json)
            self.connected_msg = encode([json])
            if self.awaiting_info:
                self.server_msgs.append(self.room_info)
                self.update_items()
                self.awaiting_info = False

        elif cmd == "RoomUpdate":
            # Same story as above
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

    def run_gui(self):
        from kvui import GameManager

        class ChibiRoboManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago Chibi Robo Client"

        self.ui = ChibiRoboManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

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

def _give_item(ctx: ChibiRoboContext, item_name: str) -> bool:
    """
    Give an item to the player in-game.

    :param ctx: The client context.
    :param item_name: Name of the item to give.
    :return: Whether the item was successfully given.
    """
    global CURR_STAGE_ID_ADDR
    global EXPECTED_INDEX_ADDR

    if not check_ingame() or dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x0e":
        return False

    item_id = ITEM_TABLE[item_name].item_id

    if dolphin_memory_engine.read_bytes(EXPECTED_INDEX_ADDR, 4) == b"\x00\x00\x00\x00" or dolphin_memory_engine.read_bytes(EXPECTED_INDEX_ADDR, 4) == b"\x00\x00\xff\xff" or dolphin_memory_engine.read_bytes(EXPECTED_INDEX_ADDR, 4) == b"\x00\x01\xff\xff":

        item_id = int(hex(item_id + 65536), 16)

        # If item is a coin increase coin count
        if "Coin" in item_name:
            moolah = dolphin_memory_engine.read_bytes(MOOLAH_ADDR, 4)

            money_value = hex( int.from_bytes(moolah, byteorder="big"))

            if "Coin C" in item_name:
                money_value = hex( int.from_bytes(moolah, byteorder="big") + 10)

            if "Coin S" in item_name:
                money_value = hex( int.from_bytes(moolah, byteorder="big") + 50)

            if "Coin G" in item_name:
                money_value = hex( int.from_bytes(moolah, byteorder="big") + 100)

            dolphin_memory_engine.write_bytes(MOOLAH_ADDR, int(money_value, 16).to_bytes(4, byteorder="big"))
            return True

        # If item is scrape increase scrape count
        if "Junk" in item_name:

            # logger.info(item_name)

            junk = dolphin_memory_engine.read_bytes(SCRAP_ADDR, 4)

            junk_value = hex(int.from_bytes(junk, byteorder="big"))

            if "Junk A" in item_name:
                junk_value = hex(int.from_bytes(junk, byteorder="big") + 10)

            if "Junk B" in item_name:
                junk_value = hex(int.from_bytes(junk, byteorder="big") + 50)

            if "Junk C" in item_name:
                junk_value = hex(int.from_bytes(junk, byteorder="big") + 100)
            dolphin_memory_engine.write_bytes(SCRAP_ADDR, int(junk_value, 16).to_bytes(4, byteorder="big"))
            return True

        # Check if we already have the item in memory (item id plus required offset)
        if dolphin_memory_engine.read_bytes(EXPECTED_INDEX_ADDR, 4) != hex(item_id + 65536):

            # logger.info(item_name)

            dolphin_memory_engine.write_bytes(EXPECTED_INDEX_ADDR, item_id.to_bytes(4, byteorder="big"))

            update_item_flag()
            # Update the next address correctly to what the game expects 0001ffff
            item_id = 131071
            dolphin_memory_engine.write_bytes(EXPECTED_INDEX_ADDR, item_id.to_bytes(4, byteorder="big"))
        else :
            update_item_flag()

        # logger.info(f"Item {item_name} was successfully added.")
        return True
    else:
        update_item_flag()

    # If unable to place the item in the array, return `False`.
    return False


def check_ingame() -> bool:
    """
    Check if the player is currently in-game.

    :return: `True` if the player is in-game, otherwise `False`.
    """

    return dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) not in ["" , '\x00\x00\x00\x0e', '\x00\x00\x00\x01', '\x00\x00\x00\x02', '\x00\x00\x00\x03', '\x00\x00\x00\x04', '\x00\x00\x00\x05', '\x00\x00\x00\x06','\x00\x00\x00\x07','\x00\x00\x00\x09','\x00\x00\x00\x0a','\x00\x00\x00\x0b','\x00\x00\x00\x10','\x00\x00\x00\x12','\x00\x00\x00\x16']

async def give_items(ctx: ChibiRoboContext) -> None:
    """
    Give the player all outstanding items they have yet to receive.

    :param ctx: client context.

    """

    if check_ingame() and dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) != b"\x00\x00\x00\x0e":
        # Read the expected index of the player, which is the index of the next item they're expecting to receive.

        # Check if there are new items.
        received_items = ctx.items_received
        unique_received_items = set(received_items)

        for item in unique_received_items:
            _give_item(ctx, LOOKUP_ID_TO_NAME[item.item])
            # logger.info(item)
            ctx.items_received.remove(item)

            return



def update_item_flag() -> None:

    global EXPECTED_INDEX_ADDR
    global CURRENT_INDEX_ADDR

    if dolphin_memory_engine.read_bytes(EXPECTED_INDEX_ADDR, 4) == b"\x00\x00\x00\x00" or dolphin_memory_engine.read_bytes(EXPECTED_INDEX_ADDR, 4) == b"\x00\x00\xff\xff":
        return
    else:

        EXPECTED_INDEX_ADDR += 4  # increment by 4 to get next flag / memory to set

        return
def reset_item_flag() -> None:

    global EXPECTED_INDEX_ADDR
    global CURRENT_INDEX_ADDR

    EXPECTED_INDEX_ADDR = 0x80396576  # increment by 4 to get next flag / memory to set

    return

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

    if ctx.curr_stage_pickup != 65535:

        # Loop through all locations to see if each has been checked.
        for location, data in LOCATION_TABLE.items():
            checked = False

            # logger.info(f'{location} Checked:  {checked}')
            checked = check_location(ctx, curr_stage_id, location, data)
            # logger.info(f'{location} Checked:  {checked}')
            # logger.info(ChibiRoboLocation.get_apid(data.code))

            if checked:
                if data.code is None:
                    if not ctx.finished_game:
                        await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                        ctx.finished_game = True
                else:
                    ctx.locations_checked.add(ChibiRoboLocation.get_apid(data.code))

        # Send the list of newly-checked locations to the server.
        locations_checked = ctx.locations_checked.difference(ctx.checked_locations)
        if locations_checked:
            logger.info(f'{len(locations_checked)} checked locations found.')
            await ctx.send_msgs([{"cmd": "LocationChecks", "locations": locations_checked}])

        # update_item_flag()

def check_location(ctx: ChibiRoboContext, curr_stage_id: int, name: str ,data: ChibiRoboLocationData) -> bool:
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
        # logger.info(name)
        checked = bool((ctx.curr_stage_pickup >> data.bit) & 1)

    return checked

def stage_hex_to_name() -> str:
    global CURR_STAGE_ID_ADDR

    if dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x0e":
        return "Menu"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x01":
        return "Kitchen"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x02":
        return "Foyer"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x03":
        return "Basement"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x04":
        return "Jenny's Room"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x05":
        return "Chibi House"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x06":
        return "Bedroom"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x07":
        return "Living Room"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x09":
        return "Backyard"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x0a":
        return "Staff Credits"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x0b":
        return "Drain"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x0e":
        return "Living Room (Birthday)"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x10":
        return "UFO"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x12":
        return "Bedroom (Past)"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x16":
        return "Mother Spider Boss"

    return "Could Not Find Room / Stage Name"

def stage_hex_to_id() -> int:
    global CURR_STAGE_ID_ADDR

    if dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x0e":
        return 0 # 'Menu'
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x01":
        return 1 # "Kitchen"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x02":
        return 2 #"Foyer"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x03":
        return 3 #"Basement"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x04":
        return 4 #"Jenny's Room"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x05":
        return 5 #"Chibi House"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x06":
        return 6 #"Bedroom"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x07":
        return 7 #"Living Room"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x09":
        return 8 #"Backyard"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x0a":
        return 9 #"Staff Credits"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x0b":
        return 10 #"Drain"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x0e":
        return 11 #"Living Room (Birthday)"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x10":
        return 12 #"UFO"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x12":
        return 13 #"Bedroom (Past)"
    elif dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x16":
        return 14 #"Mother Spider Boss"

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

async def check_alive() -> bool:
    """
    Check if the player is currently alive in-game.

    :return: `True` if the player is alive, otherwise `False`.
    """
    cur_health = read_short(CURR_BATTERY_ADDR)
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
                    # Reset the give item array while not in the game.
                    reset_item_flag()
                    sleep_time = 0.1
                    continue
                if ctx.slot is not None:
                    await give_items(ctx)
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

                    if dolphin_memory_engine.read_bytes(0x80000000, 6) != b"GGTP01":
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
                    reset_item_flag()
                    await ctx.disconnect()
                    sleep_time = 5
                    continue
        except Exception:
            dolphin_memory_engine.un_hook()
            logger.info("Connection to Dolphin failed, attempting again in 5 seconds...")
            logger.error(traceback.format_exc())
            ctx.dolphin_status = CONNECTION_LOST_STATUS
            reset_item_flag()
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
