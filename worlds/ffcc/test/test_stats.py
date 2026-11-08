"""Starting Stats and Starting Hearts: what the seed tells the patcher."""
from random import Random
import unittest

from .bases import FFCCTestBase
from ..stats import TRIBES, VANILLA_STATS, SHUFFLE_TRIBES, SAME_TOTAL, FULLY_RANDOM, make_tribe_stats


class TestMakeTribeStats(unittest.TestCase):
    def test_off_keeps_the_game_stats(self) -> None:
        self.assertIsNone(make_tribe_stats(0, Random(1), 4, 16))

    def test_shuffle_gives_every_tribe_another_tribes_stats(self) -> None:
        for seed in range(50):
            stats = make_tribe_stats(SHUFFLE_TRIBES, Random(seed), 4, 16)
            self.assertCountEqual([tuple(v) for v in stats.values()], VANILLA_STATS.values())
            for tribe in TRIBES:
                self.assertNotEqual(tuple(stats[tribe]), VANILLA_STATS[tribe])

    def test_same_total_keeps_each_total_within_the_range(self) -> None:
        for seed in range(50):
            stats = make_tribe_stats(SAME_TOTAL, Random(seed), 4, 16)
            for tribe in TRIBES:
                self.assertEqual(sum(stats[tribe]), sum(VANILLA_STATS[tribe]))
                self.assertTrue(all(4 <= v <= 16 for v in stats[tribe]))

    def test_fully_random_stays_in_the_range(self) -> None:
        for seed in range(50):
            stats = make_tribe_stats(FULLY_RANDOM, Random(seed), 9, 5)   # swapped bounds are put right
            self.assertTrue(all(5 <= v <= 9 for values in stats.values() for v in values))


class TestStartingStatsOff(FFCCTestBase):
    def test_nothing_for_the_patcher(self) -> None:
        self.assertIsNone(self.world.tribe_stats)


class TestStartingStatsOn(FFCCTestBase):
    options = {"starting_stats": "same_total", "starting_hearts": 6}

    def test_one_set_per_tribe(self) -> None:
        self.assertEqual(set(self.world.tribe_stats), set(TRIBES))
        self.assertEqual(self.world.options.starting_hearts.value, 6)
