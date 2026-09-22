"""Create a source-document collection plan for the fundamentals pilot."""

import csv
import json
from argparse import ArgumentParser
from pathlib import Path


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--universe", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--fiscal-years", nargs="+", type=int, required=True)
    args = parser.parse_args()

    universe = json.loads(args.universe.read_text(encoding="utf-8"))
    tasks = []
    for security in universe["securities"]:
        for fiscal_year in sorted(set(args.fiscal_years)):
            tasks.append(
                {
                    "ticker": security["ticker"],
                    "company": security["company"],
                    "sector": security["sector"],
                    "fiscal_period": f"{fiscal_year}-12-31",
                    "status": "pending",
                    "preferred_source": "issuer investor-relations annual report",
                    "fallback_source": "NGX corporate disclosures portal",
                    "required_evidence": [
                        "annual report PDF",
                        "actual publication or NGX submission date",
                        "book equity page",
                        "shares outstanding page",
                        "source URL and SHA-256",
                    ],
                }
            )

    plan = {
        "plan_id": "ngx-15-fundamentals-point-in-time-pilot",
        "universe_id": universe["universe_id"],
        "fiscal_years": sorted(set(args.fiscal_years)),
        "task_count": len(tasks),
        "publication_date_policy": (
            "Use the actual issuer release or NGX submission date. Apply a fixed lag only "
            "when the missing evidence is explicitly recorded."
        ),
        "ngx_disclosures_url": "https://ngxgroup.com/exchange/data/corporate-disclosures/",
        "tasks": tasks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    print(f"Created {len(tasks)} collection tasks in {args.output}")

    if args.catalog and not args.catalog.exists():
        args.catalog.parent.mkdir(parents=True, exist_ok=True)
        with args.catalog.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "ticker",
                    "fiscal_period",
                    "source_url",
                    "publication_date",
                    "source_kind",
                    "notes",
                ],
            )
            writer.writeheader()
            for task in tasks:
                writer.writerow(
                    {
                        "ticker": task["ticker"],
                        "fiscal_period": task["fiscal_period"],
                    }
                )
        print(f"Created source catalog in {args.catalog}")


if __name__ == "__main__":
    main()
