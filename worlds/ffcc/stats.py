"""Starting Stats: each tribe's base Strength, Magic and Defense, the values the
game starts every character's stats from (artifacts and equipment are added on
top). Male and female characters of a tribe share them, and so does every
player of that tribe in co-op."""
from random import Random

TRIBES = ("Clavat", "Lilty", "Yuke", "Selkie")

# The game's own values: (Strength, Magic, Defense)
VANILLA_STATS: dict[str, tuple[int, int, int]] = {
    "Clavat": (6, 13, 7),
    "Lilty":  (8, 10, 8),
    "Yuke":   (5, 15, 5),
    "Selkie": (7, 12, 6),
}

SHUFFLE_TRIBES = 1
SAME_TOTAL = 2
FULLY_RANDOM = 3


def _spread(total: int, low: int, high: int, random: Random) -> list[int]:
    """Three stats between low and high that add up to total (clamped so it can)."""
    total = max(3 * low, min(3 * high, total))
    stats = [low, low, low]
    for _ in range(total - 3 * low):
        stats[random.choice([i for i in range(3) if stats[i] < high])] += 1
    return stats


def make_tribe_stats(mode: int, random: Random, low: int, high: int) -> dict[str, list[int]] | None:
    """{tribe: [Strength, Magic, Defense]} for the Starting Stats option, or None
    to keep the game's own values."""
    if not mode:
        return None
    low, high = min(low, high), max(low, high)
    if mode == SHUFFLE_TRIBES:
        # every tribe gets another tribe's stats
        while True:
            order = list(TRIBES)
            random.shuffle(order)
            if all(tribe != other for tribe, other in zip(TRIBES, order)):
                return {tribe: list(VANILLA_STATS[other]) for tribe, other in zip(TRIBES, order)}
    if mode == SAME_TOTAL:
        return {tribe: _spread(sum(VANILLA_STATS[tribe]), low, high, random) for tribe in TRIBES}
    return {tribe: [random.randint(low, high) for _ in range(3)] for tribe in TRIBES}
