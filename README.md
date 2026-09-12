# NGX Multi-Factor Research Platform

A quantitative research platform for constructing, validating, analysing, and backtesting a **liquidity-augmented, regime-aware multi-factor model for equities listed on the Nigerian Exchange (NGX)**.

The platform combines financial-data engineering, deterministic quantitative analysis, statistical validation, market-regime modelling, portfolio simulation, and graph-based workflow orchestration in a single reproducible research system.

The project implements the software component of the academic research:

> **Graph-Orchestrated Multi-Agent Construction and Validation of a Liquidity-Augmented, Regime-Aware Multi-Factor Model for Nigerian Exchange Equities**

---

# 1. Project Overview

The NGX Multi-Factor Research Platform is designed to investigate whether systematic equity factors can explain and potentially improve the analysis of stock returns on the Nigerian Exchange.

Rather than analysing stocks using a single signal, the system combines several financial characteristics into a structured multi-factor research pipeline.

The implemented factors are:

1. Market
2. Size
3. Value
4. Momentum
5. Liquidity

The system collects and prepares NGX market and fundamental data, constructs these factors, validates their statistical behaviour, identifies different market regimes using a Hidden Markov Model, ranks eligible NGX stocks, creates a simulated long-only portfolio, backtests the portfolio, and compares the result with selected market benchmarks.

The complete research process is exposed through a web application consisting of:

* a Next.js frontend
* a FastAPI backend
* a PostgreSQL research database
* a deterministic Python quantitative engine
* LangGraph workflow orchestration

---

# 2. Core Research Question

The system is built around the following research question:

> Can a graph-orchestrated quantitative research system construct and independently validate a liquidity-augmented, regime-aware multi-factor model for Nigerian Exchange equities?

The software provides the empirical infrastructure required to answer this question using historical NGX data.

---

# 3. Research Model

The platform implements five principal equity factors.

| Factor    | Description                                                                  |
| --------- | ---------------------------------------------------------------------------- |
| Market    | Captures systematic exposure to movements in the Nigerian equity market      |
| Size      | Measures return differences between smaller and larger companies             |
| Value     | Measures return differences between relatively cheap and expensive companies |
| Momentum  | Measures persistence in medium-term historical stock performance             |
| Liquidity | Measures the relationship between trading liquidity and stock returns        |

These factor signals are used both for academic factor-return analysis and for ranking individual equities during portfolio construction.

---

# 4. Main System Capabilities

The application provides the following functionality:

* NGX company and security management
* historical market-data storage
* fundamental-data storage
* point-in-time financial-data alignment
* market-return calculation
* market-capitalisation calculation
* five-factor construction
* Newey-West statistical validation
* bootstrap confidence estimation
* Hidden Markov Model regime detection
* regime-specific factor analysis
* stock cross-sectional scoring
* portfolio construction
* monthly portfolio rebalancing
* historical backtesting
* transaction-cost adjustment
* NGX benchmark comparison
* experiment persistence
* graph-based workflow execution
* research-result visualisation

---

# 5. Technology Stack

## Frontend

The frontend is implemented with:

* Next.js
* TypeScript
* Tailwind CSS
* Recharts
* TanStack Query
* Zustand where client-side state is required

Package manager:

```text
pnpm
```

Hosting:

```text
Vercel
```

---

## Backend

The backend is implemented with:

* Python 3.12
* FastAPI
* Pydantic
* Pydantic Settings
* SQLAlchemy
* Alembic
* Pandas
* NumPy
* SciPy
* Statsmodels
* scikit-learn
* hmmlearn
* LangGraph
* HTTPX

Python package and environment manager:

```text
uv
```

Hosting:

```text
Render
```

---

## Database

The application uses:

```text
PostgreSQL
```

hosted on:

```text
Neon
```

The database stores:

* NGX companies
* market prices
* trading activity
* historical fundamentals
* experiments
* factor observations
* validation metrics
* regime classifications
* portfolio results
* execution metadata

---

# 6. System Architecture

```mermaid
flowchart TB

    USER[Researcher / Analyst]

    subgraph FRONTEND["Next.js Frontend - Vercel"]
        DASH[Research Dashboard]
        FACTOR_UI[Factor Analytics]
        REGIME_UI[Regime Analytics]
        PORTFOLIO_UI[Portfolio Analytics]
        EXPERIMENT_UI[Experiment Manager]
    end

    subgraph BACKEND["FastAPI Backend - Render"]
        API[REST API]
        SERVICES[Application Services]
        DATA_ENGINE[Data Engine]
        FACTOR_ENGINE[Factor Engine]
        QUANT_ENGINE[Statistical Engine]
        REGIME_ENGINE[Regime Engine]
        PORT_ENGINE[Portfolio Engine]
        BACKTEST_ENGINE[Backtesting Engine]
        GRAPH[LangGraph Orchestrator]
    end

    subgraph FACTORS["Factor Modules"]
        MARKET[Market]
        SIZE[Size]
        VALUE[Value]
        MOM[Momentum]
        LIQ[Liquidity]
    end

    DB[(Neon PostgreSQL)]

    subgraph SOURCES["Research Data Sources"]
        PRICES[NGX Price Data]
        FUNDAMENTALS[Company Fundamentals]
        INDEX[NGX Market Index]
        RISKFREE[Risk-Free Rate Data]
    end

    USER --> FRONTEND
    FRONTEND --> API

    API --> SERVICES

    SERVICES --> DATA_ENGINE
    SERVICES --> GRAPH
    SERVICES --> BACKTEST_ENGINE

    GRAPH --> FACTOR_ENGINE
    GRAPH --> QUANT_ENGINE
    GRAPH --> REGIME_ENGINE
    GRAPH --> PORT_ENGINE
    GRAPH --> BACKTEST_ENGINE

    FACTOR_ENGINE --> MARKET
    FACTOR_ENGINE --> SIZE
    FACTOR_ENGINE --> VALUE
    FACTOR_ENGINE --> MOM
    FACTOR_ENGINE --> LIQ

    SOURCES --> DATA_ENGINE

    DATA_ENGINE --> DB
    FACTOR_ENGINE --> DB
    QUANT_ENGINE --> DB
    REGIME_ENGINE --> DB
    PORT_ENGINE --> DB
    BACKTEST_ENGINE --> DB
    GRAPH --> DB

    DB --> SERVICES
```

