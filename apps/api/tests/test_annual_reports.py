from app.data.annual_reports import find_evidence


def test_finds_point_in_time_fundamental_evidence_by_page():
    pages = [
        "Independent auditor's report",
        "Consolidated statement of financial position Total equity 450,000 ₦ million",
        "Issued ordinary share capital Number of ordinary shares 31,396,493,786",
    ]

    hits = find_evidence(pages)

    assert {(hit.field, hit.page) for hit in hits} >= {
        ("book_equity", 2),
        ("unit_scale", 2),
        ("shares_outstanding", 3),
    }
    assert any("450,000" in hit.context for hit in hits if hit.field == "book_equity")


def test_deduplicates_repeated_labels_on_the_same_page():
    hits = find_evidence(["Total equity total equity TOTAL EQUITY"])

    assert len(hits) == 1
    assert hits[0].label == "Total equity"


def test_does_not_treat_generic_equity_text_as_book_equity():
    assert find_evidence(["The company operates in the equity market."]) == []
