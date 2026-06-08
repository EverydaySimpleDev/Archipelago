from dataclasses import dataclass

from Options import Toggle, Range, Choice, PerGameCommonOptions, DefaultOnToggle, DeathLink, OptionGroup
class OpenUpstairs(Toggle):
    """
    Opens Upstairs
    """
    display_name = "Open Upstairs"
    default = 1

class ChibiVisionOff(Toggle):
    """
    Turns off Chibi Vision
    """
    display_name = "Chibi Vision Off"
    default = 0

class PasswordRando(Toggle):
    """
    Randomizes Passwords For Left Foot And Case
    """
    display_name = "Randomizes Passwords For Left Foot And Case"
    default = 0

class BatteryDrainIdle(Range):
    """
    Battery Drain Idle
    """
    display_name = "Idle Battery Drain"
    default = 2
    range_start = 2
    range_end = 20

class BatteryDrainWalk(Range):
    """
    Battery Drain Walk
    """
    display_name = "Walk Battery Drain"
    default = 10
    range_start = 5
    range_end = 30

class BatteryDrainJog(Range):
    """
    Battery Drain Jog
    """
    display_name = "Jog Battery Drain"
    default = 20
    range_start = 10
    range_end = 50

class BatteryDrainRun(Range):
    """
    Battery Drain Run
    """
    display_name = "Run Battery Drain"
    default = 30
    range_start = 15
    range_end = 60

class BatteryDrainSlide(Range):
    """
    Battery Drain Slide
    """
    display_name = "Slide Battery Drain"
    default = 10
    range_start = 5
    range_end = 20

class BatteryDrainEquip(Range):
    """
    Battery Drain Equip
    """
    display_name = "Equip Battery Drain"
    default = 10
    range_start = 5
    range_end = 20

class BatteryDrainLift(Range):
    """
    Battery Drain Lift
    """
    display_name = "Lift Battery Drain"
    default = 30
    range_start = 15
    range_end = 60

class BatteryDrainDrop(Range):
    """
    Battery Drain Drop
    """
    display_name = "Drop Battery Drain"
    default = 10
    range_start = 5
    range_end = 20

class BatteryDrainLedgeGrab(Range):
    """
    Battery Drain Ledge Grab
    """
    display_name = "Ledge Grab Battery Drain"
    default = 60
    range_start = 30
    range_end = 120

class BatteryDrainLedgeSlide(Range):
    """
    Battery Drain Ledge Slide
    """
    display_name = "Ledge Grab Battery Drain"
    default = 30
    range_start = 15
    range_end = 60

class BatteryDrainLedgeClimb(Range):
    """
    Battery Drain Ledge Climb
    """
    display_name = "Ledge Climb Battery Drain"
    default = 60
    range_start = 30
    range_end = 120

class BatteryDrainLedgeDrop(Range):
    """
    Battery Drain Ledge Drop
    """
    display_name = "Ledge Drop Battery Drain"
    default = 10
    range_start = 5
    range_end = 20

class BatteryDrainLedgeTeeter(Range):
    """
    Battery Drain Ledge Teeter
    """
    display_name = "Ledge Teeter Battery Drain"
    default = 30
    range_start = 15
    range_end = 60

class BatteryDrainJump(Range):
    """
    Battery Drain Jump
    """
    display_name = "Jump Battery Drain"
    default = 60
    range_start = 30
    range_end = 120

class BatteryDrainFall(Range):
    """
    Battery Drain Fall
    """
    display_name = "Fall Battery Drain"
    default = 2000
    range_start = 50
    range_end = 4000

class BatteryDrainLadderGrab(Range):
    """
    Battery Drain Ladder Grab
    """
    display_name = "Ladder Grab Battery Drain"
    default = 30
    range_start = 15
    range_end = 60

class BatteryDrainLadderAscend(Range):
    """
    Battery Drain Ladder Ascend
    """
    display_name = "Ladder Ascend Battery Drain"
    default = 60
    range_start = 30
    range_end = 120

class BatteryDrainLadderDescend(Range):
    """
    Battery Drain Ladder Descen
    """
    display_name = "Ladder Descend Battery Drain"
    default = 60
    range_start = 30
    range_end = 120

class BatteryDrainLadderTop(Range):
    """
    Battery Drain Ladder Top
    """
    display_name = "Ladder Top Battery Drain"
    default = 60
    range_start = 30
    range_end = 120

class BatteryDrainLadderBottom(Range):
    """
    Battery Drain Ladder Bottom
    """
    display_name = "Ladder Bottom Battery Drain"
    default = 10
    range_start = 5
    range_end = 20

class BatteryDrainRopeGrab(Range):
    """
    Battery Drain Rope Grab
    """
    display_name = "Rope Grab Battery Drain"
    default = 30
    range_start = 15
    range_end = 60

