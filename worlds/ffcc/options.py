from dataclasses import dataclass

from Options import Toggle, Range, Choice, PerGameCommonOptions, DefaultOnToggle, DeathLink, OptionGroup


class VictoryGoal(Choice):
    """
    What will send victory / goal of the game
    """
    display_name = "Goal / Victory"

    option_credits = 0

    default = 0

@dataclass
class FFCCGameOptions(PerGameCommonOptions):
    victory_goal: VictoryGoal


FFCC_option_groups = [

    OptionGroup("Misc", [
        VictoryGoal, DeathLink
    ]),

]