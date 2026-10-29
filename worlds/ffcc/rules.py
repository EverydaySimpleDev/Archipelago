"""
How the game gates progress:

  1. YEARS     - each world-map area opens in a certain year (Year N Key items).
  2. MIASMA    - most areas sit behind a Miasma Stream, the chalice must hold
                 the stream's element. Elements come from hotspots inside
                 dungeons, and the Unknown element (Lynari Desert) crosses all.
  3. STAGE KEYS (option) - every dungeon except River Belle Path needs its key.
  4. RINGS     - some dungeons can't be finished without certain spells.
                 Rings count, magicite doesn't (since they are not kept in inventory).
  5. LOADING ZONES (option) - a world-map spot may lead to a different
                 dungeon. Rules follow the SPOT for 1-2 and the DUNGEON for 3-4.
  6. MYRRH     - the year only moves on when the chalice is filled: 3 drops from
                 3 different trees. A harvested tree grows back after 4 drops
                 elsewhere, so from Year 2 on 6 different trees are needed.
                 Each tree is a "Myrrh Drop" event, and "being in Year N" needs
                 the Year Keys and enough Myrrh Drops.
  7. CYCLES    - a dungeon's next cycle comes after its tree is harvested and
                 grows back (4 drops from other trees, 3 drops a year), so
                 cycle N needs about 2 more years per cycle. The chest table
                 (chest_table.py) only lists chests a player can reach in
                 each cycle, so cycle locations just need the right year.

The world needs from generate_early (sent to the randomizer as JSON):
  self.zone_plan   {spot: dungeon}, spots named by their vanilla dungeon
  self.gate_table  Miasma Stream elements, 4 rows (years 1-4, repeating) x 4 gates
  self.hotspots    each dungeon's hotspot elements, 4 rows (years 1-4, repeating)
                   x one element per hotspot (make_hotspots)
  self.menus       each world-map stop's "Change element" choices, 4 rows like
                   the hotspots (make_menus)
"""

from BaseClasses import LocationProgressType
from rule_builder.rules import Has, HasAll, CanReachRegion
from .items import MYRRH_DROP
from .options import VictoryGoal
from .regions import MYRRH_DUNGEONS

FIRE, WATER, WIND, EARTH = "Fire", "Water", "Wind", "Earth"

# 1 + 2: world-map areas
# area: (year it opens, area you reach it from, Miasma Stream gate slot or None)
AREAS = {
    "Tipa Peninsula":    (1, None,                None),
    "Iron Mine Downs":   (1, "Tipa Peninsula",    0),
    "Vale of Alfitaria": (2, "Iron Mine Downs",   1),
    "Veo Lu":            (2, "Vale of Alfitaria", 2),
    "Plains of Fum":     (3, "Iron Mine Downs",   None),   # Jegon River ferry
    "Rebena Plains":     (4, "Plains of Fum",     3),
    # Mount Kilanda is only reached by boat. In Year 4 the only boat that goes
    # there is the Jegon River pier's (in Iron Mine Downs). Port Tipa's only
    # sails while the river is dry, and stops once Veo Lu Sluice is healed.
    "Kilanda Islands":   (4, "Iron Mine Downs",   None),   # Jegon River pier boat
    "Lynari Isle":       (5, "Tipa Peninsula",    None),   # Port Tipa boat
}

# The Jegon River dries up in Year 5 until Veo Lu Sluice is healed (Life on its
# pumpflowers) or Year 8 comes. The Plains of Fum ferry needs that river, so
# Veo Lu Sluice must stay on this side of it, in one of these areas, or a
# player in Year 5 could be cut off from it until Year 8.
SLUICE_AREAS = {"Tipa Peninsula", "Iron Mine Downs", "Vale of Alfitaria", "Veo Lu"}
# Crossing the river (to the Plains of Fum, and so Rebena Plains and the Abyss)
# needs a way to refill it from Year 5 on: Life on the six pumpflowers in Veo
# Lu Sluice. Magicite isn't kept, so that means the Ring of Life. The logic
# always asks for it, so the ring is never placed where a dry river hides it.
RIVER_CROSSING = "Plains of Fum"
RIVER_NEEDS = "Ring of Life"
RIVER_DRY_YEARS = range(5, 8)    # in the game the ferry only stops in Years 5-7

