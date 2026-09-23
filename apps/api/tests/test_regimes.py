import pandas as pd

from app.quant.regimes import build_regime_analysis


def test_regime_analysis_blocks_short_monthly_sample_with_explicit_coverage():
    market = pd.DataFrame(
        {
            "observation_month": [f"2024-{month:02d}" for month in range(1, 13)],
            "market_excess_return": [0.01, -0.02, 0.03, 0.01, 0.0, 0.02, -0.01, 0.01, 0.02, -0.03, 0.01, 0.02],
        }
    )

    result = build_regime_analysis(market)

    assert result["status"] == "blocked"
    assert result["coverage"]["monthly_endpoints"] == 12
    assert result["coverage"]["minimum_observations"] == 36
    assert result["model"] is None
    assert result["timeline"] == []
