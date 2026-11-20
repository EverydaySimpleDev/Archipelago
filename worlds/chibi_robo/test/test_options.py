from .bases import ChibiRoboTestBase
from ..options import STICKER_NAMES


class DefaultStickerGoalTest(ChibiRoboTestBase):
    def test_default_requires_every_sticker(self) -> None:
        self.assertEqual(self.world.options.required_stickers.value, STICKER_NAMES)


class RandomStickerGoalTest(ChibiRoboTestBase):
    options = {"required_stickers": ["Random"]}

    def test_random_resolves_to_a_nonempty_real_subset(self) -> None:
        stickers = self.world.options.required_stickers.value
        self.assertTrue(stickers)
        self.assertNotIn("Random", stickers)
        self.assertTrue(stickers <= STICKER_NAMES)


class EmptyStickerGoalTest(ChibiRoboTestBase):
    options = {"required_stickers": []}

    def test_empty_selection_resolves_to_a_nonempty_real_subset(self) -> None:
        stickers = self.world.options.required_stickers.value
        self.assertTrue(stickers)
        self.assertTrue(stickers <= STICKER_NAMES)


class PjSuitStyleTest(ChibiRoboTestBase):
    def test_each_style_maps_to_a_distinct_object_name(self) -> None:
        expected = {
            "old_boxers": "item_pajama_kiji_2",
            "outdated_scarf": "item_pajama_kiji_3",
            "small_handkerchief": "item_pajama_kiji",
        }
        for style, object_name in expected.items():
            with self.subTest(style=style):
                self.world.options.pj_suit_style.value = self.world.options.pj_suit_style.from_any(style).value
                self.assertEqual(
                    self.world._get_object_name("Old Clothes", self.player, self.player, self.world.options),
                    object_name,
                )
