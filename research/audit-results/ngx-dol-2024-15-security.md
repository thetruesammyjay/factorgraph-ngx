# NGX 15-security price-universe audit for 2024

**Universe:** `ngx-15-2024`  
**Accepted source documents:** 217  
**Validated observations:** 3,255  
**Decision:** The 15-security price universe passes structural validation and can proceed with explicit stale-price controls. The full factor study remains blocked by unavailable verified liquidity fields.

## Coverage

All 15 securities appeared in every accepted Daily Official List document. Each ticker has 217 observations between 2 January and 31 December 2024. After internal-date reconciliation, the panel contains no duplicate ticker-date keys, missing ticker dates within accepted documents, or non-positive marked prices.

The universe configuration is versioned in `data/universes/ngx-15-2024.json`. It records the selection basis, issuer names, and sectors without treating inclusion as an investment recommendation.

## Stale-price diagnostics

| Ticker | Observations | Unique closes | Longest unchanged run | Rows without Official Close |
| --- | ---: | ---: | ---: | ---: |
| ACCESSCORP | 217 | 109 | 4 | 91 |
| AIICO | 217 | 46 | 6 | 170 |
| DANGCEM | 217 | 16 | 63 | 217 |
| FBNH | 217 | 130 | 3 | 136 |
| GTCO | 217 | 131 | 5 | 111 |
| MTNN | 217 | 69 | 11 | 204 |
| NB | 217 | 69 | 12 | 197 |
| NESTLE | 217 | 26 | 24 | 216 |
| OKOMUOIL | 217 | 22 | 25 | 217 |
| PRESCO | 217 | 27 | 62 | 213 |
| SEPLAT | 217 | 27 | 39 | 217 |
| TOTAL | 217 | 12 | 75 | 217 |
| UBA | 217 | 119 | 3 | 65 |
| WAPCO | 217 | 85 | 6 | 190 |
| ZENITHBANK | 217 | 115 | 4 | 89 |

The results show meaningful cross-sectional variation in trading continuity. UBA, FBNH, GTCO, ZENITHBANK, and ACCESSCORP change price frequently, while TOTAL, DANGCEM, PRESCO, SEPLAT, NESTLE, and OKOMUOIL contain long unchanged-price runs. A monthly return panel may be constructed from the marked prices, but every return must retain stale-price metadata so sensitivity tests can exclude or separately model long non-trading runs.

## Remaining blocker

All 3,255 rows have null total daily volume, traded value, and transaction count because the Daily Official List's “Business Done Qty” has not been verified as total daily activity. The Liquidity factor must remain unavailable. Price-only Momentum analysis can proceed cautiously, while Size and Value still require point-in-time shares outstanding, market capitalisation, and book-equity inputs.

## Next implementation

The next data milestone is a point-in-time fundamentals pilot for these issuers. It should collect fiscal period, actual publication date, book equity, shares outstanding, source URL, file hash, and effective date. In parallel, benchmark and risk-free series should be collected for NGX ASI and the selected CBN Treasury-bill proxy.
