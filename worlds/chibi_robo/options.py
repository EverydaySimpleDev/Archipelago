from dataclasses import dataclass

from Options import Toggle, Range, Choice, PerGameCommonOptions, DefaultOnToggle


class DebugMenu(DefaultOnToggle):
    """
    Enable Debug Menu
    """
    display_name = "Turn Debug Menu On?"
    option_yes = 1
    option_no = 0
    default = 0

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
    default = 0

class OpenDownStairs(Toggle):
    """
    Opens DownStairs
    """
    display_name = "Open Downstairs"
    default = 0

class ChibiVisionOff(Toggle):
    """
    Turns off Chibi Vision
    """
    display_name = "Chibi Vision Off"
    default = 0

@dataclass
class ChibiRobobGameOptions(PerGameCommonOptions):
    debug_menu: DebugMenu
    free_pjs: FreePJs
    charged_giga_battery: ChargedGigaBattery
    open_upstairs: OpenUpstairs
    open_downstairs: OpenDownStairs
    chibi_vision_off: ChibiVisionOff