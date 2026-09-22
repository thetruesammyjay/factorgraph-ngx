"""Acquisition helpers for auditable public source documents."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from urllib.parse import urlparse

import httpx


def is_https_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def document_filename(ticker: str, fiscal_period: str) -> str:
    year = fiscal_period[:4]
    return f"{ticker.lower()}-annual-report-{year}.pdf"


def acquire_pdf(
    client: httpx.Client,
    *,
    ticker: str,
    fiscal_period: str,
    source_url: str,
    output_directory: Path,
) -> dict[str, object]:
    """Download one PDF or verify an existing copy and return manifest metadata."""
    path = output_directory / document_filename(ticker, fiscal_period)
    record: dict[str, object] = {
        "ticker": ticker,
        "fiscal_period": fiscal_period,
        "source_url": source_url,
        "local_filename": path.name,
    }

    if not is_https_url(source_url):
        return record | {"status": "invalid_source_url"}

    if path.exists():
        content = path.read_bytes()
        if content.startswith(b"%PDF"):
            return record | {
                "status": "already_downloaded",
                "bytes": len(content),
                "sha256": sha256(content).hexdigest(),
            }

    try:
        response = client.get(source_url)
        record["http_status"] = response.status_code
        response.raise_for_status()
    except httpx.HTTPError as exc:
        return record | {"status": "request_error", "error": type(exc).__name__}

    if not response.content.startswith(b"%PDF"):
        return record | {
            "status": "invalid_document",
            "content_type": response.headers.get("content-type"),
        }

    output_directory.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(".pdf.part")
    temporary_path.write_bytes(response.content)
    temporary_path.replace(path)
    return record | {
        "status": "downloaded",
        "bytes": len(response.content),
        "sha256": sha256(response.content).hexdigest(),
    }