---

# 7. Research Workflow

Each experiment moves through a fixed quantitative research pipeline.

```mermaid
flowchart TD

    START([Start Experiment])

    CONFIG[Load Experiment Configuration]

    LOAD[Load Research Dataset]

    VALIDATE_DATA[Validate Dataset]

    ALIGN[Point-in-Time Alignment]

    MARKET[Market Factor]
    SIZE[Size Factor]
    VALUE[Value Factor]
    MOM[Momentum Factor]
    LIQ[Liquidity Factor]

    SYNC[Combine Factor Outputs]

    STATS[Statistical Validation]

    HMM[Estimate Market Regimes]

    REGIME_ANALYSIS[Analyse Factors by Regime]

    SCORE[Calculate Stock Scores]

    PORTFOLIO[Construct Portfolio]

    BACKTEST[Run Historical Backtest]

    BENCHMARK[Compare with Benchmarks]

    SAVE[Persist Experiment]

    END([Complete])

    START --> CONFIG
    CONFIG --> LOAD
    LOAD --> VALIDATE_DATA
    VALIDATE_DATA --> ALIGN

    ALIGN --> MARKET
    ALIGN --> SIZE
    ALIGN --> VALUE
    ALIGN --> MOM
    ALIGN --> LIQ

    MARKET --> SYNC
    SIZE --> SYNC
    VALUE --> SYNC
    MOM --> SYNC
    LIQ --> SYNC

    SYNC --> STATS
    STATS --> HMM
    HMM --> REGIME_ANALYSIS
    REGIME_ANALYSIS --> SCORE
    SCORE --> PORTFOLIO
    PORTFOLIO --> BACKTEST
    BACKTEST --> BENCHMARK
    BENCHMARK --> SAVE
    SAVE --> END
```

---

# 8. Research Universe

The application maintains a configurable universe of NGX-listed equities.

Each company record contains:

* ticker
* company name
* sector
* listing status
* listing date where available
* delisting date where applicable

A security becomes eligible for an experiment only when the required research inputs are available.

Typical eligibility checks include:

* minimum price-history coverage
* minimum trading frequency
* known shares outstanding
* valid book-equity observations
* sufficient data for momentum formation
* sufficient observations for liquidity calculations

The experiment engine dynamically determines the eligible universe for each research date.

---

# 9. Research Period

Experiments are configurable by date.

The primary historical study is designed around:

```text
2019-01-01
to
2025-12-31
```

Each experiment stores its own:

* start date
* end date
* eligible universe
* factor configuration
* validation configuration
* portfolio configuration
* regime configuration

---

# 10. Data Model

The research pipeline uses four main classes of input data.

## Market Prices

Daily security observations include:

```text
ticker
trading_date
close
volume
trading_value
```

Additional fields may include:

```text
open
high
low
adjusted_close
```

where available.

---

## Company Fundamentals

Required fundamental observations include:

```text
fiscal_period
publication_date
book_equity
shares_outstanding
```

Additional fundamentals can be stored for future research extensions.

---

## Market Benchmark

The application stores NGX market-index observations for:

* benchmark comparison
* market-factor calculation
* beta estimation
* regime modelling

---

## Risk-Free Rate

Risk-free observations are used when calculating:

* excess market returns
* excess portfolio returns
* CAPM regressions
* Sharpe ratios where applicable

---

# 11. Point-in-Time Data Alignment

A central component of the system is its point-in-time data engine.

Financial statements are not considered available on their fiscal-period end date.

For example:

```text
Fiscal Period:
31 December 2023

Publication Date:
28 March 2024
```

The 2023 fundamental information becomes available only from:

```text
28 March 2024
```

The point-in-time engine therefore uses:

```text
effective_from = publication_date
```

for fundamental observations.

Where an exact publication date is unavailable, the dataset can explicitly use a configured reporting lag such as:

```text
effective_from =
fiscal_period_end + 90 days
```

The database records the source of the effective date.

Possible values include:

```text
ACTUAL_PUBLICATION_DATE
FIXED_LAG_ESTIMATE
```

