from dataclasses import dataclass
from Options import Toggle, Range, Choice, PerGameCommonOptions, DefaultOnToggle, DeathLink, OptionGroup


class VictoryGoal(Choice):
    """What is required to send the victory condition."""
    display_name = "Victory Goal"
    option_all_myrrh  = 0   # collect all 13 Myrrh drops (normal ending)
    option_final_boss = 1   # defeat the final boss (Mount Vellenge)
    default = 0


class ProgressiveArtifacts(Toggle):
    """Replace the 73 distinct artifact items with 73 copies of Progressive Artifact.
    Each copy received grants the next artifact in sequence rather than a specific one."""
    display_name = "Progressive Artifacts"


class CycleLocationChecks(DefaultOnToggle):
    """When enabled, reaching Cycle 2 or 3 in a dungeon counts as a location check
    and gives a random item reward from the pool.
    When disabled, cycle advancement still auto-tracks on the map but gives no item reward
    and adds no extra locations to the multiworld."""
    display_name = "Cycle Location Checks"


class YearLocationChecks(DefaultOnToggle):
    """When enabled, each year advancement counts as a location check with a random item reward.
    When disabled, year advancement still auto-tracks on the map tracker but gives no item reward."""
    display_name = "Year Location Checks"


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
    default = 1


class BonusSetTrapWeight(Range):
    """Relative weight for the Bonus Set Reset Trap (changes dungeon bonus). 0 = disabled."""
    display_name = "Bonus Set Reset Trap Weight"
    range_start = 0
    range_end = 10
    default = 1


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
    cycle_location_checks:       CycleLocationChecks
    year_location_checks:        YearLocationChecks
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
    OptionGroup("General", [VictoryGoal, ProgressiveArtifacts, CycleLocationChecks, YearLocationChecks]),
    OptionGroup("Traps", [
        IncludeTraps, FrozenTrapWeight, BurnedTrapWeight, SlowedTrapWeight,
        PoisonedTrapWeight, ChaliceElementTrapWeight, BonusSetTrapWeight, FoodPreferenceTrapWeight,
    ]),
    OptionGroup("Misc", [DeathLink]),
]
