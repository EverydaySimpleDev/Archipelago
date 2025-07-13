from BaseClasses import ItemClassification as IC
from Utils import visualize_regions
from worlds.chibi_robo import ChibiRoboItem, ChibiRoboItemData
from worlds.generic.Rules import add_rule, set_rule, forbid_item, add_item_rule, allow_self_locking_items

blaster = "Chibi-Blaster Chibi-Gear"
mug = "Mug Chibi-Gear"
spoon = "Spoon Chibi-Gear"
tooth_brush = "Toothbrush Chibi-Gear"
squirter = "Squirter Chibi-Gear"
charge_chip = "Charge Chip"
red_shoe = "Red Shoe"

def set_rules(self) -> None:

    multiworld = self.multiworld
    player = self.player


    set_rule(multiworld.get_entrance('Foyer - Kitchen', player),
             lambda state: state.has(mug, player))

    set_rule(multiworld.get_entrance('Living Room - Foyer', player),
             lambda state: state.has(mug, player))

    set_rule(multiworld.get_entrance('Living Room - Backyard', player),
             lambda state: state.has(mug, player))

    set_rule(multiworld.get_entrance('Backyard - Living Room', player),
             lambda state: state.has(blaster, player))

    set_rule(multiworld.get_entrance("Jenny's Room - Foyer", player),
             lambda state: state.has(mug, player))

    set_rule(multiworld.get_entrance('Living Room - Kitchen', player),
             lambda state: state.has(tooth_brush, player))

    set_rule(multiworld.get_entrance('Living Room - Foyer', player),
             lambda state: state.has(tooth_brush, player))

    set_rule(multiworld.get_entrance('Living Room - Backyard', player),
             lambda state: state.has(tooth_brush, player))

    set_rule(multiworld.get_entrance('Backyard - Living Room', player),
             lambda state: state.has(tooth_brush, player))

    set_rule(multiworld.get_entrance('Living Room - Mother Spider', player),
             lambda state: state.has(spoon, self.player) and
                           state.has(blaster, self.player) and
                           state.has(tooth_brush, self.player) and
                           state.has(charge_chip, self.player) and
                           state.has(squirter, self.player) and
                           state.has(mug, self.player) and
                           state.has("Alien Ear Chip", self.player) and
                           state.has("Giga-Battery", self.player) and
                           state.has("Giga-Charger", self.player) and
                           state.has("Left Leg", self.player) and
                           state.has("Toy Receipt", self.player) and
                           state.has("Wedding Band", self.player) and
                           state.has("Chibi-Radar Chibi-Gear", self.player))

    # TODO: Replace with real event / item
    multiworld.completion_condition[player] = lambda state: state.can_reach_region("Staff Credits", player)

    # from Utils import visualize_regions
    visualize_regions(multiworld.get_region("Menu", self.player), "chibi_robo.puml")