This ensures that all backtests use only information that would have been available at the simulated research date.

---

# 12. Data Processing Pipeline

```mermaid
flowchart LR

    RAW[Raw Research Data]

    NORMALISE[Normalise Columns]

    DATE_CHECK[Validate Dates]

    DEDUPE[Remove Duplicates]

    MISSING[Missing-Data Analysis]

    PRICE_CHECK[Price Validation]

    FUND_CHECK[Fundamental Validation]

    PIT[Point-in-Time Alignment]

    RESAMPLE[Monthly Research Dataset]

    FINAL[Validated Dataset]

    RAW --> NORMALISE
    NORMALISE --> DATE_CHECK
    DATE_CHECK --> DEDUPE
    DEDUPE --> MISSING
    MISSING --> PRICE_CHECK
    PRICE_CHECK --> FUND_CHECK
    FUND_CHECK --> PIT
    PIT --> RESAMPLE
    RESAMPLE --> FINAL
```

---

# 13. Market Factor

The Market factor measures the excess return of the equity market above the risk-free rate.

```text
MKT_t
=
R_m,t
-
R_f,t
```

Individual stock market sensitivity can be estimated through:

```text
R_i,t - R_f,t
=
alpha_i
+
beta_i(MKT_t)
+
epsilon_i,t
```

The Market module produces:

* market excess-return series
* security beta estimates
* regression alpha
* regression R²
* model diagnostics

---

# 14. Size Factor

The Size factor is based on market capitalisation.

```text
Market Capitalisation
=
Closing Price
×
Shares Outstanding
```

Stocks are ranked according to market capitalisation.

The factor-return series is constructed as:

```text
SMB
=
Small-Capitalisation Portfolio
-
Large-Capitalisation Portfolio
```

SMB represents:

```text
Small Minus Big
```

The system stores:

* company market capitalisation
* size percentile
* size classification
* SMB factor return

---

# 15. Value Factor

The Value factor uses book-to-market.

```text
Book-to-Market
=
Book Equity
/
Market Capitalisation
```

Stocks with larger book-to-market ratios are classified as relatively higher-value securities.

The factor is:

```text
HML
=
High Book-to-Market Portfolio
-
Low Book-to-Market Portfolio
```

HML represents:

```text
High Minus Low
```

The Value module uses only point-in-time-valid accounting information.

---

# 16. Momentum Factor

Momentum measures the persistence of medium-term historical returns.

The platform implements:

```text
12-1 Momentum
```

For a stock evaluated at month `t`:

```text
Momentum Score
=
Cumulative return from t-12 through t-2
```

Month `t-1` is excluded.

Stocks are ranked into winner and loser groups.

Factor return:

```text
MOM
=
Winner Portfolio
-
Loser Portfolio
```

The Momentum module stores:

* formation-period return
* stock rank
* momentum classification
* MOM factor return

---

# 17. Liquidity Factor

Liquidity is the central NGX-specific augmentation in the model.

The system supports multiple liquidity signals.

## Amihud Illiquidity

```text
ILLIQ_i
=
Average(
|R_i,d|
/
TradingValue_i,d
)
```

where `d` represents a trading day.

Larger values indicate greater price movement for a given amount of traded value and therefore lower liquidity.

---

## Share Turnover

```text
Turnover
=
Shares Traded
/
Shares Outstanding
```

Higher turnover generally indicates stronger liquidity.

---

## Liquidity Score

The portfolio engine can construct a standardised liquidity score from the available measures.

For example:

```text
Liquidity Score
=
z(Turnover)
-
z(Amihud Illiquidity)
```

The exact implementation is configurable and recorded as experiment metadata.

---

# 18. Factor Engine

Each factor is implemented as an independent Python module.

All factors implement a common interface.

```python
from abc import ABC, abstractmethod


class Factor(ABC):
    name: str

    @abstractmethod
    def calculate(self, dataset):
        ...

    @abstractmethod
    def validate_inputs(self, dataset):
        ...

    @abstractmethod
    def describe(self) -> dict:
        ...
```

The modules are located under:

```text
apps/api/app/factors/
```

---

# 19. Statistical Validation

Factor results are passed into the statistical engine.

Each factor receives a validation report containing:

* number of observations
* mean monthly return
* annualised return
* standard deviation
* annualised volatility
* Sharpe ratio
* Newey-West t-statistic
* bootstrap confidence interval
* maximum drawdown

---

# 20. Newey-West Statistics

The research platform uses heteroskedasticity and autocorrelation-consistent standard errors.

This is necessary because financial-return time series may contain:

* heteroskedasticity
* serial correlation

The validation engine computes a Newey-West adjusted t-statistic for each factor.

A configurable research threshold is stored in experiment configuration.

Example:

```text
newey_west_threshold = 2.5
```

The result is stored alongside the full statistical report.

---

# 21. Bootstrap Validation

The platform uses bootstrap resampling to estimate uncertainty in factor performance.

Default configuration:

```text
bootstrap_iterations = 10000
```

The bootstrap engine produces:

* resampled mean-return distribution
* lower confidence bound
* upper confidence bound
* empirical probability estimates
* reproducibility metadata

