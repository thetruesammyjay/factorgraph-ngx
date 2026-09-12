import pandas as pd

def transaction_cost(turnover: pd.Series | float, basis_points: float = 50) -> pd.Series | float:
    return turnover * (basis_points / 10_000)

def net_returns(gross: pd.Series, turnover: pd.Series, basis_points: float = 50) -> pd.Series:
    return gross - transaction_cost(turnover, basis_points)