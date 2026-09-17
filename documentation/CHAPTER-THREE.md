# CHAPTER THREE

# RESEARCH METHODOLOGY AND SYSTEM DESIGN

## 3.0 Introduction

This chapter presents the software engineering methodology used to design and implement the graph-orchestrated multi-agent system for liquidity-augmented, regime-aware multi-factor analysis of Nigerian Exchange equities. An iterative and incremental software development methodology was adopted. The system was divided into functional increments instead of being developed as one complete unit. Each increment passed through requirements analysis, system design, implementation, testing, and review before integration with the next increment.

The methodology was suitable because the system contains several dependent modules. The database structure and data-preparation functions had to exist before factor values could be calculated. Factor outputs had to exist before regime analysis and stock ranking could be performed. Portfolio construction depended on the ranking results, while historical backtesting depended on portfolio weights and later returns. The web interface and REST API also depended on stable analytical outputs. Incremental development allowed each dependency to be implemented and tested before the next module used it.

Brhel et al. (2015) identify iterative and incremental design and development as a core principle of user-centred Agile software development. Campanelli and Parreiras (2015) also report that Agile methods can be tailored to suit a project's objectives and development environment. These findings support the adapted methodology used for this study. The project applied short implementation cycles, continuous testing, and revision without claiming to follow every practice of a formal Scrum framework.

Development was organised into five increments:

1. The first increment defined the software requirements and established the project structure, configuration, web application, FastAPI service, and health endpoints.
2. The second increment implemented the research database, schema migrations, dataset versioning, data validation, ingestion structures, and point-in-time fundamental alignment.
3. The third increment implemented the Market, Size, Value, Momentum, and Liquidity factor modules. It also added statistical validation and Hidden Markov Model regime estimation.
4. The fourth increment added security ranking, portfolio construction, transaction costs, historical backtesting, benchmark comparison, LangGraph orchestration, and research API endpoints.
5. The fifth increment integrated the landing page and research dashboards, improved responsive behaviour, connected production configuration, strengthened automated testing, and prepared the project documentation.

Testing and review occurred within every increment. A defect found during integration was returned to the relevant requirement, design decision, or module for correction. This cycle continued until the increment satisfied its acceptance conditions and could be connected to the rest of the system.

**Figure 3.1: Iterative and Incremental Software Development Process Used for the System**

## 3.1 Requirements Elicitation

The study derived requirements from the research question, the factor definitions, the proposed NGX data request, the system architecture, and the need for reproducible research. The study grouped the requirements into functional and non-functional requirements.

The functional requirements define what the system must do. The system must load and inspect source data. It must align fundamental observations and calculate factor values. It must estimate regimes, construct portfolios, run backtests, store experiment information, and display results.

The non-functional requirements define how the system must operate. The system must protect the database connection, preserve source provenance, reject invalid data, use deterministic calculations where possible, and expose clear workflow status. These requirements support data integrity and repeatable research.

**Table 3.1: Analysed software requirements**

| ID | Software requirement | Acceptance condition |
| --- | --- | --- |
| FR-01 | Store companies, security identifiers, prices, fundamentals, corporate actions, benchmarks, and risk-free observations. | Each valid record is stored in the required table with a valid key. |
| FR-02 | Register a dataset version and its source metadata. | A dataset version contains a name, source, coverage period, and manifest. |
| FR-03 | Read and normalise NGX source files. | The system converts supported source files to the canonical column names. |
| FR-04 | Validate dates, prices, trading values, duplicates, and required columns. | Invalid records produce a validation error before database insertion. |
| FR-05 | Align fundamentals by information availability. | Each fundamental record has an effective date and effective-date source. |
| FR-06 | Calculate Market, Size, Value, Momentum, and Liquidity factors. | Each factor receives valid input data and returns a dated factor series. |
| FR-07 | Calculate factor statistics and regression diagnostics. | The system returns observations, mean return, volatility, Sharpe ratio, Newey-West result, and confidence interval fields where data permits. |
| FR-08 | Estimate market regimes with a Gaussian Hidden Markov Model. | The system stores state assignments, state probabilities, transition information, and state summaries. |
| FR-09 | Rank securities and construct a configurable portfolio. | The system selects eligible securities, applies the portfolio rule, and records weights. |
| FR-10 | Backtest the portfolio and compare it with a benchmark. | The system returns periodic returns, cumulative return, drawdown, risk measures, and benchmark comparison. |
| FR-11 | Orchestrate the research stages as a directed workflow. | The workflow executes dependent stages in order and reports node status. |
| FR-12 | Provide REST endpoints and web views for research results. | A client can request dashboard, factor, regime, portfolio, and experiment data. |
| NFR-01 | Preserve reproducibility. | Dataset version, experiment configuration, random seed, and calculation settings are stored. |
| NFR-02 | Prevent look-ahead bias. | A fundamental observation is not available before its effective date. |
| NFR-03 | Protect sensitive configuration and database access. | Production credentials remain in environment configuration and are not stored in source code. |
| NFR-04 | Preserve data integrity. | Database constraints reject invalid prices, negative trading values, and invalid shares outstanding values. |
| NFR-05 | Support failure reporting. | A failed workflow stage returns a clear error and does not present incomplete results as complete. |
| NFR-06 | Support later data-source changes. | A source adapter can map a new file format to the canonical schema without changing factor formulas. |

