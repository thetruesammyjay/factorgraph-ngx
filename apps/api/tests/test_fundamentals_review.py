import pandas as pd

from app.data.fundamentals_review import create_review_queue, promote_approved_reviews


def evidence_record() -> dict:
    return {
        "ticker": "ZENITHBANK",
        "fiscal_period": "2023-12-31",
        "status": "review_required",
        "publication_date": "2024-03-15",
        "source_url": "https://example.test/zenith.pdf",
        "source_sha256": "a" * 64,
        "source_document": "zenithbank-annual-report-2023.pdf",
        "hits": [
            {"field": "book_equity", "page": 120},
            {"field": "shares_outstanding", "page": 142},
            {"field": "unit_scale", "page": 120},
        ],
    }


def test_creates_review_queue_with_candidate_pages():
    queue = create_review_queue({"records": [evidence_record()]})

    assert queue.loc[0, "review_status"] == "pending"
    assert queue.loc[0, "candidate_book_equity_pages"] == "120"
    assert queue.loc[0, "candidate_shares_outstanding_pages"] == "142"
    assert queue.loc[0, "source_sha256"] == "a" * 64


def test_promotes_only_explicitly_approved_complete_rows():
    queue = create_review_queue({"records": [evidence_record()]})
    queue.loc[0, [
        "review_status", "reviewer", "reviewed_at", "book_equity",
        "shares_outstanding", "unit_multiplier", "reporting_scope",
        "book_equity_page", "shares_outstanding_page", "unit_page",
    ]] = [
        "approved", "Samuel Ifiezibe", "2026-09-22", "100", "31396",
        "1000000", "GROUP", "120", "142", "120",
    ]

    result = promote_approved_reviews(queue)

    assert result.errors == []
    assert len(result.frame) == 1
    assert result.frame.loc[0, "page_reference"] == (
        "book_equity p.120; shares_outstanding p.142; unit p.120"
    )


def test_rejects_approved_row_without_reviewer_and_page_citations():
    queue = create_review_queue({"records": [evidence_record()]})
    queue.loc[0, "review_status"] = "approved"

    result = promote_approved_reviews(queue)

    assert any("requires reviewer" in error for error in result.errors)
    assert any("requires book_equity_page" in error for error in result.errors)
    assert isinstance(result.frame, pd.DataFrame)
