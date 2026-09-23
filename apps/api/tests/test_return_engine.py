import pandas as pd
import pytest

from app.quant.return_engine import (
    build_daily_returns,
    build_equal_weight_market_proxy,
    build_monthly_returns,
    latest_momentum_snapshot,
)


def price_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"trading_date": "2024-01-02", "ticker": "AAA", "close": 100, "price_status": "official_trade"},
            {"trading_date": "2024-01-03", "ticker": "AAA", "close": 100, "price_status": "carried_market_price"},
            {"trading_date": "2024-02-01", "ticker": "AAA", "close": 110, "price_status": "official_trade"},
            {"trading_date": "2024-03-01", "ticker": "AAA", "close": 121, "price_status": "official_trade"},
            {"trading_date": "2024-04-01", "ticker": "AAA", "close": 133.1, "price_status": "official_trade"},
            {"trading_date": "2024-01-02", "ticker": "BBB", "close": 200, "price_status": "official_trade"},
            {"trading_date": "2024-02-01", "ticker": "BBB", "close": 180, "price_status": "official_trade"},
            {"trading_date": "2024-03-01", "ticker": "BBB", "close": 180, "price_status": "carried_market_price"},
            {"trading_date": "2024-04-01", "ticker": "BBB", "close": 198, "price_status": "official_trade"},
        ]
    )


def test_daily_returns_keep_marked_and_trade_to_trade_series_separate():
    daily, coverage = build_daily_returns(price_frame())
    aaa = daily[daily["ticker"] == "AAA"].reset_index(drop=True)

    assert aaa.loc[1, "marked_return"] == 0
    assert pd.isna(aaa.loc[1, "official_trade_return"])
    assert aaa.loc[2, "official_trade_return"] == pytest.approx(0.1)
    assert coverage.carried_price_rows == 2
    assert coverage.official_trade_returns == 5


def test_monthly_market_proxy_and_momentum_are_deterministic():
    daily, _ = build_daily_returns(price_frame())
    monthly = build_monthly_returns(daily)
    proxy = build_equal_weight_market_proxy(monthly)
    momentum = latest_momentum_snapshot(monthly, months=3)

    february = proxy[proxy["observation_month"] == "2024-02"].iloc[0]
    assert february["marked_equal_weight_return"] == pytest.approx(0)
    assert february["official_security_count"] == 2
    assert momentum.iloc[0]["ticker"] == "AAA"
    assert momentum.iloc[0]["momentum_return"] == pytest.approx(0.331)


def test_duplicate_price_keys_are_rejected():
    duplicated = pd.concat([price_frame(), price_frame().iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match="duplicate ticker-date"):
        build_daily_returns(duplicated)
