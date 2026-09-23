"""Validation and deterministic merging for annual public-market datasets."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class MergeCoverage:
    rows: int
    start_date: str
    end_date: str
    years: list[int]
    months: int
    entities: int
    rows_by_year: dict[str, int]

    def to_dict(self) -> dict:
        return asdict(self)


def merge_annual_csvs(
    annual_paths: dict[int, Path],
    *,
    date_column: str,
    key_columns: list[str],
    entity_column: str,
) -> tuple[pd.DataFrame, MergeCoverage]:
    """Merge annual CSVs after enforcing their declared year and unique keys."""
    if not annual_paths:
        raise ValueError("at least one annual input is required")

    frames: list[pd.DataFrame] = []
    rows_by_year: dict[str, int] = {}
    required = {date_column, entity_column, *key_columns}
    for year, path in sorted(annual_paths.items()):
        frame = pd.read_csv(path)
        missing = sorted(required.difference(frame.columns))
        if missing:
            raise ValueError(f"{path.name} missing columns: {', '.join(missing)}")
        dates = pd.to_datetime(frame[date_column], errors="coerce")
        if dates.isna().any():
            raise ValueError(f"{path.name} contains invalid {date_column} values")
        actual_years = sorted(dates.dt.year.unique().tolist())
        if actual_years != [year]:
            raise ValueError(
                f"{path.name} declared as {year} but contains years {actual_years}"
            )
        frame = frame.copy()
        frame[date_column] = dates.dt.strftime("%Y-%m-%d")
        if frame[key_columns].duplicated().any():
            raise ValueError(f"{path.name} contains duplicate keys: {key_columns}")
        rows_by_year[str(year)] = len(frame)
        frames.append(frame)

    merged = pd.concat(frames, ignore_index=True)
    if merged[key_columns].duplicated().any():
        raise ValueError(f"annual inputs overlap on keys: {key_columns}")
    merged = merged.sort_values(key_columns, kind="stable").reset_index(drop=True)
    dates = pd.to_datetime(merged[date_column])
    coverage = MergeCoverage(
        rows=len(merged),
        start_date=dates.min().date().isoformat(),
        end_date=dates.max().date().isoformat(),
        years=sorted(dates.dt.year.unique().tolist()),
        months=int(dates.dt.to_period("M").nunique()),
        entities=int(merged[entity_column].nunique()),
        rows_by_year=rows_by_year,
    )
    return merged, coverage