def _stream_sides():
    """{area: the areas reachable from it without crossing a Miasma Stream}.
    The Jegon River ferry and the boats don't cross a stream, so e.g. Iron
    Mine Downs and the Plains of Fum are one side. A stream only lets the
    caravan through while the chalice holds its element, so the element for
    a stream has to be picked up on the side the caravan is coming from."""
    side = {area: {area} for area in AREAS}
    for area, (_, came_from, gate) in AREAS.items():
        if came_from and gate is None:
            merged = side[area] | side[came_from]
            for member in merged:
                side[member] = merged
    return {area: frozenset(members) for area, members in side.items()}


STREAM_SIDE = _stream_sides()

# Which area each world-map spot is in (spots keep their area when shuffled).
TOWN_AREA = {
    "Marr's Pass": "Iron Mine Downs", "Alfitaria": "Vale of Alfitaria",
    "Shella": "Veo Lu", "Fields of Fum": "Plains of Fum", "Leuda": "Lynari Isle",
}

SPOT_AREA = {
    "River Belle Path": "Tipa Peninsula", "Goblin Wall": "Tipa Peninsula",
    "The Mine of Cathuriges": "Iron Mine Downs", "The Mushroom Forest": "Iron Mine Downs",
    "Tida": "Vale of Alfitaria", "Moschet Manor": "Vale of Alfitaria",
    "Veo Lu Sluice": "Veo Lu",
    "Selepation Cave": "Plains of Fum", "Daemon's Court": "Plains of Fum",
    "Conall Curach": "Rebena Plains", "Rebena Te Ra": "Rebena Plains",
    "Lynari Desert": "Lynari Isle",
    "Mount Kilanda": "Kilanda Islands",
}

# Elements a dungeon's hotspots give (they move with the dungeon).
DUNGEON_ELEMENTS = {
    "River Belle Path": [WATER, WIND], "Goblin Wall": [FIRE, EARTH],
    "The Mine of Cathuriges": [FIRE], "The Mushroom Forest": [WATER],
    "Tida": [WIND, EARTH], "Moschet Manor": [WATER, FIRE],
    "Selepation Cave": [WIND], "Lynari Desert": [EARTH],   # + Unknown
}
ELEMENT_BY_VALUE = {1: FIRE, 2: WATER, 4: WIND, 8: EARTH}
UNKNOWN = "Unknown"

# Every hotspot of a dungeon, in the game's order (area file, then the order
# its SPAWN_MONSTER places them). The patcher numbers them the same way.
HOTSPOTS = {
    "River Belle Path": [WATER, WIND, WATER],
    "Goblin Wall": [EARTH, FIRE],
    "The Mine of Cathuriges": [FIRE, FIRE],
    "The Mushroom Forest": [WATER, WATER, WATER],
    "Tida": [WIND, EARTH, EARTH],
    "Moschet Manor": [WATER, FIRE],
    "Selepation Cave": [WIND],
    "Lynari Desert": [EARTH, EARTH, UNKNOWN, EARTH, EARTH],
}
VANILLA_HOTSPOTS = {dungeon: [list(row) for _ in range(4)] for dungeon, row in HOTSPOTS.items()}


def elements_in_year(hotspots, dungeon, y):
    """The elements a dungeon's hotspots give in Year y (Unknown aside)."""
    rows = (hotspots or VANILLA_HOTSPOTS).get(dungeon)
    return set(rows[(y - 1) % 4]) - {UNKNOWN} if rows else set()

