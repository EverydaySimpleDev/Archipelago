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
# Saves over total times player has recharged that is no longer increased via patcher
EXPECTED_INDEX_ADDR = 0x803686a6

GIVE_ITEM_ARRAY_ADDR = 0x8038f778

CURRENT_INDEX_ADDR = 0

# This address contains the current stage / room ID.
CURR_STAGE_ID_ADDR = 0x8025f847

CURR_GAME_STATE = 0x8025df17

# This address is used to check/set the player's battery
CURR_BATTERY_ADDR = 0x8038f748

GC_GAME_ID_ADDRESS = 0x80000000

MOOLAH_ADDR = 0x8038f752

SCRAP_ADDR = 0X8038f756

HAPPY_POINTS_ADDR = 0x8038f73e

BASE_ITEM_ADDR = 0x80370000

class ChibiRoboJSONToTextParser(JSONtoTextParser):
    def _handle_color(self, node: JSONMessagePart):
        return self._handle_text(node)  # No colors for the in-game text


class FFCCCommandProcessor(ClientCommandProcessor):
    def __init__(self, ctx: CommonContext):
        """
        Initialize the command processor with the provided context.

        :param ctx: Context for the client.
        """
        super().__init__(ctx)

    def _cmd_dolphin(self) -> None:
        """
        Display the current Dolphin emulator connection status.
        """
        if isinstance(self.ctx, FFCCContext):
            logger.info(f"Dolphin Status: {self.ctx.dolphin_status}")
            return


class FFCCContext(CommonContext):
    command_processor = FFCCCommandProcessor
    game = "Final Fantasy Crystal Chronicles"
    items_handling: int = 0b111
    len_give_item_array: int = 0x272
    items_received = []
    victory: int

    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        super().__init__(server_address, password)
        self.dolphin_sync_task: Optional[asyncio.Task[None]] = None
        self.dolphin_status: str = CONNECTION_INITIAL_STATUS
        self.awaiting_rom: bool = False
        self.has_send_death: bool = False

        self.proxy = None
        self.proxy_task = None
        self.gamejsontotext = FFCCJSONToTextParser(self)
        self.autoreconnect_task = None
        self.endpoint = None
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
        ctx = FFCCContext
        if cmd == "Connected":

            json = args
            if "slot_info" in json.keys():
                json["slot_info"] = {}
                ctx.victory = args["slot_data"]["victory_goal"]
            if "death_link" in args["slot_data"]:
                Utils.async_start(self.update_death_link(bool(args["slot_data"]["death_link"])))
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

def _give_death(ctx: FFCCContext) -> None:
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

async def check_death(ctx: FFCCContext) -> None:
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
                await ctx.send_death(ctx.player_names[ctx.slot] + " ran out of hearts.")
        else:
            ctx.has_send_death = False

def _give_item(ctx: FFCCContext, item_name: str, player: int) -> bool:
    """
    Give an item to the player in-game.

    :param ctx: The client context.
    :param item_name: Name of the item to give.
    :return: Whether the item was successfully given.
    """

    if not check_ingame() or dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) == b"\x00\x00\x00\x0e":
        return False

    item_id = ITEM_TABLE[item_name].item_id
    is_special = ITEM_TABLE[item_name].special
    IC = ITEM_TABLE[item_name].classification

    # Loop through the item array, placing the item in an empty slot.
    for idx in range(ctx.len_give_item_array):

        item_slot = dolphin_memory_engine.read_bytes(GIVE_ITEM_ARRAY_ADDR + idx, 2)
        current_item = dolphin_memory_engine.read_byte((GIVE_ITEM_ARRAY_ADDR + idx) + 1)

        if item_name == "Giga Battery Charge":
            # Make sure the giga battery doesn't go over 9000 otherwise player can't pick up the maxed battery
            cur_charge = read_4byte_short(0x80367c4c)
            if cur_charge < 9000:
                write_4byte_short(0x80367c4c, cur_charge + 1000)
                return True
            else:
                return True

        elif item_name == "Max Battery Increase":

            cur_max = read_4byte_short(0x8038f74a)
            write_4byte_short(0x8038f74a, cur_max + 20)

            return True

        if ctx.slot == player:
            if is_special:
                dolphin_memory_engine.write_byte(item_id, 1)
                return True
            else:
                return True

        if item_slot == b'\xff\xff':

            dolphin_memory_engine.write_byte((GIVE_ITEM_ARRAY_ADDR + idx), 0x00)
            dolphin_memory_engine.write_byte((GIVE_ITEM_ARRAY_ADDR + idx) + 1, item_id)
            dolphin_memory_engine.write_byte((GIVE_ITEM_ARRAY_ADDR + idx) + 3, 1)
            return True

        elif current_item == item_id and IC == 0:

            # logger.info(hex(item_id))
            # logger.info(hex(current_item))
            # logger.info("Same Item: " + item_name)

            current_item_qty = dolphin_memory_engine.read_byte((GIVE_ITEM_ARRAY_ADDR + idx) + 3) +1
            dolphin_memory_engine.write_byte((GIVE_ITEM_ARRAY_ADDR + idx) + 3, current_item_qty)
            return True

        elif is_special:
                dolphin_memory_engine.write_byte(item_id, 1)
                return True

    # If unable to place the item in the array, return `False`.
    return False

