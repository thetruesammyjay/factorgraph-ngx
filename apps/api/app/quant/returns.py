import pandas as pd

def simple_returns(prices: pd.Series) -> pd.Series:
    return prices.sort_index().pct_change().dropna()

def cumulative_return(returns: pd.Series) -> float:
    return float((1 + returns).prod() - 1)

def max_drawdown(returns: pd.Series) -> float:
    curve = (1 + returns).cumprod()
    return float((curve / curve.cummax() - 1).min())