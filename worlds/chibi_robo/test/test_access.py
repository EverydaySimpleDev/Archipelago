from BaseClasses import CollectionState, ItemClassification as IC
from .bases import ChibiRoboTestBase

blaster = "Chibi-Blaster Chibi-Gear"
mug = "Mug Chibi-Gear"
tooth_brush = "Toothbrush Chibi-Gear"
squirter = "Squirter Chibi-Gear"
charge_chip = "Charge Chip"
copter = "Chibi-Copter Chibi-Gear"
drake_suit = "Drake Redcrest Suit"


class FoyerAccessTest(ChibiRoboTestBase):
    """Foyer is only reachable once the "basement key" gear (toothbrush, mug, Drake Redcrest Suit) is held,
    in addition to the key for whichever door is used to get there."""

    def _can_reach_foyer(self, items) -> bool:
        state = CollectionState(self.multiworld)
        for name in items:
            state.collect(self.world.create_item(name))
        return state.can_reach("Foyer", "Region", self.player)

    def test_missing_core_gear_blocks_foyer(self) -> None:
        core_gear = [tooth_brush, mug, drake_suit]
        for missing in core_gear:
            with self.subTest(missing=missing):
                held = [item for item in core_gear if item != missing] + ["Living Room - Foyer Key"]
                self.assertFalse(self._can_reach_foyer(held))

    def test_missing_key_blocks_foyer(self) -> None:
        core_gear = [tooth_brush, mug, drake_suit]
        self.assertFalse(self._can_reach_foyer(core_gear))

    def test_core_gear_and_key_reaches_foyer(self) -> None:
        core_gear = [tooth_brush, mug, drake_suit]
        self.assertTrue(self._can_reach_foyer(core_gear + ["Living Room - Foyer Key"]))


class SecondFloorAccessTest(ChibiRoboTestBase):
    """Jenny's Room/Bedroom (second floor) require either the Foyer Ladder + Chibi-Copter, or the Foyer Teleport,
    on top of the core gear/key needed to reach the Foyer and the door key itself. A story event also requires
    the player to have visited the Basement first, so "Foyer - Basement Key" is required too."""

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


class GoalAccessTest(ChibiRoboTestBase):
    """Reaching the Staff Credits region (the completion condition) requires the full item set gating
    the Living Room - Mother Spider entrance - the full base gear/suit set, plus every door key
    (matching rules.py's has_all_items/mother_spider_rule exactly)."""

    required_items = [
        tooth_brush, blaster, charge_chip, squirter, mug, "Alien Ear Chip", "Giga-Battery",
        "Wedding Band", "Chibi-Radar Chibi-Gear", copter, "Dog Bone", "Foyer Ladder",
        "Foyer Teleport", drake_suit, "Frog Suit", "Trauma Suit", "Old Clothes",
        "Foyer - Basement Key", "Living Room - Backyard Key", "Living Room - Kitchen Key", "Living Room - Foyer Key",
        "Kitchen - Foyer Key", "Foyer - Jenny's Room Key", "Foyer - Bedroom Key",
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
    """When the stickers goal includes the Frog Ring sticker, all nine Frog Ring items are additionally
    required to reach the goal, on top of the usual full-gear requirement, and those items become
    progression so the fill algorithm guarantees they're placed reachably."""

    options = {
        "victory_goal": "stickers",
        "required_stickers": ["Frog Ring"],
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
