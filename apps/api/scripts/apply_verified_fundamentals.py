"""Merge page-verified observations into the fundamentals review worksheet."""

import json
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--observations", type=Path, required=True)
    args = parser.parse_args()

    review = pd.read_csv(args.review, dtype=str, keep_default_na=False)
    payload = json.loads(args.observations.read_text(encoding="utf-8"))
    for record in payload["records"]:
        identity = (record["ticker"], record["fiscal_period"])
        matched = (review["ticker"] == identity[0]) & (
            review["fiscal_period"] == identity[1]
        )
        if matched.sum() != 1:
            raise ValueError(f"expected one review row for {identity}, found {matched.sum()}")
        if review.loc[matched, "evidence_status"].iloc[0] != "review_required":
            raise ValueError(f"{identity} does not have reviewable source evidence")
        values = {
            **record,
            "publication_date": record.get("publication_date") or "",
            "review_status": "approved",
            "reviewer": payload["reviewer"],
            "reviewed_at": payload["reviewed_at"],
        }
        for column, value in values.items():
            if column in review.columns:
                review.loc[matched, column] = str(value)

    review.to_csv(args.review, index=False)
    print(f"Recorded {len(payload['records'])} verified observations in {args.review}")


if __name__ == "__main__":
    main()
