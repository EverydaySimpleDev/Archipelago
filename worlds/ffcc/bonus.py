"""
The world decides each seed's pools here, so the patcher, the client
and the trackers all see the same items.
"""
from typing import Dict, List, Optional

from .bonus_table import BONUS_TABLE, BONUS_CANDIDATES, ITEM_NAMES
from .items import STAGE_KEYS

# Items a randomized pool never gets: the Spell Rings (Fire, Blizzard, Thunder,
# Life) and the stage keys, which the logic treats as progression, and the
# AP Item.
NOT_IN_BONUS = {0xdf, 0xe0, 0xe1, 0xe3, 0x162} | {iid for _, iid in STAGE_KEYS}
RANDOM_CANDIDATES = [v for v in BONUS_CANDIDATES if v not in NOT_IN_BONUS]

# Bonus points are multiplied by this before they're compared with a tier's
# threshold: index = number of players - 1.
PLAYER_FACTOR = (1.35, 1.25, 1.1, 1.0)
CYCLE_START = {1: 0, 2: 2, 3: 4}     # entry offered = cycle start + tier


def make_bonus_pools(random=None) -> Dict[str, List[List[int]]]:
    """{dungeon: 8 entries of 4 item ids}: the vanilla pools, or with `random`
    every item replaced by a random candidate."""
    pools = {}
    for dungeon, (_, entries) in BONUS_TABLE.items():
        pools[dungeon] = [[random.choice(RANDOM_CANDIDATES) if random else v for v in entry]
                          for entry in entries]
    return pools


def offered_entry(cycle: int, tier: int) -> int:
    """The entry the bonus screen offers for a cycle (1-3) and tier (0-3)."""
    return CYCLE_START[min(max(cycle, 1), 3)] + tier


def solo_points(threshold: int) -> int:
    """Bonus points one player needs to reach a tier with this threshold."""
    points = 0
    while points * PLAYER_FACTOR[0] < threshold:
        points += 1
    return points


def item_name(item_id: Optional[int]) -> str:
    return ITEM_NAMES.get(item_id, f"item {item_id:#x}") if item_id is not None else "-"
