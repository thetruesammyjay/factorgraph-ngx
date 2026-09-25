# CHAPTER FIVE

# SUMMARY, CONCLUSION AND RECOMMENDATIONS

## 5.1 Summary of Findings

This project designed and implemented a graph-orchestrated, point-in-time research platform for Nigerian Exchange equities. The platform combines data validation, financial calculations, graph execution, API services, optional relational persistence, and a web console.

The public-data pilot covers 15 securities from January 2023 to December 2024. It contains 6,375 daily security-date observations across 425 dates. Fundamental evidence contains 30 reviewed FY2022 and FY2023 observations. Eight effective dates are verified filing dates. The other 22 use the declared 90-day estimate.

The system calculates marked-price and official-trade returns separately. It aligns monthly market and risk-free observations and calculates point-in-time Size and Value characteristics. The pilot produces 22 monthly Size and Value spreads. Their Newey-West t-statistics are 0.84, and both 95% bootstrap intervals include zero. These results are preliminary and do not establish factor premiums.

The system can create Momentum formation ranks, but its regression sample has only 11 complete observations. Liquidity is blocked because verified daily volume and traded value are missing. Regime estimation is blocked because the sample has 24 monthly endpoints and the configured minimum is 36. The system exposes these limits instead of returning unsupported results.

The software provides preflight plans, executable LangGraph runs, ordered node traces, run fingerprints, API access, experiment inspection, and a research console. PostgreSQL persistence is available when configured. The pilot demonstrates an inspectable research workflow, not a complete empirical model for the NGX.

## 5.2 Conclusions

The project shows that a deterministic research platform can organise public NGX data and apply point-in-time controls. It links source evidence to financial observations, distinguishes price statuses, and makes calculation and eligibility rules visible.

The pilot also shows that software capability does not replace data sufficiency. The available evidence supports preliminary Size and Value calculations, but the short sample does not support strong conclusions about persistent factor returns. Missing trading activity blocks liquidity analysis. The available monthly history does not support regime estimation under the configured rule.

The project meets its engineering objective. It implements a reproducible and inspectable platform for NGX factor research. It does not conclude that the tested factors earn reliable premiums or that regime-aware allocation improves performance.

## 5.3 Recommendations

1. Extend daily price collection across a longer period and retain source documents, price status, and retrieval manifests.
2. Obtain verified daily volume and traded value before calculating or reporting a Liquidity factor.
3. Verify filing dates and preserve page-level evidence for all fundamental observations.
4. Expand the issuer universe only after applying explicit listing, coverage, and data-quality rules.
5. Collect at least 36 monthly endpoints before evaluating the three-state regime model, then assess state stability and sensitivity.
6. Treat current Size and Value statistics as preliminary and avoid presenting them as investment evidence.
7. Preserve data versions, run fingerprints, graph traces, and software revision details for each reported experiment.
8. Ask a supervisor or independent researcher to review the methods and interpretation before submission.

## 5.4 Contribution to Knowledge

The project contributes an implemented research workflow for public NGX data. It combines point-in-time fundamental alignment, source-level provenance, price-status-aware returns, factor eligibility gates, deterministic portfolio analysis, and inspectable graph runs.

It also demonstrates a practical way to represent unavailable evidence. The platform marks Liquidity and regime analysis as blocked and gives the reason. This makes data sufficiency part of the research output and reduces the risk of treating missing information as valid evidence.

The contribution is a software platform and documented pilot process. The project does not claim a new asset-pricing theory or a conclusive discovery about NGX factor premiums.

## 5.5 Future Work

Future work should extend the validated price history and add verified trading activity. A longer history would support regime estimation and more stable factor statistics. Additional annual reports and verified filing dates would strengthen point-in-time analysis.

The platform can also add corporate-action adjustment evidence, delisted securities, more risk models, sensitivity analysis for portfolio breakpoints, and better transaction-cost estimates. Any new factor should pass a documented input and sample-size gate before the platform reports empirical results.

A later study can compare subperiods and wider issuer universes. It should use out-of-sample evaluation and report sensitivity to universe rules, data revisions, and trading costs.