Random seeds are configurable and stored with the experiment.

---

# 22. Market Regime Detection

The system estimates latent NGX market states using a Gaussian Hidden Markov Model.

The regime model uses:

```text
Monthly NGX Market Return
+
Rolling Market Volatility
```

The default number of states is:

```text
3
```

The HMM estimates:

* hidden state sequence
* posterior state probabilities
* state means
* state covariance
* transition probabilities
* state persistence

---

# 23. Regime Interpretation

States are numbered statistically:

```text
State 0
State 1
State 2
```

Economic labels are assigned after model estimation.

Possible descriptions include:

* stable market
* expansionary market
* high-volatility stress market

The system does not assume a label before the statistical properties of each state are examined.

---

# 24. Regime Validation

The regime engine calculates diagnostics such as:

* number of observations in each state
* average state return
* state volatility
* average duration
* transition probability
* convergence status

The frontend displays whether the states are statistically distinguishable enough for useful interpretation.

---

# 25. Regime-Specific Factor Analysis

For every factor, the application calculates performance within each estimated regime.

Metrics include:

* mean factor return
* volatility
* Sharpe ratio
* positive-return frequency
* maximum drawdown
* t-statistic

This allows the study to investigate whether a factor remains robust under different market conditions.

---

# 26. Cross-Sectional Stock Scoring

The system converts individual factor characteristics into comparable stock-level scores.

Signals are standardised cross-sectionally.

Example:

```text
z_size
z_value
z_momentum
z_liquidity
```

The initial composite model is:

```text
Composite Score
=
0.25 × Size
+
0.25 × Value
+
0.25 × Momentum
+
0.25 × Liquidity
```

The Market factor is used primarily for market-risk estimation and benchmark modelling rather than direct ranking.

---

# 27. Portfolio Construction

The portfolio engine ranks securities by composite score.

The default portfolio is:

```text
Long-Only
```

The highest-ranked securities are selected.

Example:

```text
portfolio_size = 10
```

If ten securities are selected, equal weighting gives:

```text
weight_i = 1 / 10
```

or:

```text
10% per security
```

Portfolio size is configurable.

---

# 28. Portfolio Rebalancing

The initial strategy uses monthly rebalancing.

At each rebalance date:

```text
1. Retrieve point-in-time-valid data
2. Calculate stock factor signals
3. Standardise factor scores
4. Calculate composite score
5. Rank securities
6. Select top N
7. Assign equal weights
8. Hold until next rebalance
```

No future observations may influence the current rebalance decision.

---

# 29. Transaction Costs

The backtest supports configurable trading costs.

```text
Net Return
=
Gross Portfolio Return
-
Estimated Trading Costs
```

A simple basis-point model may initially be used.

Example:

```text
transaction_cost_bps = 50
```

Transaction costs are applied according to portfolio turnover.

---

# 30. Backtesting Engine

The backtesting engine performs historical portfolio simulation.

```mermaid
flowchart TD

    DATE[Rebalance Date]

    UNIVERSE[Build Eligible Universe]

    SIGNALS[Calculate Factor Signals]

    SCORE[Calculate Composite Scores]

    RANK[Rank Securities]

    SELECT[Select Top N]

    WEIGHT[Assign Equal Weights]

    RETURN[Observe Next Holding-Period Returns]

    COST[Apply Transaction Costs]

    STORE[Store Portfolio Result]

    NEXT[Advance to Next Rebalance]

    DATE --> UNIVERSE
    UNIVERSE --> SIGNALS
    SIGNALS --> SCORE
    SCORE --> RANK
    RANK --> SELECT
    SELECT --> WEIGHT
    WEIGHT --> RETURN
    RETURN --> COST
    COST --> STORE
    STORE --> NEXT
```

---

# 31. Backtest Outputs

Every completed backtest generates:

* periodic portfolio returns
* cumulative return
* annualised return
* CAGR
* annualised volatility
* Sharpe ratio
* Sortino ratio
* maximum drawdown
* portfolio beta
* turnover
* transaction costs
* number of holdings

---

# 32. Benchmark Models

The system compares portfolio and factor performance against four research references.

## NGX All-Share Index

The primary market-performance benchmark.

---

## CAPM

```text
R_p - R_f
=
alpha
+
beta(MKT)
+
epsilon
```

---

## NGX Three-Factor Model

```text
R_p - R_f
=
alpha
+
beta_MKT MKT
+
beta_SMB SMB
+
beta_HML HML
+
epsilon
```

---

## Proposed Model

```text
R_p - R_f
=
alpha
+
beta_MKT MKT
+
beta_SMB SMB
+
beta_HML HML
+
beta_MOM MOM
+
beta_LIQ LIQ
+
epsilon
```

The system additionally analyses these factor relationships across identified market regimes.

---

# 33. Experiment Model

Every research run is stored as an experiment.

An experiment records:

```json
{
  "name": "ngx-five-factor-baseline",
  "start_date": "2019-01-01",
  "end_date": "2025-12-31",
  "factors": [
    "market",
    "size",
    "value",
    "momentum",
    "liquidity"
  ],
  "portfolio_method": "equal_weight",
  "portfolio_size": 10,
  "rebalance_frequency": "monthly",
  "regime_count": 3,
  "bootstrap_iterations": 10000,
  "newey_west_threshold": 2.5,
  "fundamental_availability_policy": "actual_or_fixed_lag",
  "fixed_reporting_lag_days": 90
}
```