# Elements a world-map stage's menu offers (the menu belongs to the stage, so
# with Shuffle Loading Zones these stay put while the dungeons move). In the
# game the menu only appears once that stage is cleared. With Stage
# Keys the patcher makes it always appear and need no key.
# The dungeon whose hotspot gives Unknown, which crosses every Miasma Stream.
UNKNOWN_SOURCE = "Lynari Desert"

SPOT_ELEMENTS = {spot: [e for e in els if e != "Unknown"] for spot, els in DUNGEON_ELEMENTS.items()}
VANILLA_MENUS = {spot: [list(els) for _ in range(4)] for spot, els in SPOT_ELEMENTS.items()}


def menu_elements_in_year(menus, spot, y):
    """The elements a world-map stop's "Change element" menu offers in Year y."""
    rows = (menus or VANILLA_MENUS).get(spot)
    return rows[(y - 1) % 4] if rows else []

# 3: stage keys
def stage_key(dungeon):
    return f"{dungeon} Key"          # e.g. "Goblin Wall Key" (in game: artifact 0xE9)

# 4: rings a dungeon needs to be finished
ALL_RINGS = ["Ring of Fire", "Ring of Blizzard", "Ring of Thunder", "Ring of Life"]
NEEDS_RINGS = {
    "Tida":           ["Ring of Fire"],      # burn the spider webs
    "Rebena Te Ra":   ALL_RINGS,             # red/blue/purple switches + Holy for Lich
    "Lynari Desert":  ALL_RINGS,             # cactus, rock, mushroom and flower puzzles
    "Mount Vellenge": ALL_RINGS,
}
# Chests that only open after something is done in another dungeon:
# {(dungeon, chest): dungeon that has to be reachable first}.
CHEST_NEEDS_DUNGEON = {
    # behind the log bridge, which is blown up with bombs in Daemon's Court
    ("Conall Curach", 12): "Daemon's Court",
    ("Conall Curach", 21): "Daemon's Court",
}

# Rebena Te Ra chests that need tight timing to reach alone (Mog has to cast
# the spell). Only in logic with the "Rebena Te Ra Timed Chests" option.
REBENA_TIMED_CHESTS = (6, 9)

# Holy = an element ring + Ring of Life, so anywhere Lich ends up (boss
# shuffle) needs Ring of Life and one element ring - add it here from the
# boss plan if bosses are shuffled.


# Year a spot first opens: its area's year, except Goblin Wall's spot, which only
# shows up in Year 2 unless the "Goblin Wall in Year 1" option is on.
def spot_open_year(spot, goblin_year1=False):
    if spot == "Goblin Wall" and not goblin_year1:
        return 2
    return AREAS[SPOT_AREA[spot]][0]

YEARS_PER_CYCLE = 2      # tree regrows after 4 other drops, 3 drops per year
LAST_YEAR_KEY = 5        # the game carries on past Year 5

def drops_to_reach(n):
    """Myrrh trees needed before Year n: 3 to leave Year 1, 6 from then on."""
    return 0 if n < 2 else 3 if n == 2 else 6


# Small helpers
def year(n):
    """Rule for 'the player can be in year n' (None = no requirement)."""
    if n < 2:
        return None
    return HasAll(*[f"Year {y} Key" for y in range(2, n + 1)]) & Has(MYRRH_DROP, drops_to_reach(n))


def all_of(*rules):
    """AND together the rules that aren't None."""
    rules = [r for r in rules if r is not None]
    if not rules:
        return None
    out = rules[0]
    for r in rules[1:]:
        out = out & r
    return out


def any_of(*rules):
    """OR together the rules. None (no requirement) makes the whole thing None."""
    if any(r is None for r in rules):
        return None
    out = None
    for r in rules:
        out = r if out is None else out | r
    return out

def first_hunt_cycle(enemy):
    """The earliest cycle an enemy type of the Monster Hunt can be found in
    (Mount Vellenge has a single cycle)."""
    from .locations import MONSTERS
    return min(1 if dungeon == "Mount Vellenge" else min(cycles)
               for dungeon, cycles in MONSTERS[enemy][4].items())


