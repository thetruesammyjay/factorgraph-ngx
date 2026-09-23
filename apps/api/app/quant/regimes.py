from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM


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
    return [RegimeSummary(int(state), float(group.market_return.mean()), float(group.market_return.std()), len(group)) for state, group in joined.groupby("state")]


def build_regime_analysis(
    market_factor: pd.DataFrame,
    *,
    states: int = 3,
    minimum_observations: int = 36,
    volatility_window: int = 3,
    seed: int = 42,
) -> dict:
    """Fit a deterministic Gaussian HMM when the monthly sample is sufficient."""
    if states < 2:
        raise ValueError("states must be at least two")
    if volatility_window < 2:
        raise ValueError("volatility_window must be at least two")

    if market_factor.empty or "market_excess_return" not in market_factor:
        endpoints = 0
        complete_returns = 0
        features = pd.DataFrame()
    else:
        returns = pd.to_numeric(market_factor["market_excess_return"], errors="coerce")
        endpoints = len(market_factor)
        complete_returns = int(returns.notna().sum())
        features = build_regime_features(returns, window=volatility_window)

    feature_observations = len(features)
    coverage = {
        "monthly_endpoints": endpoints,
        "complete_market_returns": complete_returns,
        "feature_observations": feature_observations,
        "minimum_observations": minimum_observations,
        "states": states,
        "volatility_window": volatility_window,
    }
    if endpoints < minimum_observations:
        return {
            "status": "blocked",
            "reason": (
                f"The current experiment has only {endpoints} monthly endpoints; a multi-state "
                f"regime model requires at least {minimum_observations} observations for this pilot."
            ),
            "coverage": coverage,
            "model": None,
            "timeline": [],
            "statistics": [],
            "transition_matrix": None,
        }
    if feature_observations < minimum_observations - 1:
        return {
            "status": "blocked",
            "reason": "rolling volatility leaves too few complete regime feature observations",
            "coverage": coverage,
            "model": None,
            "timeline": [],
            "statistics": [],
            "transition_matrix": None,
        }

    values = features[["market_return", "rolling_volatility"]].to_numpy(dtype=float)
    best_model = None
    best_score = -np.inf
    for candidate_seed in (seed, seed + 1, seed + 2):
        model = GaussianHMM(
            n_components=states,
            covariance_type="full",
            n_iter=500,
            random_state=candidate_seed,
        )
        try:
            model.fit(values)
            score = float(model.score(values))
        except (ValueError, np.linalg.LinAlgError):
            continue
        if np.isfinite(score) and score > best_score:
            best_model = model
            best_score = score
    if best_model is None:
        return {
            "status": "blocked",
            "reason": "Gaussian HMM failed to converge for every deterministic seed",
            "coverage": coverage,
            "model": None,
            "timeline": [],
            "statistics": [],
            "transition_matrix": None,
        }

    state_values = best_model.predict(values)
    probabilities = best_model.predict_proba(values)
    summaries = [asdict(summary) for summary in summarise_regimes(features, pd.Series(state_values, index=features.index))]
    months = market_factor.loc[features.index, "observation_month"].astype(str).tolist()
    timeline = [
        {
            "observation_month": month,
            "state": int(state),
            "probabilities": [float(value) for value in row],
        }
        for month, state, row in zip(months, state_values, probabilities)
    ]
    return {
        "status": "eligible",
        "reason": None,
        "coverage": coverage,
        "model": {
            "algorithm": "GaussianHMM",
            "covariance_type": "full",
            "converged": bool(best_model.monitor_.converged),
            "iterations": int(best_model.monitor_.iter),
            "log_likelihood": best_score,
            "seed": seed,
        },
        "timeline": timeline,
        "statistics": summaries,
        "transition_matrix": best_model.transmat_.tolist(),
    }
