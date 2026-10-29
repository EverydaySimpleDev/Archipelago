import io
import json
import os
import zipfile
from typing import Any, ClassVar, Dict, List, Optional, Union

import settings
from BaseClasses import Item, ItemClassification, Tutorial, MultiWorld
from worlds.AutoWorld import World, WebWorld
from worlds.LauncherComponents import components, Component, launch_subprocess, Type, icon_paths, SuffixIdentifier
from worlds.Files import APPlayerContainer

from .game_id import game_name
from .regions import create_regions, connect_entrances
from .items import (FFCCItem, FFCCItemData, ITEM_TABLE, FILLER_ITEM_TABLE, TRAP_ITEMS,
                    ITEM_TABLE_DESC, LOOKUP_ID_TO_NAME, item_name_groups,
                    PROGRESSIVE_ARTIFACT_NAME, PROGRESSIVE_ARTIFACT_CODE, _ARTIFACTS,
                    CYCLE_PLACEHOLDER_ITEM, YEAR_PLACEHOLDER_ITEM, PROGRESSIVE_EQUIPMENT_COUNT)
from .locations import (FFCCLocation, LOCATION_TABLE, MONSTER_LOCATION_TABLE, ENEMY_LOCATION_TABLE,
                        SHOP_LOCATION_TABLE, SHOP_LOCATIONS, SHOPS, location_groups)
from .options import FFCCGameOptions, FFCC_option_groups, SHORTCUT_OPTIONS
from .rules import (set_rules, set_location_rules, layout_is_beatable, first_year_dungeons,
                    stage_key, SPOT_AREA, excluded_count, make_hotspots, VANILLA_HOTSPOTS,
                    make_menus, VANILLA_MENUS)
from .regions import MYRRH_DUNGEONS, myrrh_location
from .bonus import make_bonus_pools
from .items import MYRRH_DROP, MYRRH_DROP_DATA, ARTIFACT_TYPES, UNUSED_ITEM_IDS, progressive_artifact_order

VERSION: tuple = (0, 2, 0)

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

icon_paths["FFCC_icon"] = f"ap:{__name__}/icons/FFCCAPIcon.png"

class FFCCTrackerPack(settings.FilePath):
    """The FFCC PopTracker pack (.zip). Universal Tracker shows its dungeon maps
    in the client. It asks for the file the first time if it isn't set."""
    required = False
    ut_dialog_name = "Select the FFCC PopTracker pack (.zip)"

class FFCCSettings(settings.Group):
    ut_pack_path: Union[FFCCTrackerPack, str] = FFCCTrackerPack()

# Universal Tracker's map page: the pack's location sections are named
# "<dungeon> - Chest <n>" / "Cycle <c>", the AP locations
# "<dungeon> - Cycle <c> - Chest <n>".
# Universal Tracker: every pin section of the PopTracker pack (chests,
# enemies, shop slots) -> its AP location, UT puts these pins on its map page and colours hinted ones.
TRACKER_LOCATION_IDS = {
    f"{data.region} - Chest {data.chest}/Cycle {data.cycle}": FFCCLocation.get_apid(data.code)
    for data in LOCATION_TABLE.values()
    if not data.is_event
}
try:
    from .tracker_names import PIN_SECTIONS
    TRACKER_LOCATION_IDS.update(PIN_SECTIONS)
except ImportError:
    pass

# Index of each dungeon's map in the pack's maps/maps.json.
TRACKER_MAP_INDEX = {
    "River Belle Path": 0, "Goblin Wall": 1, "The Mine of Cathuriges": 2, "The Mushroom Forest": 3,
    "Moschet Manor": 4, "Veo Lu Sluice": 5, "Daemon's Court": 6, "Selepation Cave": 7,
    "Conall Curach": 8, "Mount Vellenge": 9, "Lynari Desert": 10, "Tida": 11,
    "Mount Kilanda": 12, "Rebena Te Ra": 13,
}