def excluded_count(options):
    """How many of the seed's locations only get filler (see set_location_rules):
    Monster Hunt locations and "Cycle N Reached" past Progression Cycles."""
    from .locations import LOCATION_TABLE, ENEMY_LOCATION_TABLE, hunt_list, enemy_is_boss
    progression_cycles = options.progression_cycles.value
    hunt, bosses = options.monster_hunt_checks, bool(options.monster_hunt_bosses)
    count = 0
    if hunt == hunt.option_enemy_types:
        count += sum(1 for enemy in hunt_list(bosses) if first_hunt_cycle(enemy) > progression_cycles)
    elif hunt == hunt.option_every_enemy:
        count += sum(1 for name, data in ENEMY_LOCATION_TABLE.items()
                     if data.cycle > progression_cycles and (bosses or not enemy_is_boss(name)))
    if options.cycle_location_checks:
        count += sum(1 for name, data in LOCATION_TABLE.items()
                     if data.is_event and data.region != "Menu" and data.cycle > progression_cycles)
    return count


def set_rules(self) -> None:
    if self.options.victory_goal == VictoryGoal.option_all_myrrh:
        # every Myrrh tree reachable (each dungeon's entrance rule already
        # includes its year, Miasma element, stage key and rings)
        self.set_completion_rule(Has(MYRRH_DROP, len(MYRRH_DUNGEONS)))
    elif self.options.victory_goal == VictoryGoal.option_monster_hunt:
        # every enemy type of the hunt can be found
        self.set_completion_rule(all_of(*self.hunt_rules.values()))
    else:
        # final boss: reaching Mount Vellenge (its entrance needs Year 5,
        # Unknown, Veo Lu Sluice, all rings and its key)
        self.set_completion_rule(CanReachRegion("Mount Vellenge"))


