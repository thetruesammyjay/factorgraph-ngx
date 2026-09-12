# CHAPTER TWO

# LITERATURE REVIEW

This chapter reviews literature related to the proposed system. The review covers factor investing, emerging-market equity returns, liquidity, machine learning in asset pricing, market regimes, and quantitative research workflows. The review also identifies the gap addressed by this study. The proposed system is designed as a graph-orchestrated multi-agent system. It coordinates specialised analytical tasks for factor construction, regime analysis, portfolio evaluation, and experiment tracking.

## 2.1 Background Concept

Factor investing studies whether measurable company or market characteristics explain differences in stock returns. A factor can describe a market exposure or a portfolio return spread. Common equity factors include market, size, value, profitability, investment, momentum, and liquidity.

Fama and French (2015) present a five-factor asset pricing model that extends a three-factor structure with profitability and investment. Their results show that a group of factors can explain patterns in average returns more effectively than a single market factor in their sample. Hou, Xue, and Zhang (2015) also use factor portfolios to organise several return patterns into an investment-based model.

Factor research depends on the definition of the signal and the method used to form portfolios. A size signal requires market capitalisation. A value signal requires a valuation measure such as book equity relative to market capitalisation. A momentum signal requires a historical return window. A liquidity signal requires trading information. The researcher must define the observation date, ranking rule, portfolio rule, and rebalancing frequency for each factor.

The proposed system applies this concept to NGX equities. It constructs five research factors:

- Market
- Size
- Value
- Momentum
- Liquidity

The Market factor represents the excess return of the NGX equity market above the selected risk-free rate. The Size factor uses market capitalisation. The Value factor uses point-in-time book-to-market information. The Momentum factor uses a 12-1 month formation return. The Liquidity factor uses trading activity and an Amihud-style illiquidity measure.

Emerging markets require separate empirical testing. Zaremba (2015) finds that value, size, and momentum effects vary across national markets. Foye (2018) also reports that factor results can differ across emerging markets. These studies support the need to test the NGX market directly instead of treating a result from a developed market as a universal result.

Liquidity is important because a security can have a high estimated return and still be difficult or costly to trade. Abdullahi and Fakunmoju (2019) study the relationship between liquidity and stock returns in the Nigerian market. Their work supports the inclusion of liquidity information in a Nigerian equity research system.

The system also uses market-regime analysis. A market regime is a period with a distinct pattern of return, volatility, or transition behaviour. Nystrup, Kolm, and Stenfors (2020) apply Hidden Markov Models to regime-switching factor investing. Their work supports the use of hidden states to compare factor performance under different market conditions.

Research quality also depends on the treatment of data and model choices. Harvey, Liu, and Zhu (2016) discuss the problem of false discoveries in the cross-section of expected returns. McLean and Pontiff (2016) show that return predictability can decline outside the original research sample and after publication. These findings support the use of transparent configurations, out-of-sample evaluation, data versioning, and multiple statistical checks.

Figure 2.1 presents the conceptual framework for the proposed system.

**Figure 2.1: Conceptual Framework for the Proposed Graph-Orchestrated Multi-Agent System**

~~~mermaid
flowchart TD
    A[NGX price data] --> D[Data ingestion]
    B[Company fundamentals] --> D
    C[Benchmark and risk-free data] --> D
    D --> E[Data validation]
    E --> F[Point-in-time alignment]
    F --> G[Five-factor construction]
    G --> H[Statistical validation]
    H --> I[Market regime estimation]
    I --> J[Regime-specific factor analysis]
    J --> K[Security ranking]
    K --> L[Portfolio construction]
    L --> M[Historical backtest]
    M --> N[Benchmark comparison]
    N --> O[Versioned experiment results]
~~~

The framework begins with NGX source data. The data pipeline checks and aligns the records before it constructs the factors. The statistical engine evaluates the factor series. The regime engine identifies latent market states. The portfolio engine ranks securities and simulates a portfolio. The system stores the dataset version, configuration, and results so that the experiment can be repeated.

## 2.2 Theoretical Framework

Four theoretical perspectives support this study: factor asset pricing theory, liquidity and market microstructure theory, regime-switching theory, and reproducible computational research.

### 2.2.1 Factor Asset Pricing Theory

Factor asset pricing theory explains returns through exposure to common risk or return characteristics. The theory supports the use of portfolio return spreads to measure whether a characteristic relates to future returns.

Fama and French (2015) provide a recent multi-factor framework based on market, size, value, profitability, and investment. Hou, Xue, and Zhang (2015) provide another factor framework based on market, size, investment, and profitability. These studies show that researchers can use factor portfolios to test whether observable characteristics explain cross-sectional return differences.

The proposed system adapts the factor approach to the research question and available NGX data. It retains market, size, and value concepts. It adds momentum and liquidity because these characteristics are relevant to the stated research model. The system does not claim that the NGX factors must produce the same results as factors in other markets. It calculates the factor series and evaluates the results with stated statistical procedures.

### 2.2.2 Liquidity and Market Microstructure Theory

