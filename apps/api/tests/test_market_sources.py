from pathlib import Path

import pytest

from app.data.market_sources import parse_cbn_91_day_ntb, parse_ngx_weekly_asi


def test_parse_cbn_91_day_ntb_filters_year_and_tenor():
    records = [
        {"id": 1, "auctionDate": "January-10-2024", "tenor": "91DAY", "rate": "5.25"},
        {"id": 2, "auctionDate": "January-10-2024", "tenor": "182DAY", "rate": "7"},
        {"id": 3, "auctionDate": "January-08-2025", "tenor": "91DAY", "rate": "9"},
    ]

    result = parse_cbn_91_day_ntb(records)

    assert len(result) == 1
    assert result.loc[0, "annual_rate_percent"] == 5.25
    assert result.loc[0, "source_id"] == "cbn-ntb-1"


def test_parse_cbn_91_day_ntb_rejects_duplicate_dates():
    records = [
        {"id": 1, "auctionDate": "January-10-2024", "tenor": "91DAY", "rate": "5"},
        {"id": 2, "auctionDate": "January-10-2024", "tenor": "91DAY", "rate": "6"},
    ]
    with pytest.raises(ValueError, match="duplicate"):
        parse_cbn_91_day_ntb(records)


def test_parse_ngx_weekly_asi_reports_missing_row(monkeypatch, tmp_path: Path):
    class Page:
        def extract_text(self):
            return "WEEKLY REPORT without index table"

    class Reader:
        def __init__(self):
            self.pages = [Page()]

    monkeypatch.setattr("app.data.market_sources.PdfReader", lambda _: Reader())
    with pytest.raises(ValueError, match="ASI row not found"):
        parse_ngx_weekly_asi(tmp_path / "report.pdf", __import__("datetime").date(2024, 1, 5), "source")
