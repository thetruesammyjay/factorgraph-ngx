"""Conservative page-level evidence discovery in issuer annual reports."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

from pypdf import PdfReader

SPACE = re.compile(r"\s+")
EVIDENCE_PATTERNS = {
    "book_equity": (
        re.compile(r"\btotal equity\b", re.IGNORECASE),
        re.compile(r"\bshareholders['’]? (?:funds|equity)\b", re.IGNORECASE),
        re.compile(r"\bequity attributable to (?:owners|shareholders)\b", re.IGNORECASE),
    ),
    "shares_outstanding": (
        re.compile(r"\bissued (?:ordinary )?share capital\b", re.IGNORECASE),
        re.compile(r"\bnumber of (?:ordinary )?shares\b", re.IGNORECASE),
        re.compile(r"\bordinary shares in issue\b", re.IGNORECASE),
    ),
    "unit_scale": (
        re.compile(r"\b(?:in )?thousands of naira\b", re.IGNORECASE),
        re.compile(r"\b(?:in )?millions of naira\b", re.IGNORECASE),
        re.compile(r"\b(?:in )?billions of naira\b", re.IGNORECASE),
        re.compile(r"₦\s*(?:'000|000|m|million|bn|billion)\b", re.IGNORECASE),
    ),
}


@dataclass(frozen=True)
class EvidenceHit:
    field: str
    page: int
    label: str
    context: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _context(text: str, start: int, end: int, radius: int = 100) -> str:
    normalized = SPACE.sub(" ", text).strip()
    label = SPACE.sub(" ", text[start:end]).strip()
    location = normalized.lower().find(label.lower())
    if location < 0:
        return label
    left = max(0, location - radius)
    right = min(len(normalized), location + len(label) + radius)
    return normalized[left:right]


def find_evidence(pages: list[str]) -> list[EvidenceHit]:
    """Find labels and nearby text without assigning values financial meaning."""
    hits: list[EvidenceHit] = []
    seen: set[tuple[str, int, str]] = set()
    for page_number, text in enumerate(pages, start=1):
        for field, patterns in EVIDENCE_PATTERNS.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    label = SPACE.sub(" ", match.group(0)).strip()
                    key = (field, page_number, label.lower())
                    if key in seen:
                        continue
                    seen.add(key)
                    hits.append(
                        EvidenceHit(
                            field=field,
                            page=page_number,
                            label=label,
                            context=_context(text, match.start(), match.end()),
                        )
                    )
    return hits


def extract_evidence(path: Path) -> tuple[int, list[EvidenceHit]]:
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return len(pages), find_evidence(pages)
