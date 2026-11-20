"""The client works out which of the player's own items the game gives by itself (from a chest or a shop), with the
same rule the patcher uses to put them there."""
import types

from Fill import distribute_items_restrictive

from .bases import FFCCTestBase
from ..client import _given_by_the_game


class TestGivenByTheGame(FFCCTestBase):
    options = {"shop_checks": True}

    def test_client_matches_patcher(self) -> None:
        distribute_items_restrictive(self.multiworld)
        ctx = types.SimpleNamespace(physical_chest_ap_ids=set(), slot=self.player)
        checked = 0
        for location in self.multiworld.get_locations(self.player):
            if location.address is None or location.item is None or location.item.code is None:
                continue
            patcher = self.world._item_in_chest(location) or self.world._shop_item_id(location) is not None
            received = types.SimpleNamespace(item=location.item.code, location=location.address,
                                             player=location.item.player)
            self.assertEqual(_given_by_the_game(ctx, received), patcher, location.name)
            checked += 1
        self.assertGreater(checked, 0)

    def test_old_seeds_still_use_their_list(self) -> None:
        """Seeds made before this still send the list in their slot data."""
        ctx = types.SimpleNamespace(physical_chest_ap_ids={12345}, slot=self.player)
        received = types.SimpleNamespace(item=0, location=12345, player=self.player + 1)
        self.assertTrue(_given_by_the_game(ctx, received))
