"""Merge audited annual price, benchmark, and risk-free datasets."""

from __future__ import annotations

import json
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path

from app.data.multi_year import merge_annual_csvs
from app.data.provenance import dataset_fingerprint, input_identity


def annual_inputs(values: list[str]) -> dict[int, Path]:
    result: dict[int, Path] = {}
    for value in values:
        try:
            year_text, path_text = value.split("=", 1)
            year = int(year_text)
        except ValueError as exc:
            raise ValueError(f"expected YEAR=PATH, received {value!r}") from exc
        if year in result:
            raise ValueError(f"duplicate input year: {year}")
        result[year] = Path(path_text)
    return result


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--prices", action="append", required=True, metavar="YEAR=PATH")
    parser.add_argument("--benchmark", action="append", required=True, metavar="YEAR=PATH")
    parser.add_argument("--risk-free", action="append", required=True, metavar="YEAR=PATH")
    parser.add_argument("--prices-output", required=True, type=Path)
    parser.add_argument("--benchmark-output", required=True, type=Path)
    parser.add_argument("--risk-free-output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    args = parser.parse_args()

    try:
        groups = {
            "prices": annual_inputs(args.prices),
            "benchmark": annual_inputs(args.benchmark),
            "risk_free": annual_inputs(args.risk_free),
        }
    except ValueError as exc:
        parser.error(str(exc))
    year_sets = {name: set(paths) for name, paths in groups.items()}
    if len({tuple(sorted(years)) for years in year_sets.values()}) != 1:
        parser.error(f"all input groups must contain the same years: {year_sets}")

    prices, price_coverage = merge_annual_csvs(
        groups["prices"], date_column="trading_date",
        key_columns=["trading_date", "ticker"], entity_column="ticker",
    )
    benchmark, benchmark_coverage = merge_annual_csvs(
        groups["benchmark"], date_column="observation_date",
        key_columns=["observation_date", "index_code"], entity_column="index_code",
    )
    risk_free, risk_free_coverage = merge_annual_csvs(
        groups["risk_free"], date_column="observation_date",
        key_columns=["observation_date", "tenor"], entity_column="tenor",
    )

    outputs = {
        "prices": args.prices_output,
        "benchmark": args.benchmark_output,
        "risk_free": args.risk_free_output,
    }
    for frame, path in zip((prices, benchmark, risk_free), outputs.values(), strict=True):
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)

    identities = {
        f"{group}_{year}": input_identity(path)
        for group, paths in groups.items()
        for year, path in sorted(paths.items())
    }
    coverage = {
        "prices": price_coverage.to_dict(),
        "benchmark": benchmark_coverage.to_dict(),
        "risk_free": risk_free_coverage.to_dict(),
    }
    years = sorted(next(iter(year_sets.values())))
    fingerprint = dataset_fingerprint(identities, {"years": years, "coverage": coverage})
    document = {
        "dataset_id": f"ngx-public-{years[0]}-{years[-1]}-{fingerprint[:12]}",
        "generated_at": datetime.now(UTC).isoformat(),
        "years": years,
        "fingerprint": fingerprint,
        "inputs": identities,
        "outputs": {name: input_identity(path) for name, path in outputs.items()},
        "coverage": coverage,
        "validation": {
            "declared_years_match_rows": True,
            "unique_primary_keys": True,
            "consistent_year_sets": True,
        },
    }
    text = json.dumps(document, indent=2) + "\n"
    for path in (args.manifest, args.review):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(json.dumps({"dataset_id": document["dataset_id"], "coverage": coverage}, indent=2))


if __name__ == "__main__":
    main()