## 3.2 System Design

The proposed system is a web-based research application with presentation, application, analytical, orchestration, and data-management responsibilities. The separation of these responsibilities allows the researcher to inspect stored results through the web interface without placing financial calculations inside the page components.

The presentation component uses Next.js and TypeScript. It provides the landing page and research views for factors, market regimes, portfolios, backtests, and experiments. The interface sends structured requests to the FastAPI service and displays the returned research results.

The application component uses FastAPI to validate requests and expose the research functions through REST endpoints. Research services translate an experiment configuration into the state required by the analytical workflow. They also manage experiment status and provide structured responses to the web application.

The analytical component uses Python modules for data preparation, point-in-time alignment, factor construction, statistical validation, regime estimation, and security ranking. Other modules handle portfolio construction, transaction-cost adjustment, historical backtesting, and benchmark comparison. Each module has a defined input and output so that it can be tested separately.

LangGraph coordinates the analytical modules as an ordered set of specialised graph nodes. A node receives the current experiment state, performs one research task, and returns an updated state. The next node uses that state as its input. This design provides a traceable execution path from the selected dataset to the final experiment results.

PostgreSQL provides persistent storage for companies, historical identifiers, prices, fundamentals, corporate actions, benchmark observations, risk-free observations, dataset versions, and experiment records. The data-preparation modules read the required observations from the database, while the workflow stores experiment metadata and completed results. External NGX and supporting data sources enter the system through the ingestion and validation process before analytical modules can use them.

### 3.2.1 Use Case Diagram

The main actor is the researcher. The researcher configures an experiment, selects the date range, selects the factors, reviews the data status, starts the workflow, and examines the results. The system performs data validation, factor construction, statistical validation, regime analysis, portfolio construction, and backtesting.

The database and data sources support the system but do not act as human users. The workflow controls the order of computational activities.

**Figure 3.2: Use Case Diagram for the Research System**

### 3.2.2 Data Model

The data model separates issuer identity, security identifiers, observations, source versions, and experiments.

The companies table stores the issuer record. The security_identifiers table stores ticker and ISIN validity periods. The price_observations table stores daily security data with a composite key of company and trading date. The fundamental_observations table stores fiscal information and its publication and effective dates. The corporate_actions table stores events that can affect price interpretation.

The benchmark_observations table stores NGX All Share and other benchmark observations. The risk_free_observations table stores dated rates by tenor. The dataset_versions table stores source and coverage metadata. The experiments table stores research configuration and a logical reference to the dataset version used by the experiment.

The model uses constraints and indexes to protect data quality. Price records cannot contain a non-positive close price. Trading volume and trading value cannot be negative. Fundamental records cannot contain non-positive shares outstanding. The model also prevents duplicate daily observations for one company.

**Figure 3.3: Core Data Model**

### 3.2.3 Activity Diagram

The research activity starts when the researcher selects an experiment configuration. The system loads and inspects the selected dataset. If validation fails, the system records the errors and marks the experiment as failed. If validation succeeds, the system aligns fundamentals by their effective dates and constructs the five factors.

