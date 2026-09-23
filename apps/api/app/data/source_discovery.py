"""Conservative annual-report link discovery from reviewed official pages."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import pandas as pd

SPACE = re.compile(r"\s+")
NEGATIVE_TERMS = {
    "sustainability": -80,
    "interim": -70,
    "quarter": -70,
    "unaudited": -70,
    "abridged": -35,
    "presentation": -40,
    "transcript": -50,
}
TRUE_SELECTIONS = {"1", "true", "yes", "x"}
FALSE_SELECTIONS = {"", "0", "false", "no"}
SOURCE_CATALOG_COLUMNS = [
    "ticker",
    "fiscal_period",
    "source_url",
    "publication_date",
    "source_kind",
    "notes",
]


@dataclass(frozen=True)
class ReportCandidate:
    url: str
    link_text: str
    fiscal_year: int
    score: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SelectionResult:
    catalog: pd.DataFrame
    errors: list[str]
    selected_count: int


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attributes = dict(attrs)
        self._href = attributes.get("href")
        self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            self.links.append((self._href, SPACE.sub(" ", " ".join(self._text)).strip()))
            self._href = None
            self._text = []


def discover_report_links(
    html: str, base_url: str, fiscal_year: int
) -> list[ReportCandidate]:
    parser = LinkParser()
    parser.feed(html)
    candidates: dict[str, ReportCandidate] = {}
    year = str(fiscal_year)
    for href, text in parser.links:
        url = urljoin(base_url, href)
        parsed = urlparse(url)
        if parsed.scheme != "https":
            continue
        filename = parsed.path.rsplit("/", maxsplit=1)[-1]
        searchable = f"{text} {filename}".lower()
        if year not in searchable or "annual" not in searchable or "report" not in searchable:
            continue
        score = 100
        score += 35 if parsed.path.lower().endswith(".pdf") else 0
        score += 15 if f"annual report {year}" in searchable else 0
        score += 10 if "audited" in searchable else 0
        score += sum(penalty for term, penalty in NEGATIVE_TERMS.items() if term in searchable)
        candidate = ReportCandidate(url=url, link_text=text, fiscal_year=fiscal_year, score=score)
        previous = candidates.get(url)
        if previous is None or candidate.score > previous.score:
            candidates[url] = candidate
    return sorted(candidates.values(), key=lambda item: (-item.score, item.url))


def apply_reviewed_selections(
    review: pd.DataFrame, catalog: pd.DataFrame, discovery: dict
) -> SelectionResult:
    """Apply explicit, provenance-checked candidate selections to a source catalog."""
    required_review = {
        "selected",
        "ticker",
        "fiscal_period",
        "candidate_url",
        "landing_url",
        "reviewer",
        "reviewed_at",
        "publication_date",
        "review_notes",
    }
    errors = [
        f"review worksheet missing column: {column}"
        for column in sorted(required_review.difference(review.columns))
    ]
    errors.extend(
        f"source catalog missing column: {column}"
        for column in sorted(set(SOURCE_CATALOG_COLUMNS).difference(catalog.columns))
    )
    if errors:
        return SelectionResult(catalog.copy(), errors, 0)

    candidates = {
        (record["ticker"], record["fiscal_period"], candidate["url"])
        for record in discovery["records"]
        for candidate in record.get("candidates", [])
    }
    reviewed = review.copy().fillna("")
    reviewed["ticker"] = reviewed["ticker"].astype(str).str.strip().str.upper()
    selections = reviewed["selected"].astype(str).str.strip().str.lower()
    invalid_markers = sorted(set(selections).difference(TRUE_SELECTIONS | FALSE_SELECTIONS))
    if invalid_markers:
        errors.append(f"invalid selection markers: {', '.join(invalid_markers)}")
    selected = reviewed[selections.isin(TRUE_SELECTIONS)].copy()
    if selected.empty:
        errors.append("no report candidates were selected")

    duplicate_keys = selected.duplicated(["ticker", "fiscal_period"], keep=False)
    for ticker, fiscal_period in sorted(
        set(zip(selected.loc[duplicate_keys, "ticker"], selected.loc[duplicate_keys, "fiscal_period"]))
    ):
        errors.append(f"{ticker} {fiscal_period}: select exactly one candidate")

    for _, row in selected.iterrows():
        identity = f"{row['ticker']} {row['fiscal_period']}"
        if (row["ticker"], row["fiscal_period"], row["candidate_url"]) not in candidates:
            errors.append(f"{identity}: selected URL is absent from discovery evidence")
        if not str(row["reviewer"]).strip():
            errors.append(f"{identity}: reviewer is required")
        if pd.isna(pd.to_datetime(row["reviewed_at"], errors="coerce")):
            errors.append(f"{identity}: reviewed_at must be a valid date")
        publication = pd.to_datetime(row["publication_date"], errors="coerce")
        if str(row["publication_date"]).strip() and pd.isna(publication):
            errors.append(f"{identity}: publication_date must be a valid date")
        fiscal = pd.to_datetime(row["fiscal_period"], errors="coerce")
        if pd.notna(publication) and pd.notna(fiscal) and publication < fiscal:
            errors.append(f"{identity}: publication_date precedes fiscal_period")

    result = catalog.copy().fillna("")
    result["ticker"] = result["ticker"].astype(str).str.strip().str.upper()
    if result.duplicated(["ticker", "fiscal_period"]).any():
        errors.append("source catalog contains duplicate ticker/fiscal_period rows")
    catalog_keys = set(zip(result["ticker"], result["fiscal_period"]))
    for _, row in selected.iterrows():
        key = (row["ticker"], row["fiscal_period"])
        if key not in catalog_keys:
            errors.append(f"{key[0]} {key[1]}: source catalog row is missing")

    if errors:
        return SelectionResult(result[SOURCE_CATALOG_COLUMNS], errors, len(selected))

    for _, row in selected.iterrows():
        mask = (result["ticker"] == row["ticker"]) & (
            result["fiscal_period"] == row["fiscal_period"]
        )
        publication_date = str(row["publication_date"]).strip()
        result.loc[mask, "source_url"] = row["candidate_url"]
        result.loc[mask, "source_kind"] = "issuer_annual_report"
        if publication_date:
            result.loc[mask, "publication_date"] = publication_date
        audit_note = (
            f"Selected from {row['landing_url']}; reviewed by {row['reviewer']} "
            f"on {row['reviewed_at']}"
        )
        if str(row["review_notes"]).strip():
            audit_note += f"; {row['review_notes']}"
        result.loc[mask, "notes"] = audit_note
    return SelectionResult(result[SOURCE_CATALOG_COLUMNS], [], len(selected))
