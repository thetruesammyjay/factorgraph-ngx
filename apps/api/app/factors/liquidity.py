import pandas as pd
from app.factors.base import Factor

class LiquidityFactor(Factor):
    name = "liquidity"
    def validate_inputs(self, dataset: pd.DataFrame) -> None:
        for column in ("daily_return", "trading_value", "turnover"):
            if column not in dataset: raise ValueError(f"Missing liquidity input: {column}")
    def calculate(self, dataset: pd.DataFrame) -> pd.Series:
        self.validate_inputs(dataset)
        illiq = (dataset["daily_return"].abs() / dataset["trading_value"].replace(0, pd.NA)).groupby(dataset["ticker"]).transform("mean")
        return (dataset["turnover"].groupby(dataset["observation_date"]).transform("mean") - illiq.groupby(dataset["observation_date"]).transform("mean"))
    def describe(self) -> dict[str, str]:
        return {"name": self.name, "formula": "z(Turnover) - z(Amihud)", "description": "Turnover adjusted for illiquidity"}