class BatteryDrainRopeAscend(Range):
    """
    Battery Drain Rope Ascend
    """
    display_name = "Rope Ascend Battery Drain"
    default = 60
    range_start = 30
    range_end = 120

class BatteryDrainRopeDescend(Range):
    """
    Battery Drain Rope Descen
    """
    display_name = "Rope Descend Battery Drain"
    default = 10
    range_start = 5
    range_end = 20

class BatteryDrainRopeTop(Range):
    """
    Battery Drain Rope Top
    """
    display_name = "Rope Top Battery Drain"
    default = 60
    range_start = 30
    range_end = 120

class BatteryDrainRopeBottom(Range):
    """
    Battery Drain Rope Bottom
    """
    display_name = "Rope Bottom Battery Drain"
    default = 10
    range_start = 5
    range_end = 20

class BatteryDrainPush(Range):
    """
    Battery Drain Push
    """
    display_name = "Push Battery Drain"
    default = 60
    range_start = 30
    range_end = 120

class BatteryDrainCopterHover(Range):
    """
    Battery Drain Copter Hover
    """
    display_name = "Copter Hover Battery Drain"
    default = 1000
    range_start = 100
    range_end = 2000

class BatteryDrainCopterDescend(Range):
    """
    Battery Drain Copter Descend
    """
    display_name = "Copter Descend Battery Drain"
    default = 30
    range_start = 15
    range_end = 60

class BatteryDrainPopperShoot(Range):
    """
    Battery Drain Blaster Shoot
    """
    display_name = "Blaster Battery Drain"
    default = 100
    range_start = 50
    range_end = 200

class BatteryDrainPopperShootCharge(Range):
    """
    Battery Drain Blaster Charge
    """
    display_name = "Blaster Charge Battery Drain"
    default = 500
    range_start = 250
    range_end = 1000

class BatteryDrainRadarScan(Range):
    """
    Battery Drain Radar Scanq
    """
    display_name = "Radar Scan Battery Drain"
    default = 300
    range_start = 100
    range_end = 600

class BatteryDrainRadarFollow(Range):
    """
    Battery Drain Radar Follow
    """
    display_name = "Radar Follow Battery Drain"
    default = 80
    range_start = 40
    range_end = 160

class BatteryDrainBrush(Range):
    """
    Battery Drain Brush
    """
    display_name = "Brush Battery Drain"
    default = 250
    range_start = 100
    range_end = 500

class BatteryDrainSpoon(Range):
    """
    Battery Drain Spoon
    """
    display_name = "Spoon Battery Drain"
    default = 250
    range_start = 100
    range_end = 500

class BatteryDrainMug(Range):
    """
    Battery Drain Mug
    """
    display_name = "Mug Battery Drain"
    default = 500
    range_start = 250
    range_end = 1000

class BatteryDrainSquirterSuck(Range):
    """
    Battery Drain Squirter Suck
    """
    display_name = "Squirter Suck Battery Drain"
    default = 100
    range_start = 50
    range_end = 200

class BatteryDrainSquirterSpray(Range):
    """
    Battery Drain Squirter Spray
    """
    display_name = "Squirter Spray Battery Drain"
    default = 100
    range_start = 50
    range_end = 200

class FavoriteCharacterVoice(Choice):
    """
    The voice the player will hear when
    Picking Up An AP Item
    """
    display_name = "Favorite Character Voice"
    option_telly = 0
    # option_jenny_frog = 1
    # option_jenny_frog = 14
    option_jenny = 2
    option_dad = 3
    option_mom = 4
    option_drake = 7
    option_plank_beard = 8
    option_cincy = 9
    option_peekoe = 10
    option_peeko_underwater = 29
    option_sophie = 11
    option_sonny = 12
    option_sarge = 13
    option_primo = 15
    option_mr_prongs = 16
    option_aliens = 17
    option_funky = 18
    option_dinha = 19
    option_dina_toothless = 24
    option_princess_pitts = 20
    option_mort = 21
    option_sunshine = 22
    option_sunshine_hungry = 23
    option_fred_the_frog = 25
    option_freda_the_frog = 26
    option_toa = 27
    option_eggplant = 30

    default = 0

class VictoryGoal(Choice):
    """
    What will send victory / goal of the game
    """
    display_name = "Goal / Victory"

    option_credits = 0
    option_activate_giga_robo = 1

    default = 1

class LogicSetting(Choice):
    """
    To enable logic / rules
    """
    display_name = "Logic Settings"

    option_logic_disabled = 0
    option_logic_enabled = 1

    default = 1

class PjSuiteStyle(Choice):
    """
    PJ Suite Style
    """
    display_name = "PJ Suite Style"

    option_old_boxers = 0
    option_outdated_scarf = 1
    option_small_handkerchief = 2

    default = 0
