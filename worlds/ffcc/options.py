from dataclasses import dataclass
from Options import Toggle, Range, Choice, PerGameCommonOptions, DefaultOnToggle, DeathLink, OptionGroup


class VictoryGoal(Choice):
    """What is required to send the victory condition.

    - **All Myrrh:** collect all 13 Myrrh drops.
    - **Final Boss:** defeat the final boss (Mount Vellenge).
    - **Monster Hunt:** defeat at least one of every enemy type (bosses too with
      "Monster Hunt Bosses").
    - **Mog Stamps:** collect all 23 Mog Stamps from the Moogle Nests.
    - **Mog Grooming:** dye or trim a Moogle's fur in any Moogle Nest (see "Mog
      Grooming Goal" and "Mog Grooming Percent")."""
    display_name = "Victory Goal"
    option_all_myrrh = 0
    option_final_boss = 1
    option_monster_hunt = 2
    option_mog_stamps = 3
    option_mog_grooming = 4
    default = 0


class MogGroomingGoal(Choice):
    """With the Mog Grooming goal, what you do to a Moogle in a Moogle Nest.

    - **dye:** dye at least Mog Grooming Percent of its fur, in any colours
    - **trim:** cut at least Mog Grooming Percent of its fur
    - **both:** both of these"""
    display_name = "Mog Grooming Goal"
    option_dye = 0
    option_trim = 1
    option_both = 2
    default = 0


class MogGroomingPercent(Range):
    """With the Mog Grooming goal, how much of the Moogle's fur has to be dyed
    or cut. A few spots can't be reached, so it goes up to 95."""
    display_name = "Mog Grooming Percent"
    range_start = 10
    range_end = 95
    default = 50


class MogGroomingChecks(Choice):
    """Checks for grooming a Moogle in a Moogle Nest.

    - **radars:** dye the Moogle so one colour shows most, in the game's rings and
      lines (each colour turns on a GBA radar): Red (Monster Radar), Green
      (Score Radar), Blue (Treasure Radar)
    - **milestones:** dye 25%, 50% and 75% of its fur, and cut 25%, 50% and 75%
    - **all:** both"""
    display_name = "Mog Grooming Checks"
    option_off = 0
    option_radars = 1
    option_milestones = 2
    option_all = 3
    default = 0


class MogGroomingOnly(Toggle):
    """A seed of only Mog grooming: no chests or other checks of this world,
    just the Mog Grooming Checks (all of them) and the Mog Grooming goal. The
    grooming tools are items, and you start with one dye."""
    display_name = "Mog Grooming Only"


class GroomingTools(Choice):
    """The Moogle's grooming tools are items: Red Dye, Blue Dye, Green Dye,
    Mog Soap and Mog Scissors (the game's Red, Blue, Green, Wash and Trim).
    In a Moogle Nest a tool does nothing until you find it.

    - **off:** the tools work from the start
    - **with_goal:** only with the Mog Grooming goal
    - **always:** in every seed"""
    display_name = "Grooming Tools"
    option_off = 0
    option_with_goal = 1
    option_always = 2
    default = 1


class ProgressiveArtifacts(Toggle):
    """Replace the 73 distinct artifact items with 73 copies of Progressive Artifact.
    Each copy received grants the next artifact in sequence rather than a specific one."""
    display_name = "Progressive Artifacts"


