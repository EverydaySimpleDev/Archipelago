"""Options that change the locations or the logic generate and fill."""
from .bases import FFCCTestBase


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