@dataclass
class ChibiRoboGameOptions(PerGameCommonOptions):
    victory_goal: VictoryGoal
    pk_suit_style: PjSuiteStyle
    logic_setting: LogicSetting
    open_upstairs: OpenUpstairs
    chibi_vision_off: ChibiVisionOff
    password_rando: PasswordRando
    death_link: DeathLink
    battery_drain_idle: BatteryDrainIdle
    battery_drain_walk: BatteryDrainWalk
    battery_drain_jog: BatteryDrainJog
    battery_drain_run: BatteryDrainRun
    battery_drain_slide: BatteryDrainSlide
    battery_drain_equip: BatteryDrainEquip
    battery_drain_lift: BatteryDrainLift
    battery_drain_drop: BatteryDrainDrop
    battery_drain_ledge_grab: BatteryDrainLedgeGrab
    battery_drain_ledge_slide: BatteryDrainLedgeSlide
    battery_drain_ledge_climb: BatteryDrainLedgeClimb
    battery_drain_ledge_drop: BatteryDrainLedgeDrop
    battery_drain_ledge_teeter: BatteryDrainLedgeTeeter
    battery_drain_jump: BatteryDrainJump
    battery_drain_fall: BatteryDrainFall
    battery_drain_ladder_grab: BatteryDrainLadderGrab
    battery_drain_ladder_ascend: BatteryDrainLadderAscend
    battery_drain_ladder_descend: BatteryDrainLadderDescend
    battery_drain_ladder_top: BatteryDrainLadderTop
    battery_drain_ladder_bottom: BatteryDrainLadderBottom
    battery_drain_rope_grab: BatteryDrainRopeGrab
    battery_drain_rope_ascend: BatteryDrainRopeAscend
    battery_drain_rope_descend: BatteryDrainRopeDescend
    battery_drain_rope_top: BatteryDrainRopeTop
    battery_drain_rope_bottom: BatteryDrainRopeBottom
    battery_drain_push: BatteryDrainPush
    battery_drain_copter_hover: BatteryDrainCopterHover
    battery_drain_copter_descend: BatteryDrainCopterDescend
    battery_drain_popper_shoot: BatteryDrainPopperShoot
    battery_drain_pooper_shoot_charge: BatteryDrainPopperShootCharge
    battery_drain_radar_scan: BatteryDrainRadarScan
    battery_drain_radar_follow: BatteryDrainRadarFollow
    battery_drain_brush: BatteryDrainBrush
    battery_drain_spoon: BatteryDrainSpoon
    battery_drain_mug: BatteryDrainMug
    battery_drain_squirter_suck: BatteryDrainSquirterSuck
    battery_drain_squirter_spray: BatteryDrainSquirterSpray
    favorite_character_voice: FavoriteCharacterVoice

chibi_robo_option_groups = [
    OptionGroup("Stage Locks", [
        OpenUpstairs,
        PasswordRando
    ]),
    OptionGroup("Quality Of Life Changes", [
        PjSuiteStyle,
        VictoryGoal,
        FavoriteCharacterVoice,
        DeathLink
    ]),
    OptionGroup("Misc", [
        ChibiVisionOff,
        LogicSetting
    ]),
    OptionGroup("Battery Drain (Use at your own risk!!)", [
        BatteryDrainIdle,
        BatteryDrainWalk,
        BatteryDrainJog,
        BatteryDrainRun,
        BatteryDrainSlide,
        BatteryDrainEquip,
        BatteryDrainLift,
        BatteryDrainDrop,
        BatteryDrainLedgeGrab,
        BatteryDrainLedgeSlide,
        BatteryDrainLedgeClimb,
        BatteryDrainLedgeDrop,
        BatteryDrainLedgeTeeter,
        BatteryDrainJump,
        BatteryDrainFall,
        BatteryDrainLadderGrab,
        BatteryDrainLadderAscend,
        BatteryDrainLadderDescend,
        BatteryDrainLadderTop,
        BatteryDrainLadderBottom,
        BatteryDrainRopeGrab,
        BatteryDrainRopeAscend,
        BatteryDrainRopeDescend,
        BatteryDrainRopeTop,
        BatteryDrainRopeBottom,
        BatteryDrainPush,
        BatteryDrainCopterHover,
        BatteryDrainCopterDescend,
        BatteryDrainPopperShoot,
        BatteryDrainPopperShootCharge,
        BatteryDrainRadarScan,
        BatteryDrainRadarFollow,
        BatteryDrainBrush,
        BatteryDrainSpoon,
        BatteryDrainMug,
        BatteryDrainSquirterSuck,
        BatteryDrainSquirterSpray
    ]),
]