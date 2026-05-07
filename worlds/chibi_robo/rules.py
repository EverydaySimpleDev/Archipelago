from BaseClasses import ItemClassification as IC, CollectionState
from Utils import visualize_regions
from worlds.chibi_robo import ChibiRoboItem, ChibiRoboItemData
from worlds.generic.Rules import add_rule, set_rule, forbid_item, add_item_rule, allow_self_locking_items
from rule_builder.rules import Has, HasAll, Rule, HasAllCounts, CanReachRegion

blaster = "Chibi-Blaster Chibi-Gear"
mug = "Mug Chibi-Gear"
spoon = "Spoon Chibi-Gear"
tooth_brush = "Toothbrush Chibi-Gear"
squirter = "Squirter Chibi-Gear"
charge_chip = "Charge Chip"
red_shoe = "Red Shoe"
copter = "Chibi-Copter Chibi-Gear"

def set_rules(self) -> None:

    multiworld = self.multiworld
    player = self.player

    backyard_to_living = multiworld.get_entrance("Backyard - Living Room", player)

    kitchen_to_living = multiworld.get_entrance("Kitchen - Living Room", player)

    kitchen_to_foyer = multiworld.get_entrance("Kitchen - Foyer", player)

    living_to_kitchen = multiworld.get_entrance("Living Room - Kitchen", player)

    foyer_to_kitchen = multiworld.get_entrance("Foyer - Kitchen", player)

    living_to_backyard = multiworld.get_entrance("Living Room - Backyard", player)

    reach_second_floor = HasAll("Foyer Ladder", copter) | Has("Foyer Teleport")

    foyer_to_jenny = multiworld.get_entrance("Foyer - Jenny's Room", player)

    foyer_to_bedroom = multiworld.get_entrance("Foyer - Bedroom", player)

    bedroom_to_foyer = multiworld.get_entrance("Bedroom - Foyer", player)

    living_to_foyer = multiworld.get_entrance("Living Room - Foyer", player)

    foyer_to_living = multiworld.get_entrance("Foyer - Living Room", player)

    living_to_spider = multiworld.get_entrance("Living Room - Mother Spider", player)

    can_enter_basement = HasAll(tooth_brush, mug)

    self.set_rule(living_to_foyer, can_enter_basement)

    self.set_rule(kitchen_to_foyer, can_enter_basement)

    can_enter_backyard = Has(blaster)

    self.set_rule(living_to_backyard, can_enter_backyard)

    if self.options.open_upstairs == 0:
        self.set_rule(foyer_to_jenny, reach_second_floor)
        self.set_rule(foyer_to_bedroom, reach_second_floor)

        has_all_items = HasAll(tooth_brush, blaster, charge_chip, squirter, mug, "Alien Ear Chip", "Giga-Battery",
                               "Wedding Band", "Chibi-Radar Chibi-Gear", copter, "Dog Bone", "Foyer Ladder" , "Foyer Teleport")
    else:
        has_all_items = HasAll(tooth_brush, blaster, charge_chip, squirter, mug, "Alien Ear Chip", "Giga-Battery", "Wedding Band", "Chibi-Radar Chibi-Gear", copter, "Dog Bone")

    self.set_rule(living_to_spider, has_all_items)

    self.set_completion_rule(CanReachRegion("Staff Credits"))

    # from Utils import visualize_regions
    # visualize_regions(multiworld.get_region("Menu", self.player), "chibi_robo.puml")

