# NGX public-data research pilot, 2023–2024

## Run and input coverage

The experiment was rebuilt after completion of the 2022–2023 fundamentals
review. It uses daily NGX market data for 15 securities from 3 January 2023
through 31 December 2024, the 30-row reviewed fundamentals collection, monthly
NGX All-Share Index observations, and the CBN 91-day Treasury-bill rate. The
machine-readable output, including input hashes, configuration, and Git
revision, is `research/audit-results/ngx-public-data-2023-2024-pilot.json`.

The price file contains 6,375 rows across 15 tickers and 425 dates. It produces
6,360 marked close-to-close returns and 1,320 returns between consecutive
official-trade observations. Of the staged price rows, 5,041 are carried
prices, so marked-price results are sensitive to stale closes. Benchmark and
risk-free files each cover 24 months, January 2023 through December 2024; 23
monthly market-excess returns align for analysis.

Fundamentals validation passed with 30 of 30 issuer-period observations, no
missing periods, and no validation errors. Eight publication dates are
verified; 22 observations use the documented 90-day estimate. Two negative
book-equity records remain in the source data and are excluded from Value
sorts. Liquidity remains unavailable because verified daily volume and traded
value are not present.

## Descriptive factor results

The Size sort ranks securities by point-in-time market capitalization and
forms equal-weight Small and Big groups. The Value sort ranks positive
book-to-market ratios and forms equal-weight High and Low groups. Portfolios
form at month end and hold in the next month. Each spread has 22 monthly
observations, uses Newey–West lag 4, and has a 2,000-iteration seeded bootstrap
interval.

| Spread | Mean monthly return | Annualized return | Annualized volatility | Sharpe | Newey–West t | Bootstrap 95% interval for mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Size (Small − Big) | 1.25% | 11.73% | 28.37% | 0.53 | 0.84 | −2.08% to 4.67% |
| Value (High − Low) | 2.02% | 21.88% | 29.77% | 0.81 | 0.84 | −1.53% to 5.50% |

Both intervals include zero and both HAC t-statistics are small. These pilot
results do not establish a positive Size or Value premium. They show that the
point-in-time data flow and portfolio calculations can run on the assembled
NGX sample. The single-factor market regressions are also marked preliminary:
each has 22 observations, while the longer-horizon Momentum regression has
only 11 and is blocked.

## Market and eligibility diagnostics

The 15-security marked-price equal-weight proxy has 23 monthly observations,
mean monthly return 4.21%, annualized return 59.17%, annualized volatility
25.97%, and Sharpe 1.95. The official-trade sensitivity has mean monthly return
4.36%, annualized return 60.95%, annualized volatility 27.57%, and Sharpe 1.90.
The equal-weight NGXASI excess-return series has mean monthly return 2.36%,
annualized return 27.66%, annualized volatility 30.06%, and Sharpe 0.94. These
short, volatile samples are descriptive, not forecasts.

| Component | Run status | Interpretation |
| --- | --- | --- |
| Market | Eligible | 23 aligned market-excess observations; descriptive pilot only |
| Size | Eligible | Full 30-row fundamentals coverage; 22 portfolio spread observations |
| Value | Eligible | 28 positive-equity fundamentals rows; 22 portfolio spread observations |
| Momentum | Eligible for formation | 12–1 ranking can be formed; regression validation is blocked at 11 observations |
| Liquidity | Blocked | Verified daily volume and traded value are unavailable |
| Regime model | Blocked | 24 monthly endpoints are below the model's 36-observation minimum |

“Eligible” means the input gate permits construction; it does not mean the
factor is statistically validated. The study remains a 15-security,
two-year public-data pilot, with stale-price, short-sample, fixed-lag, and
share-count limitations. In particular, the GTCO FY2022 report supplies gross
issued shares and treasury-share value but not the number of treasury shares.
This qualification is documented on that fundamentals row.

## Reproduction

From `apps/api`, run `scripts.promote_fundamentals_review` against the review
worksheet and universe, run `scripts.build_fundamentals_pilot`, then run
`scripts/build_public_data_experiment.py` with the committed 2023–2024 price,
benchmark, risk-free, and universe inputs. The full command and output paths
are documented in the repository `README.md` and `data/README.md`.
