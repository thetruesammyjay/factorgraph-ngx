"""Validate, align, and report a point-in-time fundamentals collection."""

import json
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd

from app.data.fundamentals import validate_and_align_fundamentals


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--universe", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--expected-periods", nargs="+", required=True)
    parser.add_argument("--fixed-lag-days", type=int, default=90)
    args = parser.parse_args()

    universe_document = json.loads(args.universe.read_text(encoding="utf-8"))
    universe = {security["ticker"] for security in universe_document["securities"]}
    source = pd.read_csv(args.input)
    validation = validate_and_align_fundamentals(
        source,
        universe=universe,
        lag_days=args.fixed_lag_days,
        normalize_units=False,
    )
    frame = validation.frame

    observed = set(zip(frame.get("ticker", []), frame.get("fiscal_period", []), strict=False))
    expected = {(ticker, period) for ticker in universe for period in args.expected_periods}
    missing = sorted(expected.difference(observed))
    effective_source = frame.get("effective_date_source", pd.Series(dtype="string"))
    actual_dates = int((effective_source == "ACTUAL_PUBLICATION_DATE").sum())
    status = "ready" if not validation.errors and not missing else "collection_incomplete"
    report = {
        "dataset_id": "ngx-15-point-in-time-fundamentals-pilot",
        "status": status,
        "universe_id": universe_document["universe_id"],
        "expected_observations": len(expected),
        "observed_observations": len(frame),
        "actual_publication_dates": actual_dates,
        "fixed_lag_estimates": len(frame) - actual_dates,
        "missing_ticker_periods": [
            {"ticker": ticker, "fiscal_period": period} for ticker, period in missing
        ],
        "errors": validation.errors,
        "warnings": validation.warnings,
        "point_in_time_gate": {
            "complete_ticker_period_coverage": not missing,
            "no_validation_errors": not validation.errors,
            "passed": status == "ready",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if validation.errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