---

# 34. Reproducibility

Each experiment stores:

* dataset version
* experiment configuration
* software version
* Git commit
* factor definitions
* reporting-lag policy
* bootstrap iterations
* random seed
* model parameters
* execution timestamps

This allows previous research runs to be reproduced.

---

# 35. LangGraph Orchestration

LangGraph coordinates the research workflow after the numerical modules are invoked.

The graph does not replace the quantitative engine.

It manages the pipeline.

```mermaid
flowchart TD

    START([START])

    DATA[Prepare Dataset]

    MARKET[Market Node]
    SIZE[Size Node]
    VALUE[Value Node]
    MOM[Momentum Node]
    LIQ[Liquidity Node]

    VALIDATOR[Validation Node]

    REGIME[Regime Node]

    SCORE[Scoring Node]

    PORT[Portfolio Node]

    BACKTEST[Backtest Node]

    SAVE[Persistence Node]

    END([END])

    START --> DATA

    DATA --> MARKET
    DATA --> SIZE
    DATA --> VALUE
    DATA --> MOM
    DATA --> LIQ

    MARKET --> VALIDATOR
    SIZE --> VALIDATOR
    VALUE --> VALIDATOR
    MOM --> VALIDATOR
    LIQ --> VALIDATOR

    VALIDATOR --> REGIME
    REGIME --> SCORE
    SCORE --> PORT
    PORT --> BACKTEST
    BACKTEST --> SAVE
    SAVE --> END
```

---

# 36. Research State

The graph shares a typed research state.

```python
from typing import TypedDict


class ResearchState(TypedDict):
    experiment_id: str

    config: dict

    dataset_version: str

    eligible_universe: list[str]

    market_factor: dict | None
    size_factor: dict | None
    value_factor: dict | None
    momentum_factor: dict | None
    liquidity_factor: dict | None

    validation_results: dict | None

    regime_results: dict | None

    stock_scores: dict | None

    portfolio_results: dict | None

    backtest_results: dict | None

    errors: list[dict]
```

---

# 37. Failure Handling

Each graph node reports:

```text
pending
running
completed
failed
```

Example failure:

```json
{
  "node": "value_factor",
  "status": "failed",
  "reason": "Insufficient point-in-time book-equity observations",
  "retryable": false
}
```

Completed outputs from other nodes remain available.

---

# 38. Database Architecture

```mermaid
erDiagram

    COMPANY ||--o{ PRICE : has
    COMPANY ||--o{ FUNDAMENTAL : reports

    EXPERIMENT ||--o{ FACTOR_RESULT : produces
    EXPERIMENT ||--o{ REGIME_RESULT : produces
    EXPERIMENT ||--o{ PORTFOLIO_RESULT : produces

    COMPANY {
        uuid id PK
        string ticker
        string name
        string sector
        boolean active
        date listing_date
        date delisting_date
    }

    PRICE {
        uuid id PK
        uuid company_id FK
        date trading_date
        decimal close
        bigint volume
        decimal trading_value
    }

    FUNDAMENTAL {
        uuid id PK
        uuid company_id FK
        date fiscal_period
        date publication_date
        date effective_from
        string effective_date_source
        decimal book_equity
        bigint shares_outstanding
    }

    EXPERIMENT {
        uuid id PK
        string name
        json config
        string status
        string dataset_version
        string git_commit
        datetime created_at
        datetime completed_at
    }

    FACTOR_RESULT {
        uuid id PK
        uuid experiment_id FK
        string factor
        date observation_date
        decimal factor_return
        decimal mean_return
        decimal volatility
        decimal sharpe
        decimal newey_west_t
    }

    REGIME_RESULT {
        uuid id PK
        uuid experiment_id FK
        date observation_date
        int regime
        decimal probability
    }

    PORTFOLIO_RESULT {
        uuid id PK
        uuid experiment_id FK
        date observation_date
        decimal portfolio_return
        decimal benchmark_return
        decimal cumulative_return
        decimal turnover
    }
```

---

# 39. Backend Layering

The FastAPI backend follows a layered architecture.

```mermaid
flowchart LR

    ROUTES[API Routes]

    SERVICES[Application Services]

    GRAPH[LangGraph]

    FACTORS[Factor Modules]

    QUANT[Quantitative Engine]

    REPOSITORIES[Repositories]

    DB[(Neon PostgreSQL)]

    ROUTES --> SERVICES

    SERVICES --> GRAPH
    SERVICES --> FACTORS
    SERVICES --> QUANT

    GRAPH --> FACTORS
    GRAPH --> QUANT

    FACTORS --> REPOSITORIES
    QUANT --> REPOSITORIES

    REPOSITORIES --> DB
```

API routes are responsible for HTTP concerns.

Research logic belongs in:

```text
factors/
quant/
services/
graph/
```

---

# 40. Monorepo Structure

