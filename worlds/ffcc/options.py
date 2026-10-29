from dataclasses import dataclass
from Options import Toggle, Range, Choice, PerGameCommonOptions, DefaultOnToggle, DeathLink, OptionGroup


class VictoryGoal(Choice):
    """What is required to send the victory condition.
    All Myrrh: collect all 13 Myrrh drops.
    Final Boss: defeat the final boss (Mount Vellenge).
    Monster Hunt: defeat at least one of every enemy type (bosses too with
    "Monster Hunt Bosses")."""
    display_name = "Victory Goal"
    option_all_myrrh    = 0
    option_final_boss   = 1
    option_monster_hunt = 2
    default = 0


class ProgressiveArtifacts(Toggle):
    """Replace the 73 distinct artifact items with 73 copies of Progressive Artifact.
    Each copy received grants the next artifact in sequence rather than a specific one."""
    display_name = "Progressive Artifacts"


class ProgressiveArtifactOrder(Choice):
    """The order Progressive Artifacts are given in. Every artifact is still
    given once. This only picks which come first.
    Game Order: the game's own artifact order (Strength, Magic, Defense, then the rest).
    Strength First / Magic First / Defense First: that stat's artifacts first,
    then the rest in game order.
    Random Order: a random order.
    Only used with Progressive Artifacts."""
    display_name = "Progressive Artifact Order"
    option_game_order     = 0
    option_strength_first = 1
    option_magic_first    = 2
    option_defense_first  = 3
    option_random_order   = 4
    default = 0


class ProgressionCycles(Range):
    """How many cycles of each dungeon can hold progression and useful items.
    Chests in later cycles are still checks, but they only hold filler, so you
    never need to play those cycles. 3 = every cycle."""
    display_name = "Progression Cycles"
    range_start = 1
    range_end = 3
    default = 3


class CycleLocationChecks(Toggle):
    """When enabled, reaching Cycle 2 or 3 in a dungeon counts as a location check
    and gives a random item reward from the pool.
    When disabled, cycle advancement still auto-tracks on the map but gives no item reward
    and adds no extra locations to the multiworld."""
    display_name = "Cycle Location Checks"


class YearLocationChecks(Toggle):
    """When enabled, each year advancement counts as a location check with a random item reward.
    When disabled, year advancement still auto-tracks on the map tracker but gives no item reward."""
    display_name = "Year Location Checks"


class MogStampHints(DefaultOnToggle):
    """Every new Mog Stamp from a Moogle Nest hints where one of your
    progression items is (in your world or another), one you haven't found
    yet. The client sends the hint, so keep it connected."""
    display_name = "Mog Stamp Hints"


class ShopChecks(Toggle):
    """The first purchase of each slot in the towns' shops is a check (94
    slots in 8 shops, from Marr's Pass in Year 1 to Leuda in Year 5). A slot
    sells your own item if it's one a shop can sell (food, materials,
    recipes, Phoenix Downs), otherwise an "AP Item" for 10 gil. Every shop
    sells the same thing all game, instead of growing its stock with the
    story. Tipa's shop (only there with a Merchant family), the Selkie
    Peddler and the blacksmiths' crafting aren't checks. Replaces
    "Randomize Shops"."""
    display_name = "Shop Checks"


class MonsterHuntChecks(Choice):
    """Make defeating enemies the checks instead of chests.
    Off: chests are the checks.
    Enemy Types: defeating the first enemy of each type is a check (about 100
    enemy types, and enemies that only appear with more than one player aren't
    included).
    Every Enemy: defeating each enemy in each dungeon is a check (about 960,
    and an enemy that appears in several cycles is one check)."""
    display_name = "Monster Hunt Checks"
    option_off = 0
    option_enemy_types = 1
    option_every_enemy = 2
    alias_false = 0
    alias_true = 1
    default = 0


class MonsterHuntBosses(DefaultOnToggle):
    """The dungeon bosses are part of the Monster Hunt: each boss is a check
    with "Monster Hunt Checks" and has to be defeated for the "Monster Hunt"
    goal."""
    display_name = "Monster Hunt Bosses"


class StageKeys(Toggle):
    """Every dungeon except River Belle Path needs its own key to enter.
    The 13 keys are shuffled into the item pool. The element menus on the
    world map (changing the chalice's element at a stop) work without the key
    and without clearing the stage first, so the element a Miasma Stream asks
    for can always be picked up without a key."""
    display_name = "Stage Keys"


class ProgressiveEquipment(Toggle):
    """Adds Progressive Weapon, Progressive Armor and Progressive Tribal Gear
    (shield, gauntlets, helm or belt) to the item pool. Each one puts the next
    piece for your tribe in your bag, so equip it from the menu. It needs a
    free bag slot so if the bag is full it arrives once there is room."""
    display_name = "Progressive Equipment"