The workflow calculates factor statistics before it estimates market regimes. It analyses factor performance by regime. It ranks eligible securities and constructs the portfolio. It performs the backtest, compares results with the NGX benchmark, and stores the experiment.

**Figure 3.4: Research Workflow Activity Diagram**

### 3.2.4 Sequence Diagram

The proposed production sequence starts when the researcher sends an experiment request through the web application. The FastAPI service stores the configuration, marks the experiment as running, and invokes the workflow. Each workflow node receives the state produced by the preceding node. The workflow stores the final results and returns them to the API. The API then returns the completed experiment to the web application.

**Figure 3.5: Sequence Diagram**

## 3.3 System Implementation

Implementation follows the requirements and the stated workflow. Each major function is kept in a separate module. Data ingestion, validation, alignment, factor construction, statistical analysis, regime estimation, portfolio construction, and backtesting do not depend on the web page layout.

The implementation also preserves the difference between raw data and processed research data. Raw source extracts remain in the data directory and are not committed when the source terms restrict redistribution. The processed dataset receives a version and a manifest before it is used by an experiment.

### 3.3.1 Front-end Tools

The presentation tier uses Next.js and TypeScript. The landing page introduces the system and directs the researcher to the research console. The console provides views for the dashboard, factors, regimes, portfolio, and experiments.

The web interface uses responsive CSS and reusable components. The layout supports desktop and mobile screens. The header remains visible during page scrolling. The mobile view provides a menu button for navigation. The research console uses a sidebar and a top header to separate navigation from the active research view.

Charts and tables present factor history, factor statistics, regime timelines, portfolio holdings, cumulative performance, drawdown, and benchmark comparison. The interface displays a dataset version and experiment status with the result so that the researcher can identify the source of the displayed values.

### 3.3.2 Back-end Tools

The application tier uses Python 3.12 and FastAPI. Pydantic defines request and response models. Pydantic Settings reads environment configuration such as the database URL, frontend URL, bootstrap iterations, regime count, and reporting lag.

SQLAlchemy provides database access. Alembic manages schema migrations. Pandas and NumPy provide tabular and numerical operations. SciPy and Statsmodels support statistical calculations. Scikit-learn and hmmlearn support modelling tasks, including Gaussian Hidden Markov Model estimation. LangGraph coordinates the dependent research nodes. HTTPX supports external HTTP requests when a data source or supporting service requires them.

The quantitative engine remains deterministic when the method permits deterministic computation. Bootstrap calculations use a stored random seed. The experiment configuration stores the bootstrap iteration count, Newey-West threshold, regime count, portfolio size, transaction cost, and reporting-lag policy.

### 3.3.3 Database

PostgreSQL stores the research data and experiment information. The production database is hosted on Neon. The application connects through the DATABASE_URL environment variable. The value is not stored in source code.

Alembic creates and updates the schema. The first migration creates the following tables:

- companies
- security_identifiers
- price_observations
- fundamental_observations
- corporate_actions
- benchmark_observations
- risk_free_observations
- dataset_versions
- experiments

The database uses foreign keys to connect observations to companies and dataset versions. Composite keys prevent duplicate price, benchmark, and risk-free observations. Indexes support queries by ticker, company, sector, trading date, effective date, and dataset version.

The dataset_versions table supports reproducibility. It stores the source name, coverage period, manifest, and version identifier. An experiment stores the dataset version used in the research run. This record prevents a later data update from silently changing an earlier experiment.

### 3.3.4 Data Ingestion and Validation

The data pipeline accepts source extracts from NGX and other documented sources. The ingestion layer reads supported CSV files and returns a tabular data frame. The cleaning layer normalises column names and converts date fields to the canonical format.

The data rules examine required columns, date values, duplicate keys, positive close prices, non-negative trading values, and required fundamental fields. The audit process reports missing values. It does not fill them without a stated method.

The pipeline uses these canonical input structures:

prices:

ticker, trading_date, close, volume, trading_value

fundamentals:

ticker, fiscal_period, publication_date, book_equity, shares_outstanding

benchmark:

benchmark_code, trading_date, close