def set_location_rules(self) -> None:

    multiworld = self.multiworld
    player = self.player

    #  TODO: Look Into Copter Item
    # copter = "Chibi-Copter Chibi-Gear"

    # Living Room
    add_rule(multiworld.get_location("Living Room - Frog Ring (Behind Window)", player),
             lambda state: state.has(blaster, player))

    # Kitchen
    add_rule(multiworld.get_location("Kitchen - Table Happy Block", player),
             lambda state: state.has(blaster, player))

    add_rule(multiworld.get_location("Kitchen - Cabinet Happy Block", player),
             lambda state: state.has(blaster, player))

    add_rule(multiworld.get_location("Kitchen - Bandage Location", player),
             lambda state: state.has(blaster, player))

    add_rule(multiworld.get_location("Kitchen - Frog Ring (Table)", player),
             lambda state: state.has(blaster, player))

    add_rule(multiworld.get_location("Kitchen - High Cupboard 10M Coin", player),
             lambda state: state.has(blaster, player))

    #  Drain
    add_rule(multiworld.get_location("Sink Drain - Frog Ring", player),
             lambda state: state.has(blaster, player))

    #  Foyer
    add_rule(multiworld.get_location("Foyer - Waterfall Frog Ring", player),
             lambda state: state.has(blaster, player))

    #  Foyer
    add_rule(multiworld.get_location("Foyer - Waterfall Frog Ring", player),
             lambda state: state.has(blaster, player))

    #  Basement
    add_rule(multiworld.get_location("Basement - Giga Charger", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    add_rule(multiworld.get_location("Basement - Wastepaper on Shelf", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    add_rule(multiworld.get_location("Basement - Gunpowder", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    add_rule(multiworld.get_location("Basement - Frog Ring", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    add_rule(multiworld.get_location("Basement - Purple Can", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    add_rule(multiworld.get_location("Basement - Cabinet Trash A", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    add_rule(multiworld.get_location("Basement - Cabinet Trash B", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    add_rule(multiworld.get_location("Basement - Shelf Happy Block B", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    add_rule(multiworld.get_location("Basement - Shelf Happy Block A", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    add_rule(multiworld.get_location("Basement - Rafters Happy Block B", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    add_rule(multiworld.get_location("Basement - Rafters Happy Block A", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    add_rule(multiworld.get_location("Basement - Swing 10M Coin", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    # Backyard
    add_rule(multiworld.get_location("Backyard - Scurvy Splinter", player),
             lambda state: state.has(spoon, self.player) and
                           state.has(blaster, self.player))

    add_rule(multiworld.get_location("Backyard - Right Awning Happy Block C", player),
             lambda state: state.has(spoon, self.player) and
                           state.has(blaster, self.player) and
                           state.has(charge_chip, self.player)and
                           state.has(squirter, self.player))

    add_rule(multiworld.get_location("Backyard - Right Awning Happy Block B", player),
             lambda state: state.has(spoon, self.player) and
                           state.has(blaster, self.player) and
                           state.has(charge_chip, self.player) and
                           state.has(squirter, self.player))

    add_rule(multiworld.get_location("Backyard - Left Awning Happy Block", player),
             lambda state: state.has(spoon, self.player) and
                           state.has(blaster, self.player) and
                           state.has(charge_chip, self.player) and
                           state.has(squirter, self.player))

    add_rule(multiworld.get_location("Backyard - Tree Happy Block", player),
             lambda state: state.has(blaster, self.player) and
                           state.has(charge_chip, self.player))

    add_rule(multiworld.get_location("Backyard - Right Awning Happy Block A", player),
             lambda state: state.has(spoon, self.player) and
                           state.has(blaster, self.player) and
                           state.has(charge_chip, self.player) and
                           state.has(squirter, self.player))

    add_rule(multiworld.get_location("Backyard - White Block", player),
             lambda state: state.has(spoon, self.player) and
                           state.has(blaster, self.player) and
                           state.has(charge_chip, self.player) and
                           state.has(squirter, self.player))

    # Jenny's Room
    add_rule(multiworld.get_location("Jenny's Room - AA Battery", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    add_rule(multiworld.get_location("Jenny's Room - D Battery", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    add_rule(multiworld.get_location("Jenny's Room - C Battery", player),
             lambda state: state.has(mug, self.player) and
                           state.has(blaster, self.player))

    # add_rule(multiworld.get_location("Victory", player),
    #          lambda state: state.has(spoon, self.player) and
    #                        state.has(blaster, self.player) and
    #                        state.has(tooth_brush, self.player) and
    #                        state.has(charge_chip, self.player) and
    #                        state.has(squirter, self.player) and
    #                        state.has(mug, self.player) and
    #                        state.has("Alien Ear Chip", self.player) and
    #                        state.has("Giga-Battery", self.player) and
    #                        state.has("Giga-Charger", self.player) and
    #                        state.has("Left Leg", self.player) and
    #                        state.has("Toy Receipt", self.player) and
    #                        state.has("Wedding Band", self.player) and
    #                        state.has("Chibi-Radar Chibi-Gear", self.player))