def set_location_rules(self) -> None:
    mw, p = self.multiworld, self.player
    plan = self.zone_plan            # {spot: dungeon}, vanilla = every spot to itself
    gates = self.gate_table
    keys_on = bool(getattr(self.options, "stage_keys", False))
    goblin_year1 = self.goblin_year1
    spot_of = {dungeon: spot for spot, dungeon in plan.items()}

    def has_element(element, side, y):
        """Can the chalice be set to `element` on this side of the streams in Year y?
        Enter a dungeon there that has it, use the element menu of a world-map
        stop there (Stage Keys: no key needed), or get Unknown in Lynari
        Desert there (Unknown crosses every stream). Unknown picked up earlier
        doesn't count: the player may not have taken it, or changed element
        since, so Lynari Desert has to be reachable on this side as well."""
        sources = [CanReachRegion(d) for d in HOTSPOTS
                   if (element in elements_in_year(self.hotspots, d, y) or d == UNKNOWN_SOURCE) and d in spot_of
                   and SPOT_AREA[spot_of[d]] in side]
        if keys_on:
            sources += [all_of(can_reach_area(SPOT_AREA[spot]), year(spot_open_year(spot, goblin_year1)))
                        for spot in SPOT_ELEMENTS
                        if element in menu_elements_in_year(self.menus, spot, y)
                        and spot in plan and SPOT_AREA[spot] in side]
        return any_of(*sources)

    area_rules = {}

    def can_reach_area(area):
        if area not in area_rules:
            area_rules[area] = _area_rule(area)
        return area_rules[area]

    def _area_rule(area):
        opens, came_from, gate = AREAS[area]
        rule = all_of(year(opens), can_reach_area(came_from) if came_from else None)
        if area == RIVER_CROSSING:
            rule = all_of(rule, Has(RIVER_NEEDS), CanReachRegion("Veo Lu Sluice"))
        if gate is not None:
            # A Miasma Stream asks for a different element each year (the table
            # repeats every 4 years), so it can be crossed in whichever year the
            # chalice can hold that year's element, not only the year it opens.
            # Years past the last Year Key need nothing more than that key.
            rule = all_of(rule, any_of(*[
                all_of(year(min(y, LAST_YEAR_KEY)),
                       has_element(ELEMENT_BY_VALUE[gates[(y - 1) % 4][gate]], STREAM_SIDE[came_from], y))
                for y in range(opens, opens + 4)
            ]))
        return rule

    # Every dungeon: reach the area of the spot it sits on, then its own key and rings.
    for dungeon, spot in spot_of.items():
        rule = all_of(
            can_reach_area(SPOT_AREA[spot]),
            year(spot_open_year(spot, goblin_year1)),
            Has(stage_key(dungeon)) if keys_on and dungeon != "River Belle Path" else None,
            *[Has(ring) for ring in NEEDS_RINGS.get(dungeon, [])],
        )
        if rule is not None:
            self.set_rule(mw.get_entrance(f"Menu -> {dungeon}", p), rule)

    # Mount Vellenge (never shuffled): Year 5, the Unknown element from Lynari
    # Desert, Veo Lu Sluice cleared, all rings, and its key.
    self.set_rule(mw.get_entrance("Menu -> Mount Vellenge", p), all_of(
        year(5),
        CanReachRegion("Lynari Desert"),
        CanReachRegion("Veo Lu Sluice"),
        Has(stage_key("Mount Vellenge")) if keys_on else None,
        *[Has(ring) for ring in NEEDS_RINGS["Mount Vellenge"]],
    ))

    # Cycle 2/3 locations (chests and "Cycle N Reached"): the dungeon's
    # entrance rule applies through its region. Add the years it takes to
    # harvest the tree and let it grow back. Some chests also need another
    # dungeon first (CHEST_NEEDS_DUNGEON).
    from .locations import LOCATION_TABLE
    timed_chests = bool(getattr(self.options, "rebena_te_ra_timed_chests", False))
    progression_cycles = getattr(self.options, "progression_cycles", None)
    progression_cycles = progression_cycles.value if progression_cycles is not None else 3
    hunt_checks = bool(getattr(self.options, "monster_hunt_checks", False))
    for name, data in LOCATION_TABLE.items():
        if data.region not in spot_of:
            continue
        if data.chest and hunt_checks:
            continue    # with Monster Hunt checks the chests aren't locations
        chest = int(name.rsplit(" ", 1)[1]) if " - Chest " in name else None
        if data.region == "Rebena Te Ra" and chest in REBENA_TIMED_CHESTS and not timed_chests:
            mw.get_location(name, p).progress_type = LocationProgressType.EXCLUDED
        # chests and "Cycle N Reached" past the Progression Cycles option only get filler
        if data.cycle > progression_cycles:
            mw.get_location(name, p).progress_type = LocationProgressType.EXCLUDED
        other = CHEST_NEEDS_DUNGEON.get((data.region, chest))
        need = None
        if data.cycle >= 2:
            opens = spot_open_year(spot_of[data.region], goblin_year1)
            need = min(opens + YEARS_PER_CYCLE * (data.cycle - 1), LAST_YEAR_KEY)
        rule = all_of(year(need) if need else None, CanReachRegion(other) if other else None)
        if rule is not None:
            self.set_rule(mw.get_location(name, p), rule)

    # Monster Hunt: an enemy type can be found in any dungeon it appears in,
    # in a cycle it appears in there (monster_table.py). Types only found in
    # cycles past Progression Cycles only get filler.
    from .locations import hunt_list, monster_location, MONSTERS, ENEMY_LOCATION_TABLE
    from .options import MonsterHuntChecks

    def cycle_year(dungeon, cycle):
        """The year rule for reaching `cycle` of `dungeon` (None for cycle 1)."""
        if cycle < 2 or dungeon == "Mount Vellenge":
            return None
        opens = spot_open_year(spot_of[dungeon], goblin_year1)
        return year(min(opens + YEARS_PER_CYCLE * (cycle - 1), LAST_YEAR_KEY))

    hunt_mode = getattr(self.options, "monster_hunt_checks", None)
    hunt_mode = hunt_mode.value if hunt_mode is not None else 0
    self.hunt_rules = {}
    for enemy in hunt_list(bool(getattr(self.options, "monster_hunt_bosses", True))):
        cycles = MONSTERS[enemy][4]
        self.hunt_rules[enemy] = any_of(*[all_of(CanReachRegion(dungeon), cycle_year(dungeon, min(c)))
                                          for dungeon, c in cycles.items()])
        if hunt_mode == MonsterHuntChecks.option_enemy_types:
            location = mw.get_location(monster_location(enemy), p)
            self.set_rule(location, self.hunt_rules[enemy])
            if first_hunt_cycle(enemy) > progression_cycles:
                location.progress_type = LocationProgressType.EXCLUDED

    # Shop Checks: a shop slot needs its town's world-map area. Shella only
    # lets in a caravan with a Shella Mark (Yukes aside), which the enemies
    # of Veo Lu Sluice drop.
    if getattr(self.options, "shop_checks", False):
        from .locations import SHOP_LOCATIONS, SHOPS
        for name, (_, shop, _, _) in SHOP_LOCATIONS.items():
            town = SHOPS[shop][1]
            rule = all_of(can_reach_area(TOWN_AREA[town]),
                          CanReachRegion("Veo Lu Sluice") if town == "Shella" else None)
            if rule is not None:
                self.set_rule(mw.get_location(name, p), rule)

    # Every Enemy: each enemy's location is in its dungeon's region. It also
    # needs the first cycle it appears in.
    if hunt_mode == MonsterHuntChecks.option_every_enemy:
        for location in mw.get_locations(p):
            data = ENEMY_LOCATION_TABLE.get(location.name)
            if data is None:
                continue
            rule = cycle_year(data.region, data.cycle)
            if rule is not None:
                self.set_rule(location, rule)
            if data.cycle > progression_cycles:
                location.progress_type = LocationProgressType.EXCLUDED

    # A new year begins once the previous year can be finished: be in that
    # year and have enough Myrrh trees to fill the chalice.
    # (self.set_rule registers the indirect conditions CanReachRegion needs.)
    for name, data in LOCATION_TABLE.items():
        if data.region == "Menu" and name.startswith("Year "):
            y = data.cycle                      # Year N Begins stores N here
            self.set_rule(mw.get_location(name, p), all_of(
                year(min(y - 1, LAST_YEAR_KEY)), Has(MYRRH_DROP, drops_to_reach(y))))


