# Data sources

Document each price, fundamental, benchmark, and risk-free source with coverage
dates, licensing, transformation rules, and ingestion timestamp.

## Issuer fundamentals

Use audited annual reports from issuer investor-relations websites as the
preferred source and the NGX corporate-disclosures portal as the fallback. Do
not substitute aggregator estimates for audited statement values.

For every observation, preserve the source URL, downloaded filename, SHA-256
hash, statement page, reporting scope, currency, and source unit. Normalize
values to NGN and base units. The annual report's public release date is the
effective date; when that evidence is unavailable, retain the missing
publication date and explicitly label the configured fixed-lag estimate.
