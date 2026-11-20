"""The Mog grooming checks and Mog Grooming Only seeds."""
from .bases import FFCCTestBase
from ..items import GROOMING_TOOLS
from ..locations import GROOMING_LOCATIONS, LOCATION_TABLE

RADARS = {
    "Mog Radar - Red (Monster Radar)": "Red Dye",
    "Mog Radar - Green (Score Radar)": "Green Dye",
    "Mog Radar - Blue (Treasure Radar)": "Blue Dye",
}
DYED = ["Mog Grooming - Dyed 25%", "Mog Grooming - Dyed 50%", "Mog Grooming - Dyed 75%"]
CUT = ["Mog Grooming - Cut 25%", "Mog Grooming - Cut 50%", "Mog Grooming - Cut 75%"]


class TestGroomingChecks(FFCCTestBase):
    options = {"victory_goal": "final_boss", "grooming_tools": "always", "mog_grooming_checks": "all"}

    def test_all_checks_exist(self) -> None:
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        for name in GROOMING_LOCATIONS:
            self.assertIn(name, names)

    def test_tools_are_in_the_pool(self) -> None:
        pool = {item.name for item in self.multiworld.itempool if item.player == self.player}
        for name, _, _ in GROOMING_TOOLS:
            self.assertIn(name, pool)

    def test_each_radar_needs_its_dye(self) -> None:
        for location, dye in RADARS.items():
            self.assertAccessDependency([location], [[dye]], only_check_listed=True)

    def test_dye_milestones_need_any_dye(self) -> None:
        self.assertAccessDependency(DYED, [["Red Dye"], ["Blue Dye"], ["Green Dye"]], only_check_listed=True)

    def test_cut_milestones_need_the_scissors(self) -> None:
        self.assertAccessDependency(CUT, [["Mog Scissors"]], only_check_listed=True)


class TestGroomingChecksWithoutTools(FFCCTestBase):
    options = {"victory_goal": "final_boss", "grooming_tools": "off", "mog_grooming_checks": "radars"}

    def test_only_radars_and_no_tools(self) -> None:
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        for name in RADARS:
            self.assertIn(name, names)
        for name in DYED + CUT:
            self.assertNotIn(name, names)
        pool = {item.name for item in self.multiworld.itempool if item.player == self.player}
        for name, _, _ in GROOMING_TOOLS:
            self.assertNotIn(name, pool)
        for location in RADARS:
            self.assertTrue(self.can_reach_location(location))


class TestGroomingOnly(FFCCTestBase):
    options = {"mog_grooming_only": True}

    def test_only_grooming_locations(self) -> None:
        names = {location.name for location in self.multiworld.get_locations(self.player)}
        self.assertEqual(names, set(GROOMING_LOCATIONS))
        self.assertFalse(names & set(LOCATION_TABLE))

    def test_starts_with_a_dye(self) -> None:
        start = [item.name for item in self.multiworld.precollected_items[self.player]]
        self.assertEqual(len([name for name in start if name.endswith(" Dye")]), 1)

    def test_goal_is_mog_grooming(self) -> None:
        options = self.world.options
        self.assertEqual(options.victory_goal, options.victory_goal.option_mog_grooming)

    def test_start_dye_is_in_the_slot_data(self) -> None:
        start = [item.name for item in self.multiworld.precollected_items[self.player] if item.name.endswith(" Dye")]
        self.assertEqual(self.world.fill_slot_data()["grooming_start_dye"], start[0])


class TestTrackerKeepsTheStartDye(FFCCTestBase):
    """Universal Tracker rebuilds the world from the slot data. It must start with the seed's dye,
    or it would show the wrong radar check in logic."""
    options = {"mog_grooming_only": True}

    def setUp(self) -> None:
        self.multiworld_re_gen = {"grooming_start_dye": "Blue Dye", "mog_grooming_only": 1}
        super().setUp()

    def world_setup(self, *args, **kwargs) -> None:
        from BaseClasses import MultiWorld
        original = MultiWorld.__init__
        passthrough = {self.game: self.multiworld_re_gen}

        def init(mw: MultiWorld, *a, **kw) -> None:
            original(mw, *a, **kw)
            mw.re_gen_passthrough = passthrough
        MultiWorld.__init__ = init
        try:
            super().world_setup(*args, **kwargs)
        finally:
            MultiWorld.__init__ = original

    def test_uses_the_seed_dye(self) -> None:
        start = [item.name for item in self.multiworld.precollected_items[self.player]]
        self.assertIn("Blue Dye", start)
        self.assertNotIn("Blue Dye", [item.name for item in self.multiworld.itempool])