```text
ngx-multifactor/
│
├── apps/
│   │
│   ├── web/
│   │   ├── app/
│   │   │   ├── page.tsx
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   ├── factors/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [factor]/
│   │   │   │       └── page.tsx
│   │   │   ├── regimes/
│   │   │   │   └── page.tsx
│   │   │   ├── portfolio/
│   │   │   │   └── page.tsx
│   │   │   └── experiments/
│   │   │       ├── page.tsx
│   │   │       └── [id]/
│   │   │           └── page.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── charts/
│   │   │   ├── dashboard/
│   │   │   ├── factors/
│   │   │   ├── regimes/
│   │   │   ├── portfolio/
│   │   │   └── ui/
│   │   │
│   │   ├── hooks/
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   ├── constants.ts
│   │   │   └── utils.ts
│   │   │
│   │   ├── types/
│   │   ├── public/
│   │   ├── .env.local.example
│   │   ├── package.json
│   │   ├── pnpm-lock.yaml
│   │   └── tsconfig.json
│   │
│   └── api/
│       │
│       ├── app/
│       │   ├── main.py
│       │
│       │   ├── api/
│       │   │   ├── router.py
│       │   │   ├── health.py
│       │   │   ├── companies.py
│       │   │   ├── factors.py
│       │   │   ├── regimes.py
│       │   │   ├── portfolios.py
│       │   │   └── experiments.py
│       │
│       │   ├── factors/
│       │   │   ├── base.py
│       │   │   ├── market.py
│       │   │   ├── size.py
│       │   │   ├── value.py
│       │   │   ├── momentum.py
│       │   │   └── liquidity.py
│       │
│       │   ├── quant/
│       │   │   ├── returns.py
│       │   │   ├── statistics.py
│       │   │   ├── regressions.py
│       │   │   ├── bootstrap.py
│       │   │   ├── regimes.py
│       │   │   ├── scoring.py
│       │   │   ├── portfolio.py
│       │   │   ├── transaction_costs.py
│       │   │   └── backtest.py
│       │
│       │   ├── graph/
│       │   │   ├── graph.py
│       │   │   ├── nodes.py
│       │   │   └── state.py
│       │
│       │   ├── data/
│       │   │   ├── ingestion.py
│       │   │   ├── cleaning.py
│       │   │   ├── validation.py
│       │   │   └── alignment.py
│       │
│       │   ├── db/
│       │   │   ├── models.py
│       │   │   ├── session.py
│       │   │   └── repositories.py
│       │
│       │   ├── schemas/
│       │   ├── services/
│       │   ├── core/
│       │   │   ├── config.py
│       │   │   ├── logging.py
│       │   │   └── exceptions.py
│       │   │
│       │   └── tests/
│       │       ├── data/
│       │       ├── factors/
│       │       ├── quant/
│       │       ├── graph/
│       │       └── api/
│       │
│       ├── alembic/
│       ├── scripts/
│       │   ├── audit_data.py
│       │   ├── import_prices.py
│       │   ├── import_fundamentals.py
│       │   ├── build_dataset.py
│       │   └── run_experiment.py
│       │
│       ├── .python-version
│       ├── .env.example
│       ├── alembic.ini
│       ├── pyproject.toml
│       ├── uv.lock
│       └── Dockerfile
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
│
├── research/
│   └── notebooks/
│
├── docs/
│   ├── architecture.md
│   ├── methodology.md
│   ├── data-sources.md
│   └── data-dictionary.md
│
├── .github/
│   └── workflows/
│       ├── api.yml
│       └── web.yml
│
├── README.md
├── CONTEXT.md
├── .gitignore
└── LICENSE
```

---

# 41. REST API

Base path:

```text
/api/v1
```

---

## Health

```http
GET /api/v1/health
```

---

## Companies

```http
GET /api/v1/companies
GET /api/v1/companies/{ticker}
GET /api/v1/companies/{ticker}/prices
GET /api/v1/companies/{ticker}/fundamentals
```

---

## Factors

```http
GET /api/v1/factors
GET /api/v1/factors/{factor}
GET /api/v1/factors/{factor}/history
GET /api/v1/factors/{factor}/statistics
```

---

## Regimes

```http
GET /api/v1/regimes
GET /api/v1/regimes/timeline
GET /api/v1/regimes/statistics
```

---

## Experiments

```http
POST /api/v1/experiments
GET /api/v1/experiments
GET /api/v1/experiments/{experiment_id}
POST /api/v1/experiments/{experiment_id}/run
```

---

## Portfolio

```http
GET /api/v1/portfolios/{experiment_id}
GET /api/v1/portfolios/{experiment_id}/holdings
GET /api/v1/portfolios/{experiment_id}/performance
```

---

# 42. Frontend Application

The frontend contains five primary research views.

---

## Dashboard

Route:

```text
/dashboard
```

Displays:

* research universe size
* active experiment
* experiment period
* factor-validation summary
* latest regime
* model portfolio performance
* NGX benchmark performance
* Sharpe ratio
* maximum drawdown

---

## Factor Analytics

Route:

```text
/factors
```

Displays:

```text
Market
Size
Value
Momentum
Liquidity
```

Each factor displays:

* cumulative factor return
* mean return
* volatility
* Sharpe ratio
* Newey-West t-statistic
* maximum drawdown
* confidence interval
* regime-specific performance

