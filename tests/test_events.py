import json
from dataclasses import FrozenInstanceError

import pytest

from replaylab.events import MAX_INT, QuoteEvent

BASE = dict(
    seq=1, timestamp_ns=0, symbol="ALFA", bid_ticks=100, ask_ticks=101, bid_size=10, ask_size=20
)


def test_round_trip_and_immutable():
    event = QuoteEvent(**BASE)
    assert QuoteEvent.from_json(event.to_json()) == event
    with pytest.raises(FrozenInstanceError):
        event.seq = 2


@pytest.mark.parametrize(
    "field,value",
    [
        ("seq", 0),
        ("seq", True),
        ("seq", MAX_INT + 1),
        ("timestamp_ns", -1),
        ("bid_ticks", 1.5),
        ("bid_ticks", 0),
        ("ask_ticks", "101"),
        ("bid_size", 0),
        ("ask_size", -2),
        ("symbol", "alfa"),
        ("symbol", ""),
        ("bid_ticks", 102),
    ],
)
def test_reject_invalid_fields(field, value):
    with pytest.raises(ValueError):
        QuoteEvent(**(BASE | {field: value}))


@pytest.mark.parametrize(
    "payload",
    [
        "[]",
        "null",
        "{",
        '{"seq":1,"seq":2}',
        json.dumps(BASE | {"extra": 1}),
        json.dumps({k: v for k, v in BASE.items() if k != "seq"}),
    ],
)
def test_reject_invalid_json_schema(payload):
    with pytest.raises(ValueError):
        QuoteEvent.from_json(payload)


def test_locked_quote_allowed():
    assert QuoteEvent(**(BASE | {"ask_ticks": 100})).ask_ticks == 100
