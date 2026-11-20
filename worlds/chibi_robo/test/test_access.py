from BaseClasses import CollectionState, ItemClassification as IC
from .bases import ChibiRoboTestBase

blaster = "Chibi-Blaster Chibi-Gear"
mug = "Mug Chibi-Gear"
tooth_brush = "Toothbrush Chibi-Gear"
squirter = "Squirter Chibi-Gear"
charge_chip = "Charge Chip"
copter = "Chibi-Copter Chibi-Gear"
drake_suit = "Drake Redcrest Suit"
radar = "Chibi-Radar Chibi-Gear"


class FoyerAccessTest(ChibiRoboTestBase):
    """Foyer is only reachable once the "basement key" gear (toothbrush, mug, Drake Redcrest Suit) and the
    Foyer - Basement Key are held, in addition to the key for whichever door is used to get there."""

    def _can_reach_foyer(self, items) -> bool:
        state = CollectionState(self.multiworld)
        for name in items:
            state.collect(self.world.create_item(name))
        return state.can_reach("Foyer", "Region", self.player)

    core_gear = [tooth_brush, mug, drake_suit, "Foyer - Basement Key"]

    def test_missing_core_gear_blocks_foyer(self) -> None:
        for missing in self.core_gear:
            with self.subTest(missing=missing):
                held = [item for item in self.core_gear if item != missing] + ["Living Room - Foyer Key"]
                self.assertFalse(self._can_reach_foyer(held))

    def test_missing_key_blocks_foyer(self) -> None:
        self.assertFalse(self._can_reach_foyer(self.core_gear))

    def test_core_gear_and_key_reaches_foyer(self) -> None:
        self.assertTrue(self._can_reach_foyer(self.core_gear + ["Living Room - Foyer Key"]))


class SecondFloorAccessTest(ChibiRoboTestBase):
    """Jenny's Room/Bedroom (second floor) require either the Foyer Ladder + Chibi-Copter, or the Foyer Teleport,
    on top of the core gear/key needed to reach the Foyer and the door key itself. A story event also requires
    the player to have visited the Basement first, so "Foyer - Basement Key" is required too."""

    options = {"open_upstairs": 0}

    base_gear = [tooth_brush, mug, drake_suit, "Living Room - Foyer Key", "Foyer - Jenny's Room Key", "Foyer - Basement Key"]

    def _can_reach_jennys_room(self, items) -> bool:
        state = CollectionState(self.multiworld)
        for name in items:
            state.collect(self.world.create_item(name))
        return state.can_reach("Jenny's Room", "Region", self.player)

    def test_ladder_alone_without_copter_blocks_second_floor(self) -> None:
        self.assertFalse(self._can_reach_jennys_room(self.base_gear + ["Foyer Ladder"]))

    def test_ladder_and_copter_reaches_second_floor(self) -> None:
        self.assertTrue(self._can_reach_jennys_room(self.base_gear + ["Foyer Ladder", copter]))

    def test_teleport_alone_reaches_second_floor(self) -> None:
        self.assertTrue(self._can_reach_jennys_room(self.base_gear + ["Foyer Teleport"]))

    def test_neither_route_blocks_second_floor(self) -> None:
        self.assertFalse(self._can_reach_jennys_room(self.base_gear))


class OpenUpstairsAccessTest(ChibiRoboTestBase):
    """With Open Upstairs on, the stairs replace the Foyer Ladder + Chibi-Copter / Foyer Teleport. The Basement
    story event and the door key are still required."""

    options = {"open_upstairs": 1}

    base_gear = [tooth_brush, mug, drake_suit, "Living Room - Foyer Key", "Foyer - Jenny's Room Key", "Foyer - Basement Key"]

    def _can_reach_jennys_room(self, items) -> bool:
        state = CollectionState(self.multiworld)
        for name in items:
            state.collect(self.world.create_item(name))
        return state.can_reach("Jenny's Room", "Region", self.player)

    def test_stairs_reach_second_floor_without_ladder_or_teleport(self) -> None:
        self.assertTrue(self._can_reach_jennys_room(self.base_gear))

    def test_basement_key_still_required(self) -> None:
        self.assertFalse(self._can_reach_jennys_room([item for item in self.base_gear if item != "Foyer - Basement Key"]))

    def test_room_key_still_required(self) -> None:
        self.assertFalse(self._can_reach_jennys_room([item for item in self.base_gear if item != "Foyer - Jenny's Room Key"]))


