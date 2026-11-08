"""Every option preset makes a seed that fills and can be beaten."""
import unittest

from test.general import gen_steps, setup_multiworld
from worlds.AutoWorld import call_all
from Fill import distribute_items_restrictive  # after the worlds load: Fill and the worlds import each other

from .. import FFCCWorld
from ..presets import options_presets


class TestPresets(unittest.TestCase):
    def test_every_preset_generates(self) -> None:
        for name, preset in options_presets.items():
            with self.subTest(preset=name):
                multiworld = setup_multiworld(FFCCWorld, gen_steps, seed=1, options=preset)
                distribute_items_restrictive(multiworld)
                call_all(multiworld, "post_fill")
                self.assertTrue(multiworld.can_beat_game(multiworld.state), f"{name} can't be beaten")
                for option_name, value in preset.items():
                    option = getattr(multiworld.worlds[1].options, option_name)
                    if option_name not in ("victory_goal", "monster_hunt_checks", "shop_checks", "stage_keys",
                                           "cycle_location_checks", "year_location_checks"):
                        self.assertEqual(option.value, type(option).from_any(value).value, option_name)
