# Data dictionary

Core observations include ticker, trading_date, close, volume, trading_value,
fiscal_period, publication_date, effective_from, book_equity, and shares
outstanding.

## Point-in-time fundamentals

- `fiscal_period`: reporting-period end date, not the data-availability date.
- `publication_date`: actual issuer release or NGX submission date when documented.
- `effective_from`: first date the value may enter an experiment. It equals the
  publication date when known, otherwise the configured fixed-lag date.
- `effective_date_source`: `ACTUAL_PUBLICATION_DATE` or `FIXED_LAG_ESTIMATE`.
- `book_equity`: equity attributable under the declared `reporting_scope`,
  normalized to NGN using `monetary_unit_multiplier`.
- `shares_outstanding`: period-end issued shares used for market-cap and B/M
  construction, normalized to individual shares.
- `reporting_scope`: normally `GROUP`; exceptions must be stated explicitly.
- `source_sha256`: lowercase SHA-256 of the exact annual-report PDF.
- `page_reference`: page containing the reported value so manual review is bounded.

Raw annual-report monetary values are multiplied by `monetary_unit_multiplier`.
Share counts are scaled independently with `shares_unit_multiplier`, because reports
often present currency in thousands or millions while stating shares as actual units.
For example, a statement presented in millions uses `1000000`. Currency
conversion must occur before ingestion; the pilot accepts normalized NGN only.

## Benchmark and risk-free observations

- `index_code`: stable benchmark identifier; the pilot expects `NGXASI` by default.
- `close`: positive index closing level for `observation_date`.
- `tenor`: risk-free instrument tenor; the pilot expects `91D` by default.
- `annual_rate_percent`: quoted annual rate in percentage points, so `18.5` means
  18.5%, rather than decimal `0.185`.
- `source_id`: identifier linked to the exact source manifest or downloaded file.

The monthly benchmark observation is the last available dated level in each
calendar month. For the 2024 public pilot, the source is the official NGX weekly
report, so this is a weekly closing level and may precede the final trading day.
Its return is the percentage change between consecutive selected levels. The
monthly risk-free return is `(1 + annual_rate_percent / 100)^(1/12) - 1`. The
Market factor is the aligned benchmark return minus this effective monthly rate.

## Point-in-time characteristics

- `market_cap`: monthly close multiplied by the latest eligible shares outstanding.
- `log_market_cap`: natural logarithm of eligible market capitalisation.
- `book_to_market`: positive book equity divided by market capitalisation.
- `size_rank`: ascending monthly market-cap rank; rank 1 is the smallest issuer.
- `value_rank`: descending monthly book-to-market rank; rank 1 has the highest ratio.
- `size_eligible` and `value_eligible`: factor-specific inclusion decisions.
- `size_exclusion_reason` and `value_exclusion_reason`: explicit reason when a
  characteristic is unavailable.

The as-of join never selects an observation with `effective_from` later than the
monthly price date. Negative book equity remains available for audit but is
excluded from Value rankings.
