# Python standard libraries
import base64
import io
import logging
import os
import zipfile
from base64 import b64encode
from typing import List, Dict, Optional, Union

from typing import Any, ClassVar
from logging import Logger
import dolphin_memory_engine
import yaml
import json

import Utils
import settings 
# Archipelago imports
from worlds.AutoWorld import World, WebWorld
from worlds.LauncherComponents import components, Component, launch_subprocess, Type, icon_paths
from BaseClasses import Item, ItemClassification, Tutorial, CollectionState, MultiWorld
from .regions import create_regions, connect_entrances
from .game_id import game_name
from .items import ChibiRoboItem, ITEM_TABLE, item_name_groups, ChibiRoboItemData, ITEM_TABLE_DESC, FILLER_ITEM_TABLE
from .locations import ChibiRoboLocation, LOCATION_TABLE, location_groups, ChibiRoboLocationData
from .options import ChibiRoboGameOptions, chibi_robo_option_groups, STICKER_NAMES
from BaseClasses import ItemClassification as IC
from worlds.Files import APPlayerContainer
from .rules import set_rules, set_location_rules

VERSION: tuple[int, int, int] = (1, 2, 3)

def launch_client():
    from . import client
    launch_subprocess(client.launch, name="ChibiRoboClient")


components.append(Component("Chibi Robo Client",
                            func=launch_client,
                            component_type=Type.CLIENT,
                            icon="chibi_body_icon"))

icon_paths["chibi_body_icon"] = f"ap:{__name__}/icons/chibi_body_icon.png"

class UTPackPath(settings.FilePath):

    required = False                        # set True to require the pack on launch
    ut_dialog_name = "Select Chibi Robo PopTracker pack (.zip)"

class ChibiRoboSettings(settings.Group):
    ut_pack_path: Union[UTPackPath, str] = UTPackPath()

class ChibiRoboWebWorld(WebWorld):
    theme = "dirt"

    item_descriptions = ITEM_TABLE_DESC

    bug_report_page = "https://github.com/EverydaySimpleDev/Archipelago",

    setup_en = Tutorial(
        tutorial_name="Start Guide",
        description="A guide to playing Chibi Robo! Plug Into Adventure! in Archipelago.",
        language="English",
        file_name="guide_en.md",
        link="guide/en",
        authors=["EverydaySimpleDev"]
    )

    tutorials = [setup_en]

    option_groups = chibi_robo_option_groups

class ChibiRoboContainer(APPlayerContainer):
    """
    This class defines the container file
    """

    game: str = game_name
    patch_file_ending: str = ".zip"

    def __init__(self, patch_data: Dict[str, str] | io.BytesIO, base_path: str = "", output_directory: str = "",
                 player: Optional[int] = None, player_name: str = "", server: str = ""):
        self.patch_data = patch_data
        self.file_path = base_path
        container_path = os.path.join(output_directory, base_path + ".zip")
        super().__init__(container_path, player, player_name, server)

    def write_contents(self, opened_zipfile: zipfile.ZipFile) -> None:
        for filename, yml in self.patch_data.items():
            opened_zipfile.writestr(filename, yml)
        super().write_contents(opened_zipfile)


def _chibi_robo_map_index(stage_id) -> int:
    """Convert a stage_hex_to_id() integer to an index in the EmoTracker maps.json.
    maps.json order: 0=backyard, 1=basement, 2=livingroom, 3=foyer, 4=foyer2f,
                     5=jennysroom, 6=kitchen, 7=drain, 8=bedroom
    """
    return {
        1:  6,  # Kitchen
        2:  3,  # Foyer (first floor)
        3:  1,  # Basement
        4:  5,  # Jenny's Room
        6:  8,  # Bedroom
        7:  2,  # Living Room
        8:  0,  # Backyard
        10: 7,  # Sink Drain
    }.get(int(stage_id) if stage_id not in (None, "") else -1, 2)