def tracker_map_index(dungeon) -> int:
    """The map Universal Tracker opens for the dungeon the client says the player
    is in (outside dungeons it keeps River Belle Path's)."""
    return TRACKER_MAP_INDEX.get(dungeon or "", 0)

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
        for name, data in {**LOCATION_TABLE, **MONSTER_LOCATION_TABLE, **ENEMY_LOCATION_TABLE,
                           **SHOP_LOCATION_TABLE}.items()
        if data.code is not None
    }
    settings_key = "ffcc_options"
    settings: ClassVar[FFCCSettings]

    # Universal Tracker: the PopTracker pack gives the map page, and the client
    # stores the dungeon the player is in under ffcc_stage_<team>_<slot>, which
    # turns the map page to that dungeon.
    tracker_world: ClassVar = {
        "external_pack_key":       "ut_pack_path",
        "map_page_maps":           "maps/maps.json",
        "map_page_locations":      "locations/locations.json",
        "poptracker_name_mapping": TRACKER_LOCATION_IDS,
        "map_page_setting_key":    "ffcc_stage_{team}_{player}",
        "map_page_index":          tracker_map_index,
    }

    item_name_groups:    ClassVar[dict] = item_name_groups
    location_name_groups: ClassVar[dict] = location_groups

    def create_regions(self) -> None:
        create_regions(self.multiworld, self.player, self.options)

    # Dungeons the loading-zone shuffle moves (Mount Kilanda stays put, and Mount
    # Vellenge isn't a world-map spot of its own).
    SHUFFLED_SPOTS = [spot for spot in SPOT_AREA if spot != "Mount Kilanda"]

    VANILLA_GATES = [[2, 8, 4, 1], [1, 2, 8, 4], [4, 1, 2, 8], [8, 4, 1, 2]]

    @staticmethod
    def interpret_slot_data(slot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Universal Tracker builds the world again from the slot data. Hand it
        all of it, so generate_early can reuse the seed's world-map layout."""
        return slot_data

    # Options the logic or the item pool depend on. They go in the slot data, and
    # Universal Tracker gets them back from there: it rebuilds the world with
    # default options, so without this its logic would not match the seed's.
    LOGIC_OPTIONS = (
        "victory_goal", "progressive_artifacts", "progressive_equipment", "stage_keys",
        "goblin_wall_year_one", "shuffle_loading_zones", "randomize_miasma_streams",
        "cycle_location_checks", "year_location_checks", "rebena_te_ra_timed_chests",
        "progression_cycles", "include_traps", "monster_hunt_checks", "monster_hunt_bosses",
        "shop_checks", "hotspot_elements",
    )

    def generate_early(self) -> None:
        tracker = getattr(self.multiworld, "re_gen_passthrough", {}).get(self.game)
        if tracker is not None:
            for name in self.LOGIC_OPTIONS:
                if name in tracker and not isinstance(tracker[name], dict):
                    getattr(self.options, name).value = int(tracker[name])
            # seeds made before the year tables got their own keys kept the
            # hotspot table under the option's name (Match Miasma Streams)
            if isinstance(tracker.get("hotspot_elements"), dict):
                self.options.hotspot_elements.value = 1
                tracker = dict(tracker, hotspot_table=tracker["hotspot_elements"],
                               menu_table=tracker.get("menu_elements"))
        keys = bool(self.options.stage_keys)
        shuffle_zones = bool(self.options.shuffle_loading_zones)
        shuffle_gates = bool(self.options.randomize_miasma_streams)
        # Goblin Wall in Year 1 is forced on with either shuffle. A shuffled Miasma
        # Stream can ask for any element in Year 1, and Goblin Wall's Fire and Earth
        # keep every element within reach. With loading zones shuffled, the dungeon
        # placed on Goblin Wall's spot (often River Belle Path) must show up in Year 1.
        if shuffle_gates or shuffle_zones:
            self.options.goblin_wall_year_one.value = 1
        self.goblin_year1 = bool(self.options.goblin_wall_year_one)

        # Miasma Stream elements [year % 4 row][gate slot], the world-map
        # layout {spot: dungeon}, the hotspot elements {dungeon: [year row]}
        # and the stops' element menus {spot: [year row]}.
        # Shuffled ones are kept only if every year can be finished
        # (rules.layout_is_beatable).
        hotspot_mode = {1: "matched", 2: "shuffled"}.get(self.options.hotspot_elements.value)
        vanilla_plan = {spot: spot for spot in SPOT_AREA}
        self.gate_table, self.zone_plan = self.VANILLA_GATES, vanilla_plan
        self.hotspots = make_hotspots(hotspot_mode, self.gate_table, vanilla_plan, self.random)
        self.menus = make_menus(hotspot_mode is not None, self.gate_table)
        # Universal Tracker rebuilding a seed: use the layout the seed was made
        # with instead of rolling a new one.
        if tracker is not None:
            self.zone_plan = tracker.get("world_zones") or vanilla_plan
            self.gate_table = tracker.get("miasma_elements") or self.VANILLA_GATES
            self.hotspots = tracker.get("hotspot_table") or VANILLA_HOTSPOTS
            self.menus = tracker.get("menu_table") or VANILLA_MENUS
        for _ in range(0 if tracker is not None else 10000):
            gates = self.VANILLA_GATES
            if shuffle_gates:
                gates = [self.random.sample(row, 4) for row in self.VANILLA_GATES]
            plan = vanilla_plan
            if shuffle_zones:
                dungeons = self.SHUFFLED_SPOTS[:]
                self.random.shuffle(dungeons)
                plan = dict(vanilla_plan, **dict(zip(self.SHUFFLED_SPOTS, dungeons)))
            hotspots = make_hotspots(hotspot_mode, gates, plan, self.random)
            menus = make_menus(hotspot_mode is not None, gates)
            if layout_is_beatable(plan, gates, keys, self.goblin_year1, hotspots, menus):
                self.gate_table, self.zone_plan, self.hotspots, self.menus = gates, plan, hotspots, menus
                break

        # The order Progressive Artifacts give artifacts in (sent to the client).
        order = self.options.progressive_artifact_order
        if tracker is not None and tracker.get("progressive_artifact_order"):
            self.artifact_order = tracker["progressive_artifact_order"]
        elif order == order.option_random_order:
            self.artifact_order = progressive_artifact_order(random=self.random)
        else:
            first = {order.option_strength_first: "Strength", order.option_magic_first: "Magic",
                     order.option_defense_first: "Defense"}.get(order.value, "")
            self.artifact_order = progressive_artifact_order(first)

        # End-of-dungeon bonus pools, shuffled with Randomize Bonus Pools.
        if tracker is not None and tracker.get("bonus_pools"):
            self.bonus_pools = tracker["bonus_pools"]
        else:
            self.bonus_pools = make_bonus_pools(self.random if self.options.randomize_bonus_pools else None)

        if keys:
            # Year 1 needs three Myrrh trees: River Belle Path plus two dungeons
            # whose keys must turn up early, along with the Year 2 Key.
            early = self.multiworld.local_early_items[self.player]
            for dungeon in first_year_dungeons(self.zone_plan, self.gate_table, self.goblin_year1,
                                               self.hotspots, self.menus):
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
            "stage_keys", "progressive_equipment",
            # options the logic depends on, for Universal Tracker
            "goblin_wall_year_one", "shuffle_loading_zones", "randomize_miasma_streams",
            "cycle_location_checks", "year_location_checks", "rebena_te_ra_timed_chests",
            "progression_cycles", "magicite_needs_ring", "hide_collected_chests", "items_dropped_at_your_feet",
            "keep_picked_up_artifacts",
            "monster_hunt_checks", "monster_hunt_bosses", "shop_checks", "hotspot_elements",
            "mog_stamp_hints",
        )
        data["progressive_artifact_order"] = self.artifact_order
        data["bonus_pools"] = self.bonus_pools
        data["miasma_elements"] = self.gate_table
        # {spot: dungeon}, so the tracker knows which dungeons are across the river
        data["world_zones"] = self.zone_plan
        # the year tables (the option itself is "hotspot_elements")
        data["hotspot_table"] = self.hotspots
        data["menu_table"] = self.menus
        if self.options.mog_stamp_hints:
            data["stamp_hints"] = self.stamp_hints()

        # Locations whose item the patcher puts in the chest itself. The game
        # gives those on pickup, so the client doesn't give them again.
        data["physical_chest_ap_ids"] = [
            FFCCLocation.get_apid(LOCATION_TABLE[location.name].code)
            for location in self.multiworld.get_locations(self.player)
            if self._item_in_chest(location)
        ]
        if self.options.shop_checks:
            # what each shop sells, so the client can tell which shop is open
            data["shop_stock"] = self.shop_stock()
            # slots selling this player's own item: buying it gives it already
            data["physical_chest_ap_ids"] += [
                FFCCLocation.get_apid(SHOP_LOCATION_TABLE[location.name].code)
                for location in self.multiworld.get_locations(self.player)
                if location.name in SHOP_LOCATION_TABLE and self._shop_item_id(location)
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

    def stamp_hints(self) -> List[List[int]]:
        """[[player, location id]] of every place one of this player's
        progression items is, in any world, shuffled: the order Mog Stamps
        hint them in (the client skips the ones already found)."""
        spots = [[loc.player, loc.address] for loc in self.multiworld.get_locations()
                 if loc.item and loc.item.player == self.player and loc.item.advancement
                 and loc.address is not None]
        self.random.shuffle(spots)
        return spots

    # Item types a shop can sell. Anything else on a shop slot is sold as the
    # AP Item, and the client hands it over when it's bought.
    SHOP_ITEM_TYPES = ("Food", "Material", "Recipe", "Phoenix Down")
    AP_ITEM_ID = 0x162

    def _shop_item_id(self, location) -> Optional[int]:
        """The in-game ID of this shop slot's item, if the shop sells it itself."""
        item = location.item
        if item is None or item.player != self.player:
            return None
        item_data = ITEM_TABLE.get(item.name)
        if item_data is None or item_data.item_id is None or item_data.type not in self.SHOP_ITEM_TYPES:
            return None
        return item_data.item_id

    def shop_stock(self) -> Dict[str, List[int]]:
        """{shop key: the item ID on each slot}, the list the patcher writes."""
        stock = {key: [self.AP_ITEM_ID] * shop[4] for key, shop in SHOPS.items()}
        for name, (_, key, slot, _) in SHOP_LOCATIONS.items():
            location = self.multiworld.get_location(name, self.player)
            stock[key][slot - 1] = self._shop_item_id(location) or self.AP_ITEM_ID
        return stock

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
                "skip_mio_questions", "trap_visuals", "items_dropped_at_your_feet", "keep_picked_up_artifacts",
                "randomize_shops",
                "randomize_shop_prices", "randomize_bonus_pools",
                "chest_color_matches_contents", "hide_collected_chests", "magicite_needs_ring", "best_bonus_tier",
                "monster_hunt_checks", "shop_checks",
                *SHORTCUT_OPTIONS,
            ),
            # {spot: dungeon} for the patcher (same names the randomizer's JSON uses)
            "world_zones": self.zone_plan,
            # Miasma Stream table the logic used (only sent when shuffled)
            "miasma_elements": self.gate_table if self.options.randomize_miasma_streams else None,
            # {dungeon: 8 entries of 4 item ids}, written into newbattle.cfd
            "bonus_pools": self.bonus_pools,
            # {dungeon: 4 year rows of one element per hotspot}, only when changed
            "hotspot_elements": self.hotspots if self.options.hotspot_elements else None,
            # {stop: 4 year rows of its "Change element" choices}, with Hotspot Elements
            "menu_elements": self.menus if self.options.hotspot_elements else None,
            # {shop key: item ID per slot}, only with Shop Checks
            "shop_stock": self.shop_stock() if self.options.shop_checks else None,
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
        if data.type in ("Trap", "Progressive Artifact", "Placeholder", "Progressive Equipment"):
            continue  # handled separately below. Placeholders are pre-placed at event locs
        if data.type == "Stage Key" and not world.options.stage_keys:
            continue
        if data.type == "Artifact" and use_progressive:
            continue  # replaced by Progressive Artifacts below
        if data.code in UNUSED_ITEM_IDS:
            continue  # not a real item in the game
        pool.append(FFCCItem(name, world.player, data))

    # Add one Progressive Artifact per artifact when that option is on
    if use_progressive:
        pa_data = ITEM_TABLE[PROGRESSIVE_ARTIFACT_NAME]
        for _ in range(len(_ARTIFACTS)):
            pool.append(FFCCItem(PROGRESSIVE_ARTIFACT_NAME, world.player, pa_data))

    # Progressive equipment: one copy per upgrade step
    if world.options.progressive_equipment:
        for name, count in PROGRESSIVE_EQUIPMENT_COUNT.items():
            for _ in range(count):
                pool.append(FFCCItem(name, world.player, ITEM_TABLE[name]))

    # With Monster Hunt checks there are far fewer locations than items: keep
    # every progression item, then progressive equipment, then as many other
    # useful items as fit (picked at random), leaving room for the filler the
    # excluded locations need.
    locations = len(world.multiworld.get_unfilled_locations(world.player))
    if len(pool) > locations:
        room = locations - excluded_count(world.options)
        progression = [item for item in pool if item.advancement]
        equipment = [item for item in pool if not item.advancement and item.name in PROGRESSIVE_EQUIPMENT_COUNT]
        useful = [item for item in pool if item.useful and not item.advancement
                  and item.name not in PROGRESSIVE_EQUIPMENT_COUNT]
        world.random.shuffle(useful)
        pool = (progression + equipment + useful)[:max(room, len(progression))]

    # Pad remaining slots with weighted filler (traps if enabled, food/phoenix otherwise)
    unfilled = locations - len(pool)
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
