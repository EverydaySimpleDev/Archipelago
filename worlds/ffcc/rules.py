from BaseClasses import ItemClassification as IC, CollectionState
from Utils import visualize_regions
from worlds.ffcc import FFCCItem, FFCCItemData
from worlds.generic.Rules import add_rule, set_rule, forbid_item, add_item_rule, allow_self_locking_items
from rule_builder.rules import Has, HasAll, Rule, HasAllCounts, CanReachRegion

def set_rules(self) -> None:

    multiworld = self.multiworld
    player = self.player

    self.set_completion_rule(CanReachRegion("Staff Credits"))

    # from Utils import visualize_regions
    # visualize_regions(multiworld.get_region("Menu", self.player), "chibi_robo.puml")

def set_location_rules(self) -> None:

    multiworld = self.multiworld
    player = self.player


    # bedroom_pajama_suit = multiworld.get_location("Bedroom - Pajama Suit", player)
    # self.set_rule(bedroom_pajama_suit, can_reach_pajama)

