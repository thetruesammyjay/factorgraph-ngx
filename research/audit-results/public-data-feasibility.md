# Public-data feasibility audit

**Audit date:** 21 September 2026  
**Pilot securities:** DANGCEM, ZENITHBANK, SEPLAT  
**Decision:** Proceed with the public-data build, but describe the first result as a data-feasibility pilot until daily liquidity coverage and point-in-time fundamentals pass the completeness thresholds.

## What was tested

Three official NGX Daily Official List (Equities) PDFs were downloaded for 22 September 2022, 29 December 2023, and 31 December 2024. Each file was hashed with SHA-256 and registered in `data/manifests/public-audit-2026-09-21.json`. The raw files are deliberately excluded from Git.

The three PDFs are machine-readable. `pypdf` extracted all pages, and each test security appeared in every file. This establishes that the documents can be acquired, preserved, identified by hash, and parsed without optical character recognition.

A full-month retrieval test then checked all 22 weekdays in December 2024. Eighteen official PDFs downloaded successfully and four dates returned HTTP 404: 17, 25, 26, and 27 December. The latter dates include public holidays, so a trading-calendar reconciliation is required before describing 18/22 as missing-data coverage. DANGCEM, ZENITHBANK, and SEPLAT appeared in all 18 retrieved documents.

The positioned-text parser produced 54 keyed observations with no duplicate keys, missing ticker dates, or non-positive current market prices. It also exposed substantial stale-price risk: DANGCEM had no Official Close in all 18 files, SEPLAT had none in all 18, and ZENITHBANK lacked one in 7. DANGCEM's Current Market Price was unchanged throughout the retrieved month. The extraction therefore passes its structural check, while research readiness remains blocked pending stale-price review and a verified liquidity source. Detailed machine-readable results are in `research/audit-results/ngx-dol-december-2024-validation.json`.

## Fields observed

The Daily Official List exposes the security symbol and name, public quotation price, official open, official close, current market price, the date and quantity shown under “Ex - Business Done,” 52-week high and low, dividend fields, EPS, and P/E.

The 31 December 2024 sample produced recognisable rows for all three pilot securities, including an official/current price of NGN 45.50 for ZENITHBANK, NGN 431.00 for DANGCEM, and NGN 5,130.00 for SEPLAT. These values are recorded here only as extraction checks; they are not yet a research dataset.

## Critical limitation

The `Qty` column sits under “Ex - Business Done.” It must not be silently interpreted as total daily traded volume. The public PDF also does not expose an unambiguous daily traded-value or daily number-of-transactions field. Therefore, the sampled Daily Official Lists can support price-history investigation, but they do not by themselves prove that the Amihud liquidity factor can be built correctly.

The PDF layout also joins adjacent columns during text extraction. A production parser needs page-aware validation and reconciliation against a second source or manually checked samples. Blank official-open or official-close cells must remain missing; they must not be converted to zero or forward-filled before the stale-price rules run.

## Fundamental-data result

The three issuers publish annual reports publicly, but direct scripted downloads were blocked or stale during this audit. This does not make the reports unavailable: it means the collection workflow must support a browser-assisted manual download from each issuer or the NGX corporate-disclosures portal. Every saved report must retain its source URL, retrieval date, SHA-256 hash, fiscal period, and actual disclosure/publication date.

For point-in-time tests, the publication date controls when a book-equity observation becomes eligible. The year-end date printed on the statements is not an acceptable substitute. If the actual date cannot be established, the record must declare the fixed-lag estimate used by the experiment.

## Go/no-go assessment

| Requirement | Audit status | Consequence |
| --- | --- | --- |
| Official public price documents | Pass for three sampled dates | Continue a bounded historical coverage audit. |
| Machine-readable security rows | Pass | Build and test a layout-aware parser. |
| Full daily close series | Not yet established | Enumerate trading dates and measure retrieval success before factor estimation. |
| Daily volume and traded value | Not established from the sampled PDFs | Do not claim a validated liquidity factor yet. |
| Public annual reports | Available, automated retrieval unreliable | Use controlled manual acquisition and hash every file. |
| Point-in-time publication dates | Not yet collected | Do not run the Value factor until aligned metadata exists. |
| ASI and risk-free series | Sources identified, not collected in this audit | Collect after the equity coverage gate passes. |

## Next collection gate

The next job should audit one complete calendar month before attempting 2019–2025. For every expected NGX trading day, it should record HTTP result, file signature, page count, extractability, and the presence of the three pilot tickers. The result should report:

1. expected and retrieved trading days;
2. valid closes per ticker;
3. non-trading or stale-price observations;
4. whether any official public source supplies daily volume and traded value;
5. manual corrections required by the parser; and
6. source terms or access restrictions that affect reproducibility.

Proceed to the 15-security universe only if the monthly audit meets the declared price-completeness threshold and a defensible liquidity input is found. If public volume/value coverage remains unavailable, the implementation should still demonstrate Market, Size, Value, and Momentum where their inputs pass validation, while marking Liquidity as unavailable rather than fabricating it.
