from worlds.generic.Rules import add_rule, set_rule, forbid_item, add_item_rule

def set_rules(self) -> None:

    # Set Toothbrush to only show up in the Living Room
    set_rule(self.multiworld.get_entrance("Living Room - Kitchen", self.player),
             lambda state: state.has("Toothbrush Chibi-Gear", self.player))

    set_rule(self.multiworld.get_entrance("Living Room - Foyer", self.player),
             lambda state: state.has("Toothbrush Chibi-Gear", self.player))

    set_rule(self.multiworld.get_entrance("Living Room - Backyard", self.player),
             lambda state: state.has("Toothbrush Chibi-Gear", self.player))

    # Set Toothbrush to only show up in the Living Room
    set_rule(self.multiworld.get_entrance("Living Room - Kitchen", self.player),
             lambda state: state.has("Mug Chibi-Gear", self.player))

    set_rule(self.multiworld.get_entrance("Living Room - Foyer", self.player),
             lambda state: state.has("Mug Chibi-Gear", self.player))

    set_rule(self.multiworld.get_entrance("Living Room - Backyard", self.player),
             lambda state: state.has("Mug Chibi-Gear", self.player))

    # TODO: Replace with real event / item
    # self.multiworld.completion_condition[self.player] = lambda state: state.has("Chibi-Blaster Chibi-Gear", self.player)

    # from Utils import visualize_regions
    # visualize_regions(self.multiworld.get_region("Menu", self.player), "chibi_robo.puml")



