# CHAPTER TWO

# LITERATURE REVIEW

This chapter reviews factor research, emerging-market evidence, Nigerian liquidity studies, regime models, and reproducible computational workflows. It uses these ideas to define the research gap for a point-in-time NGX research platform. The implemented project is deterministic. It does not use language-model agents to calculate or interpret financial results.

## 2.1 Background Concept

Factor analysis studies whether market exposures or company characteristics help explain differences in equity returns. Researchers form factor portfolios by ranking securities on measures such as market capitalisation, book-to-market equity, past returns, profitability, investment, and liquidity.

Fama and French (2017) test a five-factor model across international markets and report regional differences. Foye (2018) also reports variation in factor results across emerging markets. These findings support market-specific tests rather than direct transfer of results from another exchange.

Each factor needs suitable evidence. Size requires market capitalisation. Value requires book equity and market capitalisation. Momentum requires a sufficient historical return window. Liquidity requires valid trading activity measures. The researcher must define the formation date, eligible universe, ranking method, holding period, and rebalancing rule.

This project implements a pilot for NGX data. It derives market excess returns and point-in-time Size and Value characteristics. It constructs preliminary monthly Size and Value spreads and 12–1 Momentum formation ranks. The available daily price files do not provide verified volume and traded value, so Liquidity remains blocked. The 24-month pilot also falls below the sample minimum for regime estimation.

Point-in-time data handling matters because company reports become public after their fiscal periods. A system must use filing dates where evidence is available. If it uses a fallback date, it must label that date as an estimate. The implemented research workflow is shown in Chapter Four.

## 2.2 Theoretical Framework

Four perspectives inform the system: factor asset pricing, liquidity and market microstructure, regime-switching analysis, and reproducible computational research. The platform implements only analyses supported by the available pilot.

### 2.2.1 Factor Asset Pricing Theory

Factor asset-pricing theory represents common return patterns through market or company characteristics. Researchers use factor portfolios and regressions to test whether characteristics relate to realised returns.

Fama and French (2017) evaluate a multi-factor model across international markets. Foye (2018) studies a five-factor model in emerging markets. Their work motivates market-specific measurement and transparent portfolio rules.

This project uses the factor framework as an empirical method. It calculates market excess returns and constructs preliminary Size and Value spreads. It also forms Momentum rankings when the return window is available. The pilot does not support a complete model with validated premiums. Its sample is short, and the Size and Value bootstrap intervals include zero.

### 2.2.2 Liquidity and Market Microstructure Theory

Liquidity concerns the speed and cost of trading an asset. Volume, traded value, transaction counts, bid-ask spreads, and price impact can measure different aspects of liquidity. A price-only file cannot establish these trading conditions.

An Amihud-style measure relates absolute return movement to traded value:

~~~text
ILLIQ_i = mean(absolute daily return_i / daily traded value_i)
~~~

The measure requires verified traded value and valid daily returns. The public pilot does not contain verified daily volume or traded value. The platform therefore records Liquidity as blocked. It does not replace missing turnover with zero or with a price proxy.

Yahaya et al. (2023) study liquidity and volatility on the NGX. Alaba et al. (2024) examine liquidity and Nigerian market performance. These studies support the relevance of local liquidity research. They do not supply the missing daily observations for this project.

### 2.2.3 Regime-Switching Theory

Regime-switching models represent changes in a time series through latent states. A Hidden Markov Model estimates state probabilities and transitions from observed features such as returns and volatility.

Nystrup et al. (2020) apply Hidden Markov Models to regime-switching factor investing. Their work provides a basis for examining factor behaviour across market conditions. Regime estimation still requires enough observations to estimate state distributions and transitions.

The platform includes a three-state Gaussian HMM workflow. Its configured pilot minimum is 36 monthly endpoints. The 2023–2024 dataset has 24 endpoints. The model therefore remains blocked for this pilot. No state labels or regime-specific findings are reported.

### 2.2.4 Reproducible Computational Research

Reproducible computational research records the data, transformations, configuration, and software version behind a result. Harvey et al. (2016) discuss false discoveries in asset-pricing research. McLean and Pontiff (2016) show that published return predictors can weaken outside their original samples.

