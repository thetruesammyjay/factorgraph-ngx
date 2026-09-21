"""Conservative parser for the positioned text in NGX Daily Official Lists."""

import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from pypdf import PdfReader

NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
REPORT_DATE = re.compile(
    r"Daily Official List \(Equities\) For (\d{2})/(\d{2})/(\d{4})"
)


@dataclass(frozen=True)
class NgxPriceRow:
    trading_date: str
    ticker: str
    security_name: str
    official_open: float | None
    official_close: float | None
    current_market_price: float
    close: float
    volume: None
    trading_value: None
    number_of_transactions: None
    price_status: str
    source_file: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _number(value: str) -> float | None:
    match = NUMBER.search(value)
    return float(match.group().replace(",", "")) if match else None


def parse_layout_text(text: str, tickers: set[str], source_file: str) -> list[NgxPriceRow]:
    date_match = REPORT_DATE.search(text)
    if not date_match:
        raise ValueError(f"report date not found in {source_file}")
    day, month, year = map(int, date_match.groups())
    trading_date = date(year, month, day).isoformat()

    lines = text.splitlines()
    rows: list[NgxPriceRow] = []
    header: str | None = None

    for index, line in enumerate(lines):
        if all(label in line for label in ("Security Name", "Official Open", "Market Price")):
            header = line
            continue

        stripped = line.lstrip()
        ticker = next((value for value in tickers if stripped.startswith(f"{value} ")), None)
        if ticker is None:
            continue
        if header is None:
            raise ValueError(f"column header not found before {ticker} in {source_file}")

        name_at = header.index("Security Name")
        quote_at = header.index("Price (N)")
        open_at = header.index("Official Open")
        close_at = header.index("Official Close")
        market_at = header.index("Market Price")
        div_at = header.index("Div", market_at)

        ticker_at = line.index(ticker)
        security_name = line[ticker_at + len(ticker) : quote_at].strip()
        continuation_at = max(header.index("Symbol") + 10, name_at - 8)
        for next_line in lines[index + 1 : index + 4]:
            continuation = next_line[continuation_at:quote_at].strip()
            indentation = len(next_line) - len(next_line.lstrip())
            if indentation < continuation_at or not continuation:
                break
            security_name = f"{security_name} {continuation}"

        official_open = _number(line[open_at:close_at])
        official_close = _number(line[close_at:market_at])
        current_market_price = _number(line[market_at:div_at])
        if current_market_price is None:
            raise ValueError(f"market price not found for {ticker} in {source_file}")

        status = "official_trade" if official_close is not None else "carried_market_price"
        rows.append(
            NgxPriceRow(
                trading_date=trading_date,
                ticker=ticker,
                security_name=security_name,
                official_open=official_open,
                official_close=official_close,
                current_market_price=current_market_price,
                close=current_market_price,
                volume=None,
                trading_value=None,
                number_of_transactions=None,
                price_status=status,
                source_file=source_file,
            )
        )

    return rows


def parse_pdf(path: Path, tickers: set[str]) -> list[NgxPriceRow]:
    reader = PdfReader(path)
    text = "\n".join(
        page.extract_text(extraction_mode="layout") or "" for page in reader.pages
    )
    return parse_layout_text(text, tickers=tickers, source_file=path.name)
