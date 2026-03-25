from dataclasses import dataclass

from Options import Toggle, Range, Choice, PerGameCommonOptions, DefaultOnToggle, DeathLink, OptionGroup

class FreePJs(DefaultOnToggle):
    """
    Makes PJs in shop free
    """
    display_name = "Free PJs"
    default = 0

class ChargedGigaBattery(DefaultOnToggle):
    """
    Makes Giga Battery Charged
    """
    display_name = "Charged Giga Battery"
    default = 0

class OpenUpstairs(Toggle):
    """
    Opens Upstairs
    """
    display_name = "Open Upstairs"
    default = 1

class OpenDownStairs(Toggle):
    """
    Opens DownStairs
    """
    display_name = "Open Downstairs"
    default = 1

class ChibiVisionOff(Toggle):
    """
    Turns off Chibi Vision
    """
    display_name = "Chibi Vision Off"
    default = 0

@dataclass
class ChibiRoboGameOptions(PerGameCommonOptions):
    free_pjs: FreePJs
    charged_giga_battery: ChargedGigaBattery
    open_upstairs: OpenUpstairs
    open_downstairs: OpenDownStairs
    chibi_vision_off: ChibiVisionOff
    death_link: DeathLink

chibi_robo_option_groups = [
    OptionGroup("Stage Locks", [
        OpenUpstairs, OpenDownStairs
    ]),
    OptionGroup("Quality Of Life Changes", [
        FreePJs, ChargedGigaBattery, ChibiVisionOff, DeathLink
    ])
]