The platform records source manifests, file hashes, dataset fingerprints, experiment configuration, node status, and software revision where available. Deterministic calculations use explicit settings, including bootstrap seeds. A graph run stores its ordered trace and output summaries. These controls support inspection and repeatability. They do not remove the limits of a short or incomplete dataset.

## 2.3 Related Works

### 2.3.1 Multi-Factor Asset Pricing

Fama and French (2017) test a five-factor model across international markets and report regional differences. Foye (2018) evaluates a five-factor model in emerging markets. These studies provide a basis for factor portfolio analysis, but they do not present the NGX-specific data collection and point-in-time software platform implemented here.

### 2.3.2 Size, Value, and Momentum in Emerging Markets

Emerging-market factor results can depend on coverage, market structure, and period. Foye (2018) reports variation in five-factor performance across emerging markets. Irejeh and Aninoritse (2024) test a Fama–French three-factor model using NGX-listed companies and report relationships involving market, size, and book-to-market measures.

This project adds a software-engineering contribution. It records point-in-time evidence, preserves source provenance, and executes calculations through an inspectable workflow. Its 2023–2024 pilot is too short to support broad claims about persistent factor premiums.

### 2.3.3 Liquidity and Nigerian Equity Returns

Abdullahi and Fakunmoju (2019) examine market liquidity and stock returns in Nigeria. Yahaya et al. (2023) examine liquidity and volatility on the NGX. Alaba et al. (2024) analyse liquidity and stock-market performance in Nigeria.

These studies establish local interest in liquidity. They do not remove the need for verified daily trading activity. The public Daily Official List files collected for this project provide price fields but not verified daily volume or traded value. The platform therefore does not report liquidity returns.

### 2.3.4 Machine Learning and Empirical Asset Pricing

Gu et al. (2020) compare machine-learning methods for empirical asset pricing. Their work shows that flexible models can capture nonlinear relations, while careful validation remains necessary.

This project uses explicit financial formulas for returns and characteristics. It does not use a machine-learning model to generate price, fundamental, or factor evidence. A Gaussian HMM is available for regime analysis, but the pilot fails its minimum-data gate. The system reports that constraint instead of fitting an unsupported model.

### 2.3.5 Regime-Aware Factor Investing

Nystrup et al. (2020) study factor investing with Hidden Markov Models. Their work motivates analysis of factors under different market states.

The current project implements the regime workflow and its readiness checks. It does not report estimated regimes for the 24-month pilot because the configured minimum is 36 monthly endpoints. Software support does not mean that the current dataset supports an empirical result.

### 2.3.6 Graph-Orchestrated Quantitative Workflows

Confalonieri et al. (2024) examine workflow representations that help explain data-science processes. A graph can make dependencies and execution order visible. LangGraph applies graph-based orchestration to stateful application workflows.

This project uses LangGraph to coordinate deterministic research nodes. Nodes prepare data, align fundamentals, check eligibility, calculate supported outputs, and save run information. Financial formulas remain in Python modules. The graph coordinates computation; it does not act as an independent financial agent.

### 2.3.7 Open-Access Evidence Reinforcing the Research Gap

Recent open-access Nigerian studies show that liquidity remains an active local research topic. Yahaya et al. (2023) study liquidity and volatility on the NGX. Alaba et al. (2024) examine liquidity and stock-market performance. Irejeh and Aninoritse (2024) test a three-factor model on NGX-listed equities.

The present project addresses a different problem: how to build an auditable platform that collects public data, records point-in-time assumptions, applies eligibility gates, and runs deterministic analyses. The sources reviewed for this study do not present the same end-to-end implementation with document-level provenance, carried-price treatment, fundamental availability dates, factor eligibility status, graph-run traces, and a web interface for NGX pilot analysis. This statement describes the reviewed works and does not imply that no other NGX research system exists.

## 2.4 Summary of Literature Review

The literature provides methods for factor portfolio construction, emerging-market testing, liquidity measurement, regime analysis, and computational research. It also shows why local data coverage and transparent assumptions matter.

