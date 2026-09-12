# CHAPTER ONE

# INTRODUCTION

## 1.1 Background to the Study

The Nigerian Exchange (NGX) provides an important market for studying equity returns, risk, liquidity, and portfolio performance. Investors and researchers can examine listed companies through market prices, trading activity, company fundamentals, and market-index data. However, these data sources do not become useful research evidence until a system collects, validates, aligns, and analyses them in a consistent way.

Factor investing provides a structured method for studying differences in stock returns. Instead of relying on one market indicator, a factor model groups securities according to measurable characteristics. Common characteristics include market exposure, company size, value, momentum, profitability, investment, and liquidity. Fama and French (2015) show that a multi-factor model can explain average stock returns more effectively than a single market factor. Their analysis uses a specific sample. Hou, Xue, and Zhang (2015) also show that factor portfolios can summarise several return patterns through a systematic investment approach.

Evidence from emerging markets shows that factor behaviour can differ across countries and periods. Zaremba (2015) reports that value, size, and momentum effects can vary across national markets. This result supports the need for country-specific testing rather than direct transfer of results from developed markets to the Nigerian market. The NGX market also has features that make liquidity important. These features include differences in trading activity, price availability, company size, and the number of actively traded securities. Abdullahi and Fakunmoju (2019) examine liquidity and stock returns in the Nigerian market and show the relevance of market conditions to return analysis.

A factor model requires more than formulas. It requires a reliable research process. The system examines daily prices for duplicate observations, invalid values, missing dates, and inconsistent security identifiers. Fundamental data must be linked to the date on which the information became available. If a backtest uses a financial statement before its publication date, the result may contain look-ahead bias. The system must also preserve missing observations instead of silently replacing them with invented values.

The proposed study addresses these requirements by designing a graph-orchestrated multi-agent system for liquidity-augmented, regime-aware multi-factor analysis of Nigerian Exchange equities. The system stores company information, daily prices, fundamentals, corporate actions, benchmark observations, risk-free rates, and dataset versions. It then prepares a monthly research dataset and calculates five factors:

1. Market
2. Size
3. Value
4. Momentum
5. Liquidity

The system uses a directed research workflow. The workflow loads and inspects the dataset. It aligns fundamentals by availability date. It constructs factor series and calculates statistical diagnostics. It estimates market regimes, ranks securities, constructs a portfolio, performs a backtest, and stores the experiment. LangGraph provides workflow orchestration. Python provides quantitative calculations. FastAPI exposes research services. PostgreSQL stores versioned research data and experiment records. Next.js provides the web interface.

Machine learning research supports the use of structured computational methods in empirical asset pricing. Gu, Kelly, and Xiu (2020) show that machine learning methods can use nonlinear relationships among financial predictors. The system does not use a machine learning model as a replacement for the factor definitions or statistical tests. It uses deterministic factor formulas and statistical procedures as the source of financial results. The graph workflow coordinates the calculations and records their configuration so that an experiment can be repeated.

Market conditions can also change over time. A factor that performs well during a stable period may behave differently during a high-volatility period. A Hidden Markov Model can represent market regimes as unobserved states that generate different return and volatility patterns. Nystrup, Kolm, and Stenfors (2020) support the use of Hidden Markov Models for regime-aware factor analysis.

The study therefore combines financial data engineering, factor construction, statistical validation, regime analysis, portfolio simulation, and workflow orchestration. The study targets academic research. It does not provide financial advice, execute live trades, or guarantee future investment performance.

## 1.2 Statement of the Problem

Researchers who study NGX equities may need to combine data from several sources. These sources can use different ticker formats, date formats, frequencies, and definitions. A market-price file may identify a company by ticker, while a financial statement may use a company name or an ISIN. A price record may contain a trading date, while a fundamental record may contain a fiscal period and a later publication date. Without a common data model, these records are difficult to join correctly.

