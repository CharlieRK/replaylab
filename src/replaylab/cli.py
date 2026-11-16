"""Stream JSON Lines to stdout; keep errors on stderr."""

import argparse

from replaylab.events import QuoteEvent
from replaylab.generator import generate_events


def main() -> None:
    parser = argparse.ArgumentParser(description="ReplayLab synthetic quote tools")
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="write synthetic events as JSONL to stdout")
    generate.add_argument("--count", type=int, default=100)
    generate.add_argument("--seed", type=int, default=42)
    validate = commands.add_parser(
        "validate", help="validate schema and contiguous sequence from 1"
    )
    validate.add_argument("path")
    args = parser.parse_args()
    try:
        if args.command == "generate":
            for event in generate_events(args.count, args.seed):
                print(event.to_json())
        else:
            count = 0
            with open(args.path, encoding="utf-8") as source:
                for line_number, line in enumerate(source, 1):
                    try:
                        event = QuoteEvent.from_json(line)
                        if event.seq != count + 1:
                            raise ValueError(f"expected sequence {count + 1}, got {event.seq}")
                    except ValueError as exc:
                        raise ValueError(f"line {line_number}: {exc}") from exc
                    count += 1
            print(f"Validated {count} events")
    except (ValueError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")
