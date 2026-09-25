# Research data

`raw/` is reserved for source extracts. `processed/` contains validated, versioned research datasets.

Do not commit confidential or licensed source data. Every dataset used in an experiment should carry a version and a data dictionary entry.

## Production schema

The API migration creates these PostgreSQL tables:

- `companies`: issuer master data and current security metadata.
- `security_identifiers`: ticker and ISIN history, including validity periods.
- `price_observations`: daily OHLC, close/adjusted close, volume and trading value.
- `fundamental_observations`: fiscal values with publication and effective dates.
- `corporate_actions`: splits, rights issues, bonus issues and dividends.
- `benchmark_observations`: NGX All Share and other benchmark series.
- `risk_free_observations`: dated annualized rates by tenor.
- `dataset_versions`: immutable source snapshot metadata and manifests.
- `experiments`: research configurations linked to a dataset version.

Fundamentals must use `effective_from` when selecting observations for a
backtest. Use the actual publication date when available; otherwise record the
fixed-lag method in `effective_date_source`.

## Migration commands

Run these from `apps/api` with the API environment loaded:

```powershell
uv run alembic current
uv run alembic check
uv run alembic upgrade head
```

The raw NGX files remain outside the database and outside Git. Import jobs
should register their source file hashes and coverage in `dataset_versions`
before loading canonical observations.

CSV schemas for public-data collection are kept in `templates/`. Committed
source manifests contain URLs, retrieval metadata, hashes, and coverage without
committing the downloaded files themselves. The first public-source assessment
is documented in `research/audit-results/public-data-feasibility.md`.

## December 2024 pilot

From `apps/api`, build the three-security pilot with:

```powershell
uv run python -m scripts.build_ngx_dol_pilot `
  --input ../../data/raw/ngx-dol-2024-12 `
  --output ../../data/processed/ngx-dol-december-2024-pilot.csv `
  --report ../../research/audit-results/ngx-dol-december-2024-validation.json `
  --api-report app/data/reports/latest.json `
  --tickers DANGCEM ZENITHBANK SEPLAT
```

The processed CSV is reproducible and ignored by Git. The validation report is
committed because it records coverage, duplicate checks, stale-price runs, and
the deliberate absence of unverified liquidity values.

For the annual audit, use the same commands with a 2024 date range, the
`data/raw/ngx-dol-2024` directory, `--download-manifest`, a stable `--dataset-id`,
and `--workers 4`. The annual decision and monthly statistics are documented in
`research/audit-results/ngx-dol-2024-coverage.md`.

The versioned 15-security universe is stored in `universes/ngx-15-2024.json`.
Pass it to the builder with `--universe ../../data/universes/ngx-15-2024.json`;
the resulting audit is documented in
`research/audit-results/ngx-dol-2024-15-security.md`.

## Point-in-time fundamentals pilot

The 2024 pilot targets fiscal years 2022 and 2023 for all 15 issuers, giving 30
issuer-period collection tasks. Create the collection plan from `apps/api`:

```powershell
uv run python -m scripts.create_fundamentals_plan `
  --universe ../../data/universes/ngx-15-2024.json `
  --output ../../data/manifests/fundamentals-2024-pilot-plan.json `
  --catalog ../../data/collection/fundamentals-document-sources.csv `
  --fiscal-years 2022 2023
```

After reviewing each issuer or NGX disclosure page, enter the direct HTTPS PDF
URL, publication date, and source type in the source catalog. Download and hash
the configured documents with:

Official issuer landing pages are recorded separately in
`collection/fundamentals-issuer-pages.csv`. Discover candidate report links with:

```powershell
uv run python -m scripts.discover_fundamentals_sources `
  --plan ../../data/manifests/fundamentals-2024-pilot-plan.json `
  --registry ../../data/collection/fundamentals-issuer-pages.csv `
  --output ../../research/audit-results/fundamentals-2024-source-discovery.json `
  --review ../../data/collection/fundamentals-source-candidates.csv
```

Discovery matches fiscal years against link labels and PDF filenames, not
upload-directory dates. It ranks candidates but never selects one. Review the
candidate worksheet and verify that the document is the complete issuer annual
report. Mark exactly one candidate with `yes`, `true`, `1`, or `x`, and provide
the reviewer, review date, and any independently verified publication date.

Apply reviewed selections to the download catalog with:

```powershell
uv run python -m scripts.apply_fundamentals_source_review `
  --review ../../data/collection/fundamentals-source-candidates.csv `
  --discovery ../../research/audit-results/fundamentals-2024-source-discovery.json `
  --catalog ../../data/collection/fundamentals-document-sources.csv `
  --report ../../research/audit-results/fundamentals-2024-source-selection.json
