from dataclasses import dataclass

from Options import Toggle, Range, Choice, PerGameCommonOptions


class DebugMenu(Choice):
    # Enable Debug Menu
    display_name = "Turn Debug Menu On?"
    option_yes = 1
    option_no = 0
    default = 0  # default to normal

class FreePJs(Toggle):
    # Makes PJs in shop free
    display_name = "Free PJs"

class ChargedGigaBattery(Toggle):
    # Makes Giga Battery Charged
    display_name = "Charged Giga Battery"

class OpenUpstairs(Toggle):
    # Opens Upstairs
    display_name = "Open Upstairs"

class OpenDownStairs(Toggle):
    # Opens DownStairs
    display_name = "Open Downstairs"

class ChibiVisionOff(Toggle):
    # Turns off Chibi Vision
    display_name = "Chibi Vision Off"

@dataclass
class ChibiRobobGameOptions(PerGameCommonOptions):
    debug_menu: DebugMenu
    free_pjs: FreePJs
    charged_giga_battery: ChargedGigaBattery
    open_upstairs: OpenUpstairs
    open_downstairs: OpenDownStairs
    chibi_vision_off: ChibiVisionOff