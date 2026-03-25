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

def set_rules(self) -> None:

    multiworld = self.multiworld
    player = self.player

    backyard_to_living = multiworld.get_entrance("Backyard - Living Room", player)

    kitchen_to_living = multiworld.get_entrance("Kitchen - Living Room", player)

    kitchen_to_foyer = multiworld.get_entrance("Kitchen - Foyer", player)

    living_to_kitchen = multiworld.get_entrance("Living Room - Kitchen", player)

    foyer_to_kitchen = multiworld.get_entrance("Foyer - Kitchen", player)

    living_to_backyard = multiworld.get_entrance("Living Room - Backyard", player)

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

    self.set_rule(foyer_to_jenny, can_enter_backyard)

    self.set_rule(foyer_to_bedroom, can_enter_backyard)

    has_all_items = HasAll(tooth_brush, blaster, charge_chip, squirter, mug, "Alien Ear Chip", "Giga-Battery", "Wedding Band", "Chibi-Radar Chibi-Gear")

    self.set_rule(living_to_spider, has_all_items)

    self.set_completion_rule(CanReachRegion("Staff Credits"))

    # from Utils import visualize_regions
    # visualize_regions(multiworld.get_region("Menu", self.player), "chibi_robo.puml")

def set_location_rules(self) -> None:

    multiworld = self.multiworld
    player = self.player

    has_blaster = Has(blaster)

    reach_charger = HasAll( blaster, mug)

    reach_ship = HasAll(spoon, blaster)

    reach_backyard_awning = HasAll(spoon, blaster, charge_chip, squirter)

    reach_backyard_tree_happy_block = HasAll( blaster, charge_chip)

    # reach_jenny_battery = Has(red_shoe) & Has (blaster)

    # Living Room
    living_room_frog_ring_window = multiworld.get_location("Living Room - Frog Ring (Behind Window)", player)
    self.set_rule(living_room_frog_ring_window, has_blaster)

    # living_room_frog_ring_window = multiworld.get_location("Living Room - Plant Shelf Happy Block (Upper)", player)
    # self.set_rule(living_room_frog_ring_window, has_blaster)
    #
    # living_room_frog_ring_window = multiworld.get_location("Living Room - Happy Block above Fireplace", player)
    # self.set_rule(living_room_frog_ring_window, has_blaster)
    #
    # living_room_frog_ring_window = multiworld.get_location("Living Room - Happy Block above Chibi House", player)
    # self.set_rule(living_room_frog_ring_window, has_blaster)

    # Kitchen
    kitchen_table_happy_block = multiworld.get_location("Kitchen - Spoon Location", player)
    self.set_rule(kitchen_table_happy_block, has_blaster)

    # kitchen_table_happy_block = multiworld.get_location("Kitchen - Table Happy Block", player)
    # self.set_rule(kitchen_table_happy_block, has_blaster)

    # kitchen_cabinet_happy_block = multiworld.get_location("Kitchen - Cabinet Happy Block", player)
    # self.set_rule(kitchen_cabinet_happy_block, has_blaster)

    kitchen_bandage = multiworld.get_location("Kitchen - Bandage Location", player)
    self.set_rule(kitchen_bandage, has_blaster)

    kitchen_frog_ring_table = multiworld.get_location("Kitchen - Frog Ring (Table)", player)
    self.set_rule(kitchen_frog_ring_table, has_blaster)

    # kitchen_high_cupboard_10_coin = multiworld.get_location("Kitchen - High Cupboard 10M Coin", player)
    # self.set_rule(kitchen_high_cupboard_10_coin, has_blaster)

    #  Drain
    sink_frog_ring = multiworld.get_location("Sink Drain - Frog Ring", player)
    self.set_rule(sink_frog_ring, has_blaster)

    #  Foyer
    foyer_frog_ring = multiworld.get_location("Foyer - Waterfall Frog Ring", player)
    self.set_rule(foyer_frog_ring, has_blaster)

    # foyer_frog_ring = multiworld.get_location("Foyer - Top of Stairs 10M Coin", player)
    # self.set_rule(foyer_frog_ring, has_blaster)

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

    # basement_shelf_happy_block_b= multiworld.get_location("Basement - Shelf Happy Block B", player)
    # self.set_rule(basement_shelf_happy_block_b, reach_charger)
    #
    # basement_shelf_happy_block_a = multiworld.get_location("Basement - Shelf Happy Block A", player)
    # self.set_rule(basement_shelf_happy_block_a, reach_charger)
    #
    # basement_rafters_happy_block_b = multiworld.get_location("Basement - Rafters Happy Block B", player)
    # self.set_rule(basement_rafters_happy_block_b, reach_charger)
    #
    # basement_rafters_happy_block_a = multiworld.get_location("Basement - Rafters Happy Block A", player)
    # self.set_rule(basement_rafters_happy_block_a, reach_charger)
    #
    # basement_swing_10m_coin = multiworld.get_location("Basement - Swing 10M Coin", player)
    # self.set_rule(basement_swing_10m_coin, reach_charger)

    # Backyard
    backyard_ship = multiworld.get_location("Backyard - Scurvy Splinter", player)
    self.set_rule(backyard_ship, reach_ship)

    # backyard_right_awning_happy_block_c = multiworld.get_location("Backyard - Right Awning Happy Block C", player)
    # self.set_rule(backyard_right_awning_happy_block_c, reach_backyard_awning)
    #
    # backyard_right_awning_happy_block_b = multiworld.get_location("Backyard - Right Awning Happy Block B", player)
    # self.set_rule(backyard_right_awning_happy_block_b, reach_backyard_awning)
    #
    # backyard_left_awning_happy_block = multiworld.get_location("Backyard - Left Awning Happy Block", player)
    # self.set_rule(backyard_left_awning_happy_block, reach_backyard_awning)
    #
    # backyard_tree_happy_block = multiworld.get_location("Backyard - Tree Happy Block", player)
    # self.set_rule(backyard_tree_happy_block, reach_backyard_tree_happy_block)
    #
    # backyard_right_awning_happy_block_a = multiworld.get_location("Backyard - Right Awning Happy Block A", player)
    # self.set_rule(backyard_right_awning_happy_block_a, reach_backyard_awning)

    backyard_white_block= multiworld.get_location("Backyard - White Block", player)
    self.set_rule(backyard_white_block, reach_backyard_awning)

    # Jenny's Room
    # jenny_aa_battery = multiworld.get_location("Jenny's Room - AA Battery", player)
    # self.set_rule(jenny_aa_battery, reach_jenny_battery)

    # jenny_d_battery = multiworld.get_location("Jenny's Room - D Battery", player)
    # self.set_rule(jenny_d_battery, reach_jenny_battery)

    # jenny_c_battery = multiworld.get_location("Jenny's Room - C Battery", player)
    # self.set_rule(jenny_c_battery, reach_jenny_battery)


