"""Options that change the locations or the logic generate and fill."""
import unittest

from .bases import FFCCTestBase
from .. import FFCCWorld
from ..rules import SPOT_AREA, VANILLA_HOTSPOTS, reachable_dungeons


class TestStageKeys(FFCCTestBase):
    options = {"stage_keys": True}

    def test_goblin_wall_needs_its_key(self) -> None:
        self.assertAccessDependency(["Goblin Wall - Cycle 1 - Chest 1"], [["Goblin Wall Key"]],
                                    only_check_listed=True)


class TestShopChecks(FFCCTestBase):
    options = {"shop_checks": True}


class TestShuffledWorld(FFCCTestBase):
    options = {
        "shuffle_loading_zones": True,
        "randomize_miasma_streams": True,
        "hotspot_elements": "match_miasma_streams",
    }


class TestFewerCycles(FFCCTestBase):
    options = {"progression_cycles": 1, "cycle_location_checks": True, "year_location_checks": True}


class TestProgressiveItems(FFCCTestBase):
    options = {"progressive_artifacts": True, "progressive_equipment": True, "extra_spell_rings": True}

class TestCycleLocksGlobal(FFCCTestBase):
    options = {"cycle_locks": "global"}

    def test_cycles_need_progressive_cycles(self) -> None:
        self.assertAccessDependency(["River Belle Path - Cycle 2 - Chest 1", "River Belle Path - Cycle 3 - Chest 1"],
                                    [["Progressive Cycle"]], only_check_listed=True)


class TestCycleLocksPerDungeon(FFCCTestBase):
    options = {"cycle_locks": "per_dungeon"}

    def test_cycles_need_their_dungeons_item(self) -> None:
        self.assertAccessDependency(["River Belle Path - Cycle 2 - Chest 1", "River Belle Path - Cycle 3 - Chest 1"],
                                    [["Progressive River Belle Path Cycle"]], only_check_listed=True)

    def test_cycle_3_needs_both_copies(self) -> None:
        self.collect_all_but(["Progressive River Belle Path Cycle"])
        self.collect(self.get_item_by_name("Progressive River Belle Path Cycle"))
        self.assertTrue(self.can_reach_location("River Belle Path - Cycle 2 - Chest 1"))
        self.assertFalse(self.can_reach_location("River Belle Path - Cycle 3 - Chest 1"))


class TestSkipMiasmaStreams(FFCCTestBase):
    options = {
        "skip_miasma_streams": True,
        "shuffle_loading_zones": True,
        "randomize_miasma_streams": True,
        "stage_keys": True,
    }


class TestOpenGates(unittest.TestCase):
    """With no element anywhere, only open gates let the caravan past the
    first Miasma Stream in Year 1."""

    def test_open_gates_need_no_element(self) -> None:
        plan = {spot: spot for spot in SPOT_AREA}
        no_elements = {dungeon: [[] for _ in range(4)] for dungeon in VANILLA_HOTSPOTS}
        for gates_open in (False, True):
            reached, _ = reachable_dungeons(plan, FFCCWorld.VANILLA_GATES, 1, hotspots=no_elements,
                                            gates_open=gates_open)
            self.assertEqual("The Mine of Cathuriges" in reached, gates_open)


class TestMonsterHuntTint(FFCCTestBase):
    """Traps look like progression by default, as the chests do."""
    options = {"monster_hunt_checks": "enemy_types"}

    def test_slot_data_has_the_colours(self) -> None:
        gold, blue, white = [255, 215, 60], [90, 170, 255], [255, 255, 255]
        self.assertEqual(self.world.fill_slot_data()["monster_hunt_tint"], [gold, blue, white, gold])


class TestMonsterHuntTrapColour(FFCCTestBase):
    options = {"monster_hunt_checks": "every_enemy", "trap_tint": "red"}

    def test_traps_get_their_own_colour(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["monster_hunt_tint"][3], [255, 70, 70])


class TestAllInOneRadar(FFCCTestBase):
    options = {"all_in_one_radar": True}


class TestChestsAndMonsterHunt(FFCCTestBase):
    """Chest Checks keeps the chests as checks next to the Monster Hunt."""
    options = {"monster_hunt_checks": "enemy_types"}

    def test_chests_and_enemies_are_locations(self) -> None:
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        self.assertIn("River Belle Path - Cycle 1 - Chest 1", names)
        self.assertIn("Monster Hunt - Goblin (Sword)", names)


class TestOnlyMonsterHunt(FFCCTestBase):
    options = {"monster_hunt_checks": "enemy_types", "chest_checks": False}

    def test_no_chests(self) -> None:
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        self.assertNotIn("River Belle Path - Cycle 1 - Chest 1", names)


class TestLaterCyclesRemoved(FFCCTestBase):
    """Later Cycles: Removed leaves the checks after Progression Cycles out."""
    options = {"progression_cycles": 2, "later_cycles": "removed", "cycle_location_checks": True,
               "monster_hunt_checks": "every_enemy", "cycle_locks": "per_dungeon"}

    def test_no_cycle_3_checks(self) -> None:
        from ..locations import LOCATION_TABLE, ENEMY_LOCATION_TABLE
        for location in self.multiworld.get_locations(self.player):
            data = LOCATION_TABLE.get(location.name) or ENEMY_LOCATION_TABLE.get(location.name)
            if data is not None and location.address is not None:
                self.assertLessEqual(data.cycle, 2, location.name)

    def test_one_unlock_per_dungeon(self) -> None:
        from ..items import dungeon_cycle_item
        count = sum(1 for item in self.multiworld.itempool if item.name == dungeon_cycle_item("Tida"))
        self.assertEqual(count, 1)


class TestLaterCyclesRemovedHuntGoal(FFCCTestBase):
    """The Monster Hunt goal leaves out types found only in removed cycles."""
    options = {"victory_goal": "monster_hunt", "progression_cycles": 1, "later_cycles": "removed"}

    def test_goal_has_no_later_types(self) -> None:
        from ..locations import first_hunt_cycle
        self.assertTrue(all(first_hunt_cycle(enemy) == 1 for enemy in self.world.hunt_rules))


class TestGbaLootPages(FFCCTestBase):
    options = {"gba_bonus_pool": True, "gba_enemy_drops": True}


class TestNoMonsterHuntTint(FFCCTestBase):
    """Without Monster Hunt Checks there is nothing to tint."""
    options = {"monster_hunt_tint": True}

    def test_slot_data_has_no_colours(self) -> None:
        self.assertIsNone(self.world.fill_slot_data()["monster_hunt_tint"])

