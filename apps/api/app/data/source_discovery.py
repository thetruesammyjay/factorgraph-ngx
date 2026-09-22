"""Conservative annual-report link discovery from reviewed official pages."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

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


@dataclass(frozen=True)
class ReportCandidate:
    url: str
    link_text: str
    fiscal_year: int
    score: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


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