Liquidity theory links trading conditions to the cost and risk of buying or selling a security. A liquid security can usually trade with lower delay and lower price impact. An illiquid security may require a larger price movement to attract a trade.

A trading-value measure can support an Amihud-style illiquidity calculation:

~~~text
ILLIQ_i =
average(
  absolute daily return_i
  divided by daily trading value_i
)
~~~

A higher value indicates more return movement for a given amount of trading value. The value therefore represents lower liquidity.

Abdullahi and Fakunmoju (2019) examine liquidity and stock returns in the Nigerian market. The study provides local support for examining liquidity with other return characteristics. The proposed system stores volume and trading value so that the researcher can test liquidity definitions and document the selected definition in the experiment configuration.

Liquidity theory also affects portfolio construction. A strategy may select a security because of its factor score, but trading cost can reduce the realised portfolio return. The proposed system therefore applies a configurable transaction-cost estimate during backtesting.

### 2.2.3 Regime-Switching Theory

Regime-switching theory assumes that an observed time series can behave differently across unobserved states. A market can have a stable state, a positive-return state, or a high-volatility state. The state is not known directly. The model estimates the state from observed data.

A Gaussian Hidden Markov Model represents each state with a probability distribution and represents movement between states with a transition matrix. The proposed system uses monthly market return and rolling market volatility as regime features. It estimates three states by default. The researcher interprets the states after reviewing their estimated returns, volatility, persistence, and transition probabilities.

Nystrup, Kolm, and Stenfors (2020) show how Hidden Markov Models can support factor-investing decisions across changing market states. The proposed system uses the model for regime description and regime-specific factor analysis. It does not assume that a state label has a fixed economic meaning before estimation.

### 2.2.4 Reproducible Computational Research

Reproducible computational research requires a clear record of data, methods, parameters, and outputs. A result should be traceable to the dataset and instructions that produced it.

This principle is important in factor research because small changes can affect results. Examples include a different missing-data rule, a different reporting lag, a different ranking date, a different portfolio breakpoint, or a different transaction-cost assumption. Harvey, Liu, and Zhu (2016) show why researchers should control false discoveries when they examine many possible return predictors. McLean and Pontiff (2016) show why results should be tested beyond the original sample.

The proposed system implements reproducibility through dataset versions, data manifests, experiment configurations, fixed random seeds, graph node status, and stored results. The system also separates raw source files from prepared data. This design allows the researcher to identify the exact input and configuration used for an experiment.

## 2.3 Related Works

### 2.3.1 Multi-Factor Asset Pricing

Fama and French (2015) test a five-factor model that includes market, size, value, profitability, and investment. Their work provides a basis for the use of factor portfolios in return explanation. Hou, Xue, and Zhang (2015) propose a related factor approach that uses investment and profitability signals. Fama and French (2017) test a five-factor model across international markets and show that factor results can vary by region.

These studies provide established factor concepts, but they do not provide a complete NGX research system. They also do not define the data ingestion, point-in-time alignment, graph execution, dashboard, and experiment persistence required by this study.

### 2.3.2 Size, Value, and Momentum in Emerging Markets

Zaremba (2015) studies value, size, and momentum across national equity markets. The study reports that the strength of these effects can vary across markets. Foye (2018) examines the Fama-French five-factor model in emerging markets and reports differences in factor behaviour across markets.

These studies support country-level factor testing. They also show the need for a system that allows factor definitions and eligibility rules to remain visible and configurable.

### 2.3.3 Liquidity and Nigerian Equity Returns

Abdullahi and Fakunmoju (2019) examine market liquidity and stock returns in the Nigerian Stock Exchange market. Their study considers liquidity with macroeconomic variables and uses historical Nigerian data.

The study is relevant to the proposed system because it provides local evidence for the relationship between liquidity and stock returns. However, it does not provide the complete multi-factor, regime-aware, graph-orchestrated workflow proposed in this project. The proposed system extends the research setting by combining liquidity with market, size, value, and momentum signals.

### 2.3.4 Machine Learning and Empirical Asset Pricing

Gu, Kelly, and Xiu (2020) compare machine learning methods for empirical asset pricing. They report that nonlinear interactions among predictors can improve return prediction in their data. Their work shows the value of systematic model comparison and disciplined validation.

The proposed system uses machine learning in a limited and controlled way. The system uses a Gaussian Hidden Markov Model for regime estimation. The core factor definitions remain explicit and deterministic. This design makes the financial calculations easier to inspect and reduces the risk that an opaque prediction model replaces the research definition.

### 2.3.5 Regime-Aware Factor Investing

Nystrup, Kolm, and Stenfors (2020) study factor investing with Hidden Markov Models. Their work connects factor selection with estimated market regimes. It supports the idea that factor performance can vary across market conditions.

The proposed system differs in its workflow scope. It inspects input data, aligns fundamentals by availability date, constructs factors, estimates regimes, calculates regime-specific statistics, builds a portfolio, and stores the complete experiment. This design allows the researcher to examine both factor behaviour and the consequences of a portfolio rule.

### 2.3.6 Graph-Orchestrated Quantitative Workflows

