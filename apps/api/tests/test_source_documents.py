from hashlib import sha256

import httpx

from app.data.source_documents import acquire_pdf


def test_acquire_pdf_downloads_and_hashes_document(tmp_path):
    content = b"%PDF-1.7\nannual report"
    transport = httpx.MockTransport(lambda request: httpx.Response(200, content=content))

    with httpx.Client(transport=transport) as client:
        result = acquire_pdf(
            client,
            ticker="ZENITHBANK",
            fiscal_period="2023-12-31",
            source_url="https://example.com/report.pdf",
            output_directory=tmp_path,
        )

    assert result["status"] == "downloaded"
    assert result["sha256"] == sha256(content).hexdigest()
    assert (tmp_path / "zenithbank-annual-report-2023.pdf").read_bytes() == content


def test_acquire_pdf_reuses_verified_local_document(tmp_path):
    content = b"%PDF-existing"
    path = tmp_path / "uba-annual-report-2022.pdf"
    path.write_bytes(content)
    transport = httpx.MockTransport(lambda request: (_ for _ in ()).throw(AssertionError()))

    with httpx.Client(transport=transport) as client:
        result = acquire_pdf(
            client,
            ticker="UBA",
            fiscal_period="2022-12-31",
            source_url="https://example.com/report.pdf",
            output_directory=tmp_path,
        )

    assert result["status"] == "already_downloaded"
    assert result["sha256"] == sha256(content).hexdigest()


def test_acquire_pdf_rejects_non_pdf_and_insecure_url(tmp_path):
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, content=b"<html>blocked</html>")
    )

    with httpx.Client(transport=transport) as client:
        invalid_document = acquire_pdf(
            client,
            ticker="MTNN",
            fiscal_period="2023-12-31",
            source_url="https://example.com/report",
            output_directory=tmp_path,
        )
        insecure_url = acquire_pdf(
            client,
            ticker="MTNN",
            fiscal_period="2022-12-31",
            source_url="http://example.com/report.pdf",
            output_directory=tmp_path,
        )

    assert invalid_document["status"] == "invalid_document"
    assert insecure_url["status"] == "invalid_source_url"
    assert list(tmp_path.iterdir()) == []
