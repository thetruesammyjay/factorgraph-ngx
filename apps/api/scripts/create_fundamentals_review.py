"""Create the human-review worksheet from the annual-report evidence index."""

import json
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd

from app.data.fundamentals_review import create_review_queue


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--replace", action="store_true")
    parser.add_argument(
        "--merge",
        action="store_true",
        help="preserve completed review rows while refreshing source evidence",
    )
    args = parser.parse_args()

    if args.replace and args.merge:
        parser.error("choose either --replace or --merge")
    if args.output.exists() and not (args.replace or args.merge):
        parser.error("output exists; use --merge or --replace")
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    queue = create_review_queue(evidence)
    if args.output.exists() and args.merge:
        previous = pd.read_csv(args.output, dtype=str, keep_default_na=False)
        completed = previous[previous["review_status"].isin(["approved", "rejected"])]
        completed = completed.set_index(["ticker", "fiscal_period"])
        for index, row in queue.iterrows():
            key = (row["ticker"], row["fiscal_period"])
            if key not in completed.index:
                continue
            preserved = completed.loc[key]
            for column in queue.columns:
                if column in preserved.index and column not in {
                    "evidence_status",
                    "candidate_book_equity_pages",
                    "candidate_shares_outstanding_pages",
                    "candidate_unit_pages",
                }:
                    queue.loc[index, column] = preserved[column]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    queue.to_csv(args.output, index=False)
    print(f"Created {len(queue)} review rows in {args.output}")


if __name__ == "__main__":
    main()
