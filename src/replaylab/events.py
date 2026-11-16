"""Version-one quote schema: integer prices, one global sequence per stream."""

import json
import re
from dataclasses import asdict, dataclass

MAX_INT = 2**63 - 1  # Compatible with SQLite INTEGER storage in the next milestone.
SYMBOL = re.compile(r"[A-Z][A-Z0-9.]{0,11}")


def require_integer(name: str, value: object, minimum: int = 1) -> None:
    # bool is an int subclass, but is not a valid price, size, or sequence number.
    if type(value) is not int or not minimum <= value <= MAX_INT:
        raise ValueError(f"{name} must be an integer in [{minimum}, {MAX_INT}]")


def require_symbol(value: object) -> None:
    if not isinstance(value, str) or SYMBOL.fullmatch(value) is None:
        raise ValueError(
            "symbol must be 1–12 uppercase letters, digits, or dots; start with a letter"
        )


@dataclass(frozen=True, slots=True)
class QuoteEvent:
    seq: int
    timestamp_ns: int
    symbol: str
    bid_ticks: int
    ask_ticks: int
    bid_size: int
    ask_size: int

    def __post_init__(self) -> None:
        for name in ("seq", "bid_ticks", "ask_ticks", "bid_size", "ask_size"):
            require_integer(name, getattr(self, name))
        require_integer("timestamp_ns", self.timestamp_ns, minimum=0)
        require_symbol(self.symbol)
        if self.bid_ticks > self.ask_ticks:
            raise ValueError("bid_ticks must not exceed ask_ticks")

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_json(cls, line: str) -> "QuoteEvent":
        def unique_keys(pairs: list[tuple]) -> dict:
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError(f"duplicate JSON field: {key}")
                result[key] = value
            return result

        payload = json.loads(line, object_pairs_hook=unique_keys)
        if not isinstance(payload, dict):
            raise ValueError("event must be a JSON object")
        try:
            return cls(**payload)
        except TypeError as exc:
            raise ValueError(f"invalid event fields: {exc}") from exc