class BackyardLocationTest(ChibiRoboTestBase):
    """Backyard checks: the Frog Ring and Frog Suit don't need the Chibi-Blaster, and the Scurvy Splinter is dug up
    with the Spoon."""

    base_gear = ["Living Room - Backyard Key"]

    def _can_reach(self, location, items) -> bool:
        state = CollectionState(self.multiworld)
        for name in self.base_gear + items:
            state.collect(self.world.create_item(name))
        return self.multiworld.get_location(location, self.player).can_reach(state)

    def test_frog_ring_needs_only_copter(self) -> None:
        self.assertTrue(self._can_reach("Backyard - Frog Ring", [copter]))
        self.assertFalse(self._can_reach("Backyard - Frog Ring", []))

    def test_frog_suit_needs_only_squirter(self) -> None:
        self.assertTrue(self._can_reach("Backyard - Frog Suit", [squirter]))
        self.assertFalse(self._can_reach("Backyard - Frog Suit", []))

    def test_scurvy_splinter_needs_spoon(self) -> None:
        self.assertTrue(self._can_reach("Backyard - Scurvy Splinter", ["Spoon Chibi-Gear"]))
        self.assertFalse(self._can_reach("Backyard - Scurvy Splinter", []))


class GoalAccessTest(ChibiRoboTestBase):
    """Reaching the Staff Credits region (the completion condition) requires the full item set gating
    the Living Room - Mother Spider entrance - the full base gear/suit set, plus every door key
    (matching rules.py's has_all_items/mother_spider_rule exactly)."""

    required_items = [
        tooth_brush, blaster, charge_chip, squirter, mug, "Spoon Chibi-Gear", "Alien Ear Chip", "Giga-Battery",
        "Wedding Band", "Chibi-Radar Chibi-Gear", copter, "Dog Bone", "Foyer Ladder",
        "Foyer Teleport", drake_suit, "Frog Suit", "Trauma Suit", "Old Clothes",
        "Foyer - Basement Key", "Living Room - Backyard Key", "Living Room - Kitchen Key", "Living Room - Foyer Key",
        "Kitchen - Foyer Key", "Foyer - Jenny's Room Key", "Foyer - Bedroom Key", "Dinahs Teeth", "Passed-out Frog",
        "Toy Receipt", "Circuit Schematic",
    ]

    def _can_reach_credits(self, items) -> bool:
        state = CollectionState(self.multiworld)
        for name in items:
            state.collect(self.world.create_item(name))
        return state.can_reach("Staff Credits", "Region", self.player)

    def test_missing_any_required_item_blocks_goal(self) -> None:
        for missing in self.required_items:
            with self.subTest(missing=missing):
                held = [item for item in self.required_items if item != missing]
                self.assertFalse(self._can_reach_credits(held))

    def test_full_item_set_reaches_goal(self) -> None:
        self.assertTrue(self._can_reach_credits(self.required_items))


class FrogRingStickerGoalAccessTest(ChibiRoboTestBase):
    """When the stickers goal includes the Frog Ring sticker, all ten Frog Ring items are additionally
    required to reach the goal, on top of the usual full-gear requirement, and those items become
    progression so the fill algorithm guarantees they're placed reachably."""

    options = {
        "victory_goal": "stickers",
        "required_stickers": ["Frog Ring Sticker"],
    }

    frog_rings = [
        "Foyer Waterfall Frog Ring",
        "Basement Frog Ring",
        "Backyard Frog Ring",
        "Jenny's Room Frog Ring",
        "Living Room Frog Ring (Behind Window)",
        "Living Room Frog Ring (Corkboard)",
        "Living Room Frog Ring (Shelf)",
        "Kitchen Frog Ring (Table)",
        "Sink Drain Frog Ring",
        "Mother Spider Frog Ring",
    ]

    def _can_reach_credits(self, items) -> bool:
        # Frog Ring items are only classified as progression once this goal makes them so (see create_itempool),
        # so pull the real pool items rather than world.create_item(), which always uses the base classification.
        state = CollectionState(self.multiworld)
        for name in items:
            state.collect(self.get_item_by_name(name))
        return state.can_reach("Staff Credits", "Region", self.player)

    def test_missing_any_frog_ring_blocks_goal(self) -> None:
        for missing in self.frog_rings:
            with self.subTest(missing=missing):
                held = GoalAccessTest.required_items + [name for name in self.frog_rings if name != missing]
                self.assertFalse(self._can_reach_credits(held))

    def test_full_gear_and_all_frog_rings_reaches_goal(self) -> None:
        self.assertTrue(self._can_reach_credits(GoalAccessTest.required_items + self.frog_rings))

    def test_frog_ring_items_are_progression_in_pool(self) -> None:
        pool_items = {item.name: item for item in self.multiworld.itempool if item.player == self.player}
        for name in self.frog_rings:
            with self.subTest(name=name):
                self.assertIn(IC.progression, pool_items[name].classification)


