"""Index candidate annual-report pages for manual fundamentals review."""

import json
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path

from pypdf.errors import PdfReadError

from app.data.annual_reports import extract_evidence

AVAILABLE_STATUSES = {"downloaded", "already_downloaded"}


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--documents", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    records: list[dict[str, object]] = []
    for source in manifest["records"]:
        identity = {
            "ticker": source["ticker"],
            "fiscal_period": source["fiscal_period"],
        }
        if source["status"] not in AVAILABLE_STATUSES:
            records.append(identity | {"status": "document_unavailable", "hits": []})
            continue

        path = args.documents / str(source["local_filename"])
        if not path.exists():
            records.append(identity | {"status": "file_missing", "hits": []})
            continue
        content = path.read_bytes()
        if sha256(content).hexdigest() != source["sha256"]:
            records.append(identity | {"status": "hash_mismatch", "hits": []})
            continue

        try:
            page_count, hits = extract_evidence(path)
        except (OSError, PdfReadError) as exc:
            records.append(
                identity
                | {
                    "status": "extraction_error",
                    "error": type(exc).__name__,
                    "hits": [],
                }
            )
            continue
        fields = sorted({hit.field for hit in hits})
        records.append(
            identity
            | {
                "status": "review_required" if hits else "no_labels_found",
                "source_sha256": source["sha256"],
                "source_document": source["local_filename"],
                "source_url": source["source_url"],
                "publication_date": source.get("publication_date"),
                "page_count": page_count,
                "candidate_fields": fields,
                "hits": [hit.to_dict() for hit in hits],
            }
        )

    counts: dict[str, int] = {}
    for record in records:
        status = str(record["status"])
        counts[status] = counts.get(status, 0) + 1
    output = {
        "dataset_id": manifest["dataset_id"],
        "purpose": "Candidate pages for human-reviewed fundamentals extraction",
        "automatic_values_accepted": False,
        "status_counts": dict(sorted(counts.items())),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output["status_counts"], indent=2))


if __name__ == "__main__":
    main()
