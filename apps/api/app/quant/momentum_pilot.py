"""Deterministic, lagged momentum portfolio for the constrained 2024 pilot."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from app.quant.statistics import describe_returns


@dataclass(frozen=True)
class MomentumPilotCoverage:
    months: int
    invested_months: int
    holdings: int
    marked_return_months: int
    complete_official_return_months: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def _formation_scores(monthly: pd.DataFrame, lookback_months: int) -> pd.DataFrame:
    frame = monthly.sort_values(["ticker", "observation_month"]).copy()
    frame["formation_return"] = frame.groupby("ticker")["marked_monthly_return"].transform(
        lambda values: (
            (1 + values)
            .rolling(lookback_months, min_periods=lookback_months)
            .apply(lambda window: window.prod() - 1, raw=False)
            .shift(1)
        )
    )
    return frame


def run_momentum_pilot(
    monthly: pd.DataFrame,
    *,
    lookback_months: int = 3,
    portfolio_size: int = 5,
    transaction_cost_bps: float = 50,
) -> dict:
    """Run a monthly top-momentum pilot with a one-period information lag."""
    if lookback_months < 1:
        raise ValueError("lookback_months must be positive")
    if portfolio_size < 1:
        raise ValueError("portfolio_size must be positive")
    required = {
        "observation_month",
        "ticker",
        "marked_monthly_return",
        "official_monthly_return",
    }
    missing = sorted(required.difference(monthly.columns))
    if missing:
        raise ValueError(f"monthly returns missing columns: {', '.join(missing)}")
    if monthly[["observation_month", "ticker"]].duplicated().any():
        raise ValueError("monthly returns contain duplicate month-ticker keys")

    scored = _formation_scores(monthly, lookback_months)
    months = sorted(scored["observation_month"].unique())
    tickers = sorted(scored["ticker"].unique())
    previous_weights = pd.Series(0.0, index=tickers)
    performance_rows: list[dict] = []
    holding_rows: list[dict] = []

    for month in months:
        cross_section = scored[scored["observation_month"] == month].copy()
        eligible = cross_section.dropna(subset=["formation_return", "marked_monthly_return"])
        selected = eligible.nlargest(portfolio_size, "formation_return").copy()
        current_weights = pd.Series(0.0, index=tickers)
        if not selected.empty:
            current_weights.loc[selected["ticker"]] = 1 / len(selected)

        if previous_weights.sum() == 0 and current_weights.sum() > 0:
            turnover = 1.0
        else:
            turnover = float((current_weights - previous_weights).abs().sum() / 2)
        cost = turnover * transaction_cost_bps / 10_000
        marked_gross = (
            float(selected["marked_monthly_return"].mean()) if not selected.empty else None
        )
        official_available = selected["official_monthly_return"].notna().sum()
        official_gross = (
            float(selected["official_monthly_return"].mean())
            if official_available
            else None
        )
        performance_rows.append(
            {
                "observation_month": month,
                "positions": len(selected),
                "turnover": turnover,
                "transaction_cost": cost,
                "marked_gross_return": marked_gross,
                "marked_net_return": marked_gross - cost if marked_gross is not None else None,
                "official_gross_return": official_gross,
                "official_net_return": official_gross - cost if official_gross is not None else None,
                "official_return_coverage": (
                    official_available / len(selected) if len(selected) else None
                ),
            }
        )
        for rank, (_, row) in enumerate(
            selected.sort_values(["formation_return", "ticker"], ascending=[False, True]).iterrows(),
            start=1,
        ):
            holding_rows.append(
                {
                    "observation_month": month,
                    "ticker": row["ticker"],
                    "rank": rank,
                    "formation_return": float(row["formation_return"]),
                    "weight": float(current_weights[row["ticker"]]),
                }
            )
        previous_weights = current_weights

    performance = pd.DataFrame(performance_rows)
    holdings = pd.DataFrame(holding_rows)
    invested = performance[performance["positions"] > 0]
    coverage = MomentumPilotCoverage(
        months=len(months),
        invested_months=len(invested),
        holdings=len(holdings),
        marked_return_months=int(invested["marked_net_return"].notna().sum()),
        complete_official_return_months=int(
            invested["official_return_coverage"].eq(1).sum()
        ),
    )
    statistics = (
        describe_returns(invested["marked_net_return"])
        if not invested.empty
        else None
    )
    return {
        "status": "preliminary",
        "methodology": {
            "signal": f"prior {lookback_months}-month compounded marked-price return",
            "information_lag": "one month",
            "selection": f"top {portfolio_size} securities by formation return",
            "weighting": "equal weight",
            "rebalance_frequency": "monthly",
            "transaction_cost_bps": transaction_cost_bps,
            "official_return_interpretation": "sensitivity series over selected holdings with an observed official-trade return",
        },
        "coverage": coverage.to_dict(),
        "statistics": statistics,
        "performance": performance,
        "holdings": holdings,
    }
