from app.data.source_discovery import discover_report_links


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