```

The command rejects multiple choices for one issuer-period, edited URLs that do
not occur in the discovery evidence, missing reviewer metadata, invalid dates,
and publication dates before fiscal year-end. Unselected catalog rows and
previously recorded publication dates remain unchanged.

```powershell
uv run python -m scripts.fetch_fundamentals_documents `
  --plan ../../data/manifests/fundamentals-2024-pilot-plan.json `
  --catalog ../../data/collection/fundamentals-document-sources.csv `
  --output ../../data/raw/fundamentals-2024-pilot `
  --manifest ../../data/manifests/fundamentals-2024-documents.json
```

The command resumes from valid local PDFs, rejects insecure URLs and non-PDF
responses, and records a SHA-256 hash for every accepted document. Raw PDFs are
ignored by Git; the evidence manifest is committed.

After documents are available, create a page-level evidence index:

```powershell
uv run python -m scripts.index_fundamentals_evidence `
  --manifest ../../data/manifests/fundamentals-2024-documents.json `
  --documents ../../data/raw/fundamentals-2024-pilot `
  --output ../../research/audit-results/fundamentals-2024-evidence.json
```

The index reports candidate pages for book equity, shares outstanding, and unit
labels. It never promotes nearby numbers into the canonical dataset. A reviewer
must inspect the PDF page, choose consolidated or company-only scope, confirm
the relevant year column and unit, and enter the supported value manually.

Create the human-review worksheet once the evidence index has been refreshed:

```powershell
uv run python -m scripts.create_fundamentals_review `
  --evidence ../../research/audit-results/fundamentals-2024-evidence.json `
  --output ../../data/collection/fundamentals-2024-review.csv `
  --merge
```

The command refuses to overwrite an existing worksheet unless `--merge` or
`--replace` is passed. Merge preserves completed reviews while refreshing
evidence for newly downloaded documents. A reviewer must enter the
financial values, statement scope, units, separate book-equity and share-count
page citations, their name, review date, and `approved` status.

Promote approved rows through the canonical validator with:

```powershell
uv run python -m scripts.promote_fundamentals_review `
  --review ../../data/collection/fundamentals-2024-review.csv `
  --universe ../../data/universes/ngx-15-2024.json `
  --output ../../data/collection/fundamentals-2024-pilot.csv `
  --report ../../research/audit-results/fundamentals-2024-promotion.json
```

Promotion fails when there are no approved rows, required review evidence is
missing, or the canonical point-in-time validator rejects an observation.

Enter only report-supported values in
`collection/fundamentals-2024-pilot.csv`. Record the source URL, document name,
SHA-256 hash, reporting scope, separate monetary and share-count multipliers,
and exact page reference. Use
the report release date as `publication_date`; leave it blank only when the
date cannot be established, so the builder labels its fixed-lag fallback.

```powershell
uv run python -m scripts.build_fundamentals_pilot `
  --input ../../data/collection/fundamentals-2024-pilot.csv `
  --universe ../../data/universes/ngx-15-2024.json `
  --output ../../data/processed/fundamentals-2024-pilot.csv `
  --report ../../research/audit-results/fundamentals-2024-pilot-status.json `
  --expected-periods 2022-12-31 2023-12-31 `
  --fixed-lag-days 90
```

The current review contains all 30 expected issuer-periods and passes the
point-in-time gate. Its two-year Size and Value portfolio results are still
preliminary; complete input coverage does not turn the short pilot into evidence
of a persistent factor premium.

For a new fiscal period or a future replacement review, regenerate the
issuer-period queue. It preserves the current canonical observations and
identifies missing periods without fabricating values:

```powershell
uv run python scripts/build_fundamentals_completion.py `
  --universe ../../data/universes/ngx-15-2024.json `
  --input ../../data/collection/fundamentals-2024-pilot.csv `
  --fiscal-periods 2022-12-31 2023-12-31 `
  --output ../../data/collection/fundamentals-2024-completion-queue.csv `
  --report ../../research/audit-results/fundamentals-2024-completion.json
```

Review each `missing` or `needs_review` task, verify its annual-report pages,
units, reporting scope, and publication date, then promote only approved rows.
The queue is a collection control; it never fabricates a fundamental value.

## Deterministic return and eligibility pilot

The first experiment uses the validated 15-security price dataset and reviewed
canonical fundamentals. It preserves marked-price returns separately from
official trade-to-trade returns, aggregates monthly equal-weight market proxies,
calculates a short-horizon momentum snapshot, and evaluates every factor's
input gate.

