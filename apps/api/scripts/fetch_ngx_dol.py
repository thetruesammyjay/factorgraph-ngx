"""Download a bounded date range of public NGX Daily Official List PDFs."""

import json
import time
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from hashlib import sha256
from pathlib import Path

import httpx

URL_TEMPLATE = (
    "https://doclib.ngxgroup.com/DownloadsContent/"
    "Daily%20Official%20List%20-%20Equities%20for%20{date}.pdf"
)


def weekdays(start: date, end: date):
    current = start
    while current <= end:
        if current.weekday() < 5:
            yield current
        current += timedelta(days=1)


def fetch_date(
    client: httpx.Client,
    trading_date: date,
    output: Path,
    repository_root: Path,
    delay: float,
) -> dict:
    ngx_date = trading_date.strftime("%d-%m-%Y")
    url = URL_TEMPLATE.format(date=ngx_date)
    path = output / f"ngx-dol-equities-{trading_date.isoformat()}.pdf"
    record = {
        "date": trading_date.isoformat(),
        "source_url": url,
        "local_path": path.resolve().relative_to(repository_root).as_posix(),
    }

    if path.exists() and path.read_bytes().startswith(b"%PDF"):
        content = path.read_bytes()
        record.update(
            http_status=200,
            status="already_downloaded",
            bytes=len(content),
            sha256=sha256(content).hexdigest(),
        )
        return record

    try:
        response = client.get(url)
        record["http_status"] = response.status_code
        if response.status_code == 200 and response.content.startswith(b"%PDF"):
            path.write_bytes(response.content)
            record.update(
                status="downloaded",
                bytes=len(response.content),
                sha256=sha256(response.content).hexdigest(),
            )
        else:
            record["status"] = "not_available"
    except httpx.HTTPError as exc:
        record.update(status="request_error", error=type(exc).__name__)
    time.sleep(delay)
    return record


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, type=date.fromisoformat)
    parser.add_argument("--end", required=True, type=date.fromisoformat)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--delay", default=0.25, type=float)
    parser.add_argument("--workers", default=1, type=int)
    args = parser.parse_args()

    if args.end < args.start:
        parser.error("--end must not be before --start")

    args.output.mkdir(parents=True, exist_ok=True)
    repository_root = Path(__file__).resolve().parents[3]
    dates = list(weekdays(args.start, args.end))
    records = []
    headers = {"User-Agent": "factorgraph-ngx academic data audit/0.1"}

    with (
        httpx.Client(follow_redirects=True, headers=headers, timeout=30) as client,
        ThreadPoolExecutor(max_workers=args.workers) as executor,
    ):
        futures = {
            executor.submit(
                fetch_date,
                client,
                trading_date,
                args.output,
                repository_root,
                args.delay,
            ): trading_date
            for trading_date in dates
        }
        for future in as_completed(futures):
            record = future.result()
            records.append(record)
            print(f"{record['date']}: {record['status']}", flush=True)

    records.sort(key=lambda record: record["date"])

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(
            {
                "dataset_id": f"ngx-dol-{args.start}-{args.end}",
                "provider": "Nigerian Exchange Limited",
                "purpose": "Bounded public-source coverage audit",
                "records": records,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