def reachable_dungeons(plan, gates, y, open_dungeons=None, elements=(), goblin_year1=False,
                       river_always_dry=False, element_menus=False, hotspots=None, menus=None):
    """Dungeons reachable in Year y on this layout, entering only `open_dungeons`
    (None = all of them). A stream opens when a dungeon on the near side of it
    (STREAM_SIDE) gives the element it asks for this year, or Unknown (Lynari
    Desert on that side). No element is carried over from an earlier year: the
    player may not have kept it. `elements` is only kept for older callers and
    is returned empty.
    The Jegon River ferry needs Veo Lu Sluice in the years the river is dry,
    or in every year with `river_always_dry` (how the AP logic treats it).
    With `element_menus` (Stage Keys), a world-map stop's element menu works
    as soon as its area is reached, without entering the dungeon.
    A dungeon that needs rings (NEEDS_RINGS) only counts once a dungeon that
    needs none is reached, since the rings have to be found somewhere first."""
    spot_of = {dungeon: spot for spot, dungeon in plan.items()}
    areas, reached = set(), set()

    def side_has(element, side):
        if any(element in elements_in_year(hotspots, d, y) or d == UNKNOWN_SOURCE
               for d in reached if SPOT_AREA[spot_of[d]] in side):
            return True
        return element_menus and any(
            element in menu_elements_in_year(menus, spot, y) and spot in plan
            and SPOT_AREA[spot] in side and SPOT_AREA[spot] in areas
            and spot_open_year(spot, goblin_year1) <= y
            for spot in SPOT_ELEMENTS)

    changed = True
    while changed:
        changed = False
        for area, (opens, came_from, gate) in AREAS.items():
            if area in areas or opens > y or (came_from and came_from not in areas):
                continue
            if area == RIVER_CROSSING and "Veo Lu Sluice" not in reached and (river_always_dry or y in RIVER_DRY_YEARS):
                continue
            if gate is not None and not side_has(ELEMENT_BY_VALUE[gates[(y - 1) % 4][gate]], STREAM_SIDE[came_from]):
                continue
            areas.add(area)
            changed = True
        for dungeon, spot in spot_of.items():
            if dungeon in reached or (open_dungeons is not None and dungeon not in open_dungeons):
                continue
            if dungeon in NEEDS_RINGS and not any(d not in NEEDS_RINGS for d in reached):
                continue
            if SPOT_AREA[spot] in areas and spot_open_year(spot, goblin_year1) <= y:
                reached.add(dungeon)
                changed = True
    return reached, set()


