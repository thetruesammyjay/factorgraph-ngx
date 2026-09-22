"""Download reviewed annual-report URLs and create an evidence manifest."""

import json
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pandas as pd

from app.data.source_documents import acquire_pdf

CATALOG_COLUMNS = {
    "ticker",
    "fiscal_period",
    "source_url",
    "publication_date",
    "source_kind",
    "notes",
}


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--timeout", default=45.0, type=float)
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    catalog = pd.read_csv(args.catalog, dtype="string", keep_default_na=False)
    missing_columns = sorted(CATALOG_COLUMNS.difference(catalog.columns))
    if missing_columns:
        parser.error(f"catalog missing columns: {', '.join(missing_columns)}")

    catalog["ticker"] = catalog["ticker"].str.strip().str.upper()
    catalog["fiscal_period"] = catalog["fiscal_period"].str.strip()
    if catalog.duplicated(["ticker", "fiscal_period"]).any():
        parser.error("catalog contains duplicate ticker/fiscal_period rows")

    sources = {
        (row.ticker, row.fiscal_period): row
        for row in catalog.itertuples(index=False)
    }
    records: list[dict[str, object]] = []
    headers = {"User-Agent": "factorgraph-ngx academic source audit/0.1"}
    with httpx.Client(follow_redirects=True, headers=headers, timeout=args.timeout) as client:
        for task in plan["tasks"]:
            key = (task["ticker"], task["fiscal_period"])
            source = sources.get(key)
            if source is None or not source.source_url.strip():
                record: dict[str, object] = {
                    "ticker": key[0],
                    "fiscal_period": key[1],
                    "status": "source_url_required",
                }
            else:
                record = acquire_pdf(
                    client,
                    ticker=key[0],
                    fiscal_period=key[1],
                    source_url=source.source_url.strip(),
                    output_directory=args.output,
                )
                record.update(
                    publication_date=source.publication_date.strip() or None,
                    source_kind=source.source_kind.strip() or None,
                    notes=source.notes.strip() or None,
                )
            records.append(record)
            print(f"{key[0]} {key[1]}: {record['status']}", flush=True)

    status_counts: dict[str, int] = {}
    for record in records:
        status = str(record["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    downloaded = sum(
        status_counts.get(status, 0) for status in ("downloaded", "already_downloaded")
    )
    manifest = {
        "dataset_id": "ngx-15-fundamentals-source-documents",
        "plan_id": plan["plan_id"],
        "retrieved_at": datetime.now(UTC).isoformat(),
        "expected_documents": len(plan["tasks"]),
        "available_documents": downloaded,
        "complete": downloaded == len(plan["tasks"]),
        "status_counts": dict(sorted(status_counts.items())),
        "records": records,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
