from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class RegimeSummary:
    state: int
    mean_return: float
    volatility: float
    observations: int

def build_regime_features(market_returns: pd.Series, window: int = 3) -> pd.DataFrame:
    return pd.DataFrame({"market_return": market_returns, "rolling_volatility": market_returns.rolling(window).std()}).dropna()

def summarise_regimes(features: pd.DataFrame, states: pd.Series) -> list[RegimeSummary]:
    joined = features.assign(state=states)
    return [RegimeSummary(int(state), float(group.market_return.mean()), float(group.market_return.std()), int(len(group))) for state, group in joined.groupby("state")]