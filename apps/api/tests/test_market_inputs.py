import pandas as pd
import pytest

from app.data.market_inputs import (
    build_monthly_market_inputs,
    validate_benchmark_observations,
    validate_risk_free_observations,
)


def test_build_monthly_market_inputs_uses_month_end_and_effective_rate():
    benchmark = pd.DataFrame(
        {
            "observation_date": ["2024-01-30", "2024-01-31", "2024-02-29"],
            "index_code": ["NGXASI"] * 3,
            "index_name": ["NGX All-Share Index"] * 3,
            "close": [99, 100, 110],
            "source_id": ["ngx"] * 3,
        }
    )
    risk_free = pd.DataFrame(
        {
            "observation_date": ["2024-01-31", "2024-02-29"],
            "series_name": ["Treasury bill"] * 2,
            "tenor": ["91d", "91d"],
            "annual_rate_percent": [12, 12],
            "source_id": ["cbn"] * 2,
        }
    )

    monthly, coverage = build_monthly_market_inputs(benchmark, risk_free)

    assert monthly["observation_month"].tolist() == ["2024-01", "2024-02"]
    assert monthly.loc[1, "market_return"] == pytest.approx(0.10)
    expected_risk_free = 1.12 ** (1 / 12) - 1
    assert monthly.loc[1, "risk_free_return"] == pytest.approx(expected_risk_free)
    assert monthly.loc[1, "market_excess_return"] == pytest.approx(
        0.10 - expected_risk_free
    )
    assert coverage.aligned_months == 2


def test_market_input_validation_rejects_duplicate_keys_and_invalid_rates():
    benchmark = pd.DataFrame(
        {
            "observation_date": ["2024-01-31", "2024-01-31"],
            "index_code": ["NGXASI", "NGXASI"],
            "index_name": ["ASI", "ASI"],
            "close": [100, 101],
            "source_id": ["ngx", "ngx"],
        }
    )
    with pytest.raises(ValueError, match="duplicate index-date"):
        validate_benchmark_observations(benchmark)

    risk_free = pd.DataFrame(
        {
            "observation_date": ["2024-01-31"],
            "series_name": ["Treasury bill"],
            "tenor": ["91D"],
            "annual_rate_percent": [-100],
            "source_id": ["cbn"],
        }
    )
    with pytest.raises(ValueError, match="greater than -100"):
        validate_risk_free_observations(risk_free)


def test_empty_templates_remain_unavailable():
    benchmark = pd.DataFrame(columns=sorted({
        "observation_date", "index_code", "index_name", "close", "source_id"
    }))
    risk_free = pd.DataFrame(columns=sorted({
        "observation_date", "series_name", "tenor", "annual_rate_percent", "source_id"
    }))

    monthly, coverage = build_monthly_market_inputs(benchmark, risk_free)

    assert monthly.empty
    assert coverage.aligned_months == 0
