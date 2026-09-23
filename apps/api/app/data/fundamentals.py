"""Validation and normalization for point-in-time issuer fundamentals."""

import re
from dataclasses import dataclass

import pandas as pd

from app.data.alignment import align_fundamentals

SHA256 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_COLUMNS = {
    "ticker", "fiscal_period", "publication_date", "book_equity",
    "shares_outstanding", "currency", "monetary_unit_multiplier",
    "shares_unit_multiplier", "reporting_scope",
    "source_id", "source_url", "source_sha256", "source_document", "page_reference",
}
MONETARY_COLUMNS = {
    "book_equity", "revenue",
    "net_income", "total_assets", "total_liabilities",
}


@dataclass(frozen=True)
class FundamentalsValidation:
    frame: pd.DataFrame
    errors: list[str]
    warnings: list[str]


def validate_and_align_fundamentals(
    frame: pd.DataFrame, universe: set[str], lag_days: int = 90
) -> FundamentalsValidation:
    errors: list[str] = []
    warnings: list[str] = []
    missing_columns = sorted(REQUIRED_COLUMNS.difference(frame.columns))
    if missing_columns:
        return FundamentalsValidation(
            frame.copy(),
            [f"missing column: {column}" for column in missing_columns],
            [],
        )

    result = frame.copy()
    result["ticker"] = result["ticker"].astype("string").str.strip().str.upper()
    unknown = sorted(set(result["ticker"].dropna()).difference(universe))
    if unknown:
        errors.append(f"tickers outside configured universe: {', '.join(unknown)}")

    result["fiscal_period"] = pd.to_datetime(result["fiscal_period"], errors="coerce")
    publication_supplied = result["publication_date"].notna() & result[
        "publication_date"
    ].astype("string").str.strip().ne("")
    result["publication_date"] = pd.to_datetime(result["publication_date"], errors="coerce")
    if result["fiscal_period"].isna().any():
        errors.append("fiscal_period contains missing or invalid dates")
    if (publication_supplied & result["publication_date"].isna()).any():
        errors.append("publication_date contains invalid supplied dates")

    monetary_multiplier = pd.to_numeric(
        result["monetary_unit_multiplier"], errors="coerce"
    )
    shares_multiplier = pd.to_numeric(result["shares_unit_multiplier"], errors="coerce")
    if monetary_multiplier.isna().any() or (monetary_multiplier <= 0).any():
        errors.append(
            "monetary_unit_multiplier contains missing, invalid, or non-positive values"
        )
    if shares_multiplier.isna().any() or (shares_multiplier <= 0).any():
        errors.append(
            "shares_unit_multiplier contains missing, invalid, or non-positive values"
        )
    for column in sorted(MONETARY_COLUMNS.intersection(result.columns)):
        result[column] = (
            pd.to_numeric(result[column], errors="coerce") * monetary_multiplier
        )
    result["shares_outstanding"] = (
        pd.to_numeric(result["shares_outstanding"], errors="coerce")
        * shares_multiplier
    )
    if "earnings_per_share" in result:
        result["earnings_per_share"] = pd.to_numeric(
            result["earnings_per_share"], errors="coerce"
        )
    if result["book_equity"].isna().any():
        errors.append("book_equity contains missing or invalid values")
    if result["shares_outstanding"].isna().any():
        errors.append("shares_outstanding contains missing or invalid values")
    if (result["shares_outstanding"].dropna() <= 0).any():
        errors.append("shares_outstanding contains non-positive values")
    if (result["book_equity"].dropna() <= 0).any():
        warnings.append("non-positive book equity must be excluded from positive-B/M sorts")

    result["currency"] = result["currency"].astype("string").str.strip().str.upper()
    if not result.empty and set(result["currency"].dropna()) != {"NGN"}:
        errors.append("pilot values must be normalized to NGN")
    if result["reporting_scope"].isna().any() or result[
        "reporting_scope"
    ].astype("string").str.strip().eq("").any():
        errors.append("reporting_scope is required")

    hashes = result["source_sha256"].astype("string").fillna("").str.strip().str.lower()
    valid_hashes = hashes.map(lambda value: bool(SHA256.fullmatch(value))).astype(bool)
    if not valid_hashes.all():
        errors.append("source_sha256 must contain lowercase 64-character SHA-256 values")
    result["source_sha256"] = hashes
    for column in ("source_id", "source_url", "source_document", "page_reference"):
        if (
            result[column].isna().any()
            or result[column].astype("string").str.strip().eq("").any()
        ):
            errors.append(f"{column} is required for every observation")

    result = align_fundamentals(result, lag_days=lag_days)
    if (result["publication_date"] < result["fiscal_period"]).fillna(False).any():
        errors.append("publication_date precedes fiscal_period")
    if (result["effective_from"] < result["fiscal_period"]).fillna(False).any():
        errors.append("effective_from precedes fiscal_period")
    if result.duplicated(["ticker", "fiscal_period", "publication_date"]).any():
        errors.append("duplicate ticker/fiscal_period/publication_date keys")

    result["fiscal_period"] = result["fiscal_period"].dt.date.astype("string")
    result["publication_date"] = result["publication_date"].dt.date.astype("string")
    result.loc[result["publication_date"] == "NaT", "publication_date"] = pd.NA
    result["effective_from"] = result["effective_from"].dt.date.astype("string")
    return FundamentalsValidation(result, errors, warnings)