class ProgressiveArtifactOrder(Choice):
    """The order Progressive Artifacts are given in. Every artifact is still
    given once. This only picks which come first. Only used with Progressive
    Artifacts.

    - **Game Order:** the game's own artifact order (Strength, Magic, Defense,
      then the rest).
    - **Strength First**, **Magic First**, **Defense First:** that stat's
      artifacts first, then the rest in game order.
    - **Random Order:** a random order."""
    display_name = "Progressive Artifact Order"
    option_game_order = 0
    option_strength_first = 1
    option_magic_first = 2
    option_defense_first = 3
    option_random_order = 4
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

    - **Off:** chests are the checks.
    - **Enemy Types:** defeating the first enemy of each type is a check (about 100
      enemy types, and enemies that only appear with more than one player aren't
      included).
    - **Every Enemy:** defeating each enemy in each dungeon is a check (about 950,
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
    piece for each player's tribe in that player's bag, so equip it from the
    menu. It needs a free bag slot, so a player whose bag is full gets it
    once there is room."""
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


class LynariDesertNorthExit(Toggle):
    """Lynari Desert's first area gets a quicksand pit at its northern dead
    end, where the two rock pillars were, that drops you into the second
    area, like the pit near the Unknown element hotspot. The bushes in front
    of it can be walked through. The logic doesn't change."""
    display_name = "Lynari Desert North Exit"


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

    - **Off:** every hotspot gives its usual element.
    - **Match Miasma Streams:** each year, the dungeons and menus on each side of the
      world share out the elements its Miasma Streams ask for, on and back.
    - **Shuffled:** random elements each year (seeds are only kept if every year can
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


class ShowEnemyHealth(Choice):
    """Shows each enemy's health above it (bosses keep their own gauge):

    - **text:** its current and max HP ("12/20")
    - **bar:** a small red health bar
    - **both:** the bar with the numbers above it"""
    display_name = "Show Enemy Health"
    option_off = 0
    option_text = 1
    option_bar = 2
    option_both = 3
    alias_true = 2
    alias_false = 0
    default = 0


class ShowPlayTimer(Choice):
    """Shows a timer in the top-right corner of the screen once you choose
    New Game or load a save (not on the title screen or the file menus). It
    only counts while you play: it stops while the game is paused, in a menu
    or loading, and keeps going through cutscenes and talking.

    - **play_time:** the save's play time
    - **speedrun_automatic:** a speedrun timer that starts at 0 when you choose
      New Game (so the intro is timed) or load a save, and stops on the final
      blow to the last boss
    - **speedrun_manual:** a speedrun timer you start, stop and reset yourself

    In both speedrun modes, hold L + R + Z and press D-pad Up to pause or
    resume the timer, Down to reset it to 0, Left to hide or show it."""
    display_name = "Show Play Timer"
    option_off = 0
    option_play_time = 1
    option_speedrun_automatic = 2
    option_speedrun_manual = 3
    alias_speedrun = 2
    alias_true = 2
    alias_false = 0
    default = 0


class ItemMessages(DefaultOnToggle):
    """Items you receive, and items of yours you find for other players, are
    named on the game's screen ("Received Ring of Fire from Alice"), a few
    lines at a time at the bottom."""
    display_name = "Show Item Messages"


class FreeCureMagicite(Toggle):
    """Each time you enter a dungeon every player gets a Stone of Cure (in the
    bag, or at controller 1's feet with "Items Dropped At Your Feet"). Magicite is lost when
    you leave a dungeon, so that's one per visit. With "Magicite Needs Its
    Ring" it can only be set once you have the Ring of Cure."""
    display_name = "Free Cure Magicite"


class ExtraSpellRings(Toggle):
    """Adds five new rings to the game and the item pool: Ring of Gravity,
    Holy, Slow, Stop and Haste. Like the other Rings, each one casts its
    spell from the command list without magicite. They're useful items only and
    the logic never asks for them."""
    display_name = "Extra Spell Rings"


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
    magicite and Phoenix Downs are dropped. Artifacts are dropped too when
    "Keep Picked-Up Artifacts" is on (it is by default), and otherwise they go
    straight into your artifact list. Progressive Equipment goes in your bag,
    because equipment can't lie on the ground. Stage keys and Spell Rings
    always go straight to you. An item counts as received once it is on the
    ground, so if you leave one behind, the client's /resend command can drop
    it again. Items despawn after 3 minutes, so make sure to pick them up!"""
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


class GilWeight(Range):
    """Adds gil (100, 500 and 1000 Gil) to the item pool's filler. Each
    amount gets this weight next to the other filler items (about 150 kinds,
    weight 1 each), so 5 makes gil a few percent of the filler. Received gil
    goes to the first player. 0 = no gil."""
    display_name = "Gil Weight"
    range_start = 0
    range_end = 20
    default = 0


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


class CommandSlotTrapWeight(Range):
    """Relative weight for the Command Slot Trap: one random command (not
    Attack or Defend) is taken off your command list. The item stays in
    your bag, so you can set it again from the menu. 0 = disabled."""
    display_name = "Command Slot Trap Weight"
    range_start = 0
    range_end = 10
    default = 1


class StartingStats(Choice):
    """Change each tribe's starting Strength, Magic and Defense. Artifacts and
    equipment add to them as usual. Male and female characters of a tribe get the
    same stats, and so does every player of that tribe in co-op.

    - **Off:** the game's own stats.
    - **Shuffle Tribes:** each tribe gets another tribe's stats (a Yuke might fight
      like a Lilty).
    - **Same Total:** each tribe keeps its total but the points are spread at random,
      between "Starting Stats Minimum" and "Starting Stats Maximum".
    - **Fully Random:** each stat is a random number between the minimum and maximum.

    The game's own stats (Strength / Magic / Defense): Clavat 6 / 13 / 7, Lilty
    8 / 10 / 8, Yuke 5 / 15 / 5, Selkie 7 / 12 / 6."""
    display_name = "Starting Stats"
    option_off = 0
    option_shuffle_tribes = 1
    option_same_total = 2
    option_fully_random = 3
    default = 0


class StartingStatsMinimum(Range):
    """The lowest a starting stat can be with "Starting Stats" set to Same Total or
    Fully Random."""
    display_name = "Starting Stats Minimum"
    range_start = 1
    range_end = 20
    default = 4


class StartingStatsMaximum(Range):
    """The highest a starting stat can be with "Starting Stats" set to Same Total or
    Fully Random."""
    display_name = "Starting Stats Maximum"
    range_start = 5
    range_end = 30
    default = 16


class StartingHearts(Range):
    """How many hearts every character starts with (the game's own is 4). Heart
    artifacts still add one each, up to the game's limit of 8."""
    display_name = "Starting Hearts"
    range_start = 2
    range_end = 8
    default = 4


@dataclass
class FFCCGameOptions(PerGameCommonOptions):
    victory_goal:                VictoryGoal
    mog_grooming_goal:           MogGroomingGoal
    mog_grooming_percent:        MogGroomingPercent
    grooming_tools:              GroomingTools
    mog_grooming_checks:         MogGroomingChecks
    mog_grooming_only:           MogGroomingOnly
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
    free_cure_magicite:          FreeCureMagicite
    show_enemy_health:           ShowEnemyHealth
    show_play_timer:             ShowPlayTimer
    item_messages:               ItemMessages
    extra_spell_rings:           ExtraSpellRings
    best_bonus_tier:             BestBonusTier
    starting_stats:              StartingStats
    starting_stats_minimum:      StartingStatsMinimum
    starting_stats_maximum:      StartingStatsMaximum
    starting_hearts:             StartingHearts
    river_belle_path_bridges:    RiverBellePathBridges
    goblin_wall_gates:           GoblinWallGates
    mine_boxes:                  MineBoxes
    tida_webs:                   TidaWebs
    moschet_manor_doors:         MoschetManorDoors
    selepation_cave_elevators:   SelepationCaveElevators
    conall_curach_log_bridges:   ConallCurachLogBridges
    rebena_te_ra_gates:          RebenaTeRaGates
    lynari_desert_unknown:       UnknownElementPuzzleSolved
    lynari_desert_north_exit:    LynariDesertNorthExit
    randomize_shops:             RandomizeShops
    randomize_shop_prices:       RandomizeShopPrices
    randomize_bonus_pools:       RandomizeBonusPools
    gil_weight:                  GilWeight
    include_traps:               IncludeTraps
    frozen_trap_weight:          FrozenTrapWeight
    burned_trap_weight:          BurnedTrapWeight
    slowed_trap_weight:          SlowedTrapWeight
    poisoned_trap_weight:        PoisonedTrapWeight
    chalice_element_trap_weight: ChaliceElementTrapWeight
    bonus_set_trap_weight:       BonusSetTrapWeight
    food_preference_trap_weight: FoodPreferenceTrapWeight
    command_slot_trap_weight:    CommandSlotTrapWeight
    death_link:                  DeathLink


FFCC_option_groups = [
    OptionGroup("General", [VictoryGoal, ProgressiveArtifacts, ProgressiveArtifactOrder, ProgressiveEquipment,
                            ProgressionCycles, CycleLocationChecks, YearLocationChecks, ShopChecks,
                            MogStampHints]),
    OptionGroup("Monster Hunt", [MonsterHuntChecks, MonsterHuntBosses]),
    OptionGroup("Mog Grooming", [MogGroomingGoal, MogGroomingPercent, GroomingTools, MogGroomingChecks,
                                 MogGroomingOnly]),
    OptionGroup("Progression", [StageKeys, ShuffleLoadingZones, RandomizeMiasmaStreams, HotspotElements,
                                GoblinWallYearOne, RebenaTeRaTimedChests]),
    OptionGroup("Gameplay", [ItemsDroppedAtYourFeet, KeepPickedUpArtifacts, MogNeverTired, SkipIntroCutscene,
                             SkipMioQuestions, TrapVisuals, ChestColorMatchesContents, HideCollectedChests,
                             MagiciteNeedsRing, FreeCureMagicite, ShowEnemyHealth, ShowPlayTimer, ItemMessages,
                             ExtraSpellRings, BestBonusTier, RandomizeShops, RandomizeShopPrices, RandomizeBonusPools,
                             GilWeight]),
    OptionGroup("Characters", [StartingStats, StartingStatsMinimum, StartingStatsMaximum, StartingHearts]),
    OptionGroup("Dungeon Shortcuts", [RiverBellePathBridges, GoblinWallGates, MineBoxes, TidaWebs, MoschetManorDoors,
                                      SelepationCaveElevators, ConallCurachLogBridges, RebenaTeRaGates,
                                      UnknownElementPuzzleSolved, LynariDesertNorthExit]),
    OptionGroup("Traps", [
        IncludeTraps, FrozenTrapWeight, BurnedTrapWeight, SlowedTrapWeight,
        PoisonedTrapWeight, ChaliceElementTrapWeight, BonusSetTrapWeight, FoodPreferenceTrapWeight,
        CommandSlotTrapWeight,
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
    "lynari_desert_north_exit",
)


def grooming_tools_on(options: "FFCCGameOptions") -> bool:
    """True if the grooming tools are items in this seed."""
    tools = options.grooming_tools
    return tools == tools.option_always or (
        tools == tools.option_with_goal and options.victory_goal == VictoryGoal.option_mog_grooming)


def grooming_location_kinds(options: "FFCCGameOptions") -> set[str]:
    """The kinds of Mog grooming checks in this seed ("radar", "dyed", "cut")."""
    checks = options.mog_grooming_checks
    kinds = set()
    if checks in (checks.option_radars, checks.option_all):
        kinds.add("radar")
    if checks in (checks.option_milestones, checks.option_all):
        kinds |= {"dyed", "cut"}
    return kinds
