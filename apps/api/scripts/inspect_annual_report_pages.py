"""Print selected annual-report pages with stable PDF page references."""

import sys
from argparse import ArgumentParser
from pathlib import Path

from pypdf import PdfReader


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("pages", nargs="+", type=int, help="One-based PDF page numbers")
    args = parser.parse_args()

    reader = PdfReader(args.pdf)
    for page_number in args.pages:
        if page_number < 1 or page_number > len(reader.pages):
            parser.error(f"page {page_number} outside PDF range 1-{len(reader.pages)}")
        text = reader.pages[page_number - 1].extract_text() or ""
        print(f"\n===== {args.pdf.name} | PDF page {page_number} =====")
        print(text)


if __name__ == "__main__":
    main()