risk_free:

observation_date, tenor, annualized_rate

The importer first creates or updates company and security-identifier records. It then inserts observations with the related dataset version. A repeated import must update the same natural key or report a conflict. It must not create duplicate observations.

### 3.3.5 Point-in-Time Alignment

The system does not treat the fiscal period as the information availability date. It uses publication_date when NGX or the source document provides that date.

When publication_date is not available, the system applies the configured reporting lag. The default configuration uses 90 days. The system stores either ACTUAL_PUBLICATION_DATE or FIXED_LAG_ESTIMATE in effective_date_source.

The value factor uses the latest fundamental observation for which effective_from is not later than the portfolio formation date. This rule prevents the backtest from using financial information that was not available when the simulated decision occurred.

### 3.3.6 Factor Construction

The factor engine exposes a common interface for factor modules. Each factor validates its required inputs, calculates the factor values, and returns a description of the calculation.

The Market factor is the market return above the risk-free rate:

~~~text
MKT_t = R_m,t - R_f,t
~~~

The Size factor uses market capitalisation:

~~~text
Market Capitalisation = Closing Price x Shares Outstanding
~~~

The Size factor compares small and large securities.

The Value factor uses book-to-market:

~~~text
Book-to-Market = Book Equity / Market Capitalisation
~~~

The Value factor uses only fundamental observations that satisfy the point-in-time rule.

The Momentum factor uses the 12-1 month formation rule. The calculation uses the cumulative return from month t-12 through month t-2. It excludes month t-1.

The Liquidity factor uses trading value and return movement. The system supports an Amihud-style measure:

~~~text
ILLIQ_i = average( |daily return_i| / daily trading value_i )
~~~

The factor configuration records the chosen ranking, breakpoint, and portfolio rules. The engine does not replace missing values with zero unless the selected method states that rule.

### 3.3.7 Statistical Validation

The statistical engine calculates descriptive and inferential metrics for factor returns. The report includes observation count, mean return, annualised return, standard deviation, annualised volatility, Sharpe ratio, maximum drawdown, Newey-West adjusted t-statistic, and bootstrap confidence interval. The system reports a metric only when the input data supports its calculation.

The statistical engine uses Newey-West adjusted errors. Return observations can exhibit changing variance and serial dependence. The selected threshold is stored in the experiment configuration. A threshold is a reporting rule. It does not by itself prove that a factor is economically useful.

The bootstrap module resamples the available factor-return observations. It records the iteration count, random seed, lower confidence bound, and upper confidence bound. Bootstrap results are reported as estimates from the selected sample. They are not presented as guarantees of future performance.

The regression module estimates market sensitivity and factor relationships when the required observations are available. It stores the coefficient, standard error, t-statistic, p-value, and R-squared fields returned by the calculation.

### 3.3.8 Regime, Portfolio, and Backtest Modules

The regime module uses a Gaussian Hidden Markov Model. Its default features are monthly NGX market return and rolling market volatility. The default model contains three states. The state labels are assigned after estimation from the estimated return, volatility, persistence, and transition values.

The portfolio module standardises the Size, Value, Momentum, and Liquidity signals. It combines the signals using the configured weights. The default composite score gives equal weight to the four ranking signals. The Market factor supports market-risk estimation and benchmark modelling.

The portfolio engine selects the highest-ranked eligible securities. The default portfolio is long-only and equal-weighted. The default portfolio size is ten securities. The strategy rebalances monthly.

The backtest engine applies the portfolio weights to subsequent returns. It accounts for portfolio turnover and an estimated transaction cost. It returns periodic returns, cumulative performance, volatility, Sharpe ratio, maximum drawdown, and benchmark comparison.

### 3.3.9 Workflow and API

LangGraph represents the research process as connected nodes. Each node has a defined task. The nodes prepare the dataset, align fundamentals, calculate factors, and inspect statistics. Other nodes estimate regimes, rank securities, construct the portfolio, run the backtest, compare the benchmark, and save the result.

FastAPI exposes the workflow through REST endpoints under /api/v1. The main resources are companies, factors, regimes, experiments, and portfolios. The API returns structured JSON so that the Next.js application can display the results.

