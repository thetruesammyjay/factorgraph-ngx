import pandas as pd

def cross_sectional_zscore(values: pd.Series) -> pd.Series:
    deviation = values.std(ddof=0)
    return (values - values.mean()) / deviation if deviation else values * 0

def composite_score(frame: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    scores = [cross_sectional_zscore(frame[column]) * weight for column, weight in weights.items()]
    return sum(scores)