```powershell
uv run python scripts/build_public_data_experiment.py `
  --prices ../../data/processed/ngx-dol-2023-2024-15-security.csv `
  --fundamentals ../../data/collection/fundamentals-2024-pilot.csv `
  --daily-output ../../data/processed/ngx-2023-2024-daily-returns.csv `
  --monthly-output ../../data/processed/ngx-2023-2024-monthly-returns.csv `
  --characteristics-output ../../data/processed/ngx-2023-2024-point-in-time-characteristics.csv `
  --universe ../../data/universes/ngx-15-2024.json `
  --report ../../research/audit-results/ngx-public-data-2023-2024-pilot.json `
  --api-report app/data/reports/pilot-latest.json `
  --momentum-months 11 `
  --momentum-skip-months 1 `
  --benchmark ../../data/processed/benchmark-2023-2024.csv `
  --risk-free ../../data/processed/risk-free-2023-2024.csv
```

The optional `--benchmark` and `--risk-free` arguments accept copies of the
schemas in `data/templates/benchmark.csv` and `data/templates/risk_free.csv`.
They must be supplied together. The default selected series are `NGXASI` and
`91D`; override them with `--benchmark-code` and `--risk-free-tenor` only when
the experiment methodology explicitly names another series.

Generated return CSVs remain ignored because they are reproducible. The compact
experiment report is committed for the API and research audit trail.

The report identifies every supplied input by filename, byte length and SHA-256
hash. Its stable dataset version is derived from those identities and the
numerical configuration, while the run metadata records the Git revision and
whether uncommitted changes existed during generation.

The report also contains a top-five 12–1 Momentum portfolio. Each rebalance
uses 11 monthly returns ending one month before formation, applies the
resulting weights to the following month, and deducts 50 basis points times
one-way turnover. Official-trade returns are retained as a coverage-labelled
sensitivity series; they are not silently substituted for missing observations.

The point-in-time characteristic output matches every monthly price to the most
recent fundamental observation whose `effective_from` date is on or before the
price date. Size uses `close × shares_outstanding`. Value uses `book_equity ÷
market_cap` and excludes non-positive book equity without excluding the issuer
from Size. Missing and excluded observations retain explicit reason codes.

The same report contains deterministic Size and Value portfolios. Each sort is
formed at month end and applied to the following month, with two equal-weight
groups: Small minus Big for Size and High book-to-market minus Low for Value.
The report includes group counts, long-short spreads, Newey-West t-statistics,
and seeded 95% bootstrap intervals. The current fundamentals gate is complete,
but all portfolio results remain labelled preliminary because this pilot spans
only two years and 22 holding periods.

It also contains market-only HAC regression diagnostics for the Size, Value,
and Momentum return series. The regressions align each target with the monthly
market excess return, report alpha and factor coefficients with Newey-West
standard errors, and mark samples shorter than 36 observations as preliminary.

The regime analysis record applies the same evidence gate before fitting a
three-state Gaussian HMM. It records the number of monthly endpoints,
complete feature observations, the configured minimum sample, and either a
blocked reason or the fitted timeline, state summaries, and transition matrix.

The API also exposes the fundamentals completion report at
`/api/v1/datasets/fundamentals/completion/latest`, allowing the web console to
show approved, missing, and remaining issuer-period tasks without altering the
canonical evidence file.

## Official market inputs

Collect annual NGX ASI weekly closes and CBN 91-day NTB auction rates from
`apps/api`:

```powershell
$env:PYTHONPATH='.'
uv run python scripts/collect_2024_market_inputs.py `
  --year 2024 `
  --raw-dir ../../data/raw/market-inputs-2024 `
  --benchmark-output ../../data/collection/benchmark-2024.csv `
  --risk-free-output ../../data/collection/risk-free-2024.csv `
  --manifest ../../data/manifests/market-inputs-2024.json `
  --review ../../research/audit-results/market-inputs-2024-review.json
```

The benchmark series is sampled from official weekly reports. Monthly alignment
uses the last weekly close available in each month and does not describe it as a
daily month-end close. The risk-free series uses the CBN primary-market `91DAY`
marginal rate from the final auction available in each month.

Merge reviewed annual files only after each annual audit passes:

```powershell
uv run python scripts/build_multi_year_dataset.py `
  --prices 2023=../../data/processed/ngx-dol-2023-15-security.csv `
  --prices 2024=../../data/processed/ngx-dol-2024-15-security.csv `
  --benchmark 2023=../../data/collection/benchmark-2023.csv `
  --benchmark 2024=../../data/collection/benchmark-2024.csv `
  --risk-free 2023=../../data/collection/risk-free-2023.csv `
  --risk-free 2024=../../data/collection/risk-free-2024.csv `
  --prices-output ../../data/processed/ngx-dol-2023-2024-15-security.csv `
  --benchmark-output ../../data/processed/benchmark-2023-2024.csv `
  --risk-free-output ../../data/processed/risk-free-2023-2024.csv `
  --manifest ../../data/manifests/ngx-public-2023-2024.json `
  --review ../../research/audit-results/ngx-public-2023-2024-merge.json
```

The merger rejects mislabeled years and duplicate keys before it writes any
combined output. Its manifest stores source and output SHA-256 identities.