The API does not place trades. It provides research data, workflow status, factor results, regime results, portfolio results, and experiment metadata. This boundary keeps the academic research system separate from a live brokerage system.

## 3.4 System Testing

Testing uses unit, component, integration, data-quality, and efficiency controls. Each control maps to a requirement in Table 3.1. The tests use controlled data for calculations. They do not represent NGX market results.

The testing process covers four levels. Unit tests examine individual formulas and validation rules. Component tests examine connected modules. Integration tests examine data flow across the API, workflow, quantitative engine, and database. Efficiency tests measure execution time in the development environment.

The production database is not used for destructive test setup. Test data uses a separate database or an isolated test configuration. Licensed NGX source data is not copied into the test suite.

### 3.4.1 Unit Testing

Unit tests inspect:

- Date parsing and canonical column names.
- Price validation.
- Duplicate detection.
- Point-in-time fundamental selection.
- Market capitalisation.
- Book-to-market calculation.
- 12-1 momentum calculation.
- Amihud-style liquidity calculation.
- Factor z-score calculation.
- Newey-West result fields.
- Bootstrap reproducibility with a fixed seed.
- Portfolio weight calculation.
- Maximum drawdown calculation.

A unit test passes when the returned value equals a manually calculated expected value or when invalid input produces the expected error.

### 3.4.2 Component Testing

Component tests connect related functions. A data component test loads a source frame, normalises it, validates it, and returns a canonical frame. A factor component test reads the prepared data and calculates one factor. A regime component test receives market features and returns states and state summaries.

A portfolio component test receives factor scores, selects the configured number of securities, assigns weights, and calculates turnover. A backtest component test applies the weights to later returns and deducts the configured transaction cost.

### 3.4.3 Integration Testing

Integration tests follow an experiment from configuration to stored results. The test creates an experiment configuration, loads a controlled dataset version, runs the workflow, and validates the result fields.

The integration tests also validate that:

- The API accepts a valid experiment request.
- The workflow executes nodes in the required order.
- A failed validation stage prevents later calculation stages.
- Fundamental observations use the effective date rule.
- Results include the dataset version.
- The portfolio output contains holdings and weights.
- The benchmark comparison uses the selected benchmark.
- Repeating an import does not create duplicate observations.

### 3.4.4 Efficiency Testing

Efficiency tests measure data-loading time, factor-calculation time, workflow time, and API response time. The measurements use the local development environment and the test dataset size. They do not represent guaranteed production performance.

The test records the number of rows, number of securities, date range, execution time, and memory conditions where available. The researcher uses these measurements to identify slow stages before loading the full NGX dataset.

**Table 3.2: Testing metrics and acceptance basis**

| Metric | What was inspected | Reason for selection |
| --- | --- | --- |
| Pass or fail status | Actual result against expected result | Indicates whether the requirement behaves correctly. |
| Functional pass rate | Passed tests divided by executed tests | Summarises functional correctness. |
| Data validation rate | Valid and rejected records | Indicates whether unsafe input is detected. |
| Requirement coverage | Requirements linked to executed tests | Indicates whether important functions are tested. |
| Calculation accuracy | Computed result against a manual result | Validates financial and statistical formulas. |
| Reproducibility | Same configuration and seed produce the same result | Validates repeatability of deterministic calculations. |
| Point-in-time control | Fundamental records selected by effective date | Validates protection against look-ahead bias. |
| Execution time | Time for a stage and complete workflow | Indicates efficiency in the test environment. |
| API response time | Time for selected API requests | Measures service responsiveness. |
| Data integrity | Valid links among source, dataset, experiment, and result | Validates research traceability. |

## 3.5 Summary

This chapter described the methodology and system design for the proposed system. The requirements came from the research question, the factor model, NGX data needs, and reproducibility requirements. The system uses a three-tier architecture. It contains a Next.js interface, a FastAPI application tier, a Python quantitative engine, LangGraph workflow orchestration, and a PostgreSQL research database.

The design includes a versioned data model, point-in-time fundamental alignment, and five factor modules. It also includes statistical validation, Hidden Markov Model regime analysis, portfolio construction, benchmark comparison, and historical backtesting. The testing plan covers unit, component, integration, data-quality, reproducibility, and efficiency validation.

