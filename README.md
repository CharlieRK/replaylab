# ReplayLab

A Python project exploring reliable market-event ingestion, deterministic replay,
and crash recovery. Independent learning project; not affiliated with Two Sigma
or any exchange. All sample quotes are synthetic, not financial data or advice.

## Current status — milestone 1

Implemented: immutable validated quote events, seeded streaming JSONL generation,
a strict file validator, tests, and GitHub Actions CI.

**Not implemented yet:** SQLite persistence, recovery, state replay, benchmarks,
or a dashboard. This is a quote-state pipeline, not an exchange matching engine
or a production trading system.

## Quick start (Python 3.12)

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
replaylab generate --count 1000 --seed 42 > /tmp/quotes.jsonl
replaylab validate /tmp/quotes.jsonl
pytest -q
ruff check .
ruff format --check .
```

On Windows, replace `/tmp/quotes.jsonl` with a local path.
The generator writes to stdout; shell redirection overwrites the target file.
For the committed five-event fixture: `replaylab validate examples/quotes.jsonl`.

## Event contract (v1)

| Field | Meaning |
| --- | --- |
| `seq` | Global sequence starting at 1, unique within one stream |
| `timestamp_ns` | Nonnegative synthetic Unix timestamp in nanoseconds |
| `symbol` | 1–12 uppercase letters, digits or dots, starting with a letter |
| `bid_ticks`, `ask_ticks` | Positive integer prices; one tick = USD 0.01 in this demo |
| `bid_size`, `ask_size` | Positive integer quantities |

Integers must fit signed SQLite 64-bit storage; booleans and floats are rejected.
Bid must not exceed ask; locked quotes are allowed. Each event replaces a
symbol's entire best bid/ask snapshot. Zero sizes and quote deletion are outside v1.
Unknown, missing, and repeated JSON keys are rejected. Blank lines are invalid.

The generator uses a private seeded RNG and fixed synthetic start time, not the
wall clock. Reproducibility targets the supported Python 3.12 runtime; the checked-in
fixture detects changes to generation behavior. Data is streamed without keeping
the full event history in memory. The validator requires sequence 1, 2, 3, ...;
an empty file is a valid zero-event stream. It does not enforce timestamp ordering.

## Planned recovery contract

One local stream per database. Identical duplicate events will be ignored;
conflicting duplicates, gaps, and out-of-order events will be rejected. Durable
input events will be separate from derived quote state. Quote state and processing
checkpoint will advance in one transaction. On restart, committed input after the
checkpoint will be processed; the source file can be safely re-submitted.

Recovery will be tested by terminating a child process around transaction commits,
then comparing recovered state with an uninterrupted run and independent replay.
No exactly-once claims across external systems or distributed workers.

## Development roadmap

- [x] 1. Schema, deterministic generator, CLI, tests, CI
- [ ] 2. SQLite event log and duplicate/conflict detection
- [ ] 3. Quote state and transactional processing checkpoint
- [ ] 4. Crash injection and restart recovery tests
- [ ] 5. Independent replay and canonical state comparison
- [ ] 6. Reproducible ingestion/processing/recovery benchmarks
- [ ] 7. Small dashboard and v0.1.0 release

Each verified milestone is committed and pushed. Incomplete work stays on development
branches; CI checks run on pushes and pull requests. Benchmark claims will include
hardware, Python version, event count, transaction size, and timing boundaries.
