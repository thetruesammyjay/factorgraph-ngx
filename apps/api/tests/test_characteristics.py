import pandas as pd

from app.factors.characteristics import (
    build_point_in_time_characteristics,
    latest_characteristic_snapshot,
)


def test_characteristics_use_only_fundamentals_effective_by_month_end():
    monthly = pd.DataFrame(
        {
            "observation_month": ["2024-01", "2024-02", "2024-03"],
            "trading_date": ["2024-01-31", "2024-02-29", "2024-03-31"],
            "ticker": ["AAA"] * 3,
            "close": [10, 20, 30],
        }
    )
    fundamentals = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA"],
            "fiscal_period": ["2022-12-31", "2023-12-31"],
            "effective_from": ["2023-03-31", "2024-03-15"],
            "effective_date_source": ["ACTUAL_PUBLICATION_DATE"] * 2,
            "book_equity": [100, 300],
            "shares_outstanding": [10, 20],
            "source_id": ["old", "new"],
        }
    )

    result, coverage = build_point_in_time_characteristics(monthly, fundamentals)

    assert result["source_id"].tolist() == ["old", "old", "new"]
    assert result["market_cap"].tolist() == [100, 200, 600]
    assert result["book_to_market"].tolist() == [1.0, 0.5, 0.5]
    assert coverage.point_in_time_observations == 3


def test_value_excludes_negative_equity_without_excluding_size():
    monthly = pd.DataFrame(
        {
            "observation_month": ["2024-04"],
            "trading_date": ["2024-04-30"],
            "ticker": ["AAA"],
            "close": [5],
        }
    )
    fundamentals = pd.DataFrame(
        {
            "ticker": ["AAA"],
            "fiscal_period": ["2023-12-31"],
            "effective_from": ["2024-03-30"],
            "effective_date_source": ["FIXED_LAG_ESTIMATE"],
            "book_equity": [-10],
            "shares_outstanding": [100],
            "source_id": ["negative"],
        }
    )

    result, _ = build_point_in_time_characteristics(monthly, fundamentals)
    snapshot = latest_characteristic_snapshot(result).iloc[0]

    assert bool(snapshot["size_eligible"])
    assert not bool(snapshot["value_eligible"])
    assert snapshot["market_cap"] == 500
    assert pd.isna(snapshot["book_to_market"])
    assert snapshot["value_exclusion_reason"] == "non_positive_or_missing_book_equity"
