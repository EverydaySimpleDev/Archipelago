"""Every victory goal generates, can be filled and can be beaten."""
from .bases import FFCCTestBase
from ..locations import MOG_STAMP_NESTS, mog_stamp_location


class TestAllMyrrh(FFCCTestBase):
    options = {"victory_goal": "all_myrrh"}


class TestFinalBoss(FFCCTestBase):
    options = {"victory_goal": "final_boss"}


class TestMonsterHuntEnemyTypes(FFCCTestBase):
    options = {"victory_goal": "monster_hunt", "monster_hunt_checks": "enemy_types"}


class TestMonsterHuntEveryEnemy(FFCCTestBase):
    options = {"victory_goal": "monster_hunt", "monster_hunt_checks": "every_enemy"}


class TestMogStamps(FFCCTestBase):
    options = {"victory_goal": "mog_stamps"}


class TestMogGroomingDye(FFCCTestBase):
    options = {"victory_goal": "mog_grooming", "mog_grooming_goal": "dye"}

    def test_needs_a_dye(self) -> None:
        """With the grooming tools as items, the dye goal needs any one dye."""
        self.assertBeatable(False)
        self.collect_by_name("Blue Dye")
        self.assertBeatable(True)


class TestMogGroomingTrim(FFCCTestBase):
    options = {"victory_goal": "mog_grooming", "mog_grooming_goal": "trim"}

    def test_needs_the_scissors(self) -> None:
        self.assertBeatable(False)
        self.collect_by_name("Mog Scissors")
        self.assertBeatable(True)


class TestMogGroomingBoth(FFCCTestBase):
    options = {"victory_goal": "mog_grooming", "mog_grooming_goal": "both"}

    def test_needs_a_dye_and_the_scissors(self) -> None:
        self.collect_by_name("Mog Scissors")
        self.assertBeatable(False)
        self.collect_by_name("Red Dye")
        self.assertBeatable(True)


class TestMogGroomingWithoutTools(FFCCTestBase):
    options = {"victory_goal": "mog_grooming", "grooming_tools": "off"}

    def test_open_from_the_start(self) -> None:
        """Without the tools as items, nothing is needed: Tipa has a Moogle Nest."""
        self.assertBeatable(True)


class TestMultipleGoalsDefault(FFCCTestBase):
    """Multiple with nothing removed: every goal."""
    options = {"victory_goal": "multiple"}

    def test_every_goal_is_in(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["victory_goals"], [0, 1, 2, 3, 4])


class TestMultipleGoalsNeedTheirItems(FFCCTestBase):
    """Final Boss and Mog Grooming: the tools are items (grooming_tools
    with_goal) and the seed isn't won without a dye."""
    options = {"victory_goal": "multiple", "multiple_goals": ["Final Boss", "Mog Grooming"],
               "mog_grooming_goal": "dye"}

    def test_needs_the_final_boss_and_a_dye(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["victory_goals"], [1, 4])
        self.collect_all_but(["Red Dye", "Blue Dye", "Green Dye"])
        self.assertBeatable(False)
        self.collect_by_name("Green Dye")
        self.assertBeatable(True)


class TestMultipleGoalsMogStamps(FFCCTestBase):
    """A Mog Stamps goal among them adds the Moogle Nest events."""
    options = {"victory_goal": "multiple", "multiple_goals": ["All Myrrh", "Mog Stamps"]}

    def test_nests_are_there(self) -> None:
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        self.assertLessEqual({mog_stamp_location(nest) for nest in MOG_STAMP_NESTS}, names)


class TestMultipleGoalsIgnoredOtherwise(FFCCTestBase):
    """Multiple Goals only counts with Victory Goal set to Multiple."""
    options = {"victory_goal": "final_boss", "multiple_goals": ["Mog Stamps"]}

    def test_only_the_victory_goal(self) -> None:
        self.assertEqual(self.world.fill_slot_data()["victory_goals"], [1])
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        self.assertFalse({mog_stamp_location(nest) for nest in MOG_STAMP_NESTS} & names)
