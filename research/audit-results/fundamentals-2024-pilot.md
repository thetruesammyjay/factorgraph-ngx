# Point-in-time fundamentals pilot for the 2024 universe

## Objective

This pilot collects fiscal-year 2022 and 2023 fundamentals for the 15-security
NGX universe. The resulting 30 issuer-period observations support a
point-in-time 2024 Value factor pilot. A 2023 fiscal value may enter a portfolio
only after its annual report became public; before then, the most recent
eligible observation remains the 2022 value.

## Collection scope

The collection plan is stored in
`data/manifests/fundamentals-2024-pilot-plan.json`. Each task requires book
equity and period-end shares outstanding. Revenue, net income, assets,
liabilities, and earnings per share are optional supporting fields.

Every accepted row must preserve the audited report or NGX disclosure URL, the
downloaded document's SHA-256 hash and filename, the exact statement page,
reporting scope, source currency, display unit, normalization multiplier, and
the actual publication date when independently observable. Issuer
investor-relations sites are preferred; the NGX corporate-disclosures portal is
the fallback. Financial-aggregator estimates are outside the evidence standard.

## Point-in-time policy

The validator uses the actual publication date as `effective_from` when that
date is supplied. If publication evidence cannot be established, it applies a
90-day lag from fiscal year-end and records `FIXED_LAG_ESTIMATE`. Both cases
remain distinguishable in every processed row and in the coverage report.

The validator rejects unknown tickers, invalid dates, non-positive shares,
non-NGN normalized values, missing provenance, malformed hashes, duplicate
observations, and publication or effective dates before fiscal year-end.
Non-positive book equity is retained with a warning and must be excluded from
positive book-to-market portfolio sorts.

## Current status

Twelve official issuer annual reports are downloaded, SHA-256 verified, and
promoted after page-level review: AIICO FY2022-FY2023, Dangote Cement
FY2022-FY2023, FBN Holdings FY2022-FY2023, GTCO FY2023, MTN Nigeria
FY2022-FY2023, Nigerian Breweries FY2022, UBA FY2022, and Lafarge Africa
FY2023. Their group book equity attributable to owners, period-end shares
outstanding, source units, scope, hashes, and exact pages are recorded in the
canonical collection.

The validated pilot now contains 12 of 30 required observations. Dangote Cement
FY2022-FY2023 and Nigerian Breweries FY2022 use verified publication dates; the
other nine use the declared 90-day fallback because board approval dates do not
establish public availability. MTN Nigeria FY2023 has negative equity and is
retained with the required positive-B/M exclusion warning.

The review queue now contains 12 approved and 18 blocked issuer-periods. The
blocked tasks remain without acceptable local report evidence and are not
imputed. The point-in-time gate remains closed until all 30 observations pass
validation.

The acquisition command reads reviewed URLs from
`data/collection/fundamentals-document-sources.csv`. It does not infer report
URLs. This preserves a human-reviewed connection between issuer, fiscal period,
publication evidence, and source document. Its download manifest distinguishes
missing URLs, request failures, invalid responses, new downloads, and verified
existing files.

The source-discovery command crawls only landing pages recorded in the reviewed
issuer-page registry. It proposes annual-report links using the fiscal year in
the anchor label or PDF filename. Upload-folder dates are deliberately ignored
because a report for one fiscal year is commonly uploaded during the next year.
Candidate scoring is advisory, and the generated worksheet requires human
selection before any URL enters the download catalog.

The source-selection gate verifies every chosen URL against the saved discovery
evidence and permits only one choice per issuer-period. It also requires the
reviewer's identity and review date. This prevents spreadsheet edits or an
ambiguous pair of reports from silently changing the acquisition catalog.

Once PDFs are present, the evidence index searches each page for conservative
book-equity, issued-share, share-count, and unit labels. It records page numbers
and short review contexts but does not infer a financial value. This separation
prevents a PDF layout error, prior-year comparison column, or company-only value
from silently entering the research dataset.

The review worksheet is a separate control boundary. Rows start as `pending`
when evidence is available and `blocked` when the source document is missing.
Promotion requires an explicit `approved` decision, reviewer identity, review
date, statement scope, separate monetary and share-count unit multipliers, and
separate page citations for book equity and shares outstanding. Only approved
rows pass to the canonical point-in-time validator.
