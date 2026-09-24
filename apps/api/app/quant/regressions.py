"""Deterministic factor-regression diagnostics for experiment reports."""

from __future__ import annotations

import pandas as pd
import statsmodels.api as sm


def _blocked(
    reason: str,
    *,
    observations: int = 0,
    predictors: list[str] | None = None,
) -> dict:
    return {
        "status": "blocked",
        "reason": reason,
        "observations": observations,
        "predictors": predictors or [],
        "newey_west_lags": None,
        "alpha": None,
        "alpha_std_error": None,
        "alpha_t": None,
        "alpha_p_value": None,
        "r_squared": None,
        "adjusted_r_squared": None,
        "coefficients": {},
    }


def factor_regression(
    excess_returns: pd.Series,
    factors: pd.DataFrame,
    *,
    lags: int | None = None,
    minimum_observations: int = 12,
) -> dict:
    """Regress a return series on supplied factors with HAC standard errors."""
    if not isinstance(factors, pd.DataFrame):
        raise TypeError("factors must be a pandas DataFrame")
    predictors = factors.copy()
    predictors.columns = [str(column) for column in predictors.columns]
    if predictors.columns.duplicated().any():
        raise ValueError("factors contain duplicate column names")
    predictor_names = list(predictors.columns)
    if not predictor_names:
        return _blocked("at least one predictor is required")

    frame = pd.concat(
        [pd.to_numeric(excess_returns, errors="coerce").rename("target"), predictors],
        axis=1,
    )
    frame = frame.apply(pd.to_numeric, errors="coerce").dropna()
    observations = len(frame)
    if observations < max(3, minimum_observations):
        return _blocked(
            f"at least {minimum_observations} complete observations are required",
            observations=observations,
            predictors=predictor_names,
        )
    if frame[predictor_names].nunique(dropna=False).eq(1).any():
        constant_predictors = frame[predictor_names].columns[
            frame[predictor_names].nunique(dropna=False).eq(1)
        ].tolist()
        return _blocked(
            "constant predictors cannot be estimated: " + ", ".join(constant_predictors),
            observations=observations,
            predictors=predictor_names,
        )

    max_lags = min(
        max(0, observations - 1),
        max(0, int(lags if lags is not None else min(4, observations - 1))),
    )
    model = sm.OLS(frame["target"], sm.add_constant(frame[predictor_names])).fit(
        cov_type="HAC", cov_kwds={"maxlags": max_lags}
    )
    coefficients = {
        name: {
            "coefficient": float(model.params[name]),
            "std_error": float(model.bse[name]),
            "t_stat": float(model.tvalues[name]),
            "p_value": float(model.pvalues[name]),
        }
        for name in predictor_names
    }
    return {
        "status": "preliminary" if observations < 36 else "eligible",
        "reason": (
            "short pilot sample; coefficients are descriptive" if observations < 36 else None
        ),
        "observations": observations,
        "predictors": predictor_names,
        "newey_west_lags": max_lags,
        "alpha": float(model.params["const"]),
        "alpha_std_error": float(model.bse["const"]),
        "alpha_t": float(model.tvalues["const"]),
        "alpha_p_value": float(model.pvalues["const"]),
        "r_squared": float(model.rsquared),
        "adjusted_r_squared": float(model.rsquared_adj),
        "coefficients": coefficients,
    }


def build_factor_regressions(
    market_inputs: pd.DataFrame,
    characteristic_performance: pd.DataFrame,
    momentum_performance: pd.DataFrame,
    *,
    minimum_observations: int = 12,
) -> dict[str, dict]:
    """Build market-only diagnostics for each available pilot factor return."""
    market = market_inputs.copy()
    if market.empty or "observation_month" not in market:
        base = pd.DataFrame(columns=["observation_month", "market_excess_return"])
    else:
        base_columns = ["observation_month", "market_excess_return"]
        if "risk_free_return" in market:
            base_columns.append("risk_free_return")
        base = market[base_columns].copy()
    base["observation_month"] = base["observation_month"].astype(str)
    base["market_excess_return"] = pd.to_numeric(
        base["market_excess_return"], errors="coerce"
    )

    outputs: dict[str, dict] = {}
    targets = {
        "size": (
            characteristic_performance,
            "holding_month",
            "size_spread_return",
            "Size spread (Small minus Big)",
        ),
        "value": (
            characteristic_performance,
            "holding_month",
            "value_spread_return",
            "Value spread (High minus Low)",
        ),
        "momentum": (
            momentum_performance,
            "observation_month",
            "marked_net_return",
            "Momentum net return",
        ),
    }
    for factor, (source, month_column, column, definition) in targets.items():
        if month_column not in source.columns and "observation_month" in source.columns:
            month_column = "observation_month"
        if source.empty or month_column not in source or column not in source:
            outputs[factor] = _blocked("factor return series is unavailable")
            outputs[factor]["target_definition"] = definition
            continue
        target = source[[month_column, column]].copy()
        target = target.rename(columns={month_column: "observation_month"})
        target["observation_month"] = target["observation_month"].astype(str)
        target[column] = pd.to_numeric(target[column], errors="coerce")
        aligned = base.merge(target, on="observation_month", how="inner")
        if factor == "momentum" and "risk_free_return" in aligned:
            aligned[column] = aligned[column] - pd.to_numeric(
                aligned["risk_free_return"], errors="coerce"
            )
        result = factor_regression(
            aligned[column],
            aligned[["market_excess_return"]],
            minimum_observations=minimum_observations,
        )
        result["target_definition"] = definition
        outputs[factor] = result
    return outputs
