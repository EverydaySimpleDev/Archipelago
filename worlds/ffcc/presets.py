"""Option presets: named bundles of options that the options page (and the Launcher's
template generator) can fill in at once. Options a preset doesn't name keep their defaults."""
from typing import Any

from .options import SHORTCUT_OPTIONS

ALL_SHORTCUTS: dict[str, Any] = {name: True for name in SHORTCUT_OPTIONS}

NO_TRAPS: dict[str, Any] = {"include_traps": False}

# One cycle per dungeon, with the later cycles left out of the seed entirely.
ONE_CYCLE: dict[str, Any] = {"progression_cycles": 1, "later_cycles": "removed"}

# Everything that shuffles the world or adds checks, without changing the goal.
FULL_RANDOMIZER: dict[str, Any] = {
    "stage_keys": True,
    "shuffle_loading_zones": True,
    "randomize_miasma_streams": True,
    "hotspot_elements": "match_miasma_streams",
    "goblin_wall_year_one": True,
    "progressive_artifacts": True,
    "progressive_equipment": True,
    "cycle_location_checks": True,
    "year_location_checks": True,
    "rebena_te_ra_timed_chests": True,
    "shop_checks": True,
    "randomize_shops": True,
    "randomize_shop_prices": True,
    "randomize_bonus_pools": True,
    "extra_spell_rings": True,
    "cycle_locks": "per_dungeon",
    # the enemy types are checks next to the chests
    "monster_hunt_checks": "enemy_types",
    "chest_checks": True,
}

options_presets: dict[str, dict[str, Any]] = {
    # A first seed: one cycle per dungeon, the dungeons opened up, no element
    # softlocks at the Miasma Streams, no traps and plenty of help on screen.
    "Beginner": {
        "victory_goal": "all_myrrh",
        **ONE_CYCLE,
        "skip_miasma_streams": True,
        "free_cure_magicite": True,
        "show_enemy_health": "both",
        **ALL_SHORTCUTS,
        **NO_TRAPS,
    },
    # Every shuffle and every kind of check, for players who know the game.
    "Full Randomizer": {
        "victory_goal": "all_myrrh",
        **FULL_RANDOMIZER,
    },
    # Full Randomizer with the hotspots shuffled too, a random artifact order,
    # reshuffled tribe stats and lots of traps.
    "Chaos": {
        "victory_goal": "all_myrrh",
        **FULL_RANDOMIZER,
        "hotspot_elements": "shuffled",
        "progressive_artifact_order": "random_order",
        "starting_stats": "same_total",
        "gil_weight": 5,
        "include_traps": True,
        "frozen_trap_weight": 5,
        "burned_trap_weight": 5,
        "slowed_trap_weight": 5,
        "poisoned_trap_weight": 5,
        "chalice_element_trap_weight": 3,
        "bonus_set_trap_weight": 3,
        "food_preference_trap_weight": 3,
        "command_slot_trap_weight": 3,
    },
    # Defeating enemies are the only checks, and beating every enemy type wins.
    "Monster Hunter": {
        "victory_goal": "monster_hunt",
        "monster_hunt_checks": "enemy_types",
        "monster_hunt_bosses": True,
        "chest_checks": False,
        "monster_hunt_tint": True,
        "show_enemy_health": "bar",
    },
    # Race to the final boss on one cycle per dungeon, with the speedrun timer
    # on screen, no Miasma Stream detours and no traps.
    "Speedrun": {
        "victory_goal": "final_boss",
        **ONE_CYCLE,
        "show_play_timer": "speedrun_automatic",
        "skip_intro_cutscene": True,
        "skip_miasma_streams": True,
        "mog_never_tired": True,
        **ALL_SHORTCUTS,
        **NO_TRAPS,
    },
    # Every goal at once, with the chests, the enemies, the shops and every
    # cycle and year as checks.
    "Completionist": {
        "victory_goal": "multiple",
        "monster_hunt_checks": "enemy_types",
        "chest_checks": True,
        "shop_checks": True,
        "cycle_location_checks": True,
        "year_location_checks": True,
        "mog_stamp_hints": True,
    },
    # Collect all 23 Mog Stamps from the Moogle Nests.
    "Stamp Collector": {
        "victory_goal": "mog_stamps",
        "mog_stamp_hints": True,
    },
    # Only the Moogle: find the grooming tools, dye and trim Mog. No dungeons.
    "Mog Grooming Only": {
        "mog_grooming_only": True,
        "mog_grooming_goal": "both",
        "mog_grooming_percent": 75,
        **NO_TRAPS,
    },
}
