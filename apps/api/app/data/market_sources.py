"""Parsers for official NGX weekly reports and CBN NTB auction records."""

from __future__ import annotations

import re
import time
from datetime import date
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

ASI_ROW = re.compile(
    r"NGX\s+All-Share\s+Index\s*\(ASI\)\s+"
    r"([\d,]+(?:\.\d+)?)\s+([\d,]+(?:\.\d+)?)",
    re.IGNORECASE,
)


def parse_ngx_weekly_asi(path: Path, observation_date: date, source_id: str) -> dict:
    """Extract the current week ASI close from an official NGX weekly PDF."""
    text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    match = ASI_ROW.search(" ".join(text.split()))
    if not match:
        raise ValueError(f"NGX ASI row not found in {path.name}")
    previous_close, current_close = (
        float(value.replace(",", "")) for value in match.groups()
    )
    if previous_close <= 0 or current_close <= 0:
        raise ValueError(f"NGX ASI close is non-positive in {path.name}")
    return {
        "observation_date": observation_date.isoformat(),
        "index_code": "NGXASI",
        "index_name": "NGX All-Share Index",
        "close": current_close,
        "return_decimal": current_close / previous_close - 1,
        "source_id": source_id,
    }


def parse_cbn_91_day_ntb(records: list[dict], year: int = 2024) -> pd.DataFrame:
    """Select dated 91-day NTB marginal rates from the official CBN response."""
    rows = []
    for record in records:
        if str(record.get("tenor", "")).upper().replace(" ", "") != "91DAY":
            continue
        try:
            parsed_date = time.strptime(record["auctionDate"], "%B-%d-%Y")
            auction_date = date(parsed_date.tm_year, parsed_date.tm_mon, parsed_date.tm_mday)
            rate = float(record["rate"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid CBN NTB record: {record.get('id')}") from exc
        if auction_date.year != year:
            continue
        rows.append(
            {
                "observation_date": auction_date.isoformat(),
                "series_name": "CBN 91-day Nigerian Treasury Bill marginal rate",
                "tenor": "91D",
                "annual_rate_percent": rate,
                "period_return_decimal": None,
                "source_id": f"cbn-ntb-{record.get('id')}",
            }
        )
    result = pd.DataFrame(rows)
    if result.empty:
        return pd.DataFrame(
            columns=[
                "observation_date",
                "series_name",
                "tenor",
                "annual_rate_percent",
                "period_return_decimal",
                "source_id",
            ]
        )
    if result[["observation_date", "tenor"]].duplicated().any():
        raise ValueError("CBN response contains duplicate 91-day auction dates")
    return result.sort_values("observation_date").reset_index(drop=True)
