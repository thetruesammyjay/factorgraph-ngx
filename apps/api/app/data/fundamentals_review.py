"""Human-review boundary between PDF evidence and canonical fundamentals."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

CANONICAL_COLUMNS = [
    "ticker",
    "fiscal_period",
    "publication_date",
    "book_equity",
    "shares_outstanding",
    "earnings_per_share",
    "revenue",
    "net_income",
    "total_assets",
    "total_liabilities",
    "currency",
    "unit_multiplier",
    "reporting_scope",
    "source_id",
    "source_url",
    "source_sha256",
    "source_document",
    "page_reference",
    "notes",
]
REVIEW_COLUMNS = [
    "review_status",
    "reviewer",
    "reviewed_at",
    *CANONICAL_COLUMNS[:-2],
    "book_equity_page",
    "shares_outstanding_page",
    "unit_page",
    "notes",
    "evidence_status",
    "candidate_book_equity_pages",
    "candidate_shares_outstanding_pages",
    "candidate_unit_pages",
]
ALLOWED_STATUSES = {"pending", "approved", "rejected", "blocked"}


@dataclass(frozen=True)
class PromotionResult:
    frame: pd.DataFrame
    errors: list[str]


def _candidate_pages(record: dict, field: str) -> str:
    pages = sorted({hit["page"] for hit in record.get("hits", []) if hit["field"] == field})
    return ";".join(str(page) for page in pages)


def create_review_queue(evidence: dict) -> pd.DataFrame:
    rows = []
    for record in evidence["records"]:
        ready_for_review = record["status"] == "review_required"
        source_document = record.get("source_document", "")
        rows.append(
            {
                "review_status": "pending" if ready_for_review else "blocked",
                "reviewer": "",
                "reviewed_at": "",
                "ticker": record["ticker"],
                "fiscal_period": record["fiscal_period"],
                "publication_date": record.get("publication_date", ""),
                "book_equity": "",
                "shares_outstanding": "",
                "earnings_per_share": "",
                "revenue": "",
                "net_income": "",
                "total_assets": "",
                "total_liabilities": "",
                "currency": "NGN",
                "unit_multiplier": "",
                "reporting_scope": "",
                "source_id": source_document.removesuffix(".pdf"),
                "source_url": record.get("source_url", ""),
                "source_sha256": record.get("source_sha256", ""),
                "source_document": source_document,
                "book_equity_page": "",
                "shares_outstanding_page": "",
                "unit_page": "",
                "notes": "",
                "evidence_status": record["status"],
                "candidate_book_equity_pages": _candidate_pages(record, "book_equity"),
                "candidate_shares_outstanding_pages": _candidate_pages(
                    record, "shares_outstanding"
                ),
                "candidate_unit_pages": _candidate_pages(record, "unit_scale"),
            }
        )
    return pd.DataFrame(rows, columns=REVIEW_COLUMNS)


def promote_approved_reviews(frame: pd.DataFrame) -> PromotionResult:
    missing = sorted(set(REVIEW_COLUMNS).difference(frame.columns))
    if missing:
        return PromotionResult(
            pd.DataFrame(columns=CANONICAL_COLUMNS),
            [f"review worksheet missing column: {column}" for column in missing],
        )

    review = frame.copy().fillna("")
    review["review_status"] = review["review_status"].astype(str).str.strip().str.lower()
    unknown = sorted(set(review["review_status"]).difference(ALLOWED_STATUSES))
    errors = [f"unknown review statuses: {', '.join(unknown)}"] if unknown else []
    approved = review[review["review_status"] == "approved"].copy()

    for index, row in approved.iterrows():
        identity = f"{row['ticker']} {row['fiscal_period']}"
        for column in (
            "reviewer",
            "reviewed_at",
            "book_equity_page",
            "shares_outstanding_page",
            "reporting_scope",
            "unit_multiplier",
        ):
            if not str(row[column]).strip():
                errors.append(f"{identity}: approved row requires {column}")
        reviewed_at = pd.to_datetime(row["reviewed_at"], errors="coerce")
        if pd.isna(reviewed_at):
            errors.append(f"{identity}: reviewed_at must be a valid date")

    if approved.empty:
        return PromotionResult(pd.DataFrame(columns=CANONICAL_COLUMNS), errors)

    def page_reference(row: pd.Series) -> str:
        references = [
            f"book_equity p.{row['book_equity_page']}",
            f"shares_outstanding p.{row['shares_outstanding_page']}",
        ]
        if str(row["unit_page"]).strip():
            references.append(f"unit p.{row['unit_page']}")
        return "; ".join(references)

    approved["page_reference"] = approved.apply(page_reference, axis=1)
    return PromotionResult(approved[CANONICAL_COLUMNS].copy(), errors)