def check_ingame() -> bool:
    """
    Check if the player is currently in-game.

    :return: `True` if the player is in-game, otherwise `False`.
    """

    # logger.info(dolphin_memory_engine.read_bytes(CURR_GAME_STATE, 1))

    return dolphin_memory_engine.read_bytes(CURR_GAME_STATE, 1) not in ["" , '\x00', '\x40', '\x07']

async def give_items(ctx: FFCCContext) -> None:
    """
    Give the player all outstanding items they have yet to receive.

    :param ctx: client context.

    """

    if check_ingame() and dolphin_memory_engine.read_bytes(CURR_STAGE_ID_ADDR, 4) != b"\x00\x00\x00\x0e":
        expected_idx = read_short(EXPECTED_INDEX_ADDR)

        # Check if there are new items.
        received_items = ctx.items_received
        if len(received_items) <= expected_idx:
            # There are no new items.
            return
        # Loop through items to give.
        for idx, item in enumerate(received_items[expected_idx:], start=expected_idx):

            received_player = received_items[idx][2]

            # Attempt to give the item and increment the expected index.
            while not _give_item(ctx, LOOKUP_ID_TO_NAME[item.item], received_player):
                await asyncio.sleep(0.01)

            # Increment the expected index.
            write_short(EXPECTED_INDEX_ADDR, idx + 1)

async def check_locations(ctx: FFCCContext) -> None:
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

        if ctx.victory == 1: # Activating Giga Robo = completing game
            activated_giga = read_4byte_short(0x803684ae)

            if activated_giga == 65536:
                await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                ctx.finished_game = True
                logger.info("Congratulations, you have completed the game!")
        else:
            if curr_stage_id == 9:  # end credits = completing game
                await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                ctx.finished_game = True
                logger.info("Congratulations, you have completed the game!")




    for location, data in LOCATION_TABLE.items():

        checked = check_location(ctx, curr_stage_id, location, data)

        if checked:
            ctx.locations_checked.add(ChibiRoboLocation.get_apid(data.code))

    locations_checked = ctx.locations_checked.difference(ctx.checked_locations)
    if locations_checked:
        await ctx.send_msgs([{"cmd": "LocationChecks", "locations": locations_checked}])


def check_location(ctx: FFCCContext, curr_stage_id: int, name: str, data: ChibiRoboLocationData) -> bool:
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

            location_addr = hex(BASE_ITEM_ADDR + data.address)

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

async def check_current_stage_changed(ctx: FFCCContext) -> None:
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

    # logger.info(cur_health)

    return cur_health > 0


async def dolphin_sync_task(ctx: FFCCContext) -> None:
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
                    dolphin_memory_engine.write_bytes(EXPECTED_INDEX_ADDR, bytes([0xFF] * ctx.len_give_item_array))
                    dolphin_memory_engine.write_bytes(GIVE_ITEM_ARRAY_ADDR, bytes([0xFF] * ctx.len_give_item_array))
                    sleep_time = 0.1
                    continue
                if ctx.slot is not None:
                    if "DeathLink" in ctx.tags:
                        await check_death(ctx)

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

async def proxy(websocket, path: str = "/", ctx: FFCCContext = None):
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


async def on_client_connected(ctx: FFCCContext):
    if ctx.room_info and ctx.is_connected():
        await ctx.send_msgs_proxy(ctx.room_info)
    else:
        ctx.awaiting_info = True


async def proxy_loop(ctx: FFCCContext):
    try:
        while not ctx.exit_event.is_set():
            if len(ctx.server_msgs) > 0:
                for msg in ctx.server_msgs:
                    await ctx.send_msgs_proxy(msg)

                ctx.server_msgs.clear()
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.exception(e)
        logger.info("Aborting FFCC Proxy Client due to errors")


def launch(*launch_args: str):
    async def main() -> None:
        parser = get_base_parser()
        args = parser.parse_args(launch_args)

        ctx = FFCCContext(args.connect, args.password)
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
