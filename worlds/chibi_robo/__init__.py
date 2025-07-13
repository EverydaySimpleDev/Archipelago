# Python standard libraries
import json
import logging
import os
import zipfile
from base64 import b64encode
from collections.abc import Mapping
from typing import Any, ClassVar, List, Dict
from collections import defaultdict
from math import ceil

from typing import Any, ClassVar, Callable, Union, cast
from logging import Logger
import dolphin_memory_engine
import Utils
import yaml
import json

# Archipelago imports
import settings
from worlds.AutoWorld import World, WebWorld
from worlds.LauncherComponents import components, Component, launch_subprocess, Type, icon_paths
from BaseClasses import Region, Location, Entrance, Item, ItemClassification, Tutorial, CollectionState, MultiWorld
from .regions import create_regions, connect_entrances
from .game_id import game_name
from .items import ChibiRoboItem, ITEM_TABLE, item_name_groups, ChibiRoboItemData, filler_item_names, ITEM_TABLE_DESC
from .locations import ChibiRoboLocation, LOCATION_TABLE, location_groups, ChibiRoboLocationData
from .options import ChibiRobobGameOptions
from BaseClasses import ItemClassification as IC
from worlds.Files import APPlayerContainer, AutoPatchRegister
from .rules import set_rules, set_location_rules

VERSION: tuple[int, int, int] = (1, 0, 0)

def launch_client():
    from . import client
    launch_subprocess(client.launch, name="ChibiRoboClient")


components.append(Component("Chibi Robo Client",
                            func=launch_client,
                            component_type=Type.CLIENT,
                            icon="chibi_body_icon"))

icon_paths["chibi_body_icon"] = f"ap:{__name__}/icons/chibi_body_icon.png"

class ChibiRoboWebWorld(WebWorld):
    theme = "dirt"

    item_descriptions = ITEM_TABLE_DESC

    bug_report_page = "https://github.com/EverydaySimpleDev/Archipelago",

    setup_en = Tutorial(
        tutorial_name="Start Guide",
        description="A guide to playing Chibi Robo! in Archipelago.",
        language="English",
        file_name="guide_en.md",
        link="guide/en",
        authors=["EverydaySimpleDev"]
    )

    tutorials = [setup_en]


class ChibiRoboContainer(APPlayerContainer, metaclass=AutoPatchRegister):
    """
    This class defines the container file
    """

    game: str = game_name
    patch_file_ending: str = ".aptcr"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if "data" in kwargs:
            self.data = kwargs["data"]
            del kwargs["data"]

        super().__init__(*args, **kwargs)

    def write_contents(self, opened_zipfile: zipfile.ZipFile) -> None:
        """
        Write the contents of the container file.
        """
        super().write_contents(opened_zipfile)

        # Record the data for the game under the key `plando`.
        opened_zipfile.writestr("plando", b64encode(bytes(yaml.safe_dump(self.data, sort_keys=False), "utf-8")))


class ChibiRoboWorld(World):
    dolphin: dolphin_memory_engine
    logger: Logger

    game = game_name
    web = ChibiRoboWebWorld()
    options_dataclass = ChibiRobobGameOptions
    options: ChibiRobobGameOptions
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

    @staticmethod
    def _get_classification_name(classification: IC) -> str:
        """
        Return a string representation of the item's highest-order classification.

        :param classification: The item's classification.
        :return: A string representation of the item's highest classification. The order of classification is
        progression > trap > useful > filler.
        """

        if IC.progression in classification:
            return "progression"
        elif IC.useful in classification:
            return "useful"
        else:
            return "filler"

    @staticmethod
    def _get_object_name(name: str, self) -> str:
        """
        Return the items object name

        """

        if name in ITEM_TABLE:
            return ITEM_TABLE[name].object_name
        else:
            return "archipelago_item"
        # raise KeyError(f"Invalid item name: {name}")

    def create_regions(self) -> None:
        create_regions(self.multiworld, self.player, self.options)

    def set_rules(self) -> None:
        set_rules(self)
        set_location_rules(self)

    def get_filler_item_name(self) -> str:
        return self.random.choice(filler_item_names)

    def fill_slot_data(self) -> Dict[str, Any]:
        return self.options.as_dict("debug_menu", "free_pjs", "charged_giga_battery", "open_upstairs", "open_downstairs","chibi_vision_off")

    def generate_output(self, output_directory: str) -> None:
        """
        Create the output file that is used to randomize the ISO.
        """
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
                    "player": location.item.player,
                    "name": location.item.name,
                    "game": location.item.game,
                    "classification": self._get_classification_name(location.item.classification),
                    "object": self._get_object_name(location.item.name, self.player),
                }
            else:
                item_info = {"name": "Nothing", "game": game_name, "classification": "filler"}
            output_locations[location.name] = item_info

        output_data.update(self.options.as_dict("debug_menu", "free_pjs", "charged_giga_battery", "open_upstairs", "open_downstairs", "chibi_vision_off"))

        mod_name = self.multiworld.get_out_file_name_base(self.player)
        out_file = os.path.join(output_directory, mod_name + ".json")

        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)

    def generate_early(self) -> None:
        self.plando_locations = dict()

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

    for name in ITEM_TABLE.keys():
        item_type: ItemClassification = ITEM_TABLE.get(name).classification
        itempool += create_multiple_items(world, name, 1, item_type)

    # Game needs toothbrush in living
    world.get_location("Living Room - Candy Wrapper by Jenny B").place_locked_item(itempool[0])
    itempool.remove(itempool[0])

    # Force Left in suitcase?
    # world.get_location("Bedroom - Left Leg in Suitcase").place_locked_item(itempool[10])
    # itempool.remove(itempool[10])

    return itempool

def create_multiple_items(world: "ChibiRoboWorld", name: str, count: int = 1,
                              item_type: ItemClassification = ItemClassification.progression) -> List[Item]:

    data = ITEM_TABLE[name]
    itemlist: List[Item] = []

    for i in range(count):
            itemlist += [ChibiRoboItem(name, world.player, data, item_type)]

    return itemlist