Kundu et al. (2025) present a multi-agent framework for quantitative finance and portfolio management analytics. Their work shows how specialised components can coordinate financial analysis tasks. Confalonieri et al. (2024) also examine graph-based representations of data-science workflows and their role in explaining how systems produce analytical results.

These studies support the use of modular and coordinated computational components. The proposed system applies the idea to a deterministic research pipeline. Each graph node has a defined task and receives the output of an earlier node. The graph records the execution order and makes the workflow easier to inspect.

## 2.4 Summary of Literature Review

The literature shows that factor models can organise the study of cross-sectional equity returns. Recent studies support the use of market, size, value, momentum, and liquidity characteristics. The literature also shows that emerging markets can produce different factor results from developed markets.

Liquidity is relevant to the Nigerian equity market because trading conditions can affect both return measurement and portfolio implementation. Regime-switching research supports the use of Hidden Markov Models to examine changes in market return and volatility. Machine learning research supports disciplined prediction and validation, but it also creates a need for controls against overfitting and false discoveries.

The review therefore supports a system with five features. The system must use explicit factor definitions. It must preserve point-in-time data availability. It must include liquidity and regime analysis. It must record data and experiment versions. It must separate computation from workflow coordination.

## 2.5 Research Gaps

The reviewed studies reveal the following gaps:

1. Many factor studies focus on markets outside Nigeria. The results may not represent the data coverage, liquidity, and trading conditions of NGX equities.
2. Studies on Nigerian liquidity do not provide an integrated system for multi-factor construction, regime analysis, portfolio simulation, and experiment tracking.
3. A factor study can produce biased results if it uses financial information before its publication date. The reviewed application literature does not provide the point-in-time data workflow required by this project.
4. Factor definitions, ranking rules, and portfolio assumptions can remain difficult to reproduce when researchers use disconnected scripts or spreadsheets.
5. A factor model can hide changes in performance when it reports only an average result for the full sample. Regime-specific analysis can provide additional information about the conditions under which a factor performs.
6. Machine learning can increase flexibility, but it can also increase model complexity and the risk of overfitting. The proposed system therefore keeps the factor calculations explicit and uses statistical validation around them.
7. Existing related works do not combine a versioned NGX data pipeline and a graph-orchestrated research workflow. They also do not combine a REST API and a web dashboard in one academic research system.

The proposed system addresses these gaps by providing an integrated research system for NGX equities. It combines data validation, point-in-time alignment, five-factor construction, statistical tests, regime estimation, portfolio backtesting, and experiment persistence.

## REFERENCES

Abdullahi, I. B., & Fakunmoju, S. K. (2019). Market liquidity and stock return in the Nigerian Stock Exchange market. *Binus Business Review, 10*(2), 87-94. https://doi.org/10.21512/bbr.v10i2.5588

Confalonieri, R., Kutz, O., Calvanese, D., Alonso, J. M., Zhou, S. M., & Daga, E. (2024). Data journeys: Explaining AI workflows through abstraction. *Semantic Web, 15, 1057-1083. https://doi.org/10.3233/SW-233407

Fama, E. F., & French, K. R. (2015). A five-factor asset pricing model. *Journal of Financial Economics, 116*(1), 1-22. https://doi.org/10.1016/j.jfineco.2014.10.010

Fama, E. F., & French, K. R. (2017). International tests of a five-factor asset pricing model. *Journal of Financial Economics, 123*(3), 441-463. https://doi.org/10.1016/j.jfineco.2016.11.004

Foye, J. (2018). A comprehensive test of the Fama-French five-factor model in emerging markets. *Emerging Markets Review, 37*, 199-222. https://doi.org/10.1016/j.ememar.2018.09.002

Gu, S., Kelly, B., & Xiu, D. (2020). Empirical asset pricing via machine learning. *The Review of Financial Studies, 33*(5), 2223-2273. https://doi.org/10.1093/rfs/hhaa009

Harvey, C. R., Liu, Y., & Zhu, H. (2016). ... and the cross-section of expected returns. *The Review of Financial Studies, 29*(1), 5-68. https://doi.org/10.1093/rfs/hhv059

Hou, K., Xue, C., & Zhang, L. (2015). Digesting anomalies: An investment approach. *The Review of Financial Studies, 28*(3), 650-705. https://doi.org/10.1093/rfs/hhu068

Kundu, S., Sahoo, D., Li, V., Rabowsky, J., & Varshney, A. (2025). A multi-agent framework for quantitative finance: An application to portfolio management analytics. *Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing: Industry Track*, 812-824. https://aclanthology.org/2025.emnlp-industry.55/

McLean, R. D., & Pontiff, J. (2016). Does academic research destroy stock return predictability? *The Journal of Finance, 71*(1), 5-32. https://doi.org/10.1111/jofi.12365

Nystrup, P., Kolm, P. N., & Stenfors, A. (2020). Regime-switching factor investing with hidden Markov models. *Journal of Risk and Financial Management, 13*(12), 311. https://doi.org/10.3390/jrfm13120311

Zaremba, A. (2015). Country selection strategies based on value, size and momentum. *Investment Analysts Journal, 44*(3), 171-198. https://doi.org/10.1080/10293523.2015.1060747