def first_year_dungeons(plan, gates, goblin_year1=False, hotspots=None, menus=None):
    """With stage keys: two dungeons whose keys, together with the always-open
    River Belle Path, let the player fill the chalice in Year 1. River Belle
    Path itself must be reachable before any key is found."""
    def reach(open_dungeons):
        return reachable_dungeons(plan, gates, 1, open_dungeons, (), goblin_year1, element_menus=True,
                                  hotspots=hotspots, menus=menus)[0]
    if "River Belle Path" not in reach({"River Belle Path"}):
        return None
    candidates = sorted(reach(None) - {"River Belle Path"})
    for i, a in enumerate(candidates):
        for b in candidates[i + 1:]:
            group = {"River Belle Path", a, b}
            if reach(group) >= group:
                return [a, b]
    return None


def layout_is_beatable(plan, gates, stage_keys=False, goblin_year1=False, hotspots=None, menus=None):
    """Check a world-map layout year by year, as if the player already had every
    key and ring: each year enough Myrrh trees must be reachable to fill the
    chalice (3 in Year 1, 6 from Year 2 on), and by Year 5 every dungeon must be
    reachable. With stage keys, River Belle Path is the only dungeon open at the
    start, so it must be reachable in Year 1 before any key is found. Veo Lu
    Sluice must sit in SLUICE_AREAS.
    `plan` is {spot: dungeon} and `gates` is the Miasma Stream table."""
    sluice = next((spot for spot, dungeon in plan.items() if dungeon == "Veo Lu Sluice"), "Veo Lu Sluice")
    if SPOT_AREA[sluice] not in SLUICE_AREAS:
        return False
    if stage_keys and first_year_dungeons(plan, gates, goblin_year1, hotspots, menus) is None:
        return False
    elements = set()
    for y in range(1, LAST_YEAR_KEY + 1):
        reached, elements = reachable_dungeons(plan, gates, y, None, elements, goblin_year1,
                                               element_menus=stage_keys, hotspots=hotspots, menus=menus)
        trees = len(reached & set(MYRRH_DUNGEONS))
        if y < LAST_YEAR_KEY and trees < drops_to_reach(y + 1):
            return False
    if not set(MYRRH_DUNGEONS) <= reached:
        return False
    # The AP logic asks for Veo Lu Sluice before every river crossing, so
    # everything must also be reachable that way, or the seed can't be filled.
    logic_reached, _ = reachable_dungeons(plan, gates, LAST_YEAR_KEY, None, elements, goblin_year1,
                                          river_always_dry=True, element_menus=stage_keys,
                                          hotspots=hotspots, menus=menus)
    return set(MYRRH_DUNGEONS) <= logic_reached


def stream_needs(gates, row):
    """{side: the elements its streams ask for in that year row}: first the
    streams leading on from that side, in gate order, then the ones leading
    back, so the way home is covered when a side's hotspots have room."""
    needs = {}
    for back in (False, True):
        for area, (_, came_from, gate) in AREAS.items():
            if gate is not None:
                els = needs.setdefault(STREAM_SIDE[area if back else came_from], [])
                element = ELEMENT_BY_VALUE[gates[row][gate]]
                if element not in els:
                    els.append(element)
    return needs