class ShuffleLoadingZones(Toggle):
    """Shuffle which dungeon each world-map spot leads to (12 dungeons - Mount Kilanda
    and Mount Vellenge stay where they are). Each spot keeps its own Miasma Stream and
    shows the building of the dungeon it now leads to. Only layouts that can be
    finished year by year are used. Veo Lu Sluice always stays on this side of the
    Jegon River (Tipa Peninsula, Iron Mine Downs, Vale of Alfitaria or Veo Lu), so
    it can be healed when the river dries up in Year 5. Also opens Goblin Wall's
    spot in Year 1."""
    display_name = "Shuffle Loading Zones"


class RebenaTeRaTimedChests(Toggle):
    """Rebena Te Ra chests 6 and 9 count as in logic. Reaching them alone needs
    painful timing (Mog casting the spell for you), so when this is off they can
    only hold filler items."""
    display_name = "Rebena Te Ra Timed Chests"


# Dungeon shortcuts: each one only makes that dungeon quicker. The logic is unchanged.
class RiverBellePathBridges(Toggle):
    """River Belle Path's two drawbridges start lowered, without standing on the floor switches."""
    display_name = "River Belle Path Bridges Lowered"


class GoblinWallGates(Toggle):
    """Every gate in Goblin Wall starts open, without hitting its switch sphere."""
    display_name = "Goblin Wall Gates Open"


class MineBoxes(Toggle):
    """The box piles in the Mine of Cathuriges that the mine cart breaks are already gone."""
    display_name = "Mine of Cathuriges Boxes Cleared"


class TidaWebs(Toggle):
    """The spider webs in Tida are already burnt away. Tida still needs the
    Ring of Fire in logic."""
    display_name = "Tida Webs Cleared"


class MoschetManorDoors(Toggle):
    """Moschet Manor's tribe switches press themselves when you enter a room,
    so every door opens without waiting for your tribe's icon."""
    display_name = "Moschet Manor Doors Open"


class SelepationCaveElevators(Toggle):
    """Selepation Cave's three elevators start at the bottom."""
    display_name = "Selepation Cave Elevators Lowered"


class ConallCurachLogBridges(Toggle):
    """Conall Curach has all its log bridges without bombing the log bridges in
    Daemon's Court first. Chests 12 and 21 still need Daemon's Court in logic."""
    display_name = "Conall Curach Log Bridges"


class RebenaTeRaGates(Toggle):
    """The gates and barriers Rebena Te Ra's switches control start open. The
    item pedestals are unchanged. Rebena Te Ra still needs all four rings in logic."""
    display_name = "Rebena Te Ra Gates Open"


class UnknownElementPuzzleSolved(Toggle):
    """Lynari Desert's Unknown element puzzle starts solved, so its hotspot gives
    Unknown right away, and the element obstacles in its second area are gone."""
    display_name = "Unknown Element Puzzle Solved"


class GoblinWallYearOne(DefaultOnToggle):
    """Goblin Wall's spot on the world map is open from Year 1 instead of Year 2.
    Always on when Shuffle Loading Zones or Randomize Miasma Streams is on."""
    display_name = "Goblin Wall in Year 1"


class RandomizeMiasmaStreams(Toggle):
    """Shuffle which element each Miasma Stream asks for, every year. Also opens
    Goblin Wall in Year 1, so every element can be found from the start."""
    display_name = "Randomize Miasma Streams"


class HotspotElements(Choice):
    """Change the elements each dungeon's hotspots (the elemental pools)
    give, every year. A dungeon keeps its usual number of different elements,
    and its name bubble and "Change element" menu on the world map show the
    year's ones. The pools keep their look, so check the chalice after
    touching one.
    Off: every hotspot gives its usual element.
    Match Miasma Streams: each year, the dungeons and menus on each side of the
    world share out the elements its Miasma Streams ask for, on and back.
    Shuffled: random elements each year (seeds are only kept if every year can
    still be finished). The menus still match the streams.
    Lynari Desert's Unknown pool always gives Unknown."""
    display_name = "Hotspot Elements"
    option_off = 0
    option_match_miasma_streams = 1
    option_shuffled = 2
    default = 0


class MogNeverTired(DefaultOnToggle):
    """Mog never gets tired while carrying the chalice."""
    display_name = "Mog Never Tired"


class SkipIntroCutscene(DefaultOnToggle):
    """Skip the opening cutscene of a new game."""
    display_name = "Skip Intro Cutscene"


class SkipMioQuestions(Toggle):
    """Skip Mio's questions at the start of a new game."""
    display_name = "Skip Mio's Questions"


