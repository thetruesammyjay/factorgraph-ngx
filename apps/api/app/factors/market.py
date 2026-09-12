import pandas as pd
from app.factors.base import Factor

class MarketFactor(Factor):
    name = "market"
    def validate_inputs(self, dataset: pd.DataFrame) -> None:
        required = {"market_return", "risk_free_rate"}
        missing = required.difference(dataset.columns)
        if missing: raise ValueError(f"Missing market inputs: {sorted(missing)}")
    def calculate(self, dataset: pd.DataFrame) -> pd.Series:
        self.validate_inputs(dataset)
        return dataset["market_return"] - dataset["risk_free_rate"]
    def describe(self) -> dict[str, str]:
        return {"name": self.name, "formula": "R_m,t - R_f,t", "description": "Market excess return"}