---

## Regime Analytics

Route:

```text
/regimes
```

Displays:

* state timeline
* posterior state probabilities
* state mean returns
* state volatility
* transition matrix
* factor performance per state

---

## Portfolio

Route:

```text
/portfolio
```

Displays:

* selected securities
* factor scores
* composite score
* portfolio weights
* sector allocation
* periodic returns
* cumulative performance
* NGX benchmark comparison
* drawdown

---

## Experiments

Route:

```text
/experiments
```

Displays:

* experiment name
* status
* date range
* dataset version
* selected factors
* regime configuration
* portfolio size
* performance summary

---

# 43. Experiment Execution UI

The experiment interface allows the researcher to define:

```text
Experiment Name

Start Date

End Date

Portfolio Size

Transaction Cost

Bootstrap Iterations

HMM State Count

Fundamental Availability Policy
```

The five factors are enabled by default.

Execution progress is displayed as:

```text
Preparing Dataset             ✓
Point-in-Time Alignment       ✓

Market Factor                 ✓
Size Factor                   ✓
Value Factor                  ✓
Momentum Factor               ✓
Liquidity Factor              ✓

Statistical Validation        ✓
Regime Estimation             ✓
Stock Ranking                 ✓
Portfolio Construction        ✓
Historical Backtest           ✓
Benchmark Comparison          ✓
```

---

# 44. Backend Environment Management

The backend uses `uv`.

The project is defined by:

```text
pyproject.toml
uv.lock
.python-version
```

---

# 45. Backend Setup

Navigate to:

```bash
cd apps/api
```

Pin Python:

```bash
uv python pin 3.12
```

Synchronise the environment:

```bash
uv sync
```

Run the backend:

```bash
uv run uvicorn app.main:app --reload
```

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

# 46. Backend Dependencies

Core dependencies can be installed with:

```bash
uv add \
  fastapi \
  "uvicorn[standard]" \
  pydantic \
  pydantic-settings \
  sqlalchemy \
  alembic \
  "psycopg[binary]" \
  pandas \
  numpy \
  scipy \
  statsmodels \
  scikit-learn \
  hmmlearn \
  langgraph \
  httpx
```

Development dependencies:

```bash
uv add --dev \
  pytest \
  pytest-asyncio \
  ruff
```

---

# 47. Database Migrations

Apply migrations:

```bash
uv run alembic upgrade head
```

Generate migration:

```bash
uv run alembic revision --autogenerate -m "create research schema"
```

---

# 48. Data Scripts

Audit raw data:

```bash
uv run python scripts/audit_data.py
```

Import prices:

```bash
uv run python scripts/import_prices.py
```

Import fundamentals:

```bash
uv run python scripts/import_fundamentals.py
```

Build the processed research dataset:

```bash
uv run python scripts/build_dataset.py
```

Run an experiment:

```bash
uv run python scripts/run_experiment.py
```

---

# 49. Testing

Run all backend tests:

```bash
uv run pytest
```

Factor tests:

```bash
uv run pytest app/tests/factors/
```

Quantitative tests:

```bash
uv run pytest app/tests/quant/
```

Data tests:

```bash
uv run pytest app/tests/data/
```

Graph tests:

```bash
uv run pytest app/tests/graph/
```

API tests:

```bash
uv run pytest app/tests/api/
```

---

# 50. Deterministic Factor Testing

Every factor calculation must have unit tests using manually verifiable datasets.

Example:

```text
Given:

Known prices
Known shares outstanding
Known market-cap breakpoints

When:

SMB is constructed

Then:

The computed SMB return must equal
the manually derived expected value
```

The same principle applies to:

* Market
* Value
* Momentum
* Liquidity
* Newey-West statistics
* bootstrap routines
* HMM feature construction
* portfolio returns

---

# 51. Frontend Setup

```bash
cd apps/web
```

Install:

```bash
pnpm install
```

Create local environment:

```bash
cp .env.local.example .env.local
```

Run:

```bash
pnpm dev
```

Frontend:

```text
http://localhost:3000
```

---

# 52. Environment Variables

## Backend

```env
APP_ENV=development

DATABASE_URL=

FRONTEND_URL=http://localhost:3000

BOOTSTRAP_ITERATIONS=10000

NEWEY_WEST_THRESHOLD=2.5

DEFAULT_REGIME_COUNT=3

DEFAULT_PORTFOLIO_SIZE=10

FUNDAMENTAL_REPORTING_LAG_DAYS=90

LOG_LEVEL=INFO
```

Optional LLM configuration may be added for research-summary generation.

The quantitative pipeline does not depend on LLM output.

---

## Frontend

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

# 53. Deployment Architecture

```mermaid
flowchart LR

    USER[User]

    VERCEL[Next.js Frontend<br/>Vercel]

    RENDER[FastAPI Research API<br/>Render]

    NEON[(PostgreSQL<br/>Neon)]

    USER --> VERCEL
    VERCEL -->|HTTPS REST API| RENDER
    RENDER -->|PostgreSQL / TLS| NEON
```

---

# 54. Vercel Deployment

Deploy:

```text
apps/web
```

Production variable:

