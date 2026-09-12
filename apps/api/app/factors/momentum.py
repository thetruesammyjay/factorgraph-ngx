import pandas as pd
from app.factors.base import Factor

class MomentumFactor(Factor):
    name = "momentum"
    def validate_inputs(self, dataset: pd.DataFrame) -> None:
        if "monthly_return" not in dataset: raise ValueError("Missing momentum input: monthly_return")
    def calculate(self, dataset: pd.DataFrame) -> pd.Series:
        self.validate_inputs(dataset)
        formation = dataset.groupby("ticker")["monthly_return"].transform(lambda values: values.shift(2).rolling(11, min_periods=11).apply(lambda x: (1 + x).prod() - 1))
        return formation.groupby(dataset["observation_date"]).mean()
    def describe(self) -> dict[str, str]:
        return {"name": self.name, "formula": "12-1 formation return", "description": "Medium-term return persistence"}