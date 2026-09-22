"""Find annual-report candidates on reviewed official issuer pages."""

import json
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pandas as pd

from app.data.source_discovery import discover_report_links

REGISTRY_COLUMNS = {"ticker", "company", "landing_url", "verified_at", "notes"}


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--timeout", type=float, default=45.0)
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    registry = pd.read_csv(args.registry, dtype="string", keep_default_na=False)
    missing = sorted(REGISTRY_COLUMNS.difference(registry.columns))
    if missing:
        parser.error(f"registry missing columns: {', '.join(missing)}")
    registry["ticker"] = registry["ticker"].str.strip().str.upper()
    if registry["ticker"].duplicated().any():
        parser.error("registry contains duplicate tickers")
    issuer_pages = {row.ticker: row for row in registry.itertuples(index=False)}

    tasks_by_ticker: dict[str, list[dict]] = {}
    for task in plan["tasks"]:
        tasks_by_ticker.setdefault(task["ticker"], []).append(task)

    records: list[dict] = []
    review_rows: list[dict] = []
    headers = {"User-Agent": "factorgraph-ngx academic source discovery/0.1"}
    with httpx.Client(follow_redirects=True, headers=headers, timeout=args.timeout) as client:
        for ticker, tasks in tasks_by_ticker.items():
            issuer = issuer_pages.get(ticker)
            landing_url = issuer.landing_url.strip() if issuer else ""
            if not landing_url:
                for task in tasks:
                    records.append(
                        {
                            "ticker": ticker,
                            "fiscal_period": task["fiscal_period"],
                            "status": "landing_url_required",
                            "candidates": [],
                        }
                    )
                continue
            try:
                response = client.get(landing_url)
                response.raise_for_status()
            except httpx.HTTPError as exc:
                for task in tasks:
                    records.append(
                        {
                            "ticker": ticker,
                            "fiscal_period": task["fiscal_period"],
                            "landing_url": landing_url,
                            "status": "request_error",
                            "error": type(exc).__name__,
                            "candidates": [],
                        }
                    )
                continue

            for task in tasks:
                fiscal_year = int(task["fiscal_period"][:4])
                candidates = discover_report_links(response.text, landing_url, fiscal_year)
                status = "candidates_found" if candidates else "no_candidates"
                records.append(
                    {
                        "ticker": ticker,
                        "fiscal_period": task["fiscal_period"],
                        "landing_url": landing_url,
                        "status": status,
                        "candidates": [candidate.to_dict() for candidate in candidates],
                    }
                )
                for rank, candidate in enumerate(candidates, start=1):
                    review_rows.append(
                        {
                            "selected": "",
                            "ticker": ticker,
                            "fiscal_period": task["fiscal_period"],
                            "rank": rank,
                            "score": candidate.score,
                            "link_text": candidate.link_text,
                            "candidate_url": candidate.url,
                            "landing_url": landing_url,
                            "review_notes": "",
                        }
                    )

    counts: dict[str, int] = {}
    for record in records:
        counts[record["status"]] = counts.get(record["status"], 0) + 1
    result = {
        "plan_id": plan["plan_id"],
        "discovered_at": datetime.now(UTC).isoformat(),
        "automatic_selection": False,
        "status_counts": dict(sorted(counts.items())),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.review.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(
        review_rows,
        columns=[
            "selected",
            "ticker",
            "fiscal_period",
            "rank",
            "score",
            "link_text",
            "candidate_url",
            "landing_url",
            "review_notes",
        ],
    ).to_csv(args.review, index=False)
    print(json.dumps(result["status_counts"], indent=2))


if __name__ == "__main__":
    main()