```env
NEXT_PUBLIC_API_URL=https://YOUR_RENDER_SERVICE.onrender.com/api/v1
```

---

# 55. Render Deployment

Render root directory:

```text
apps/api
```

Build command:

```bash
uv sync --frozen --no-dev
```

Start command:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Production variables:

```env
APP_ENV=production

DATABASE_URL=

FRONTEND_URL=https://YOUR_VERCEL_APP.vercel.app
```

---

# 56. Neon Database

Production connection:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DATABASE
```

Run:

```bash
uv run alembic upgrade head
```

after configuring the production database.

---

# 57. Logging

The backend uses structured application logs.

Example:

```json
{
  "experiment_id": "exp_01HXYZ",
  "node": "momentum_factor",
  "status": "completed",
  "duration_ms": 842,
  "timestamp": "2026-09-11T14:00:00Z"
}
```

Research runs should be traceable across:

```text
Experiment
→ Graph Node
→ Quantitative Calculation
→ Database Result
```

---

# 58. Research Integrity

All financial and statistical outputs displayed by the application must originate from reproducible calculations.

The system must never fabricate:

* market prices
* financial statements
* factor returns
* t-statistics
* confidence intervals
* regime classifications
* portfolio returns
* benchmark results

Missing observations remain missing unless transformed through an explicitly defined methodological procedure.

---

# 59. AI Usage

LLMs are optional supporting components.

They may be used for:

* explaining completed statistical results
* generating research summaries
* converting metrics into readable commentary
* assisting with error interpretation

LLMs do not perform the core financial calculations.

The deterministic Python engine remains the source of truth.

---

# 60. Development Sequence

```text
Research Database
       ↓
Data Ingestion
       ↓
Data Validation
       ↓
Point-in-Time Alignment
       ↓
Five-Factor Engine
       ↓
Statistical Validation
       ↓
Portfolio Backtesting
       ↓
HMM Regime Detection
       ↓
Regime Analysis
       ↓
Composite Stock Ranking
       ↓
FastAPI Research API
       ↓
LangGraph Orchestration
       ↓
Next.js Dashboard
       ↓
Vercel + Render + Neon
```

---

# 61. Expected Research Outputs

The system should ultimately produce empirical tables such as:

## Factor Statistics

| Factor    |     Mean | Volatility |   Sharpe | NW t-stat | CI       |
| --------- | -------: | ---------: | -------: | --------: | -------- |
| Market    | Computed |   Computed | Computed |  Computed | Computed |
| Size      | Computed |   Computed | Computed |  Computed | Computed |
| Value     | Computed |   Computed | Computed |  Computed | Computed |
| Momentum  | Computed |   Computed | Computed |  Computed | Computed |
| Liquidity | Computed |   Computed | Computed |  Computed | Computed |

---

## Regime Analysis

| Factor    |  State 0 |  State 1 |  State 2 |
| --------- | -------: | -------: | -------: |
| Market    | Computed | Computed | Computed |
| Size      | Computed | Computed | Computed |
| Value     | Computed | Computed | Computed |
| Momentum  | Computed | Computed | Computed |
| Liquidity | Computed | Computed | Computed |

---

## Model Comparison

| Model          |   Return | Volatility |   Sharpe | Max Drawdown |    Alpha |
| -------------- | -------: | ---------: | -------: | -----------: | -------: |
| NGX ASI        | Computed |   Computed | Computed |     Computed |        — |
| CAPM           | Computed |   Computed | Computed |     Computed | Computed |
| NGX FF3        | Computed |   Computed | Computed |     Computed | Computed |
| Proposed Model | Computed |   Computed | Computed |     Computed | Computed |

---

# 62. Academic Contribution

The software provides an integrated research environment for examining equity-factor behaviour on the Nigerian Exchange.

Its main technical and methodological components are:

* point-in-time financial-data processing
* NGX-specific factor construction
* liquidity augmentation
* robust statistical validation
* latent market-regime detection
* regime-specific factor evaluation
* cross-sectional stock ranking
* backtested portfolio simulation
* reproducible experiment tracking
* graph-orchestrated quantitative workflow execution

The system is designed to generate the empirical evidence required for the accompanying academic research.

---

# 63. Future Extensions

The architecture can later support:

* Profitability factor
* Investment factor
* Low-Volatility factor
* quality factors
* dividend factors
* FX regimes
* inflation regimes
* crude-oil regimes
* monetary-policy regimes
* inverse-volatility portfolios
* risk parity
* constrained portfolio optimisation
* long-short simulation
* machine-learning factor timing
* real-time NGX ingestion
* automated PDF reports
* advanced transaction-cost estimation

---

# 64. Author

**Samuel Justin Ifiezibe**

Email:

**[sammyjayisthename@gmail.com](mailto:sammyjayisthename@gmail.com)**

Research areas:

```text
Software Engineering
Quantitative Finance
Financial Data Engineering
Multi-Agent Systems
```

---

# 65. Disclaimer

This platform is developed for:

* academic research
* quantitative finance experimentation
* software engineering research
* portfolio simulation

It does not provide financial advice.

The portfolio engine produces simulated research portfolios based on historical data.

Past performance does not guarantee future investment results.