def set_location_rules(self) -> None:

    multiworld = self.multiworld
    player = self.player

    can_hover = Has(copter)

    has_blaster = Has(blaster)

    blaster_copter_lr_ladder = HasAll(blaster, copter, "Living Room Ladder", tooth_brush, mug)

    blaster_copter_lr_ladder_lr_bridge = HasAll(blaster, copter, "Living Room Ladder", "Living Room Bridge", tooth_brush, mug)

    reach_charger = HasAll( blaster, mug, copter, tooth_brush)

    # Living Room
    living_room_frog_ring_window = multiworld.get_location("Living Room - Frog Ring (Behind Window)", player)
    self.set_rule(living_room_frog_ring_window, blaster_copter_lr_ladder)

    living_room_frog_ring_corkboard = multiworld.get_location("Living Room - Frog Ring (Corkboard)", player)
    self.set_rule(living_room_frog_ring_corkboard, blaster_copter_lr_ladder_lr_bridge)

    living_room_table_cookie_box_a = multiworld.get_location("Living Room - Table Cookie Box A", player)
    self.set_rule(living_room_table_cookie_box_a, can_hover)

    living_room_table_cookie_box_b = multiworld.get_location("Living Room - Table Cookie Box B", player)
    self.set_rule(living_room_table_cookie_box_b, can_hover)

    living_room_cupholder_candy_wrapper = multiworld.get_location("Living Room - Cupholder Candy Wrapper", player)
    self.set_rule(living_room_cupholder_candy_wrapper, can_hover)

    living_room_cupholder_wastepaper = multiworld.get_location("Living Room - Cupholder Wastepaper", player)
    self.set_rule(living_room_cupholder_wastepaper, can_hover)

    living_room_cookie_crumbs_on_couch = multiworld.get_location("Living Room - Cookie Crumbs on Couch", player)
    self.set_rule(living_room_cookie_crumbs_on_couch, can_hover)

    living_room_couch_wastepaper_a = multiworld.get_location("Living Room - Couch Wastepaper A", player)
    self.set_rule(living_room_couch_wastepaper_a, can_hover)

    living_room_couch_wastepaper_b = multiworld.get_location("Living Room - Couch Wastepaper B", player)
    self.set_rule(living_room_couch_wastepaper_b, can_hover)

    living_room_couch_candy_bag = multiworld.get_location("Living Room - Couch Candy Bag", player)
    self.set_rule(living_room_couch_candy_bag, can_hover)

    living_room_couch_candy_wrapper = multiworld.get_location("Living Room - Couch Candy Wrapper", player)
    self.set_rule(living_room_couch_candy_wrapper, can_hover)

    # Kitchen
    has_kitchen_ladder = Has("Kitchen Ladder")

    has_k_ladder_blaster_copter = HasAll("Kitchen Ladder", blaster, copter)

    kitchen_spoon = multiworld.get_location("Kitchen - Spoon Location", player)
    self.set_rule(kitchen_spoon, has_kitchen_ladder)

    kitchen_cookie_crumb_by_spoon = multiworld.get_location("Kitchen - Cookie Crumbs by Spoon", player)
    self.set_rule(kitchen_cookie_crumb_by_spoon, has_kitchen_ladder)

    kitchen_cookie_box_a_by_spoon = multiworld.get_location("Kitchen - Cookie Box by Spoon A", player)
    self.set_rule(kitchen_cookie_box_a_by_spoon, has_kitchen_ladder)

    kitchen_cookie_box_b_by_spoon = multiworld.get_location("Kitchen - Cookie Box by Spoon B", player)
    self.set_rule(kitchen_cookie_box_b_by_spoon, has_kitchen_ladder)

    kitchen_bandage = multiworld.get_location("Kitchen - Bandage Location", player)
    self.set_rule(kitchen_bandage, has_k_ladder_blaster_copter)

    kitchen_frog_ring_table = multiworld.get_location("Kitchen - Frog Ring (Table)", player)
    self.set_rule(kitchen_frog_ring_table, has_blaster)

    #  Drain
    has_blaster_copter = HasAll(blaster, copter)
    sink_frog_ring = multiworld.get_location("Sink Drain - Frog Ring", player)
    self.set_rule(sink_frog_ring, has_blaster_copter)

    #  Foyer
    has_copter_f_ladder_blaster = HasAll(copter, "Foyer Ladder", blaster) | HasAll(copter, "Foyer Teleport", blaster)

    foyer_frog_ring = multiworld.get_location("Foyer - Waterfall Frog Ring", player)
    self.set_rule(foyer_frog_ring, has_copter_f_ladder_blaster)

    has_copter_f_ladder = HasAll(copter, "Foyer Ladder") | HasAll(copter, "Foyer Teleport")

    foyer_red_block = multiworld.get_location("Foyer - Red Block", player)
    self.set_rule(foyer_red_block, has_copter_f_ladder)

    #  Basement
    basement_giga_charger = multiworld.get_location("Basement - Giga Charger", player)
    self.set_rule(basement_giga_charger, reach_charger)

    basement_waste_paper_on_shelf = multiworld.get_location("Basement - Wastepaper on Shelf", player)
    self.set_rule(basement_waste_paper_on_shelf, reach_charger)

    basement_gunpowder = multiworld.get_location("Basement - Gunpowder", player)
    self.set_rule(basement_gunpowder, reach_charger)

    basement_frog_ring = multiworld.get_location("Basement - Frog Ring", player)
    self.set_rule(basement_frog_ring, reach_charger)

    basement_purple_can = multiworld.get_location("Basement - Purple Can", player)
    self.set_rule(basement_purple_can, reach_charger)

    basement_cabinet_trash_a = multiworld.get_location("Basement - Cabinet Trash A", player)
    self.set_rule(basement_cabinet_trash_a, reach_charger)

    basement_cabinet_trash_b = multiworld.get_location("Basement - Cabinet Trash B", player)
    self.set_rule(basement_cabinet_trash_b, reach_charger)

    # Backyard

    has_blaster_copter_charge_chip_squirter = HasAll(copter, "Charge Chip", blaster, squirter)

    # backyard_ship = multiworld.get_location("Backyard - Scurvy Splinter", player)
    # self.set_rule(backyard_ship, reach_ship)

    backyard_white_block = multiworld.get_location("Backyard - White Block", player)
    self.set_rule(backyard_white_block, has_blaster_copter_charge_chip_squirter)

    # Jenny's Room

    reach_j_batteries = HasAll(copter, "Red Shoe", blaster, "Foyer Ladder", mug) | HasAll(copter, "Red Shoe", blaster, "Foyer Teleport", mug)

    jenny_aa_battery = multiworld.get_location("Jenny's Room - AA Battery", player)
    self.set_rule(jenny_aa_battery, reach_j_batteries)

    jenny_d_battery = multiworld.get_location("Jenny's Room - D Battery", player)
    self.set_rule(jenny_d_battery, reach_j_batteries)

    jenny_c_battery = multiworld.get_location("Jenny's Room - C Battery", player)
    self.set_rule(jenny_c_battery, reach_j_batteries)

    jenny_purple_crayon = multiworld.get_location("Jenny's Room - Purple Crayon", player)
    self.set_rule(can_hover, jenny_purple_crayon)

    # Bedroom
    bedroom_ticket_stub = multiworld.get_location("Bedroom - Ticket Stub", player)
    self.set_rule(bedroom_ticket_stub, can_hover)

    bedroom_wastepaper_on_vanity = multiworld.get_location("Bedroom - Wastepaper on Vanity", player)
    self.set_rule(bedroom_wastepaper_on_vanity, can_hover)

    bedroom_wastepaper_on_bed = multiworld.get_location("Bedroom - Wastepaper on Bed", player)
    self.set_rule(bedroom_wastepaper_on_bed, can_hover)

    bedroom_wastepaper_by_dinah_place_a = multiworld.get_location("Bedroom - Wastepaper by Dinahs Place A", player)
    self.set_rule(bedroom_wastepaper_by_dinah_place_a, can_hover)

    bedroom_wastepaper_by_dinah_place_b = multiworld.get_location("Bedroom - Wastepaper by Dinahs Place B", player)
    self.set_rule(bedroom_wastepaper_by_dinah_place_b, can_hover)

    bedroom_cookie_crumb_on_toybox = multiworld.get_location("Bedroom - Cookie Crumbs on Toybox", player)
    self.set_rule(bedroom_cookie_crumb_on_toybox, can_hover)

    bedroom_vanity_candy_wrapper_a = multiworld.get_location("Bedroom - Vanity Candy Wrapper A", player)
    self.set_rule(bedroom_vanity_candy_wrapper_a, can_hover)

    bedroom_vanity_candy_wrapper_b = multiworld.get_location("Bedroom - Vanity Candy Wrapper B", player)
    self.set_rule(bedroom_vanity_candy_wrapper_b, can_hover)

    bedroom_vanity_candy_bag = multiworld.get_location("Bedroom - Vanity Candy Bag", player)
    self.set_rule(bedroom_vanity_candy_bag, can_hover)

