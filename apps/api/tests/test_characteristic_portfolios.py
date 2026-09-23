import pandas as pd

from app.quant.characteristic_portfolios import build_characteristic_portfolios


def test_characteristic_portfolios_lag_formation_and_report_inference():
    rows = []
    for month in pd.period_range("2023-01", periods=5, freq="M").astype(str):
        for ticker, market_cap, book_to_market, ret in (
            ("AAA", 10, 2, 0.10),
            ("BBB", 20, 1, 0.05),
            ("CCC", 30, 0.5, 0.02),
            ("DDD", 40, 0.25, -0.01),
        ):
            rows.append(
                {
                    "observation_month": month,
                    "ticker": ticker,
                    "marked_monthly_return": ret,
                    "market_cap": market_cap,
                    "book_to_market": book_to_market,
                    "size_eligible": True,
                    "value_eligible": True,
                }
            )
    result = build_characteristic_portfolios(pd.DataFrame(rows), bootstrap_iterations=100)

    first = result["performance"].iloc[0]
    assert first["formation_month"] == "2023-01"
    assert first["holding_month"] == "2023-02"
    assert first["size_spread_return"] == 0.07
    assert first["value_spread_return"] == 0.07
    assert result["coverage"]["months_with_size_spread"] == 4
    assert result["factors"]["size"]["statistics"]["newey_west_t"] is not None
