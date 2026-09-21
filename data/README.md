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
  --tickers DANGCEM ZENITHBANK SEPLAT
```

The processed CSV is reproducible and ignored by Git. The validation report is
committed because it records coverage, duplicate checks, stale-price runs, and
the deliberate absence of unverified liquidity values.

