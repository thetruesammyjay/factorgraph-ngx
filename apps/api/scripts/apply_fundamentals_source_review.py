"""Apply reviewed annual-report candidates to the document source catalog."""

import json
from argparse import ArgumentParser
from pathlib import Path

import pandas as pd

from app.data.source_discovery import apply_reviewed_selections


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--discovery", required=True, type=Path)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    review = pd.read_csv(args.review, dtype="string", keep_default_na=False)
    catalog = pd.read_csv(args.catalog, dtype="string", keep_default_na=False)
    discovery = json.loads(args.discovery.read_text(encoding="utf-8"))
    result = apply_reviewed_selections(review, catalog, discovery)
    report = {
        "selected_candidates": result.selected_count,
        "catalog_rows": len(result.catalog),
        "errors": result.errors,
        "passed": not result.errors,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if result.errors:
        raise SystemExit(1)
    result.catalog.to_csv(args.catalog, index=False)


if __name__ == "__main__":
    main()
