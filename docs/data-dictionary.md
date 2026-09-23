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
