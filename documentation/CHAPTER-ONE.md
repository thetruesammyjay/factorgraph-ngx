# CHAPTER ONE

# INTRODUCTION

## 1.1 Background to the Study

Factor analysis studies whether market exposure and company characteristics help explain differences in equity returns. Common characteristics include market capitalisation, book-to-market equity, past returns, profitability, investment, and liquidity. International research finds that factor results can differ across markets. Researchers must therefore test each market with suitable local data (Fama & French, 2017; Foye, 2018).

The Nigerian Exchange (NGX) provides a relevant setting for this work. Public sources include daily official lists, issuer reports, index observations, and government security rates. These sources use different formats, identifiers, and reporting dates. Some daily price records also carry forward a prior price when a new trade price is not reported. A research system must preserve these distinctions.

Point-in-time alignment is important. A financial statement describes a past fiscal period, but investors can use its information only after publication. A study that treats fiscal year-end as the availability date can create look-ahead bias. This platform uses a verified filing date where the evidence supports one. Where it does not, it applies a declared 90-day reporting-lag estimate and records that choice.

This project designs and implements a graph-orchestrated, point-in-time research platform for NGX equities. Deterministic Python modules calculate returns, characteristics, portfolio results, and statistics. LangGraph coordinates the research steps. FastAPI provides research services, and a Next.js console displays results. The graph does not use language-model agents to create or judge financial evidence.

The completed evaluation is a public-data pilot from January 2023 to December 2024. It covers 15 NGX securities and 30 reviewed FY2022–FY2023 fundamental observations. It provides preliminary Market, Size, Value, and Momentum outputs where input gates permit them. Verified daily volume and traded value are unavailable, so Liquidity analysis is blocked. The 24-month sample is below the regime engine’s 36-month minimum, so the pilot does not estimate market states.

## 1.2 Statement of the Problem

NGX research data is spread across official price lists, issuer reports, index records, and interest-rate sources. The records differ in format, frequency, identifiers, and coverage. Manual combination can introduce duplicate records, incorrect joins, or undocumented transformations.

Price data also needs careful interpretation. An unchanged recorded price may reflect a genuine trade at the same price or a value carried forward from a prior observation. These cases have different meanings for return analysis. The researcher must preserve source status and must not treat unavailable trading activity as zero.

Fundamental data has a timing problem. Book equity and shares outstanding refer to a fiscal period, but the annual report becomes public later. Using fiscal year-end as the information date can create look-ahead bias. A reliable process must record the effective date and evidence for the value, unit, reporting scope, and cited report page.

The available public pilot does not support every proposed analysis. It lacks verified daily volume and traded value for liquidity measurement. It has 24 monthly endpoints, below the configured minimum for a three-state regime model. A research platform must expose these limits and block unsupported calculations.

A further problem is reproducibility. If the researcher does not preserve input files, transformations, settings, and software revision, another person may not reproduce the result. This project addresses these issues with a deterministic, point-in-time platform that validates data, records evidence, applies factor-specific gates, and stores inspectable experiment runs.

## 1.3 Objectives of the Study

The general objective is to design and implement a graph-orchestrated, point-in-time research platform for factor analysis of Nigerian Exchange equities.

The specific objectives are to:

1. Design a reproducible workflow for public NGX prices, issuer fundamentals, benchmark observations, and risk-free rates.
2. Implement validation and provenance controls for source documents and structured observations.
3. Align fundamentals to verified or explicitly estimated public availability dates.
4. Implement deterministic return, Market, Size, Value, and 12–1 Momentum calculations with eligibility rules.
5. Implement Size and Value portfolio sorts with Newey-West statistics and bootstrap confidence intervals.
6. Orchestrate research tasks as inspectable graph runs and expose status and results through FastAPI and a Next.js console.
7. Evaluate the system with the available 15-security NGX pilot for January 2023 to December 2024 and report its limits.

## 1.4 Scope of the Study

The study covers the design, implementation, and pilot evaluation of a web-based research platform for NGX equities. Daily prices cover January 2023 through December 2024 for 15 securities. The fundamental dataset contains FY2022 and FY2023 observations for those issuers. All 30 rows have completed page-level review. Eight filing dates are verified; the other 22 effective dates use a documented 90-day estimate.

