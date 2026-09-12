import numpy as np
import pandas as pd

def bootstrap_mean(returns: pd.Series, iterations: int = 10_000, seed: int = 42, confidence: float = .95) -> dict[str, float]:
    values = returns.dropna().to_numpy(dtype=float)
    if not len(values): raise ValueError("Cannot bootstrap an empty return series")
    rng = np.random.default_rng(seed)
    samples = rng.choice(values, size=(iterations, len(values)), replace=True).mean(axis=1)
    alpha = (1 - confidence) / 2
    return {"mean": float(samples.mean()), "lower": float(np.quantile(samples, alpha)), "upper": float(np.quantile(samples, 1 - alpha)), "iterations": float(iterations), "seed": float(seed)}