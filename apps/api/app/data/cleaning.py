import pandas as pd

def normalise(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result.columns = [str(column).strip().lower().replace(" ", "_") for column in result.columns]
    return result.drop_duplicates()

def monthly_dataset(frame: pd.DataFrame, date_column: str = "trading_date") -> pd.DataFrame:
    result = frame.copy()
    result[date_column] = pd.to_datetime(result[date_column])
    return result.set_index(date_column).groupby("ticker").resample("ME").last().reset_index()