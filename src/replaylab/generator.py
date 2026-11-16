"""Seeded synthetic quotes; no live market data or wall-clock dependencies."""

import random
from collections.abc import Iterator

from replaylab.events import MAX_INT, QuoteEvent, require_integer, require_symbol

START_NS = 1_700_000_000_000_000_000
STEP_NS = 1_000_000


def generate_events(
    count: int, seed: int = 42, symbols: tuple[str, ...] = ("ALFA", "BETA", "GAMMA")
) -> Iterator[QuoteEvent]:
    require_integer("count", count, minimum=0)
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    if not symbols or len(set(symbols)) != len(symbols):
        raise ValueError("symbols must be nonempty and unique")
    for symbol in symbols:
        require_symbol(symbol)
    if count and START_NS + (count - 1) * STEP_NS > MAX_INT:
        raise ValueError("count would overflow the timestamp range")
    rng = random.Random(seed)
    prices = dict.fromkeys(symbols, 10_000)
    for seq in range(1, count + 1):
        symbol = rng.choice(symbols)
        prices[symbol] = max(1, prices[symbol] + rng.randint(-5, 5))
        yield QuoteEvent(
            seq=seq,
            timestamp_ns=START_NS + (seq - 1) * STEP_NS,
            symbol=symbol,
            bid_ticks=prices[symbol],
            ask_ticks=prices[symbol] + rng.randint(1, 5),
            bid_size=rng.randint(1, 1_000),
            ask_size=rng.randint(1, 1_000),
        )
