import pandas as pd

def equal_weight_portfolio(scores: pd.Series, size: int = 10) -> pd.Series:
    selected = scores.sort_values(ascending=False).head(size)
    return pd.Series(1 / len(selected), index=selected.index) if len(selected) else pd.Series(dtype=float)