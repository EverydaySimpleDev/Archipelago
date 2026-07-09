from rule_builder.rules import Has, HasAll, Rule, HasAllCounts, CanReachRegion


def set_rules(self) -> None:
    self.set_completion_rule(CanReachRegion("Mount Vellenge"))


def set_location_rules(self) -> None:
    mw = self.multiworld
    p  = self.player

    # ── Year Key gates ────────────────────────────────────────────────────────
    # Cumulative HasAll prevents circular placement (Year N Key can't land in a
    # dungeon that itself requires Year N Key).
    y2 = Has("Year 2 Key")
    y3 = HasAll("Year 2 Key", "Year 3 Key")
    y4 = HasAll("Year 2 Key", "Year 3 Key", "Year 4 Key")
    y5 = HasAll("Year 2 Key", "Year 3 Key", "Year 4 Key", "Year 5 Key")

    # ── Spell Ring gates ──────────────────────────────────────────────────────
    # Ring of <Element> permanently slots a spell that persists between dungeons.
    # Consumable Magicite Stones are NOT used here — they can be spent before
    # the gated dungeon and would give AP a false sense of availability.
    fire    = Has("Ring of Fire")
    bliz    = Has("Ring of Blizzard")
    thunder = Has("Ring of Thunder")
    life    = Has("Ring of Life")   # Holy = Life + any element

    # ── Dungeon entrance rules ─────────────────────────────────────────────────
    # Year 1 dungeons — always accessible, no key or spell required.
    # (River Belle Path, Mine of Cathuriges, Mushroom Forest)

    # Year 2 dungeons
    self.set_rule(mw.get_entrance("Menu -> Goblin Wall",   p), y2)
    self.set_rule(mw.get_entrance("Menu -> Veo Lu Sluice", p), y2)
    # Tida: Fire magic required to burn ivy off key pedestals — without it the
    # player cannot insert keys and cannot progress through the dungeon.
    self.set_rule(mw.get_entrance("Menu -> Tida",          p), y2 & fire)

    # Year 3 dungeons
    self.set_rule(mw.get_entrance("Menu -> Moschet Manor",    p), y3)
    self.set_rule(mw.get_entrance("Menu -> Daemon's Court",   p), y3)
    self.set_rule(mw.get_entrance("Menu -> Selepation Cave",  p), y3)

    # Year 4 dungeons
    self.set_rule(mw.get_entrance("Menu -> Mount Kilanda",  p), y4)
    self.set_rule(mw.get_entrance("Menu -> Conall Curach",  p), y4)
    # Rebena Te Ra: red/blue/purple magic switches require Fire, Blizzard, and
    # Thunder respectively — all three must be hit to open mandatory locked doors.
    self.set_rule(mw.get_entrance("Menu -> Rebena Te Ra",   p), y4 & fire & bliz & thunder)

    # Year 5 dungeons
    # Lynari Desert: environmental puzzles require all four elements —
    #   Thunder (cactus), Fire (mushroom rock), Blizzard (rocks), Holy (flower).
    # Holy = Life + any element, so Ring of Life is mandatory.
    all_rings = fire & bliz & thunder & life
    self.set_rule(mw.get_entrance("Menu -> Lynari Desert",    p), y5 & all_rings)
    # Mount Vellenge requires the Holy chalice element from Lynari Desert's flower puzzle.
    self.set_rule(mw.get_entrance("Menu -> Mount Vellenge",   p), y5 & all_rings)

    # ── Year N Begins location rules ──────────────────────────────────────────
    # Prevents AP from placing items in Year N Begins before the player can
    # realistically reach Year N in-game.
    for year in range(3, 6):
        self.set_rule(
            mw.get_location(f"Year {year} Begins", p),
            Has(f"Year {year - 1} Key"),
        )
