"""Collect and review official 2024 NGX ASI and CBN 91-day NTB observations."""

from __future__ import annotations

import json
from argparse import ArgumentParser
from datetime import UTC, date, datetime, timedelta
from hashlib import sha256
from pathlib import Path

import httpx
import pandas as pd

from app.data.market_inputs import build_monthly_market_inputs
from app.data.market_sources import parse_cbn_91_day_ntb, parse_ngx_weekly_asi

NGX_WEEKLY_URL = (
    "https://doclib.ngxgroup.com/market_data-site/other-market-information-site/"
    "Week%20Market%20Report/Weekly%20Market%20Report%20for%20the%20Week%20Ended%20"
    "{date}.pdf"
)
CBN_NTB_URL = "https://www.cbn.gov.ng/api/GetAllSecuritiesNTB"


def fridays(year: int) -> list[date]:
    current = date(year, 1, 1)
    current += timedelta(days=(4 - current.weekday()) % 7)
    values = []
    while current.year == year:
        values.append(current)
        current += timedelta(days=7)
    return values


def digest(content: bytes) -> str:
    return sha256(content).hexdigest()


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", required=True, type=Path)
    parser.add_argument("--benchmark-output", required=True, type=Path)
    parser.add_argument("--risk-free-output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--review-report", required=True, type=Path)
    parser.add_argument("--year", type=int, default=2024)
    args = parser.parse_args()

    args.raw_dir.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "factorgraph-ngx academic data audit/0.1"}
    ngx_records: list[dict] = []
    benchmark_rows: list[dict] = []

    with httpx.Client(follow_redirects=True, headers=headers, timeout=60) as client:
        for report_date in fridays(args.year):
            label = report_date.strftime("%d-%m-%Y")
            url = NGX_WEEKLY_URL.format(date=label)
            path = args.raw_dir / f"ngx-weekly-{report_date.isoformat()}.pdf"
            cached = path.exists() and path.read_bytes().startswith(b"%PDF")
            response = None if cached else client.get(url)
            content = path.read_bytes() if cached else response.content
            http_status = 200 if cached else response.status_code
            record = {
                "observation_date": report_date.isoformat(),
                "source_url": url,
                "http_status": http_status,
            }
            if http_status == 200 and content.startswith(b"%PDF"):
                if not cached:
                    path.write_bytes(content)
                source_id = f"ngx-weekly-{report_date.isoformat()}"
                record.update(
                    status="accepted",
                    source_id=source_id,
                    local_path=path.as_posix(),
                    bytes=len(content),
                    sha256=digest(content),
                )
                try:
                    benchmark_rows.append(
                        parse_ngx_weekly_asi(path, report_date, source_id)
                    )
                except ValueError as exc:
                    record.update(status="parse_error", error=str(exc))
            else:
                record["status"] = "not_available"
            ngx_records.append(record)

        cbn_response = client.get(CBN_NTB_URL)
        cbn_response.raise_for_status()
        cbn_content = cbn_response.content
        cbn_path = args.raw_dir / "cbn-ntb-auctions.json"
        cbn_path.write_bytes(cbn_content)
        cbn_records = cbn_response.json()

    benchmark = pd.DataFrame(benchmark_rows).sort_values("observation_date")
    risk_free = parse_cbn_91_day_ntb(cbn_records, year=args.year)
    monthly, coverage = build_monthly_market_inputs(benchmark, risk_free)

    for output in (args.benchmark_output, args.risk_free_output, args.manifest, args.review_report):
        output.parent.mkdir(parents=True, exist_ok=True)
    benchmark.to_csv(args.benchmark_output, index=False)
    risk_free.to_csv(args.risk_free_output, index=False)

    manifest = {
        "dataset_id": f"official-market-inputs-{args.year}",
        "generated_at": datetime.now(UTC).isoformat(),
        "ngx_provider": "Nigerian Exchange Limited",
        "cbn_provider": "Central Bank of Nigeria",
        "ngx_records": ngx_records,
        "cbn_source": {
            "source_url": CBN_NTB_URL,
            "http_status": cbn_response.status_code,
            "local_path": cbn_path.as_posix(),
            "bytes": len(cbn_content),
            "sha256": digest(cbn_content),
            "records_received": len(cbn_records),
            "accepted_91_day_records": len(risk_free),
        },
    }
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    accepted_ngx = [row for row in ngx_records if row["status"] == "accepted"]
    review = {
        "dataset_id": manifest["dataset_id"],
        "decision": "accepted" if coverage.aligned_months >= 2 else "insufficient_coverage",
        "coverage": coverage.to_dict(),
        "benchmark": {
            "observations": len(benchmark),
            "months": sorted(benchmark["observation_date"].str[:7].unique().tolist()),
            "duplicate_keys": int(
                benchmark[["observation_date", "index_code"]].duplicated().sum()
            ),
            "non_positive_closes": int((benchmark["close"] <= 0).sum()),
            "accepted_documents": len(accepted_ngx),
            "attempted_documents": len(ngx_records),
        },
        "risk_free": {
            "observations": len(risk_free),
            "months": sorted(risk_free["observation_date"].str[:7].unique().tolist()),
            "duplicate_keys": int(
                risk_free[["observation_date", "tenor"]].duplicated().sum()
            ),
            "rate_min": float(risk_free["annual_rate_percent"].min()),
            "rate_max": float(risk_free["annual_rate_percent"].max()),
            "rate_field": "CBN NTB marginal rate",
        },
        "aligned_market_factor": json.loads(
            monthly.where(pd.notna(monthly), None).to_json(orient="records")
        ),
    }
    args.review_report.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(review, indent=2))


if __name__ == "__main__":
    main()
