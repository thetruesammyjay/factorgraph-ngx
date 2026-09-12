import numpy as np
import pandas as pd
import statsmodels.api as sm

def factor_regression(excess_returns: pd.Series, factors: pd.DataFrame) -> dict[str, float]:
    aligned = pd.concat([excess_returns.rename("y"), factors], axis=1).dropna()
    model = sm.OLS(aligned["y"], sm.add_constant(aligned.drop(columns="y"))).fit()
    return {"alpha": float(model.params["const"]), "r_squared": float(model.rsquared), **{key: float(value) for key, value in model.params.drop("const").items()}}