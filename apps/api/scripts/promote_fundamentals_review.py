"""Promote explicitly approved review rows into the fundamentals collection."""

import json
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd

from app.data.fundamentals import validate_and_align_fundamentals
from app.data.fundamentals_review import promote_approved_reviews


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--universe", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--fixed-lag-days", type=int, default=90)
    args = parser.parse_args()

    universe_document = json.loads(args.universe.read_text(encoding="utf-8"))
    universe = {security["ticker"] for security in universe_document["securities"]}
    review = pd.read_csv(args.review, dtype="string", keep_default_na=False)
    promotion = promote_approved_reviews(review)
    validation = validate_and_align_fundamentals(
        promotion.frame, universe=universe, lag_days=args.fixed_lag_days
    )
    approved_count = (
        int(review["review_status"].str.lower().eq("approved").sum())
        if "review_status" in review
        else 0
    )
    errors = promotion.errors + validation.errors
    if approved_count == 0:
        errors.append("no approved review rows to promote")
    report = {
        "review_rows": len(review),
        "approved_rows": approved_count,
        "promoted_rows": len(validation.frame) if not errors else 0,
        "errors": errors,
        "warnings": validation.warnings,
        "passed": not errors,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    validation.frame.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
