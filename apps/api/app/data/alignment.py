"""Point-in-time alignment for issuer fundamentals."""

import pandas as pd


def align_fundamentals(frame: pd.DataFrame, lag_days: int = 90) -> pd.DataFrame:
    """Assign the first date on which each observation may enter a backtest."""

    result = frame.copy()
    publication = pd.to_datetime(result["publication_date"], errors="coerce")
    fiscal = pd.to_datetime(result["fiscal_period"], errors="coerce")
    estimated = fiscal + pd.Timedelta(days=lag_days)
    result["effective_from"] = publication.fillna(estimated)
    result["effective_date_source"] = publication.notna().map(
        {True: "ACTUAL_PUBLICATION_DATE", False: "FIXED_LAG_ESTIMATE"}
    )
    return result