The system derives monthly marked-price returns and official-trade returns. Marked-price returns use staged closing prices, including carried rows. Official-trade returns use observations classified as official trades. The experiment aligns monthly NGX All-Share Index and 91-day Treasury-bill observations.

The research outputs include market excess returns, point-in-time Size and Value characteristics, preliminary Size and Value portfolio spreads, Momentum formation ranks, regression diagnostics, Newey-West statistics, bootstrap intervals, portfolio holdings, and experiment provenance. The two-year pilot produces 22 Size and Value spread observations. Their confidence intervals include zero, so the results remain preliminary.

Liquidity is outside the completed empirical analysis because verified daily volume and traded value are absent. Regime estimation is also outside the completed pilot because 24 monthly endpoints do not meet the configured minimum of 36. The platform reports these analyses as blocked. The study does not cover live trading, broker integration, high-frequency trading, a complete NGX history, investment advice, or predictive claims about future returns.

## 1.5 Significance of the Study

The platform gives students and researchers a practical way to prepare and inspect NGX research data. It keeps source details, point-in-time dates, data-quality rules, and experiment settings visible. Users can inspect why a calculation is available, preliminary, or blocked.

The system also separates quantitative calculations from workflow coordination and presentation. Python modules calculate the financial outputs. LangGraph manages task order and state. FastAPI provides research services, and the Next.js console presents the results.

The pilot shows how data limitations affect empirical research. It makes clear that factor eligibility depends on verified inputs and sample size. This prevents an incomplete pilot from being presented as full validation.

## 1.6 Limitations of the Study

The study uses a public-data pilot that covers 15 NGX securities from January 2023 to December 2024. This two-year period is short for asset-pricing research. The results may not represent other periods, all NGX securities, or the long-run behaviour of the market. The Size and Value portfolio results are preliminary and do not establish reliable factor premiums.

Some staged daily prices are carried forward from an earlier observation. The platform keeps carried-price returns separate from returns between consecutive official-trade observations. These return series have different coverage and may produce different results. The pilot therefore does not treat every unchanged price as evidence of a new trade.

The fundamental dataset contains 30 FY2022 and FY2023 observations. Eight filing dates are verified from available evidence. The remaining 22 dates use a declared 90-day reporting-lag estimate. An estimated date may differ from the date when the information became public. Point-in-time results that use these observations therefore retain this timing uncertainty. The platform records the date basis so that users can identify estimated dates.

The available data does not include verified daily volume and traded value for the study universe. The project therefore cannot calculate or evaluate a Liquidity factor. The NGX All-Share Index and 91-day Treasury-bill data cover only the same 24-month pilot period, which also limits the statistical sample.

The regime engine requires at least 36 monthly observations. The pilot provides 24 monthly endpoints, so the system blocks regime estimation. Momentum can be formed from the available price history, but its complete return sample does not meet the configured minimum for regression analysis. These outputs must not be interpreted as validated evidence of regime effects or Momentum premiums.

The study evaluates a research platform and its deterministic outputs. It does not test live trading, execution quality, or performance with a longer history or a larger security universe. The findings are limited to the available sources, documented assumptions, and sample period used in the pilot.

## 1.7 Definition of Terms

**Benchmark:** A market index or return series used to compare research returns.

**Carried price:** A price value retained from an earlier observation when a new official trade price is unavailable.

**Effective date:** The date from which a fundamental observation is treated as public information.

**Factor:** A measurable market or company characteristic used to group or explain equity returns.

**Factor eligibility:** A decision that shows whether required inputs and sample conditions support a calculation.

**Fundamental data:** Issuer financial information, such as book equity and shares outstanding.

**Graph orchestration:** Coordination of ordered computational tasks through nodes that exchange research state.

**Liquidity:** The ability to trade a security promptly and with limited cost or price impact.

**Market capitalisation:** The market value of a company’s listed equity, based on price and shares outstanding.

**Momentum:** A return characteristic based on past performance over a defined formation window.

**Point-in-time alignment:** Use of a fundamental observation only after its public effective date.

**Portfolio sort:** A method that ranks securities by a characteristic and forms groups or return spreads.

**Risk-free rate:** A reference rate used to calculate excess returns.

**Run fingerprint:** A hash that identifies the research data and configuration used for an experiment.

**Transaction cost:** An estimated charge applied to portfolio turnover in a simulation.

