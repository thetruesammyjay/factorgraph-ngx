"""Build and validate a staged price panel from downloaded NGX DOL PDFs."""

import json
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path

import pandas as pd

from app.data.ngx_dol import parse_pdf


def longest_unchanged_run(values: pd.Series) -> int:
    groups = values.ne(values.shift()).cumsum()
    return int(values.groupby(groups).size().max())


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--api-report", type=Path)
    parser.add_argument("--tickers", nargs="+", required=True)
    args = parser.parse_args()

    requested = set(args.tickers)
    pdfs = sorted(args.input.glob("*.pdf"))
    rows = [row.to_dict() for path in pdfs for row in parse_pdf(path, requested)]
    frame = pd.DataFrame(rows).sort_values(["trading_date", "ticker"])

    duplicates = int(frame.duplicated(["trading_date", "ticker"]).sum())
    invalid_prices = int((frame["close"] <= 0).sum())
    counts = Counter(frame["ticker"])
    missing_ticker_dates = {
        ticker: len(pdfs) - counts.get(ticker, 0) for ticker in sorted(requested)
    }
    missing_liquidity = {
        column: int(frame[column].isna().sum())
        for column in ("volume", "trading_value", "number_of_transactions")
    }
    carried_counts = {
        ticker: int(
            ((frame["ticker"] == ticker) & (frame["price_status"] == "carried_market_price")).sum()
        )
        for ticker in sorted(requested)
    }
    unique_closes = {
        ticker: int(group["close"].nunique())
        for ticker, group in frame.groupby("ticker", sort=True)
    }
    longest_stale_runs = {
        ticker: longest_unchanged_run(group.sort_values("trading_date")["close"])
        for ticker, group in frame.groupby("ticker", sort=True)
    }

    passed = (
        bool(pdfs)
        and duplicates == 0
        and invalid_prices == 0
        and not any(missing_ticker_dates.values())
    )
    report = {
        "dataset_id": "ngx-dol-december-2024-pilot",
        "structural_status": "passed" if passed else "failed",
        "research_readiness": "blocked_missing_liquidity_and_stale_price_review",
        "source_pdf_count": len(pdfs),
        "observation_count": len(frame),
        "tickers": sorted(requested),
        "date_min": frame["trading_date"].min(),
        "date_max": frame["trading_date"].max(),
        "observations_by_ticker": dict(sorted(counts.items())),
        "missing_ticker_dates": missing_ticker_dates,
        "duplicate_keys": duplicates,
        "non_positive_closes": invalid_prices,
        "carried_market_prices_by_ticker": carried_counts,
        "unique_closes_by_ticker": unique_closes,
        "longest_unchanged_close_run_by_ticker": longest_stale_runs,
        "missing_liquidity_fields": missing_liquidity,
        "interpretation": (
            "Current Market Price is staged as close. Rows without an Official Close are "
            "flagged as carried_market_price. Business Done Qty is deliberately excluded "
            "because it is not verified as total daily volume."
        ),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.api_report:
        args.api_report.parent.mkdir(parents=True, exist_ok=True)
        args.api_report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