class FoyerUpstairsCopterTest(ChibiRoboTestBase):
    """The sofa and spaceship shelf candy wrappers are reached from the second floor with the Chibi-Copter."""

    options = {"open_upstairs": 1}

    locations = [f"Foyer - Candy Wrapper on Sofa {x}" for x in "ABC"] + \
                [f"Foyer - Candy Wrapper by Spaceship Shelf {x}" for x in "ABC"]
    base_gear = [tooth_brush, mug, drake_suit, "Living Room - Foyer Key", "Foyer - Basement Key"]

    def _can_reach(self, location, items) -> bool:
        state = CollectionState(self.multiworld)
        for name in items:
            state.collect(self.world.create_item(name))
        return self.multiworld.get_location(location, self.player).can_reach(state)

    def test_needs_copter(self) -> None:
        for location in self.locations:
            with self.subTest(location=location):
                self.assertTrue(self._can_reach(location, self.base_gear + [copter]))
                self.assertFalse(self._can_reach(location, self.base_gear))

    def test_needs_second_floor(self) -> None:
        for location in self.locations:
            with self.subTest(location=location):
                held = [item for item in self.base_gear if item != "Foyer - Basement Key"] + [copter]
                self.assertFalse(self._can_reach(location, held))


ufo_color_codes = [f"UFO Color Code {n}" for n in range(1, 5)]
schematic_location = "Bedroom (Past) - Circuit Schematic"


class UfoAccessTest(ChibiRoboTestBase):
    """Without the ufo_color_codes option: the UFO needs the Alien Ear Chip, Chibi-Radar and Chibi-Blaster, and the time
    machine to the Bedroom (Past) also needs the Charge Chip. The color codes aren't in the pool."""

    base_gear = ["Living Room - Backyard Key"]

    def _state(self, items) -> CollectionState:
        state = CollectionState(self.multiworld)
        for name in self.base_gear + items:
            state.collect(self.world.create_item(name))
        return state

    def test_ufo_needs_ear_chip_radar_and_blaster(self) -> None:
        ufo_gear = ["Alien Ear Chip", radar, blaster]
        self.assertTrue(self._state(ufo_gear).can_reach("UFO", "Region", self.player))
        for missing in ufo_gear:
            with self.subTest(missing=missing):
                held = [item for item in ufo_gear if item != missing]
                self.assertFalse(self._state(held).can_reach("UFO", "Region", self.player))

    def test_schematic_needs_charge_chip(self) -> None:
        location = self.multiworld.get_location(schematic_location, self.player)
        self.assertTrue(location.can_reach(self._state(["Alien Ear Chip", radar, blaster, charge_chip])))
        self.assertFalse(location.can_reach(self._state(["Alien Ear Chip", radar, blaster])))

    def test_color_code_pool(self) -> None:
        pool = {item.name for item in self.multiworld.itempool if item.player == self.player}
        for name in ufo_color_codes:
            with self.subTest(name=name):
                self.assertNotIn(name, pool)
        self.assertIn("Circuit Schematic", pool)


class UfoColorCodesAccessTest(UfoAccessTest):
    """With ufo_color_codes, all four codes are in the pool and each one is needed for the Bedroom (Past)."""

    options = {"ufo_color_codes": 1}

    def test_schematic_needs_charge_chip(self) -> None:
        location = self.multiworld.get_location(schematic_location, self.player)
        self.assertTrue(location.can_reach(self._state(["Alien Ear Chip", radar, blaster, charge_chip] + ufo_color_codes)))
        self.assertFalse(location.can_reach(self._state(["Alien Ear Chip", radar, blaster] + ufo_color_codes)))

    def test_every_color_code_is_required(self) -> None:
        location = self.multiworld.get_location(schematic_location, self.player)
        for missing in ufo_color_codes:
            with self.subTest(missing=missing):
                held = ["Alien Ear Chip", radar, blaster, charge_chip] + [code for code in ufo_color_codes if code != missing]
                self.assertFalse(location.can_reach(self._state(held)))

    def test_color_code_pool(self) -> None:
        pool = [item.name for item in self.multiworld.itempool if item.player == self.player]
        for name in ufo_color_codes:
            with self.subTest(name=name):
                self.assertEqual(pool.count(name), 1)
