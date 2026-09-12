import pandas as pd
from app.factors.base import Factor

class SizeFactor(Factor):
    name = "size"
    def validate_inputs(self, dataset: pd.DataFrame) -> None:
        for column in ("close", "shares_outstanding"):
            if column not in dataset: raise ValueError(f"Missing size input: {column}")
    def calculate(self, dataset: pd.DataFrame) -> pd.Series:
        self.validate_inputs(dataset)
        market_cap = dataset["close"] * dataset["shares_outstanding"]
        median = market_cap.groupby(dataset["trading_date"]).transform("median")
        return market_cap.where(market_cap <= median, -market_cap).groupby(dataset["trading_date"]).mean()
    def describe(self) -> dict[str, str]:
        return {"name": self.name, "formula": "SMB = Small - Big", "description": "Small-capitalisation premium"}