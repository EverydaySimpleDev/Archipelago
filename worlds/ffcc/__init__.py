import io
import json
import os
import zipfile
from typing import Any, ClassVar, Dict, List, Optional

import Utils
from BaseClasses import Item, ItemClassification, Tutorial, MultiWorld
from worlds.AutoWorld import World, WebWorld
from worlds.LauncherComponents import components, Component, launch_subprocess, Type, icon_paths
from worlds.Files import APPlayerContainer

from .game_id import game_name
from .regions import create_regions, connect_entrances
from .items import (FFCCItem, FFCCItemData, ITEM_TABLE, FILLER_ITEM_TABLE, TRAP_ITEMS,
                    ITEM_TABLE_DESC, LOOKUP_ID_TO_NAME, item_name_groups,
                    PROGRESSIVE_ARTIFACT_NAME, PROGRESSIVE_ARTIFACT_CODE, _ARTIFACTS,
                    CYCLE_PLACEHOLDER_ITEM, YEAR_PLACEHOLDER_ITEM)
from .locations import FFCCLocation, LOCATION_TABLE, location_groups
from .options import FFCCGameOptions, FFCC_option_groups
from .rules import (set_rules, set_location_rules, layout_is_beatable, first_year_dungeons,
                    stage_key, SPOT_AREA)
from .regions import MYRRH_DUNGEONS, myrrh_location
from .items import MYRRH_DROP, MYRRH_DROP_DATA

VERSION: tuple = (0, 1, 0)

IC = ItemClassification


def launch_client():
    from . import client
    launch_subprocess(client.launch, name="FFCCClient")


components.append(Component(
    "Final Fantasy Crystal Chronicles Client",
    func=launch_client,
    component_type=Type.CLIENT,
    icon="FFCC_icon",
))

icon_paths["FFCC_icon"] = f"ap:{__name__}/icons/FFCC_icon.png"

class FFCCWebWorld(WebWorld):
    theme = "dirt"
    item_descriptions = ITEM_TABLE_DESC
    bug_report_page = "https://github.com/EverydaySimpleDev/Archipelago"

    setup_en = Tutorial(
        tutorial_name="Start Guide",
        description="A guide to playing Final Fantasy Crystal Chronicles in Archipelago.",
        language="English",
        file_name="guide_en.md",
        link="guide/en",
        authors=["EverydaySimpleDev"],
    )
    tutorials = [setup_en]
    option_groups = FFCC_option_groups


class FFCCContainer(APPlayerContainer):
    game: str = game_name
    patch_file_ending: str = ".zip"

    def __init__(self, patch_data: Dict[str, str], base_path: str = "",
                 output_directory: str = "", player: Optional[int] = None,
                 player_name: str = "", server: str = ""):
        self.patch_data = patch_data
        self.file_path = base_path
        container_path = os.path.join(output_directory, base_path + ".zip")
        super().__init__(container_path, player, player_name, server)

    def write_contents(self, opened_zipfile: zipfile.ZipFile) -> None:
        for filename, content in self.patch_data.items():
            opened_zipfile.writestr(filename, content)
        super().write_contents(opened_zipfile)