class ChibiRoboWorld(World):
    dolphin: dolphin_memory_engine
    logger: Logger

    game = game_name
    web = ChibiRoboWebWorld()
    options_dataclass = ChibiRoboGameOptions
    options: ChibiRoboGameOptions
    topology_present = True

    plando_locations: Dict[str, str]

    item_name_to_id: ClassVar[dict[str, int]] = {
        name: ChibiRoboItem.get_apid(data.code) for name, data in ITEM_TABLE.items() if data.code is not None
    }

    location_name_to_id: ClassVar[dict[str, int]] = {
        name: ChibiRoboLocation.get_apid(data.code) for name, data in LOCATION_TABLE.items() if data.code is not None
    }

    item_name_groups: ClassVar[dict[str, set[str]]] = item_name_groups
    location_name_groups: ClassVar[dict[str, set[str]]] = location_groups

    settings_key = "chibi_robo_options"

    settings: ClassVar[ChibiRoboSettings]

    tracker_world: ClassVar = {
        "external_pack_key":       "ut_pack_path",            # key in ChibiRoboSettings
        "map_page_maps":           "maps/maps.json",
        "map_page_locations":      "locations/locations.json",
        # Every section in the EmoTracker pack is named "Item" rather than the AP
        # location name, so we map "Location Name/Item" → AP location ID for all 220 checks.
        "poptracker_name_mapping": {
            f"{name}/Item": ChibiRoboLocation.get_apid(data.code)
            for name, data in LOCATION_TABLE.items()
            if data.code is not None
        },
        # Auto-tab: UT watches this DataStorage key and calls map_page_index when it changes.
        # The client writes the stage_hex_to_id() integer here on every room transition.
        "map_page_setting_key": "chibi_robo_stage_{player}_{team}",
        "map_page_index":       _chibi_robo_map_index,
    }

    @staticmethod
    def interpret_slot_data(slot_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # UT calls int() on all values whose keys match known option names.
        # required_stickers is an OptionSet (list of strings) which crashes that.
        # Pass integer options normally; sticker list under a non-option key.
        result = {k: v for k, v in slot_data.items() if isinstance(v, int)}
        stickers = slot_data.get("_chibi_stickers")
        if isinstance(stickers, (list, set, frozenset)):
            result["_chibi_stickers"] = list(stickers)
        return result if result else None


    @staticmethod
    def _get_classification_name(classification: IC) -> str:
        """
        Return a string representation of the item's highest-order classification.

        :param classification: The item's classification.
        :return: A string representation of the item's highest classification.
        """

        if IC.progression in classification:
            return "progression"
        elif IC.useful in classification:
            return "useful"
        else:
            return "filler"

    @staticmethod
    def _get_object_name(name: str, player, item_for_player, player_option) -> str:
        """
        Return the items object name
        """

        if name in ITEM_TABLE and player == item_for_player:

            if name == "Old Clothes":
                if player_option.pj_suit_style.option_old_boxers:
                    return "item_pajama_kiji_2"
                if  player_option.pj_suit_style.option_outdated_scarf:
                    return "item_pajama_kiji_3"
                if  player_option.pj_suit_style.option_small_handkerchief:
                    return "item_pajama_kiji"

            return ITEM_TABLE[name].object_name
        else:
            return "archipelago_item"
        # raise KeyError(f"Invalid item name: {name}")

    @staticmethod
    def _get_location_object_id(name: str) -> int:
        """
        Return the items object name
        """

        if name in LOCATION_TABLE:
            return LOCATION_TABLE[name].object_id

        raise KeyError(f"Could not find location id")

    def create_regions(self) -> None:
        create_regions(self.multiworld, self.player, self.options)

    def set_rules(self) -> None:
        logic_enabled = self.options.logic_setting

        if logic_enabled == 1:
            set_location_rules(self)
            set_rules(self)

    def get_filler_item_name(self) -> str:
        filler = list(FILLER_ITEM_TABLE.keys())
        return self.multiworld.random.choice(filler)


    def fill_slot_data(self) -> Dict[str, Any]:
        slot_data = self.options.as_dict("victory_goal", "pj_suit_style", "open_upstairs", "password_rando", "chibi_vision_off", "favorite_character_voice", "death_link", "battery_drain_idle", "battery_drain_walk", "battery_drain_jog", "battery_drain_run", "battery_drain_slide", "battery_drain_equip", "battery_drain_lift", "battery_drain_drop", "battery_drain_ledge_grab", "battery_drain_ledge_slide", "battery_drain_ledge_climb", "battery_drain_ledge_drop", "battery_drain_ledge_teeter", "battery_drain_jump", "battery_drain_fall", "battery_drain_ladder_grab", "battery_drain_ladder_ascend", "battery_drain_ladder_descend", "battery_drain_ladder_top", "battery_drain_ladder_bottom", "battery_drain_rope_grab", "battery_drain_rope_ascend", "battery_drain_rope_descend", "battery_drain_rope_top", "battery_drain_rope_bottom", "battery_drain_push", "battery_drain_copter_hover", "battery_drain_copter_descend", "battery_drain_popper_shoot", "battery_drain_pooper_shoot_charge", "battery_drain_radar_scan", "battery_drain_radar_follow", "battery_drain_brush", "battery_drain_spoon", "battery_drain_mug", "battery_drain_squirter_suck", "battery_drain_squirter_spray")
        slot_data["_chibi_stickers"] = list(self.options.required_stickers.value)
        return slot_data

    def generate_output(self, output_directory: str) -> None:
        """
        Create the output file that is used to randomize the ISO.
        """

        if hasattr(self.multiworld, "generation_is_fake"):
            return

        multiworld = self.multiworld
        player = self.player

        output_data = {
            "Version": list(VERSION),
            "Seed": multiworld.seed_name,
            "Slot": player,
            "Name": self.player_name,
            "Locations": {}
        }

         # Output which item has been placed at each location.
        output_locations = output_data["Locations"]
        for location in multiworld.get_locations(player):

            if location.item:
                item_info = {
                    "player": multiworld.player_name[location.item.player],
                    "name": location.item.name,
                    # "game": location.item.game,
                    "classification": self._get_classification_name(location.item.classification),
                    "object": self._get_object_name(location.item.name, self.player, location.item.player, self.options),
                    "location_id": self._get_location_object_id(location.name),
                }
            else:
                item_info = {"name": "Nothing", "game": game_name, "classification": "filler"}
            output_locations[location.name] = item_info

        output_data.update(self.options.as_dict( "victory_goal","required_stickers", "pj_suit_style", "open_upstairs","password_rando", "chibi_vision_off", "favorite_character_voice", "battery_drain_idle", "battery_drain_walk", "battery_drain_jog", "battery_drain_run", "battery_drain_slide", "battery_drain_equip", "battery_drain_lift", "battery_drain_drop", "battery_drain_ledge_grab", "battery_drain_ledge_slide", "battery_drain_ledge_climb", "battery_drain_ledge_drop", "battery_drain_ledge_teeter", "battery_drain_jump", "battery_drain_fall", "battery_drain_ladder_grab", "battery_drain_ladder_ascend", "battery_drain_ladder_descend", "battery_drain_ladder_top", "battery_drain_ladder_bottom", "battery_drain_rope_grab", "battery_drain_rope_ascend", "battery_drain_rope_descend", "battery_drain_rope_top", "battery_drain_rope_bottom", "battery_drain_push", "battery_drain_copter_hover", "battery_drain_copter_descend", "battery_drain_popper_shoot", "battery_drain_pooper_shoot_charge", "battery_drain_radar_scan", "battery_drain_radar_follow", "battery_drain_brush", "battery_drain_spoon", "battery_drain_mug", "battery_drain_squirter_suck", "battery_drain_squirter_spray"))

        mod_name = f"AP-{self.multiworld.seed_name}-P{self.player}-{self.multiworld.get_file_safe_player_name(self.player)}"
        mod_dir = os.path.join(output_directory, mod_name + "_" + Utils.__version__)

        files = {
            f"AP-{multiworld.seed_name}-P{player}-{multiworld.get_file_safe_player_name(player)}.apcr": json.dumps(output_data),
        }

        apcr = ChibiRoboContainer(
            files,
            mod_dir,
            output_directory,
            self.player,
            self.multiworld.get_file_safe_player_name(self.player)
        )
        apcr.write()

    def generate_early(self) -> None:
        self.plando_locations = dict()

        if hasattr(self.multiworld, "re_gen_passthrough"):

            passthrough = self.multiworld.re_gen_passthrough.get(game_name, None)

            if passthrough is not None:
                victory = passthrough.get("victory_goal", None)

                if victory is not None:
                    self.options.victory_goal.value = victory

                stickers = passthrough.get("_chibi_stickers", None)
                if stickers is not None:
                    self.options.required_stickers.value = (
                        set(stickers) if isinstance(stickers, list) else stickers
                    )

                open_upstairs = passthrough.get("open_upstairs", None)
                if open_upstairs is not None:
                    self.options.open_upstairs.value = open_upstairs

                password_rando = passthrough.get("password_rando", None)
                if password_rando is not None:
                    self.options.password_rando.value = password_rando

                return  # skip sticker randomization — use actual seed values

        stickers = self.options.required_stickers

        if "Random" in stickers.value or not stickers.value:
            pool = sorted(STICKER_NAMES)
            count = self.random.randint(1, len(pool))
            stickers.value = set(self.random.sample(pool, count))

        self.multiworld.local_early_items[self.player]["Toothbrush Chibi-Gear"] = 1
        self.multiworld.local_early_items[self.player]["Mug Chibi-Gear"] = 1
        self.multiworld.local_early_items[self.player]["Drake Redcrest Suit"] = 1


    def get_pre_fill_items(self) -> List[Item]:
        return [self.create_item(item)
                for item in [*self.plando_locations.keys()]]

    def pre_fill(self):
        for location, item in self.plando_locations.items():
            self.multiworld.get_location(location, self.player).place_locked_item(self.create_item(item))

    def create_item(self, name: str) -> ChibiRoboItem:
        """
        Create an item for this world type and player.

        :param name: The name of the item to create.
        :raises KeyError: If an invalid item name is provided.
        """

        if name in ITEM_TABLE:
            return ChibiRoboItem(name, self.player, ITEM_TABLE[name])

        elif name in FILLER_ITEM_TABLE:
            return ChibiRoboItem(name, self.player, FILLER_ITEM_TABLE[name])

        raise KeyError(f"Invalid item name: {name}")

    def create_items(self):
      self.multiworld.itempool += create_itempool(self)


    def collect(self, state: CollectionState, item: ChibiRoboItem) -> bool:
        change = super().collect(state, item)
        return change

    def remove(self, state: CollectionState, item: ChibiRoboItem) -> bool:
        change = super().remove(state, item)
        return change

def create_itempool(world: "ChibiRoboWorld") -> List[Item]:
    itempool: List[Item] = []

    # total_locations = len(world.multiworld.get_unfilled_locations(world.player))

    for name in ITEM_TABLE.keys():
        item_type: ItemClassification = ITEM_TABLE.get(name).classification
        itempool += create_multiple_items(world, name, 1, item_type)

    for x in range(8):
        itempool += create_multiple_items(world, "Giga Battery Charge", 1, IC.filler)

    for name in FILLER_ITEM_TABLE.keys():
        item_type: ItemClassification = FILLER_ITEM_TABLE.get(name).classification
        itempool += create_multiple_items(world, name, 1, item_type)

    unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))

    while len(itempool) < unfilled_locations:
        rand_item = world.random.choice(list(FILLER_ITEM_TABLE.keys()))
        itempool += create_multiple_items(world, rand_item, 1, IC.filler)

    return itempool

def create_multiple_items(world: "ChibiRoboWorld", name: str, count: int = 1,
                              item_type: ItemClassification = ItemClassification.progression) -> List[Item]:

    if name in ITEM_TABLE:
        data = ITEM_TABLE[name]
        
    itemlist: List[Item] = []

    for i in range(count):
            itemlist += [ChibiRoboItem(name, world.player, data, item_type)]

    return itemlist