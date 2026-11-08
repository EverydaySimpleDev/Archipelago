from test.bases import WorldTestBase

from ..game_id import game_name


class FFCCTestBase(WorldTestBase):
    """A solo FFCC world. A test class that sets `options` also gets Archipelago's default
    checks: every location reachable with all items, something reachable with none, and a fill."""
    game = game_name
