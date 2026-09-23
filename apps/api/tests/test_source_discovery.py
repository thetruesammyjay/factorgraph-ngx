import pandas as pd

from app.data.source_discovery import apply_reviewed_selections, discover_report_links


def test_discovers_and_ranks_full_annual_report_pdf():
    html = """
    <a href="/reports/company-2023-annual-report.pdf">2023 Annual Report</a>
    <a href="/reports/2023-sustainability-annual-report.pdf">2023 Annual Report</a>
    <a href="/reports/q3-2023-report.pdf">Q3 2023 report</a>
    """

    candidates = discover_report_links(html, "https://issuer.example/investors/", 2023)

    assert len(candidates) == 2
    assert candidates[0].url == "https://issuer.example/reports/company-2023-annual-report.pdf"
    assert candidates[0].score > candidates[1].score


def test_resolves_relative_links_and_rejects_insecure_links():
    html = """
    <a href="../files/annual-report-2022.pdf">Annual Report 2022</a>
    <a href="http://files.example/annual-report-2022.pdf">Annual Report 2022</a>
    """

    candidates = discover_report_links(html, "https://issuer.example/investors/reports/", 2022)

    assert [candidate.url for candidate in candidates] == [
        "https://issuer.example/investors/files/annual-report-2022.pdf"
    ]


def test_excludes_wrong_year_and_non_annual_documents():
    html = """
    <a href="report-2023.pdf">Annual Report 2023</a>
    <a href="report-2022.pdf">Annual Report 2022</a>
    <a href="audited-2023.pdf">Audited Financial Statements 2023</a>
    """

    candidates = discover_report_links(html, "https://issuer.example/", 2022)

    assert len(candidates) == 1
    assert candidates[0].fiscal_year == 2022


def test_does_not_use_upload_directory_year_as_fiscal_year():
    html = """
    <a href="/uploads/2023/04/company-2022-annual-report.pdf">Annual Report 2022</a>
    """

    candidates = discover_report_links(html, "https://issuer.example/investors/", 2023)

    assert candidates == []


def selection_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    url = "https://issuer.example/annual-report-2023.pdf"
    review = pd.DataFrame(
        [
            {
                "selected": "yes",
                "ticker": "ZENITHBANK",
                "fiscal_period": "2023-12-31",
                "candidate_url": url,
                "landing_url": "https://issuer.example/investors",
                "reviewer": "Samuel Ifiezibe",
                "reviewed_at": "2026-09-23",
                "publication_date": "2024-03-15",
                "review_notes": "Complete group annual report",
            }
        ]
    )
    catalog = pd.DataFrame(
        [
            {
                "ticker": "ZENITHBANK",
                "fiscal_period": "2023-12-31",
                "source_url": "",
                "publication_date": "",
                "source_kind": "",
                "notes": "",
            }
        ]
    )
    discovery = {
        "records": [
            {
                "ticker": "ZENITHBANK",
                "fiscal_period": "2023-12-31",
                "candidates": [{"url": url}],
            }
        ]
    }
    return review, catalog, discovery


def test_applies_explicit_provenance_checked_selection():
    review, catalog, discovery = selection_inputs()

    result = apply_reviewed_selections(review, catalog, discovery)

    assert result.errors == []
    assert result.selected_count == 1
    assert result.catalog.loc[0, "source_kind"] == "issuer_annual_report"
    assert result.catalog.loc[0, "publication_date"] == "2024-03-15"
    assert "Samuel Ifiezibe" in result.catalog.loc[0, "notes"]


def test_rejects_tampered_candidate_url():
    review, catalog, discovery = selection_inputs()
    review.loc[0, "candidate_url"] = "https://attacker.example/report.pdf"

    result = apply_reviewed_selections(review, catalog, discovery)

    assert any("absent from discovery evidence" in error for error in result.errors)
    assert result.catalog.loc[0, "source_url"] == ""


def test_rejects_multiple_selections_for_one_period():
    review, catalog, discovery = selection_inputs()
    duplicate = review.copy()
    duplicate.loc[0, "candidate_url"] = "https://issuer.example/second-report-2023.pdf"
    discovery["records"][0]["candidates"].append({"url": duplicate.loc[0, "candidate_url"]})

    result = apply_reviewed_selections(
        pd.concat([review, duplicate], ignore_index=True), catalog, discovery
    )

    assert any("select exactly one candidate" in error for error in result.errors)