class FFCCWorld(World):
    game = "Final Fantasy Crystal Chronicles"
    web  = FFCCWebWorld()
    options_dataclass = FFCCGameOptions
    options: FFCCGameOptions
    topology_present = True

    item_name_to_id: ClassVar[dict] = {
        name: FFCCItem.get_apid(data.code)
        for name, data in ITEM_TABLE.items()
        if data.code is not None
    }
    location_name_to_id: ClassVar[dict] = {
        name: FFCCLocation.get_apid(data.code)
        for name, data in LOCATION_TABLE.items()
        if data.code is not None
    }
    item_name_groups:    ClassVar[dict] = item_name_groups
    location_name_groups: ClassVar[dict] = location_groups

    def create_regions(self) -> None:
        create_regions(self.multiworld, self.player, self.options)

    # Dungeons the loading-zone shuffle moves (Mount Kilanda stays put; Mount
    # Vellenge isn't a world-map spot of its own).
    SHUFFLED_SPOTS = [spot for spot in SPOT_AREA if spot != "Mount Kilanda"]

    VANILLA_GATES = [[2, 8, 4, 1], [1, 2, 8, 4], [4, 1, 2, 8], [8, 4, 1, 2]]

    def generate_early(self) -> None:
        keys = bool(self.options.stage_keys)
        shuffle_zones = bool(self.options.shuffle_loading_zones)
        shuffle_gates = bool(self.options.randomize_miasma_streams)
        # A shuffled Miasma Stream can ask for any element in Year 1; Goblin Wall's
        # Fire and Earth in Year 1 is what keeps every element within reach.
        self.goblin_year1 = bool(self.options.goblin_wall_year_one) or shuffle_gates

        # Miasma Stream elements [year % 4 row][gate slot] and the world-map
        # layout {spot: dungeon}; shuffled ones are kept only if every year can
        # be finished (rules.layout_is_beatable).
        vanilla_plan = {spot: spot for spot in SPOT_AREA}
        self.gate_table, self.zone_plan = self.VANILLA_GATES, vanilla_plan
        for _ in range(10000):
            gates = self.VANILLA_GATES
            if shuffle_gates:
                gates = [self.random.sample(row, 4) for row in self.VANILLA_GATES]
            plan = vanilla_plan
            if shuffle_zones:
                dungeons = self.SHUFFLED_SPOTS[:]
                self.random.shuffle(dungeons)
                plan = dict(vanilla_plan, **dict(zip(self.SHUFFLED_SPOTS, dungeons)))
            if layout_is_beatable(plan, gates, keys, self.goblin_year1):
                self.gate_table, self.zone_plan = gates, plan
                break

        if keys:
            # Year 1 needs three Myrrh trees: River Belle Path plus two dungeons
            # whose keys must turn up early, along with the Year 2 Key.
            early = self.multiworld.local_early_items[self.player]
            for dungeon in first_year_dungeons(self.zone_plan, self.gate_table, self.goblin_year1):
                early[stage_key(dungeon)] = 1
            early["Year 2 Key"] = 1

    def set_rules(self) -> None:
        set_location_rules(self)
        set_rules(self)

    def get_filler_item_name(self) -> str:
        return self.random.choice(list(FILLER_ITEM_TABLE.keys()))

    def fill_slot_data(self) -> Dict[str, Any]:
        data = self.options.as_dict(
            "victory_goal", "progressive_artifacts", "include_traps",
            "frozen_trap_weight", "burned_trap_weight", "slowed_trap_weight",
            "poisoned_trap_weight", "chalice_element_trap_weight",
            "bonus_set_trap_weight", "food_preference_trap_weight", "death_link",
        )

        # Locations where the item was placed physically in the chest (hybrid patch).
        # These are own-player items with a real in-game ID; the client skips the
        # memory-write for them to avoid giving the item a second time.
        physical: List[int] = []
        for location in self.multiworld.get_locations(self.player):
            if not location.item or location.item.player != self.player:
                continue
            item_data = ITEM_TABLE.get(location.item.name)
            if item_data and item_data.item_id is not None:
                loc_data = LOCATION_TABLE.get(location.name)
                if loc_data and not loc_data.is_event:
                    physical.append(FFCCLocation.get_apid(loc_data.code))
        data["physical_chest_ap_ids"] = physical

        return data

    def create_item(self, name: str) -> FFCCItem:
        if name in ITEM_TABLE:
            return FFCCItem(name, self.player, ITEM_TABLE[name])
        raise KeyError(f"Unknown FFCC item: {name!r}")

    def create_items(self) -> None:
        for dungeon in MYRRH_DUNGEONS:
            self.multiworld.get_location(myrrh_location(dungeon), self.player).place_locked_item(
                FFCCItem(MYRRH_DROP, self.player, MYRRH_DROP_DATA))
        cycle_placeholder = ITEM_TABLE[CYCLE_PLACEHOLDER_ITEM]
        year_placeholder  = ITEM_TABLE[YEAR_PLACEHOLDER_ITEM]
        for name, loc_data in LOCATION_TABLE.items():
            if not loc_data.is_event:
                continue
            loc = self.multiworld.get_location(name, self.player)
            if loc_data.region == "Menu":
                if not self.options.year_location_checks:
                    loc.place_locked_item(
                        FFCCItem(YEAR_PLACEHOLDER_ITEM, self.player, year_placeholder))
            else:
                if not self.options.cycle_location_checks:
                    loc.place_locked_item(
                        FFCCItem(CYCLE_PLACEHOLDER_ITEM, self.player, cycle_placeholder))
        self.multiworld.itempool += _create_item_pool(self)

    def generate_output(self, output_directory: str) -> None:
        multiworld = self.multiworld
        player     = self.player

        # Location → item placement data for the client / patcher
        locations_out = {}
        for location in multiworld.get_locations(player):
            if location.item:
                loc_data  = LOCATION_TABLE.get(location.name)
                if loc_data is None or loc_data.is_event:
                    continue  # no physical chest (Myrrh trees, cycle/year events) — skip patcher output
                item_data = ITEM_TABLE.get(location.item.name)
                locations_out[location.name] = {
                    "player":      multiworld.player_name[location.item.player],
                    "item":        location.item.name,
                    "item_id":     item_data.item_id if item_data else None,
                    "class":       _cls_name(location.item.classification),
                    "dungeon":     loc_data.region,
                    "cycle":       loc_data.cycle,
                    "chest":       loc_data.chest,   # game-order chest number (chest_table.py)
                }

        output_data = {
            "version":  list(VERSION),
            "seed":     multiworld.seed_name,
            "slot":     player,
            "player":   self.player_name,
            "settings": self.options.as_dict(
                "victory_goal", "progressive_artifacts", "include_traps",
                "frozen_trap_weight", "burned_trap_weight", "slowed_trap_weight",
                "poisoned_trap_weight", "chalice_element_trap_weight",
                "bonus_set_trap_weight", "food_preference_trap_weight", "death_link",
                "stage_keys", "shuffle_loading_zones", "randomize_miasma_streams",
                "goblin_wall_year_one", "mog_never_tired", "skip_intro_cutscene",
                "skip_mio_questions", "trap_visuals", "randomize_shops",
                "randomize_shop_prices", "randomize_bonus_pools",
            ),
            # {spot: dungeon} for the patcher (same names the randomizer's JSON uses)
            "world_zones": self.zone_plan,
            # Miasma Stream table the logic used (only sent when shuffled)
            "miasma_elements": self.gate_table if self.options.randomize_miasma_streams else None,
            "locations": locations_out,
        }

        mod_name = (
            f"AP-{multiworld.seed_name}"
            f"-P{player}"
            f"-{multiworld.get_file_safe_player_name(player)}"
        )
        mod_dir = os.path.join(output_directory, mod_name + "_" + Utils.__version__)
        filename = f"{mod_name}.ffcc"

        container = FFCCContainer(
            {filename: json.dumps(output_data, indent=2)},
            mod_dir,
            output_directory,
            player,
            multiworld.get_file_safe_player_name(player),
        )
        container.write()

