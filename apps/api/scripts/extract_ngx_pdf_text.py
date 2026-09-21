"""Extract text from downloaded NGX PDF files for parser development.

Raw PDFs and extracted text stay under data/raw and are excluded from Git.
This utility never assigns financial meaning to PDF columns; canonical parsing
and validation belong in the ingestion layer.
"""

from argparse import ArgumentParser
from pathlib import Path

from pypdf import PdfReader


def extract(pdf_path: Path) -> Path:
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    output_path = pdf_path.with_suffix(".txt")
    output_path.write_text(text, encoding="utf-8")
    return output_path


def main() -> None:
    parser = ArgumentParser(description="Extract text from one or more NGX PDFs")
    parser.add_argument("pdfs", nargs="+", type=Path)
    args = parser.parse_args()

    for pdf_path in args.pdfs:
        output_path = extract(pdf_path)
        print(f"{pdf_path} -> {output_path}")


if __name__ == "__main__":
    main()
