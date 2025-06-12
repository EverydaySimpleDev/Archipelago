from dataclasses import dataclass

from Options import Toggle, Range, Choice, PerGameCommonOptions


class DebugMenu(Choice):
    display_name = "Turn Debug Menu On?"
    option_yes = 1
    option_no = 0
    default = 0  # default to normal

class FreePJs(Toggle):
    display_name = "Free PJs"

class ChargedGigaBattery(Toggle):
    display_name = "Charged Giga Battery"

class OpenUpstairs(Toggle):
    display_name = "Open Upstairs"

class OpenDownStairs(Toggle):
    display_name = "Open Downstairs"

class ChibiVisionOff(Toggle):
    display_name = "Chibi Vision Off"

@dataclass
class ChibiRobobGameOptions(PerGameCommonOptions):
    debug_menu: DebugMenu
    free_pjs: FreePJs
    charged_giga_battery: ChargedGigaBattery
    open_upstairs: OpenUpstairs
    open_downstairs: OpenDownStairs
    chibi_vision_off: ChibiVisionOff