A second problem concerns the availability of financial information. A financial statement belongs to a fiscal period, but investors do not know its contents until the company publishes it. A research system may use the fiscal-period end date as the availability date. That date may precede the simulated decision date. The system may then use information that was not available at the decision date. This error can make a backtest appear more successful than a realistic strategy.

A third problem concerns the application of factor models to the NGX market. Many factor studies use large developed-market datasets. Their factor definitions, breakpoints, liquidity measures, and eligibility rules may not fit a smaller emerging market. The researcher therefore needs a system that makes each factor definition visible, configurable, and testable with NGX data.

A fourth problem concerns market regimes. A single average factor return can hide differences between calm, expansionary, and stressed market conditions. Without regime analysis, the researcher cannot examine whether a factor behaves consistently across changing market states.

A fifth problem concerns reproducibility. Manual spreadsheet calculations and disconnected scripts can make it difficult to reproduce an experiment. The researcher needs to know which dataset version, factor settings, date range, portfolio rule, transaction cost, bootstrap seed, and regime configuration produced a result.

This study addresses these problems by designing and implementing the proposed system. The system provides a versioned research database, point-in-time data alignment, five-factor construction, statistical validation, Hidden Markov Model regime analysis, portfolio backtesting, and graph-based experiment tracking.

## 1.3 Objectives of the Study

The general objective is to design and implement a graph-orchestrated multi-agent system for liquidity-augmented, regime-aware multi-factor analysis of Nigerian Exchange equities. The system will construct and validate a multi-factor model using Nigerian Exchange data.

The specific objectives are:

1. To design a versioned data pipeline for NGX prices, company fundamentals, corporate actions, benchmark observations, and risk-free rates.
2. To implement point-in-time data alignment that uses publication dates or an explicitly recorded fixed reporting lag.
3. To construct Market, Size, Value, Momentum, and Liquidity factors from eligible NGX securities.
4. To validate factor behaviour with descriptive statistics, Newey-West adjusted tests, bootstrap confidence intervals, and regression diagnostics.
5. To identify latent market regimes with a Gaussian Hidden Markov Model and analyse factor performance within each regime.
6. To rank eligible securities, construct a configurable long-only portfolio, and perform a historical backtest with transaction-cost adjustment.
7. To provide a web interface and REST API for experiment configuration, workflow execution, result storage, and research-result visualisation.
8. To preserve dataset provenance and experiment configuration so that research results can be reproduced.

## 1.4 Scope of the Study

This study covers the design and implementation of a quantitative research system for ordinary equities listed on the Nigerian Exchange. The system uses daily observations as the main input frequency and derives monthly observations for factor construction, regime modelling, and portfolio rebalancing.

The study covers the period from 1 January 2019 to 31 December 2025. The data pipeline may request earlier observations to provide a formation period for momentum calculations. The research universe contains NGX companies for which the required observations are available. The system can represent listing dates, delisting dates, ticker history, and missing observations.

The factors covered by the study are:

- Market, based on market excess return.
- Size, based on market capitalisation.
- Value, based on point-in-time book-to-market information.
- Momentum, based on a 12-1 month formation return.
- Liquidity, based on trading activity and an Amihud-style illiquidity measure.

The system also covers:

- NGX All Share Index comparison.
- Risk-free rate alignment.
- Factor portfolio construction.
- Statistical diagnostics.
- Three-state market regime estimation.
- Equal-weighted long-only portfolio construction.
- Monthly portfolio rebalancing.
- Transaction-cost adjustment.
- Experiment metadata and result persistence.
- REST API access.
- Research dashboards.

The study does not cover live order execution, broker integration, high-frequency trading, financial advice, guaranteed investment returns, or the replacement of professional investment management. It also does not claim that a factor causes a return. It measures associations and simulated historical performance under stated assumptions.

## 1.5 Significance of the Study

