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
    parser.add_argument(
        "--resume",
        action="store_true",
        help="reuse hash-matched evidence records and checkpoint after each report",
    )
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    previous_records: dict[tuple[str, str], dict[str, object]] = {}
    if args.resume and args.output.exists():
        previous = json.loads(args.output.read_text(encoding="utf-8"))
        previous_records = {
            (str(record.get("ticker")), str(record.get("fiscal_period"))): record
            for record in previous.get("records", [])
        }
    records: list[dict[str, object]] = []
    total = len(manifest["records"])
    for index, source in enumerate(manifest["records"], start=1):
        identity = {
            "ticker": source["ticker"],
            "fiscal_period": source["fiscal_period"],
        }
        print(
            f"[{index}/{total}] {identity['ticker']} {identity['fiscal_period']}: ",
            end="",
            flush=True,
        )
        if source["status"] not in AVAILABLE_STATUSES:
            records.append(identity | {"status": "document_unavailable", "hits": []})
            print("document unavailable", flush=True)
            continue

        path = args.documents / str(source["local_filename"])
        if not path.exists():
            records.append(identity | {"status": "file_missing", "hits": []})
            print("file missing", flush=True)
        else:
            content = path.read_bytes()
            actual_hash = sha256(content).hexdigest()
            if actual_hash != source["sha256"]:
                records.append(identity | {"status": "hash_mismatch", "hits": []})
                print("hash mismatch", flush=True)
            else:
                prior = previous_records.get((key := (identity["ticker"], identity["fiscal_period"])))
                if (
                    prior is not None
                    and prior.get("source_sha256") == actual_hash
                    and prior.get("status") in {"review_required", "no_labels_found"}
                ):
                    records.append(prior)
                    print("reused matching prior index", flush=True)
                else:
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
                        print(f"extraction error ({type(exc).__name__})", flush=True)
                    else:
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
                        print(f"indexed {page_count} pages; {len(hits)} candidate labels", flush=True)

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
