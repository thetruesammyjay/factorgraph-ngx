"""Build the auditable issuer-period fundamentals completion queue."""

from __future__ import annotations

import json
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from app.data.fundamentals_completion import build_completion_queue


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--universe", required=True, type=Path)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--fiscal-periods", nargs="+", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    universe_doc = json.loads(args.universe.read_text(encoding="utf-8"))
    universe = pd.DataFrame(universe_doc["securities"])
    current = pd.read_csv(args.input, dtype="string", keep_default_na=False)
    queue, summary = build_completion_queue(universe, current, args.fiscal_periods)
    report = {
        "dataset_id": "ngx-15-point-in-time-fundamentals-completion",
        "generated_at": datetime.now(UTC).isoformat(),
        "universe_id": universe_doc.get("universe_id"),
        "summary": summary.to_dict(),
        "workflow": [
            "review missing or incomplete issuer-period tasks",
            "verify book equity, shares outstanding, units, scope, and publication date",
            "promote only approved rows into the canonical fundamentals file",
            "rerun the point-in-time gate before portfolio formation",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    queue.to_csv(args.output, index=False)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
