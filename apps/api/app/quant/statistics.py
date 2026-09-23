import numpy as np
import pandas as pd
import statsmodels.api as sm


def describe_returns(
    returns: pd.Series, periods_per_year: int = 12
) -> dict[str, float | None]:
    returns = returns.dropna().astype(float)
    wealth = float((1 + returns).prod())
    annualised_return = (
        float(wealth ** (periods_per_year / max(len(returns), 1)) - 1)
        if wealth > 0
        else None
    )
    volatility = float(returns.std(ddof=1) * np.sqrt(periods_per_year))
    sharpe = float(returns.mean() / returns.std(ddof=1) * np.sqrt(periods_per_year)) if returns.std() else 0.0
    curve = (1 + returns).cumprod()
    max_drawdown = (
        float((curve / curve.cummax() - 1).min())
        if (curve > 0).all()
        else None
    )
    return {
        "observations": float(len(returns)),
        "mean_return": float(returns.mean()),
        "annualised_return": annualised_return,
        "volatility": volatility,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
    }

def newey_west_t_stat(returns: pd.Series, lags: int = 4) -> float:
    values = returns.dropna().astype(float)
    model = sm.OLS(values, np.ones(len(values))).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return float(model.tvalues.iloc[0])
