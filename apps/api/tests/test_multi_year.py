from pathlib import Path

import pandas as pd
import pytest

from app.data.multi_year import merge_annual_csvs


def write_prices(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def test_merge_annual_csvs_validates_and_sorts(tmp_path: Path) -> None:
    first = tmp_path / "2023.csv"
    second = tmp_path / "2024.csv"
    write_prices(first, [{"trading_date": "2023-12-29", "ticker": "UBA", "close": 20}])
    write_prices(second, [{"trading_date": "2024-01-02", "ticker": "UBA", "close": 21}])

    merged, coverage = merge_annual_csvs(
        {2024: second, 2023: first}, date_column="trading_date",
        key_columns=["trading_date", "ticker"], entity_column="ticker",
    )

    assert merged["close"].tolist() == [20, 21]
    assert coverage.years == [2023, 2024]
    assert coverage.months == 2
    assert coverage.rows_by_year == {"2023": 1, "2024": 1}


def test_merge_annual_csvs_rejects_wrong_declared_year(tmp_path: Path) -> None:
    path = tmp_path / "prices.csv"
    write_prices(path, [{"trading_date": "2024-01-02", "ticker": "UBA"}])
    with pytest.raises(ValueError, match="declared as 2023"):
        merge_annual_csvs(
            {2023: path}, date_column="trading_date",
            key_columns=["trading_date", "ticker"], entity_column="ticker",
        )


def test_merge_annual_csvs_rejects_duplicate_keys(tmp_path: Path) -> None:
    path = tmp_path / "prices.csv"
    row = {"trading_date": "2024-01-02", "ticker": "UBA"}
    write_prices(path, [row, row])
    with pytest.raises(ValueError, match="duplicate keys"):
        merge_annual_csvs(
            {2024: path}, date_column="trading_date",
            key_columns=["trading_date", "ticker"], entity_column="ticker",
        )
