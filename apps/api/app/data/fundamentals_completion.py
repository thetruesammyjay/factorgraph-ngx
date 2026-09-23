"""Deterministic gap tracking for point-in-time fundamentals collection."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd


@dataclass(frozen=True)
class FundamentalsCompletionSummary:
    expected_issuer_periods: int
    complete_issuer_periods: int
    missing_issuer_periods: int
    issuers_in_scope: int
    issuers_with_complete_observations: int
    remaining_issuers: list[str]
    fiscal_periods: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def build_completion_queue(
    universe: pd.DataFrame,
    current: pd.DataFrame,
    fiscal_periods: list[str],
) -> tuple[pd.DataFrame, FundamentalsCompletionSummary]:
    """Return one auditable task per issuer-period, preserving current evidence."""
    required_universe = {"ticker", "company", "sector"}
    missing = sorted(required_universe.difference(universe.columns))
    if missing:
        raise ValueError(f"universe missing columns: {', '.join(missing)}")
    periods = sorted({str(pd.Timestamp(period).date()) for period in fiscal_periods})
    if not periods:
        raise ValueError("at least one fiscal period is required")
    issuers = universe[["ticker", "company", "sector"]].copy()
    issuers["ticker"] = issuers["ticker"].astype("string").str.strip().str.upper()
    if issuers["ticker"].duplicated().any():
        raise ValueError("universe contains duplicate tickers")

    facts = current.copy()
    if "ticker" not in facts or "fiscal_period" not in facts:
        facts = pd.DataFrame(columns=["ticker", "fiscal_period"])
    else:
        facts["ticker"] = facts["ticker"].astype("string").str.strip().str.upper()
        facts["fiscal_period"] = pd.to_datetime(
            facts["fiscal_period"], errors="coerce"
        ).dt.date.astype("string")
    key = ["ticker", "fiscal_period"]
    if facts[key].duplicated().any():
        raise ValueError("current fundamentals contain duplicate issuer-period keys")
    fact_by_key = facts.set_index(key, drop=False)
    rows: list[dict] = []
    complete_keys: set[tuple[str, str]] = set()
    for issuer in issuers.itertuples(index=False):
        for period in periods:
            identity = (str(issuer.ticker), period)
            existing = fact_by_key.loc[identity] if identity in fact_by_key.index else None
            if existing is None:
                status = "missing"
                source_id = source_url = ""
                required_missing = "book_equity;shares_outstanding;reporting_scope;source_id"
            else:
                required_fields = [
                    "book_equity", "shares_outstanding", "reporting_scope", "source_id"
                ]
                missing_fields = [
                    field for field in required_fields
                    if field not in existing.index or pd.isna(existing[field]) or str(existing[field]).strip() == ""
                ]
                status = "complete" if not missing_fields else "needs_review"
                if status == "complete":
                    complete_keys.add(identity)
                required_missing = ";".join(missing_fields)
                source_id = str(existing.get("source_id", ""))
                source_url = str(existing.get("source_url", ""))
            rows.append(
                {
                    "ticker": identity[0],
                    "company": issuer.company,
                    "sector": issuer.sector,
                    "fiscal_period": period,
                    "status": status,
                    "priority": "remaining_issuer" if identity[0] not in set(facts["ticker"]) else "missing_period",
                    "required_missing": required_missing,
                    "source_id": source_id,
                    "source_url": source_url,
                }
            )
    queue = pd.DataFrame(rows).sort_values(["status", "ticker", "fiscal_period"]).reset_index(drop=True)
    complete_issuers = {ticker for ticker, _ in complete_keys}
    summary = FundamentalsCompletionSummary(
        expected_issuer_periods=len(issuers) * len(periods),
        complete_issuer_periods=len(complete_keys),
        missing_issuer_periods=len(rows) - len(complete_keys),
        issuers_in_scope=len(issuers),
        issuers_with_complete_observations=len(complete_issuers),
        remaining_issuers=sorted(set(issuers["ticker"]) - complete_issuers),
        fiscal_periods=periods,
    )
    return queue, summary
