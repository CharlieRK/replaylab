import random
from pathlib import Path

import pytest

from replaylab.generator import generate_events


def test_repeatable_contiguous_valid_quotes():
    events = list(generate_events(1000, seed=7))
    assert events == list(generate_events(1000, seed=7))
    assert events != list(generate_events(1000, seed=8))
    assert [e.seq for e in events] == list(range(1, 1001))
    assert all(a.timestamp_ns < b.timestamp_ns for a, b in zip(events, events[1:]))
    assert all(e.bid_ticks <= e.ask_ticks for e in events)
    assert {e.symbol for e in events} == {"ALFA", "BETA", "GAMMA"}


def test_does_not_modify_global_random_state():
    before = random.getstate()
    list(generate_events(50))
    assert random.getstate() == before


def test_zero_and_custom_symbol():
    assert list(generate_events(0)) == []
    assert {e.symbol for e in generate_events(10, symbols=("TEST",))} == {"TEST"}


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(count=-1),
        dict(count=True),
        dict(count=1, seed=True),
        dict(count=1, symbols=()),
        dict(count=1, symbols=("A", "A")),
        dict(count=1, symbols=("bad",)),
    ],
)
def test_invalid_config(kwargs):
    with pytest.raises(ValueError):
        list(generate_events(**kwargs))


def test_checked_in_fixture():
    fixture = Path(__file__).parents[1] / "examples" / "quotes.jsonl"
    expected = "".join(e.to_json() + "\n" for e in generate_events(5))
    assert fixture.read_text() == expected
