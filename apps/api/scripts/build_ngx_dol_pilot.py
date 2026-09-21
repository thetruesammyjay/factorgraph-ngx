"""Build and validate a staged price panel from downloaded NGX DOL PDFs."""

import json
import re
from argparse import ArgumentParser
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

from app.data.ngx_dol import parse_pdf

SOURCE_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})\.pdf$")


def longest_unchanged_run(values: pd.Series) -> int:
    groups = values.ne(values.shift()).cumsum()
    return int(values.groupby(groups).size().max())


def parse_source(args: tuple[Path, set[str]]) -> tuple[list[dict], str | None]:
    path, tickers = args
    try:
        return [row.to_dict() for row in parse_pdf(path, tickers)], None
    except (ValueError, OSError) as exc:
        return [], f"{path.name}: {exc}"


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--api-report", type=Path)
    parser.add_argument("--download-manifest", type=Path)
    parser.add_argument("--dataset-id", default="ngx-dol-pilot")
    universe_group = parser.add_mutually_exclusive_group(required=True)
    universe_group.add_argument("--tickers", nargs="+")
    universe_group.add_argument("--universe", type=Path)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()

    universe_metadata = None
    if args.universe:
        universe_metadata = json.loads(args.universe.read_text(encoding="utf-8"))
        requested = {security["ticker"] for security in universe_metadata["securities"]}
    else:
        requested = set(args.tickers)
    pdfs = sorted(args.input.glob("*.pdf"))
    work = [(path, requested) for path in pdfs]
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            parsed = list(executor.map(parse_source, work))
    else:
        parsed = [parse_source(item) for item in work]
    rows = [row for parsed_rows, _ in parsed for row in parsed_rows]
    parse_errors = [error for _, error in parsed if error]
    frame = pd.DataFrame(rows).sort_values(["trading_date", "ticker"])
    frame["requested_date"] = frame["source_file"].str.extract(SOURCE_DATE.pattern)
    mismatched = frame[frame["requested_date"] != frame["trading_date"]]
    source_date_mismatches = sorted(mismatched["source_file"].unique().tolist())
    frame = frame[frame["requested_date"] == frame["trading_date"]].drop(
        columns="requested_date"
    )
    valid_source_documents = int(frame["source_file"].nunique())

    duplicates = int(frame.duplicated(["trading_date", "ticker"]).sum())
    invalid_prices = int((frame["close"] <= 0).sum())
    counts = Counter(frame["ticker"])
    missing_ticker_dates = {
        ticker: valid_source_documents - counts.get(ticker, 0)
        for ticker in sorted(requested)
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
    monthly_observations = (
        frame.assign(month=frame["trading_date"].str[:7])
        .groupby(["month", "ticker"])
        .size()
        .unstack(fill_value=0)
        .astype(int)
        .to_dict(orient="index")
    )

    download_records = []
    if args.download_manifest:
        download_manifest = json.loads(args.download_manifest.read_text(encoding="utf-8"))
        download_records = download_manifest.get("records", [])
    monthly_download_coverage = {}
    for record in download_records:
        month = record["date"][:7]
        summary = monthly_download_coverage.setdefault(
            month, {"weekday_candidates": 0, "documents_retrieved": 0, "not_available": 0}
        )
        summary["weekday_candidates"] += 1
        if record["status"] in {"downloaded", "already_downloaded"}:
            summary["documents_retrieved"] += 1
        else:
            summary["not_available"] += 1
    for summary in monthly_download_coverage.values():
        summary["candidate_coverage_rate"] = round(
            summary["documents_retrieved"] / summary["weekday_candidates"], 4
        )
    for month, summary in monthly_download_coverage.items():
        ticker_counts = monthly_observations.get(month, {})
        valid_documents = max(ticker_counts.values(), default=0)
        summary["valid_dol_documents"] = valid_documents
        summary["source_exceptions"] = summary["documents_retrieved"] - valid_documents
        summary["valid_dol_rate"] = round(
            valid_documents / summary["documents_retrieved"], 4
        ) if summary["documents_retrieved"] else 0

    passed = (
        bool(pdfs)
        and duplicates == 0
        and invalid_prices == 0
        and not any(missing_ticker_dates.values())
    )
    valid_document_rate = round(valid_source_documents / len(pdfs), 4) if pdfs else 0
    price_expansion_ready = (
        passed
        and valid_source_documents >= 200
        and valid_document_rate >= 0.95
    )
    report = {
        "dataset_id": args.dataset_id,
        "structural_status": "passed" if passed else "failed",
        "price_universe_expansion": (
            "proceed_with_stale_price_controls" if price_expansion_ready else "hold"
        ),
        "research_readiness": "blocked_missing_liquidity",
        "source_pdf_count": len(pdfs),
        "valid_dol_document_count": valid_source_documents,
        "valid_document_rate": valid_document_rate,
        "observation_count": len(frame),
        "tickers": sorted(requested),
        "universe": universe_metadata,
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
        "parse_errors": parse_errors,
        "source_date_mismatch_files": source_date_mismatches,
        "monthly_download_coverage": monthly_download_coverage,
        "monthly_observations_by_ticker": monthly_observations,
        "price_expansion_gate": {
            "minimum_source_documents": 200,
            "minimum_valid_document_rate": 0.95,
            "requires_complete_ticker_presence_in_retrieved_documents": True,
            "passed": price_expansion_ready,
        },
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
