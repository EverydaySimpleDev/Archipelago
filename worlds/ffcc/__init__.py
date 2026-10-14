import io
import json
import os
import zipfile
from typing import Any, ClassVar, Dict, List, Optional

from BaseClasses import Item, ItemClassification, Tutorial, MultiWorld
from worlds.AutoWorld import World, WebWorld
from worlds.LauncherComponents import components, Component, launch_subprocess, Type, icon_paths, SuffixIdentifier
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
from .items import MYRRH_DROP, MYRRH_DROP_DATA, ARTIFACT_TYPES

VERSION: tuple = (0, 1, 1)

IC = ItemClassification


def launch_client(*args: str):
    from . import client
    launch_subprocess(client.launch, name="FFCCClient", args=args)


components.append(Component(
    "Final Fantasy Crystal Chronicles Client",
    func=launch_client,
    component_type=Type.CLIENT,
    file_identifier=SuffixIdentifier(".ffcc"),
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
    """The player's .ffcc file: a zip holding the seed's placement data (for the
    randomizer's AP Patch) and archipelago.json (server and slot, so opening the
    file starts the client and connects)."""
    game: str = game_name
    patch_file_ending: str = ".ffcc"

    def __init__(self, patch_data: Dict[str, str], base_path: str = "",
                 output_directory: str = "", player: Optional[int] = None,
                 player_name: str = "", server: str = ""):
        self.patch_data = patch_data
        self.file_path = base_path
        container_path = os.path.join(output_directory, base_path + self.patch_file_ending)
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
        # Goblin Wall in Year 1 is forced on with either shuffle. A shuffled Miasma
        # Stream can ask for any element in Year 1, and Goblin Wall's Fire and Earth
        # keep every element within reach; with loading zones shuffled, the dungeon
        # placed on Goblin Wall's spot (often River Belle Path) must show up in Year 1.
        if shuffle_gates or shuffle_zones:
            self.options.goblin_wall_year_one.value = 1
        self.goblin_year1 = bool(self.options.goblin_wall_year_one)

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

        # Locations whose item the patcher puts in the chest itself. The game
        # gives those on pickup, so the client doesn't give them again.
        data["physical_chest_ap_ids"] = [
            FFCCLocation.get_apid(LOCATION_TABLE[location.name].code)
            for location in self.multiworld.get_locations(self.player)
            if self._item_in_chest(location)
        ]

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

    def _item_in_chest(self, location) -> bool:
        """True if the patcher puts this location's item in the chest itself:
        one of this player's own items with an in-game ID, in a real chest,
        and not an artifact (see ARTIFACT_TYPES)."""
        item = location.item
        loc_data = LOCATION_TABLE.get(location.name)
        if item is None or item.player != self.player or loc_data is None:
            return False
        if loc_data.is_event or not loc_data.chest:
            return False
        item_data = ITEM_TABLE.get(item.name)
        return (item_data is not None and item_data.item_id is not None
                and item_data.type not in ARTIFACT_TYPES)

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
                    "in_chest":    self._item_in_chest(location),
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

        # AP_<seed>_P<slot>_<name>.ffcc - the standard name, so a room offers it
        # as the player's download
        base = multiworld.get_out_file_name_base(player)
        container = FFCCContainer(
            {f"{base}.ffcc": json.dumps(output_data, indent=2)},
            base,
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
            continue  # replaced by Progressive Artifacts below
        pool.append(FFCCItem(name, world.player, data))

    # Add one Progressive Artifact per artifact when that option is on
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
