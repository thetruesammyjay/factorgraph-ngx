import pandas as pd

def validate_prices(frame: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    required = {"ticker", "trading_date", "close", "volume", "trading_value"}
    errors.extend(f"missing column: {column}" for column in sorted(required.difference(frame.columns)))
    if "close" in frame and (frame["close"] <= 0).any(): errors.append("close contains non-positive values")
    return errors

def validate_fundamentals(frame: pd.DataFrame) -> list[str]:
    required = {"ticker", "fiscal_period", "book_equity", "shares_outstanding"}
    return [f"missing column: {column}" for column in sorted(required.difference(frame.columns))]