The study is significant to students and researchers because it provides an integrated system for empirical research on NGX equities. The system makes the data preparation process visible and records the assumptions used during analysis. This can help a researcher repeat an experiment and identify the source of a change in results.

The study is significant to financial analysts because it provides a structured way to compare Market, Size, Value, Momentum, and Liquidity signals. The analyst can inspect factor statistics, regime-specific behaviour, portfolio holdings, benchmark performance, and transaction-cost effects in one system.

The study is significant to software engineers because it demonstrates how a quantitative research process can be implemented as a set of connected workflow nodes. The design separates data ingestion, factor calculations, statistical analysis, regime modelling, portfolio construction, and backtesting. This separation can support testing and later extension.

The study is significant to the Nigerian financial research community because it focuses on NGX data. It does not assume that results from other markets apply without testing. It also treats liquidity as a central part of the model. This focus suits a market in which trading activity and data coverage may differ across securities.

The study is significant to research integrity because it records dataset versions, source metadata, effective dates, and experiment configurations. These records help the researcher identify the source of a result. The source may be a new dataset, factor definition, portfolio rule, or statistical configuration.

## 1.6 Definition of Terms

Backtest: A simulation that applies a stated investment rule to historical data.

Benchmark: A market or index series used to compare the performance of a factor or portfolio.

Corporate Action: An event such as a dividend, share split, rights issue, or bonus issue that can affect a security record or price series.

Factor: A measurable characteristic or return series used to study differences in expected or realised stock returns.

Factor Portfolio: A portfolio formed by ranking securities according to a factor characteristic.

Fundamental Data: Financial information about a company, such as book equity, earnings, assets, liabilities, and shares outstanding.

Hidden Markov Model: A statistical model that represents observed data as the output of an unobserved state process.

Liquidity: The ability to trade a security with limited delay and limited price impact.

Market Capitalisation: The value of a company’s equity, calculated as price multiplied by shares outstanding.

Point-in-Time Alignment: The process of using a financial observation only from the date on which that information became available.

Portfolio Rebalancing: The process of updating portfolio holdings and weights at a defined interval.

Risk-Free Rate: A reference return used to calculate excess returns and risk-adjusted performance measures.

Ticker: The short security identifier used by an exchange.

Transaction Cost: An estimated cost of buying or selling a security, expressed as a monetary amount or basis-point rate.

Workflow Orchestration: The coordination of dependent computational steps in a defined execution order.

## REFERENCES

Abdullahi, I. B., & Fakunmoju, S. K. (2019). Market liquidity and stock return in the Nigerian Stock Exchange market. *Binus Business Review, 10*(2), 87-94. https://doi.org/10.21512/bbr.v10i2.5588

Fama, E. F., & French, K. R. (2015). A five-factor asset pricing model. *Journal of Financial Economics, 116*(1), 1-22. https://doi.org/10.1016/j.jfineco.2014.10.010

Gu, S., Kelly, B., & Xiu, D. (2020). Empirical asset pricing via machine learning. *The Review of Financial Studies, 33*(5), 2223-2273. https://doi.org/10.1093/rfs/hhaa009

Hou, K., Xue, C., & Zhang, L. (2015). Digesting anomalies: An investment approach. *The Review of Financial Studies, 28*(3), 650-705. https://doi.org/10.1093/rfs/hhu068

McLean, R. D., & Pontiff, J. (2016). Does academic research destroy stock return predictability? *The Journal of Finance, 71*(1), 5-32. https://doi.org/10.1111/jofi.12365

Nystrup, P., Kolm, P. N., & Stenfors, A. (2020). Regime-switching factor investing with hidden Markov models. *Journal of Risk and Financial Management, 13*(12), 311. https://doi.org/10.3390/jrfm13120311

Zaremba, A. (2015). Country selection strategies based on value, size and momentum. *Investment Analysts Journal, 44*(3), 171-198. https://doi.org/10.1080/10293523.2015.1060747