def _cls_name(classification: IC) -> str:
    if IC.progression in classification:
        return "progression"
    if IC.useful in classification:
        return "useful"
    if IC.trap in classification:
        return "trap"
    return "filler"


def _create_item_pool(world: "FFCCWorld") -> List[Item]:
    pool: List[Item] = []
    use_progressive = bool(world.options.progressive_artifacts)
    use_traps       = bool(world.options.include_traps)

    for name, data in ITEM_TABLE.items():
        if data.type in ("Trap", "Progressive Artifact", "Placeholder"):
            continue  # handled separately below; Placeholders are pre-placed at event locs
        if data.type == "Stage Key" and not world.options.stage_keys:
            continue
        if data.type == "Artifact" and use_progressive:
            continue  # replaced by 73 × Progressive Artifact below
        pool.append(FFCCItem(name, world.player, data))

    # Add 73 copies of Progressive Artifact when that option is on
    if use_progressive:
        pa_data = ITEM_TABLE[PROGRESSIVE_ARTIFACT_NAME]
        for _ in range(len(_ARTIFACTS)):
            pool.append(FFCCItem(PROGRESSIVE_ARTIFACT_NAME, world.player, pa_data))

    # Pad remaining slots with weighted filler (traps if enabled, food/phoenix otherwise)
    unfilled = len(world.multiworld.get_unfilled_locations(world.player)) - len(pool)
    if unfilled > 0:
        filler_pool = _build_filler_choices(world, use_traps)
        for _ in range(unfilled):
            name = world.random.choice(filler_pool)
            pool.append(FFCCItem(name, world.player, ITEM_TABLE[name]))

    return pool


def _build_filler_choices(world: "FFCCWorld", use_traps: bool) -> list:
    """Return a weighted list of filler item names for random.choice()."""
    opts = world.options
    choices = []

    # Base filler (materials, food, phoenix down, most recipes — weight 1 each)
    choices.extend(list(FILLER_ITEM_TABLE.keys()))

    if use_traps:
        trap_weights = {
            "Frozen Trap":          opts.frozen_trap_weight.value,
            "Burned Trap":          opts.burned_trap_weight.value,
            "Slowed Trap":          opts.slowed_trap_weight.value,
            "Poisoned Trap":        opts.poisoned_trap_weight.value,
            "Chalice Element Trap": opts.chalice_element_trap_weight.value,
            "Bonus Set Trap":       opts.bonus_set_trap_weight.value,
            "Food Preference Trap": opts.food_preference_trap_weight.value,
        }
        for trap_name, weight in trap_weights.items():
            choices.extend([trap_name] * weight)

    return choices