The implemented platform applies these ideas within the limits of its public NGX pilot. It calculates Market, Size, Value, and Momentum outputs when input rules permit them. It blocks Liquidity because verified daily trading activity is absent. It blocks HMM estimation because the monthly sample is below the configured minimum. Empirical conclusions remain limited to the completed pilot.

## 2.5 Research Gaps

The review and data audit identify these gaps:

1. International factor findings cannot be assumed to hold on the NGX. Local data and market conditions require direct testing.
2. NGX research needs workflows that preserve source identity, file coverage, and price-status distinctions. Carried prices must not be confused with official trades.
3. Point-in-time fundamental analysis requires evidence about report values, units, reporting scope, cited pages, and availability dates.
4. Research outputs need explicit eligibility rules. A missing input must not be mistaken for a valid zero or an unconstrained result.
5. Short samples limit inference. The current Size and Value intervals include zero, and the sample does not support regime estimation.
6. Public NGX price files in this pilot do not provide verified daily volume and traded value. This prevents a defensible daily Liquidity factor calculation.
7. The reviewed studies do not present the same integrated platform demonstrated here: source provenance, point-in-time alignment, deterministic factor modules, graph-run traces, API access, and an interactive research console.

The project addresses these engineering and data-process gaps. Its 2023–2024 results are a pilot evaluation. Further data collection and a longer observation period are required before stronger claims about factor premiums, liquidity, or market regimes can be made.

## REFERENCES

Abdullahi, I. B., & Fakunmoju, S. K. (2019). Market liquidity and stock return in the Nigerian Stock Exchange market. *Binus Business Review, 10*(2), 87–94. https://doi.org/10.21512/bbr.v10i2.5588

Alaba, J. S., Ahmed, Y., Malik-Abdulmajeed, K. M., & Hussain, U. (2024). Stock market liquidity and stock market performance in Nigeria: Evidence from the Nigerian Exchange Limited. *iRASD Journal of Management, 6*(2), 78–89. https://doi.org/10.52131/jom.2024.0602.0124

Confalonieri, R., Kutz, O., Calvanese, D., Alonso, J. M., Zhou, S. M., & Daga, E. (2024). Data journeys: Explaining AI workflows through abstraction. *Semantic Web, 15*, 1057–1083. https://doi.org/10.3233/SW-233407

Fama, E. F., & French, K. R. (2017). International tests of a five-factor asset pricing model. *Journal of Financial Economics, 123*(3), 441–463. https://doi.org/10.1016/j.jfineco.2016.11.004

Foye, J. (2018). A comprehensive test of the Fama–French five-factor model in emerging markets. *Emerging Markets Review, 37*, 199–222. https://doi.org/10.1016/j.ememar.2018.09.002

Gu, S., Kelly, B., & Xiu, D. (2020). Empirical asset pricing via machine learning. *The Review of Financial Studies, 33*(5), 2223–2273. https://doi.org/10.1093/rfs/hhaa009

Harvey, C. R., Liu, Y., & Zhu, H. (2016). …and the cross-section of expected returns. *The Review of Financial Studies, 29*(1), 5–68. https://doi.org/10.1093/rfs/hhv059

Irejeh, E. M., & Aninoritse, L. E. (2024). Fama and French three factor model. *European Journal of Accounting, Auditing and Finance Research, 12*(5), 17–30. https://eajournals.org/ejaafr/wp-content/uploads/sites/16/2024/04/Fama-and-French-Three-Factor-Model.pdf

McLean, R. D., & Pontiff, J. (2016). Does academic research destroy stock return predictability? *The Journal of Finance, 71*(1), 5–32. https://doi.org/10.1111/jofi.12365

Nystrup, P., Kolm, P. N., & Stenfors, A. (2020). Regime-switching factor investing with hidden Markov models. *Journal of Risk and Financial Management, 13*(12), 311. https://doi.org/10.3390/jrfm13120311

Yahaya, A., John, S. A., Adegoroye, A., & Olorunfemi, O. A. (2023). Stock market liquidity and volatility on the Nigerian Exchange Limited (NGX). *World Journal of Advanced Research and Reviews, 20*(3), 147–156. https://doi.org/10.30574/wjarr.2023.20.3.2333

