from datetime import date, timedelta
import pandas as pd

def align_fundamentals(frame: pd.DataFrame, lag_days: int = 90) -> pd.DataFrame:
    result = frame.copy()
    publication = pd.to_datetime(result.get("publication_date"), errors="coerce")
    fiscal = pd.to_datetime(result["fiscal_period"], errors="coerce")
    result["effective_from"] = publication.fillna(fiscal + pd.Timedelta(days=lag_days))
    result["effective_date_source"] = publication.notna().map({True: "ACTUAL_PUBLICATION_DATE", False: "FIXED_LAG_ESTIMATE"})
    return result