"""Create the human-review worksheet from the annual-report evidence index."""

import json
from argparse import ArgumentParser
from pathlib import Path

from app.data.fundamentals_review import create_review_queue


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()

    if args.output.exists() and not args.replace:
        parser.error("output exists; use --replace only if reviewed edits may be discarded")
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    queue = create_review_queue(evidence)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    queue.to_csv(args.output, index=False)
    print(f"Created {len(queue)} review rows in {args.output}")


if __name__ == "__main__":
    main()
