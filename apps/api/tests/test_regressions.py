import numpy as np
import pandas as pd
import pytest

from app.quant.regressions import build_factor_regressions, factor_regression


def test_factor_regression_reports_hac_coefficients_and_short_sample_status():
    factor = pd.Series(np.linspace(-0.02, 0.03, 18), name="market_excess_return")
    target = 0.01 + 1.5 * factor

    result = factor_regression(target, factor.to_frame())

    assert result["status"] == "preliminary"
    assert result["observations"] == 18
    assert result["newey_west_lags"] == 4
    assert result["predictors"] == ["market_excess_return"]
    assert result["coefficients"]["market_excess_return"]["coefficient"] == pytest.approx(1.5)


def test_factor_regression_blocks_when_sample_is_too_short():
    result = factor_regression(
        pd.Series([0.01, 0.02, 0.03]),
        pd.DataFrame({"market_excess_return": [0.0, 0.01, 0.02]}),
    )

    assert result["status"] == "blocked"
    assert result["observations"] == 3
    assert result["coefficients"] == {}


def test_build_factor_regressions_aligns_factor_returns_by_month():
    market = pd.DataFrame(
        {
            "observation_month": ["2024-01", "2024-02", "2024-03", "2024-04"],
            "market_excess_return": [0.01, 0.02, -0.01, 0.03],
        }
    )
    characteristics = pd.DataFrame(
        {
            "observation_month": ["2024-01", "2024-02", "2024-03", "2024-04"],
            "size_spread_return": [0.02, 0.01, -0.02, 0.04],
            "value_spread_return": [0.01, 0.03, -0.01, 0.02],
        }
    )
    momentum = pd.DataFrame(
        {
            "observation_month": ["2024-01", "2024-02", "2024-03", "2024-04"],
            "marked_net_return": [0.01, 0.02, -0.02, 0.03],
        }
    )

    result = build_factor_regressions(
        market,
        characteristics,
        momentum,
        minimum_observations=3,
    )

    assert set(result) == {"size", "value", "momentum"}
    assert result["size"]["observations"] == 4
    assert result["value"]["target_definition"] == "Value spread (High minus Low)"
