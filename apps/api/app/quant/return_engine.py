"""Deterministic return construction with explicit stale-price treatment."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

REQUIRED_PRICE_COLUMNS = {"trading_date", "ticker", "close", "price_status"}
OFFICIAL_TRADE = "official_trade"


@dataclass(frozen=True)
class ReturnCoverage:
    observations: int
    tickers: int
    dates: int
    marked_returns: int
    official_trade_returns: int
    carried_price_rows: int
    first_date: str
    last_date: str

    def to_dict(self) -> dict[str, int | str]:
        return asdict(self)


def build_daily_returns(prices: pd.DataFrame) -> tuple[pd.DataFrame, ReturnCoverage]:
    """Construct marked-price and trade-to-trade returns without silent filling."""
    missing = sorted(REQUIRED_PRICE_COLUMNS.difference(prices.columns))
    if missing:
        raise ValueError(f"price data missing columns: {', '.join(missing)}")

    frame = prices.copy()
    frame["trading_date"] = pd.to_datetime(frame["trading_date"], errors="coerce")
    frame["ticker"] = frame["ticker"].astype("string").str.strip().str.upper()
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    if frame["trading_date"].isna().any():
        raise ValueError("price data contains invalid trading dates")
    if frame[["ticker", "trading_date"]].duplicated().any():
        raise ValueError("price data contains duplicate ticker-date keys")
    if frame["close"].isna().any() or (frame["close"] <= 0).any():
        raise ValueError("price data contains missing or non-positive closes")

    frame = frame.sort_values(["ticker", "trading_date"]).reset_index(drop=True)
    frame["marked_return"] = frame.groupby("ticker", sort=False)["close"].pct_change(
        fill_method=None
    )
    frame["is_official_trade"] = frame["price_status"].eq(OFFICIAL_TRADE)
    frame["is_carried_price"] = ~frame["is_official_trade"]
    frame["official_trade_return"] = pd.NA
    for _, group in frame[frame["is_official_trade"]].groupby("ticker", sort=False):
        returns = group["close"].pct_change(fill_method=None)
        frame.loc[group.index, "official_trade_return"] = returns
    frame["official_trade_return"] = pd.to_numeric(
        frame["official_trade_return"], errors="coerce"
    )

    coverage = ReturnCoverage(
        observations=len(frame),
        tickers=frame["ticker"].nunique(),
        dates=frame["trading_date"].nunique(),
        marked_returns=int(frame["marked_return"].notna().sum()),
        official_trade_returns=int(frame["official_trade_return"].notna().sum()),
        carried_price_rows=int(frame["is_carried_price"].sum()),
        first_date=str(frame["trading_date"].min().date()),
        last_date=str(frame["trading_date"].max().date()),
    )
    return frame, coverage


def build_monthly_returns(daily: pd.DataFrame) -> pd.DataFrame:
    """Build marked and official-trade monthly returns from validated daily rows."""
    required = {"trading_date", "ticker", "close", "is_official_trade"}
    missing = sorted(required.difference(daily.columns))
    if missing:
        raise ValueError(f"daily returns missing columns: {', '.join(missing)}")

    frame = daily.copy().sort_values(["ticker", "trading_date"])
    frame["month"] = frame["trading_date"].dt.to_period("M")
    marked = frame.groupby(["ticker", "month"], as_index=False).tail(1).copy()
    marked["marked_monthly_return"] = marked.groupby("ticker")["close"].pct_change(
        fill_method=None
    )
    marked = marked[["ticker", "month", "trading_date", "close", "marked_monthly_return"]]

    trades = frame[frame["is_official_trade"]]
    official = trades.groupby(["ticker", "month"], as_index=False).tail(1).copy()
    official["official_monthly_return"] = official.groupby("ticker")["close"].pct_change(
        fill_method=None
    )
    official = official[["ticker", "month", "official_monthly_return"]]

    result = marked.merge(official, on=["ticker", "month"], how="left")
    result["observation_month"] = result["month"].astype(str)
    return result.drop(columns="month").sort_values(["observation_month", "ticker"])


def build_equal_weight_market_proxy(monthly: pd.DataFrame) -> pd.DataFrame:
    """Aggregate monthly security returns into transparent equal-weight proxies."""
    required = {
        "observation_month",
        "marked_monthly_return",
        "official_monthly_return",
    }
    missing = sorted(required.difference(monthly.columns))
    if missing:
        raise ValueError(f"monthly returns missing columns: {', '.join(missing)}")

    rows = []
    for month, group in monthly.groupby("observation_month", sort=True):
        marked = group["marked_monthly_return"].dropna()
        official = group["official_monthly_return"].dropna()
        rows.append(
            {
                "observation_month": month,
                "marked_equal_weight_return": marked.mean() if not marked.empty else pd.NA,
                "official_equal_weight_return": (
                    official.mean() if not official.empty else pd.NA
                ),
                "marked_security_count": len(marked),
                "official_security_count": len(official),
            }
        )
    return pd.DataFrame(rows)


def latest_momentum_snapshot(
    monthly: pd.DataFrame, months: int = 3, skip_months: int = 0
) -> pd.DataFrame:
    """Rank latest short-horizon momentum using marked monthly closes."""
    if months < 1:
        raise ValueError("momentum window must be positive")
    if skip_months < 0:
        raise ValueError("skip_months cannot be negative")
    frame = monthly.sort_values(["ticker", "observation_month"]).copy()
    frame["momentum_return"] = frame.groupby("ticker")["marked_monthly_return"].transform(
        lambda values: (
            (1 + values)
            .rolling(months, min_periods=months)
            .apply(lambda window: window.prod() - 1, raw=False)
            .shift(skip_months)
        )
    )
    latest_month = frame["observation_month"].max()
    snapshot = frame[frame["observation_month"] == latest_month].copy()
    snapshot["rank"] = snapshot["momentum_return"].rank(ascending=False, method="min")
    return snapshot[
        ["observation_month", "ticker", "momentum_return", "rank"]
    ].sort_values(["rank", "ticker"], na_position="last")
