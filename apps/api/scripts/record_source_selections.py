"""Mark the highest-ranked discovered source for explicitly reviewed tasks."""

import json
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--selections", required=True, type=Path)
    args = parser.parse_args()

    review = pd.read_csv(args.review, dtype=str, keep_default_na=False)
    payload = json.loads(args.selections.read_text(encoding="utf-8"))
    review["selected"] = ""
    for record in payload["records"]:
        matched = (review["ticker"] == record["ticker"]) & (
            review["fiscal_period"] == record["fiscal_period"]
        )
        candidates = review.loc[matched].sort_values(["rank", "score"], ascending=[True, False])
        if candidates.empty:
            raise ValueError(
                f"no discovered candidate for {record['ticker']} {record['fiscal_period']}"
            )
        index = candidates.index[0]
        review.loc[index, "selected"] = "yes"
        review.loc[index, "reviewer"] = payload["reviewer"]
        review.loc[index, "reviewed_at"] = payload["reviewed_at"]
        review.loc[index, "publication_date"] = record.get("publication_date", "")
        review.loc[index, "review_notes"] = record["review_notes"]

    review.to_csv(args.review, index=False)
    print(f"Recorded {len(payload['records'])} reviewed source selections")


if __name__ == "__main__":
    main()
