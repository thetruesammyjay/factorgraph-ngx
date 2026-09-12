import numpy as np
import pandas as pd
from statsmodels.stats import diagnostic
import statsmodels.api as sm

def describe_returns(returns: pd.Series, periods_per_year: int = 12) -> dict[str, float]:
    returns = returns.dropna().astype(float)
    annualised_return = float((1 + returns).prod() ** (periods_per_year / max(len(returns), 1)) - 1)
    volatility = float(returns.std(ddof=1) * np.sqrt(periods_per_year))
    sharpe = float(returns.mean() / returns.std(ddof=1) * np.sqrt(periods_per_year)) if returns.std() else 0.0
    curve = (1 + returns).cumprod()
    return {"observations": float(len(returns)), "mean_return": float(returns.mean()), "annualised_return": annualised_return, "volatility": volatility, "sharpe": sharpe, "max_drawdown": float((curve / curve.cummax() - 1).min())}

def newey_west_t_stat(returns: pd.Series, lags: int = 4) -> float:
    values = returns.dropna().astype(float)
    model = sm.OLS(values, np.ones(len(values))).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return float(model.tvalues[0])