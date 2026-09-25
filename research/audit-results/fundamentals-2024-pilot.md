# Point-in-time fundamentals pilot

## Status

The 15-security universe now has complete fiscal-year 2022 and 2023 coverage:
30 of 30 issuer-period records passed the review and canonical validation
gates. All 30 rows in `data/collection/fundamentals-2024-review.csv` are
approved, and the promotion report is recorded in
`research/audit-results/fundamentals-2024-promotion.json`. The processed
point-in-time collection is `data/processed/fundamentals-2024-point-in-time.csv`.

Eight observations have independently verified publication dates. The other
22 have no verified filing date in the downloaded report or reviewed NGX
release evidence, so the pipeline uses its explicit 90-day fixed-lag estimate.
Board approval dates are retained in reviewer notes where visible, but are not
misrepresented as public release dates. The builder reports no missing
issuer-periods and no validation errors.

## Evidence and normalization

Each observation cites its source report URL, local filename, SHA-256 hash,
book-equity page, shares page, monetary unit, share unit, and reporting scope.
Money is normalized to naira by the recorded multiplier; share counts use the
report's stated unit and are normalized to individual shares. Consolidated
parent-attributable equity excludes non-controlling interests where the report
provides that split. Where an issuer reports only one statement or consolidated
total equity without a separate NCI line, the row names that reported scope.

GTCO's FY2022 report gives issued ordinary shares and a treasury-share balance
only in monetary terms, not the number of treasury shares. The promoted share
count therefore preserves gross issued shares and flags this limitation in the
row notes. Presco's 2023 report explicitly states its issued share count.
Negative equity observations are retained; they must be excluded from positive
book-to-market sorts. The collection currently contains two such observations.

The complete review history is in
`data/collection/fundamentals-2024-verified-observations.json`, with the
worksheet as the promotion boundary. The promotion report records 30 approved
and promoted rows, no errors, and a non-positive-equity warning. The pilot
status report records 30 expected and observed rows, 8 actual dates, and 22
fixed-lag estimates.

## Use in the 2023–2024 experiment

The deterministic experiment has been rebuilt from the complete fundamentals
collection. Point-in-time joins make each annual report usable only from its
verified publication date or the 90-day fallback date. This supports
descriptive Size and Value portfolio construction for the 15-security universe;
the two-year window remains a pilot and does not support broad claims about
NGX factor premia.

See [the experiment results](ngx-public-data-2023-2024-pilot.md) and the
machine-readable run at
`research/audit-results/ngx-public-data-2023-2024-pilot.json`.
