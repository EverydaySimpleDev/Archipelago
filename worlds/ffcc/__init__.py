# Python standard libraries
import base64
import io
import logging
import os
import zipfile
from base64 import b64encode
from typing import List, Dict, Optional

from typing import Any, ClassVar
from logging import Logger
import dolphin_memory_engine
import yaml
import json

import Utils
# Archipelago imports
from worlds.AutoWorld import World, WebWorld
from worlds.LauncherComponents import components, Component, launch_subprocess, Type, icon_paths
from BaseClasses import Item, ItemClassification, Tutorial, CollectionState, MultiWorld
from .regions import create_regions, connect_entrances
from .items import FFCCItem, ITEM_TABLE, item_name_groups, FFCCItemData, ITEM_TABLE_DESC, FILLER_ITEM_TABLE
from .locations import FFCCLocation, LOCATION_TABLE, location_groups, FFCCLocationData
from .options import FFCCGameOptions, FFCC_option_groups
from BaseClasses import ItemClassification as IC
from worlds.Files import APPlayerContainer
from .rules import set_rules, set_location_rules

VERSION: tuple[int, int, int] = (0, 0, 0)

def launch_client():
    from . import client
    launch_subprocess(client.launch, name="FFCCClient")


components.append(Component("Final Fantasy Crystal Chronicles Client",
                            func=launch_client,
                            component_type=Type.CLIENT,
                            icon="FFCC_icon"))

icon_paths["FFCC_icon"] = f"ap:{__name__}/icons/FFCC_icon.png"

class FFCCWebWorld(WebWorld):
    theme = "dirt"

    item_descriptions = ITEM_TABLE_DESC

    bug_report_page = "https://github.com/EverydaySimpleDev/Archipelago",

    setup_en = Tutorial(
        tutorial_name="Start Guide",
        description="A guide to playing Final Fantasy Crystal Chronicles in Archipelago.",
        language="English",
        file_name="guide_en.md",
        link="guide/en",
        authors=["EverydaySimpleDev"]
    )

    tutorials = [setup_en]

    option_groups = FFCC_option_groups

class FFCCContainer(APPlayerContainer):
    """
    This class defines the container file
    """

    game: str = "Final Fantasy Crystal Chronicles"
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


class FFCCWorld(World):
    dolphin: dolphin_memory_engine
    logger: Logger

    game = "Final Fantasy Crystal Chronicles"
    web = FFCCWebWorld()
    # options_dataclass = FFCCGameOptions
    # options: FFCCGameOptions
    topology_present = True

    plando_locations: Dict[str, str]

    item_name_to_id: ClassVar[dict[str, int]] = {
        name: FFCCItem.get_apid(data.code) for name, data in ITEM_TABLE.items() if data.code is not None
    }

    location_name_to_id: ClassVar[dict[str, int]] = {
        name: FFCCLocation.get_apid(data.code) for name, data in LOCATION_TABLE.items() if data.code is not None
    }

    item_name_groups: ClassVar[dict[str, set[str]]] = item_name_groups
    location_name_groups: ClassVar[dict[str, set[str]]] = location_groups

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
    def _get_object_name(name: str, self, item_for_player) -> str:
        """
        Return the items object name
        """

        if name in ITEM_TABLE and self == item_for_player:
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
        set_location_rules(self)
        set_rules(self)

    def get_filler_item_name(self) -> str:
        filler = list(FILLER_ITEM_TABLE.keys())
        return self.multiworld.random.choice(filler)


    def fill_slot_data(self) -> Dict[str, Any]:
        return self.options.as_dict( "victory_goal")

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
                    "player": multiworld.player_name[location.item.player],
                    "name": location.item.name,
                    # "game": location.item.game,
                    "classification": self._get_classification_name(location.item.classification),
                    "object": self._get_object_name(location.item.name, self.player, location.item.player),
                    "location_id": self._get_location_object_id(location.name),
                }
            else:
                item_info = {"name": "Nothing", "game": "Final Fantasy Crystal Chronicles", "classification": "filler"}
            output_locations[location.name] = item_info

        output_data.update(self.options.as_dict( "victory_goal"))

        mod_name = f"AP-{self.multiworld.seed_name}-P{self.player}-{self.multiworld.get_file_safe_player_name(self.player)}"
        mod_dir = os.path.join(output_directory, mod_name + "_" + Utils.__version__)

        files = {
            f"AP-{multiworld.seed_name}-P{player}-{multiworld.get_file_safe_player_name(player)}.ffcc": json.dumps(output_data),
        }

        ffcc = FFCCContainer(
            files,
            mod_dir,
            output_directory,
            self.player,
            self.multiworld.get_file_safe_player_name(self.player)
        )
        ffcc.write()

    def generate_early(self) -> None:
        self.plando_locations = dict()


    def get_pre_fill_items(self) -> List[Item]:
        return [self.create_item(item)
                for item in [*self.plando_locations.keys()]]

    def pre_fill(self):
        for location, item in self.plando_locations.items():
            self.multiworld.get_location(location, self.player).place_locked_item(self.create_item(item))

    def create_item(self, name: str) -> FFCCItem:
        """
        Create an item for this world type and player.

        :param name: The name of the item to create.
        :raises KeyError: If an invalid item name is provided.
        """

        if name in ITEM_TABLE:
            return FFCCItem(name, self.player, ITEM_TABLE[name])

        elif name in FILLER_ITEM_TABLE:
            return FFCCItem(name, self.player, FILLER_ITEM_TABLE[name])

        raise KeyError(f"Invalid item name: {name}")

    def create_items(self):
      self.multiworld.itempool += create_itempool(self)


    def collect(self, state: CollectionState, item: FFCCItem) -> bool:
        change = super().collect(state, item)
        return change

    def remove(self, state: CollectionState, item: FFCCItem) -> bool:
        change = super().remove(state, item)
        return change

def create_itempool(world: "FFCCWorld") -> List[Item]:
    itempool: List[Item] = []

    # total_locations = len(world.multiworld.get_unfilled_locations(world.player))

    for name in ITEM_TABLE.keys():
        item_type: ItemClassification = ITEM_TABLE.get(name).classification
        itempool += create_multiple_items(world, name, 1, item_type)

    for name in FILLER_ITEM_TABLE.keys():
        item_type: ItemClassification = FILLER_ITEM_TABLE.get(name).classification
        itempool += create_multiple_items(world, name, 1, item_type)

    unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))

    while len(itempool) < unfilled_locations:
        rand_item = world.random.choice(list(FILLER_ITEM_TABLE.keys()))
        itempool += create_multiple_items(world, rand_item, 1, IC.filler)

    return itempool

def create_multiple_items(world: "FFCCWorld", name: str, count: int = 1,
                              item_type: ItemClassification = ItemClassification.progression) -> List[Item]:

    if name in ITEM_TABLE:
        data = ITEM_TABLE[name]
        
    itemlist: List[Item] = []

    for i in range(count):
            itemlist += [FFCCItem(name, world.player, data, item_type)]

    return itemlist