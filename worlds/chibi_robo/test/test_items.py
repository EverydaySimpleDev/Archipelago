from .bases import ChibiRoboTestBase
from ..items import FILLER_ITEM_TABLE


class FillerItemTest(ChibiRoboTestBase):
    def test_every_filler_item_name_is_creatable(self) -> None:
        for name in FILLER_ITEM_TABLE:
            with self.subTest(name=name):
                self.world.create_item(name)

    def test_get_filler_item_name_is_always_creatable(self) -> None:
        for _ in range(20):
            name = self.world.get_filler_item_name()
            with self.subTest(name=name):
                self.world.create_item(name)


class EarlyItemsTest(ChibiRoboTestBase):
    def test_starting_gear_is_forced_early(self) -> None:
        early_items = self.multiworld.local_early_items[self.player]
        for name in ("Toothbrush Chibi-Gear", "Mug Chibi-Gear", "Drake Redcrest Suit"):
            with self.subTest(name=name):
                self.assertIn(name, early_items)
                self.assertGreaterEqual(early_items[name], 1)
