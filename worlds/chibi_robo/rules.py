from worlds.generic.Rules import add_rule, set_rule, forbid_item, add_item_rule

def set_rules(self) -> None:

    set_rule(self.multiworld.get_entrance("Living Room - Foyer", self.player),
             lambda state: state.has("Mug Chibi-Gear", self.player))

    set_rule(self.multiworld.get_entrance("Living Room - Backyard", self.player),
             lambda state: state.has("Chibi-Blaster Chibi-Gear", self.player))

    # self.multiworld.get_location("Staff Credits", self.player).place_locked_item(self.create_event("Victory"))
    #
    # self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)


