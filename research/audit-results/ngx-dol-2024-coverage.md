# NGX Daily Official List 2024 coverage audit

**Audit scope:** DANGCEM, SEPLAT, and ZENITHBANK  
**Candidate period:** 1 January–31 December 2024  
**Decision:** Proceed to a wider **price** universe with stale-price controls. The complete five-factor study remains blocked because daily volume and traded value are not verified.

## Annual result

The downloader tested all 262 Monday-to-Friday dates in 2024. It retrieved 225 PDF responses from the official NGX document library. After checking internal report dates and document types, 217 were valid Daily Official List documents, a 96.44% valid-document rate among retrieved PDFs.

The parser produced 651 observations: 217 for each pilot ticker. There were no duplicate ticker-date keys, missing pilot tickers within the 217 accepted documents, or non-positive closes after source-date reconciliation.

| Month | Weekday candidates | Retrieved PDFs | Valid DOL documents | Source exceptions |
| --- | ---: | ---: | ---: | ---: |
| January | 23 | 20 | 19 | 1 |
| February | 21 | 18 | 18 | 0 |
| March | 21 | 17 | 16 | 1 |
| April | 22 | 16 | 16 | 0 |
| May | 23 | 21 | 20 | 1 |
| June | 20 | 16 | 16 | 0 |
| July | 23 | 20 | 18 | 2 |
| August | 22 | 19 | 18 | 1 |
| September | 21 | 19 | 19 | 0 |
| October | 23 | 21 | 20 | 1 |
| November | 21 | 20 | 19 | 1 |
| December | 22 | 18 | 18 | 0 |

The weekday denominator includes exchange holidays, so it is not an official trading-session denominator. `not_available` dates must be reconciled against an authoritative NGX calendar before calculating final trading-day completeness.

## Source exceptions

Two URLs returned valid PDFs of a different NGX report type: 18 January returned a “List of Equities” report and 21 November returned a market-capitalisation report. Six requested-date files contained Daily Official Lists whose internal report dates differed from their URL dates. The audit excludes these mismatched files rather than assigning their values to the requested dates.

This behavior proves why the internal report date and file hash must be validated. A successful HTTP response and a PDF signature are insufficient provenance checks.

## Price behavior

| Ticker | Accepted observations | Unique closes | Longest unchanged run | Rows without Official Close |
| --- | ---: | ---: | ---: | ---: |
| DANGCEM | 217 | 16 | 63 | 217 |
| SEPLAT | 217 | 27 | 39 | 217 |
| ZENITHBANK | 217 | 115 | 4 | 89 |

The `Current Market Price` field provides a positive marked price for every accepted observation. DANGCEM and SEPLAT show long unchanged runs and no populated `Official Close` in this report layout. Returns built from these values therefore require explicit stale-price flags, non-trading-day treatment, and sensitivity tests. Forward filling must not erase the distinction between a new trade and a carried market price.

## Decision gates

The wider price-universe gate passes because the audit has more than 200 valid source documents, a valid-document rate above 95%, complete presence for all three pilot tickers within accepted documents, no duplicate keys after reconciliation, and no non-positive closes.

The full research-readiness gate remains blocked. All 651 observations lack verified total daily volume, traded value, and number of transactions. The “Business Done Qty” field is not substituted for daily volume. Liquidity-factor results must remain unavailable until a defensible source is collected.

The next collection should expand the same 2024 audit to the proposed 15-security universe. It should retain the existing source-date, document-type, stale-price, and duplicate controls before extending the time range to 2019–2025.