def _distinct(elements):
    """The elements in a list, once each, in order (Unknown left out)."""
    out = []
    for element in elements:
        if element != UNKNOWN and element not in out:
            out.append(element)
    return out


def _share_out(needs, entries, rng=None):
    """{key: its elements} for one year row. `entries` = [(key, side, vanilla
    elements)] in a fixed order. Each entry gets as many different elements
    as `vanilla` has. The entries on a side take turns through the elements
    its streams ask for (stream_needs), so between them they cover every
    one. Spare places take another needed element, then a vanilla one.
    With `rng`, each entry gets random elements instead."""
    turn, out = {}, {}
    for key, side, vanilla in entries:
        els = needs.get(side) or vanilla
        chosen = []
        for _ in vanilla:
            if rng is not None:
                element = rng.choice([e for e in (FIRE, WATER, WIND, EARTH) if e not in chosen])
            else:
                k = turn.get(side, 0)
                turn[side] = k + 1
                element = els[k % len(els)]
                if element in chosen:
                    element = next(e for e in els + vanilla + [FIRE, WATER, WIND, EARTH] if e not in chosen)
            chosen.append(element)
        out[key] = chosen
    return out


def make_hotspots(mode, gates, plan, rng=None):
    """Each dungeon's hotspot elements, one row per year (years 1-4, repeating).
    A dungeon gives as many different elements as it does in vanilla, and
    its pools keep their pattern (River Belle Path's water, wind, water
    becomes A, B, A), so the world map's bubble and menu show the same ones.
    "matched": the elements come from the streams on the dungeon's side that
    year (_share_out), the same way make_menus picks the stops' menus, so a
    dungeon on its own stop gives just what its menu offers.
    "shuffled": random different elements each year.
    Anything else: vanilla. Lynari Desert's Unknown hotspot always stays."""
    if mode not in ("matched", "shuffled"):
        return VANILLA_HOTSPOTS
    # a dungeon's elements in its menu's order, so both pick alike
    order = {dungeon: SPOT_ELEMENTS.get(dungeon) or _distinct(slots) for dungeon, slots in HOTSPOTS.items()}
    table = {dungeon: [] for dungeon in HOTSPOTS}
    entries = [(dungeon, STREAM_SIDE[SPOT_AREA[spot]], order[dungeon])
               for spot, dungeon in ((spot, plan.get(spot)) for spot in SPOT_AREA) if dungeon in HOTSPOTS]
    placed = {key for key, _, _ in entries}
    entries += [(dungeon, None, order[dungeon]) for dungeon in HOTSPOTS if dungeon not in placed]
    for row in range(4):
        chosen = _share_out(stream_needs(gates, row), entries, rng if mode == "shuffled" else None)
        for dungeon, slots in HOTSPOTS.items():
            table[dungeon].append([e if e == UNKNOWN else chosen[dungeon][order[dungeon].index(e)]
                                   for e in slots])
    return table


def make_menus(on, gates):
    """Each world-map stop's "Change element" choices, one row per year
    (years 1-4, repeating). With `on`, the stops on a side take turns through
    the elements its streams ask for that year (_share_out), so between them
    they offer every one. A stop keeps its number of choices, never offers the
    same element twice, and stays with its spot when loading zones are
    shuffled."""
    if not on:
        return VANILLA_MENUS
    menus = {spot: [] for spot in SPOT_ELEMENTS}
    entries = [(spot, STREAM_SIDE[SPOT_AREA[spot]], SPOT_ELEMENTS[spot]) for spot in SPOT_AREA
               if spot in SPOT_ELEMENTS]
    for row in range(4):
        chosen = _share_out(stream_needs(gates, row), entries)
        for spot in SPOT_ELEMENTS:
            menus[spot].append(chosen[spot])
    return menus
