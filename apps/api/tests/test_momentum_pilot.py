import pandas as pd
import pytest

from app.quant.momentum_pilot import run_momentum_pilot


def test_momentum_pilot_lags_signal_and_applies_costs():
    rows = []
    returns = {"AAA": [0.1, 0.1, 0.1, -0.2], "BBB": [0.0, 0.0, 0.0, 0.1]}
    for ticker, values in returns.items():
        for month, value in enumerate(values, start=1):
            rows.append(
                {
                    "observation_month": f"2024-{month:02d}",
                    "ticker": ticker,
                    "marked_monthly_return": value,
                    "official_monthly_return": value,
                }
            )

    result = run_momentum_pilot(
        pd.DataFrame(rows), lookback_months=3, portfolio_size=1, transaction_cost_bps=50
    )

    assert result["coverage"]["invested_months"] == 1
    assert result["holdings"].iloc[0]["ticker"] == "AAA"
    april = result["performance"].iloc[-1]
    assert april["turnover"] == 1
    assert april["marked_gross_return"] == pytest.approx(-0.2)
    assert april["marked_net_return"] == pytest.approx(-0.205)


def test_momentum_pilot_reports_incomplete_official_coverage():
    monthly = pd.DataFrame(
        {
            "observation_month": [f"2024-{month:02d}" for month in range(1, 5)],
            "ticker": ["AAA"] * 4,
            "marked_monthly_return": [0.1, 0.1, 0.1, 0.1],
            "official_monthly_return": [0.1, 0.1, 0.1, None],
        }
    )

    result = run_momentum_pilot(monthly, lookback_months=3, portfolio_size=1)

    assert result["coverage"]["complete_official_return_months"] == 0
    assert result["performance"].iloc[-1]["official_return_coverage"] == 0
