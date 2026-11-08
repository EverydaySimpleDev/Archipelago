"""Every victory goal generates, can be filled and can be beaten."""
from .bases import FFCCTestBase


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
