import pandas as pd
from app.factors.base import Factor

class ValueFactor(Factor):
    name = "value"
    def validate_inputs(self, dataset: pd.DataFrame) -> None:
        for column in ("book_equity", "market_cap"):
            if column not in dataset: raise ValueError(f"Missing value input: {column}")
    def calculate(self, dataset: pd.DataFrame) -> pd.Series:
        self.validate_inputs(dataset)
        ratio = dataset["book_equity"] / dataset["market_cap"]
        high = ratio.groupby(dataset["observation_date"]).transform("median")
        return ratio.where(ratio >= high, -ratio).groupby(dataset["observation_date"]).mean()
    def describe(self) -> dict[str, str]:
        return {"name": self.name, "formula": "HML = High B/M - Low B/M", "description": "Book-to-market premium"}