class ChestColorMatchesContents(DefaultOnToggle):
    """Chests holding a progression or useful item, for any player, are gold.
    Chests holding filler look normal."""
    display_name = "Chest Color Matches Contents"


class HideCollectedChests(DefaultOnToggle):
    """A chest doesn't appear once its check for the dungeon's current cycle is
    done, so only chests with something left to find show up. Each cycle has
    its own checks, so a chest comes back in a cycle where it hasn't been
    checked yet. Just in case the player wants to keep farming the cycles chests for items."""
    display_name = "Hide Collected Chests"


class MagiciteNeedsRing(Toggle):
    """Fire, Blizzard, Thunder, Cure and Life magicite can only be put in your
    command list once you have the matching ring (Ring of Fire, Blizzard,
    Thunder, Cure or Life). Other magicite works as usual. The Ring of Cure is
    an artifact, so Cure stays unavailable until you find it."""
    display_name = "Magicite Needs Its Ring"


class BestBonusTier(DefaultOnToggle):
    """The end-of-dungeon bonus always gives the best reward tier your score
    reached, instead of a random tier up to it."""
    display_name = "Always Best Bonus Tier"


class TrapVisuals(DefaultOnToggle):
    """Status traps show the game's own effects (ice, flames, poison, paralysis, slow)."""
    display_name = "Trap Visuals"


class ItemsDroppedAtYourFeet(DefaultOnToggle):
    """Items you receive are put on the ground in front of you instead of in
    your bag, so you pick up only what you want. Materials, food, recipes,
    magicite and Phoenix Downs are dropped. Progressive Equipment goes in your
    bag (equipment can't lie on the ground), and artifacts, stage keys and
    Spell Rings still go straight to you. An item counts as
    received once it is on the ground: one you leave behind can be dropped
    again with the client's /resend command."""
    display_name = "Items Dropped At Your Feet"


class KeepPickedUpArtifacts(DefaultOnToggle):
    """Artifacts you pick up in a dungeon go straight into your artifact list
    and are kept, instead of only lasting until the end of the dungeon (where
    you normally keep just one). With "Items Dropped At Your Feet", artifacts
    you receive are then dropped at your feet too (stage keys and Spell Rings
    still go straight to you)."""
    display_name = "Keep Picked-Up Artifacts"


class RandomizeShops(Toggle):
    """Shuffle what each shop sells. Does not currently have location checks so may break things currently"""
    display_name = "Randomize Shops"


class RandomizeShopPrices(Toggle):
    """Shuffle shop prices."""
    display_name = "Randomize Shop Prices"


class RandomizeBonusPools(Toggle):
    """Shuffle the end-of-dungeon bonus rewards. The trackers show each
    dungeon's rewards either way."""
    display_name = "Randomize Bonus Pools"


class IncludeTraps(DefaultOnToggle):
    """Add trap items to the multiworld item pool."""
    display_name = "Include Traps"


class FrozenTrapWeight(Range):
    """Relative weight for the Frozen Trap in the filler pool. 0 = disabled."""
    display_name = "Frozen Trap Weight"
    range_start = 0
    range_end = 10
    default = 2


class BurnedTrapWeight(Range):
    """Relative weight for the Burned Trap. 0 = disabled."""
    display_name = "Burned Trap Weight"
    range_start = 0
    range_end = 10
    default = 2


class SlowedTrapWeight(Range):
    """Relative weight for the Slowed Trap. 0 = disabled."""
    display_name = "Slowed Trap Weight"
    range_start = 0
    range_end = 10
    default = 2


class PoisonedTrapWeight(Range):
    """Relative weight for the Poisoned Trap. 0 = disabled."""
    display_name = "Poisoned Trap Weight"
    range_start = 0
    range_end = 10
    default = 1


class ChaliceElementTrapWeight(Range):
    """Relative weight for the Chalice Element Trap (randomizes chalice element). 0 = disabled."""
    display_name = "Chalice Element Trap Weight"
    range_start = 0
    range_end = 10
    default = 0


class BonusSetTrapWeight(Range):
    """Relative weight for the Bonus Set Reset Trap (changes dungeon bonus). 0 = disabled."""
    display_name = "Bonus Set Reset Trap Weight"
    range_start = 0
    range_end = 10
    default = 0


class FoodPreferenceTrapWeight(Range):
    """Relative weight for the Food Preference Trap (scrambles food favorites). 0 = disabled."""
    display_name = "Food Preference Trap Weight"
    range_start = 0
    range_end = 10
    default = 1