## REFERENCES

Abdullahi, I. B., & Fakunmoju, S. K. (2019). Market liquidity and stock return in the Nigerian Stock Exchange market. Binus Business Review, 10(2), 87–94. https://doi.org/10.21512/bbr.v10i2.5588

Alaba, J. S., Ahmed, Y., Malik-Abdulmajeed, K. M., & Hussain, U. (2024). Stock market liquidity and stock market performance in Nigeria: Evidence from the Nigerian Exchange Limited. iRASD Journal of Management, 6(2), 78–89. https://doi.org/10.52131/jom.2024.0602.0124 (Open access)

Confalonieri, R., Kutz, O., Calvanese, D., Alonso, J. M., Zhou, S. M., & Daga, E. (2024). Data journeys: Explaining AI workflows through abstraction. Semantic Web, 15, 1057–1083. https://doi.org/10.3233/SW-233407

Fama, E. F., & French, K. R. (2015). A five-factor asset pricing model. Journal of Financial Economics, 116(1), 1–22. https://doi.org/10.1016/j.jfineco.2014.10.010

Fama, E. F., & French, K. R. (2017). International tests of a five-factor asset pricing model. Journal of Financial Economics, 123(3), 441–463. https://doi.org/10.1016/j.jfineco.2016.11.004

Foye, J. (2018). A comprehensive test of the Fama-French five-factor model in emerging markets. Emerging Markets Review, 37, 199–222. https://doi.org/10.1016/j.ememar.2018.09.002

Gu, S., Kelly, B., & Xiu, D. (2020). Empirical asset pricing via machine learning. The Review of Financial Studies, 33(5), 2223–2273. https://doi.org/10.1093/rfs/hhaa009

Harvey, C. R., Liu, Y., & Zhu, H. (2016). ...and the cross-section of expected returns. The Review of Financial Studies, 29(1), 5–68. https://doi.org/10.1093/rfs/hhv059

Hou, K., Xue, C., & Zhang, L. (2015). Digesting anomalies: An investment approach. The Review of Financial Studies, 28(3), 650–705. https://doi.org/10.1093/rfs/hhu068

Irejeh, E. M., & Aninoritse, L. E. (2024). Fama and French three factor model. European Journal of Accounting, Auditing and Finance Research, 12(5), 17–30. https://eajournals.org/ejaafr/wp-content/uploads/sites/16/2024/04/Fama-and-French-Three-Factor-Model.pdf (Open access)

Kundu, S., Sahoo, D., Li, V., Rabowsky, J., & Varshney, A. (2025). A multi-agent framework for quantitative finance: An application to portfolio management analytics. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing: Industry Track, 812–824. https://aclanthology.org/2025.emnlp-industry.55/

McLean, R. D., & Pontiff, J. (2016). Does academic research destroy stock return predictability? The Journal of Finance, 71(1), 5–32. https://doi.org/10.1111/jofi.12365

Nguyen, P., & Pham, T. (2026). Toward reliable evaluation of LLM-based financial multi-agent systems: Taxonomy, coordination primacy, and cost awareness. arXiv. https://arxiv.org/abs/2603.27539 (Open access)

Xiao, Y., et al. (2025). TradingAgents: Multi-agents LLM financial trading framework. Proceedings of the 39th AAAI Conference on Artificial Intelligence. arXiv. https://arxiv.org/abs/2412.20138 (Open access)

Yahaya, A., John, S. A., Adegoroye, A., & Olorunfemi, O. A. (2023). Stock market liquidity and volatility on the Nigerian Exchange Limited (NGX). World Journal of Advanced Research and Reviews, 20(3), 147–156. https://doi.org/10.30574/wjarr.2023.20.3.2333 (Open access)

Nystrup, P., Kolm, P. N., & Stenfors, A. (2020). Regime-switching factor investing with hidden Markov models. Journal of Risk and Financial Management, 13(12), 311. https://doi.org/10.3390/jrfm13120311

Zaremba, A. (2015). Country selection strategies based on value, size and momentum. Investment Analysts Journal, 44(3), 171–198. https://doi.org/10.1080/10293523.2015.1060747