@dataclass
class FFCCGameOptions(PerGameCommonOptions):
    victory_goal:                VictoryGoal
    progressive_artifacts:       ProgressiveArtifacts
    progressive_artifact_order:  ProgressiveArtifactOrder
    progressive_equipment:       ProgressiveEquipment
    progression_cycles:          ProgressionCycles
    cycle_location_checks:       CycleLocationChecks
    year_location_checks:        YearLocationChecks
    shop_checks:                 ShopChecks
    mog_stamp_hints:             MogStampHints
    monster_hunt_checks:         MonsterHuntChecks
    monster_hunt_bosses:         MonsterHuntBosses
    stage_keys:                  StageKeys
    shuffle_loading_zones:       ShuffleLoadingZones
    randomize_miasma_streams:    RandomizeMiasmaStreams
    hotspot_elements:            HotspotElements
    goblin_wall_year_one:        GoblinWallYearOne
    rebena_te_ra_timed_chests:   RebenaTeRaTimedChests
    mog_never_tired:             MogNeverTired
    skip_intro_cutscene:         SkipIntroCutscene
    skip_mio_questions:          SkipMioQuestions
    trap_visuals:                TrapVisuals
    items_dropped_at_your_feet:  ItemsDroppedAtYourFeet
    keep_picked_up_artifacts:    KeepPickedUpArtifacts
    chest_color_matches_contents: ChestColorMatchesContents
    hide_collected_chests:       HideCollectedChests
    magicite_needs_ring:         MagiciteNeedsRing
    best_bonus_tier:             BestBonusTier
    river_belle_path_bridges:    RiverBellePathBridges
    goblin_wall_gates:           GoblinWallGates
    mine_boxes:                  MineBoxes
    tida_webs:                   TidaWebs
    moschet_manor_doors:         MoschetManorDoors
    selepation_cave_elevators:   SelepationCaveElevators
    conall_curach_log_bridges:   ConallCurachLogBridges
    rebena_te_ra_gates:          RebenaTeRaGates
    lynari_desert_unknown:       UnknownElementPuzzleSolved
    randomize_shops:             RandomizeShops
    randomize_shop_prices:       RandomizeShopPrices
    randomize_bonus_pools:       RandomizeBonusPools
    include_traps:               IncludeTraps
    frozen_trap_weight:          FrozenTrapWeight
    burned_trap_weight:          BurnedTrapWeight
    slowed_trap_weight:          SlowedTrapWeight
    poisoned_trap_weight:        PoisonedTrapWeight
    chalice_element_trap_weight: ChaliceElementTrapWeight
    bonus_set_trap_weight:       BonusSetTrapWeight
    food_preference_trap_weight: FoodPreferenceTrapWeight
    death_link:                  DeathLink


FFCC_option_groups = [
    OptionGroup("General", [VictoryGoal, ProgressiveArtifacts, ProgressiveArtifactOrder, ProgressiveEquipment,
                            ProgressionCycles, CycleLocationChecks, YearLocationChecks, ShopChecks,
                            MogStampHints]),
    OptionGroup("Monster Hunt", [MonsterHuntChecks, MonsterHuntBosses]),
    OptionGroup("Progression", [StageKeys, ShuffleLoadingZones, RandomizeMiasmaStreams, HotspotElements, GoblinWallYearOne,
                                RebenaTeRaTimedChests]),
    OptionGroup("Gameplay", [ItemsDroppedAtYourFeet, KeepPickedUpArtifacts, MogNeverTired, SkipIntroCutscene, SkipMioQuestions, TrapVisuals,
                             ChestColorMatchesContents, HideCollectedChests, MagiciteNeedsRing, BestBonusTier,
                             RandomizeShops, RandomizeShopPrices, RandomizeBonusPools]),
    OptionGroup("Dungeon Shortcuts", [RiverBellePathBridges, GoblinWallGates, MineBoxes, TidaWebs, MoschetManorDoors, SelepationCaveElevators, ConallCurachLogBridges, RebenaTeRaGates, UnknownElementPuzzleSolved]),
    OptionGroup("Traps", [
        IncludeTraps, FrozenTrapWeight, BurnedTrapWeight, SlowedTrapWeight,
        PoisonedTrapWeight, ChaliceElementTrapWeight, BonusSetTrapWeight, FoodPreferenceTrapWeight,
    ]),
    OptionGroup("Misc", [DeathLink]),
]

# Option keys of the dungeon shortcuts. The patcher's shortcuts.py uses the same keys.
SHORTCUT_OPTIONS = (
    "river_belle_path_bridges",
    "goblin_wall_gates",
    "mine_boxes",
    "tida_webs",
    "moschet_manor_doors",
    "selepation_cave_elevators",
    "conall_curach_log_bridges",
    "rebena_te_ra_gates",
    "lynari_desert_unknown",
)
