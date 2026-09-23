export type FactorKey = "market" | "size" | "value" | "momentum" | "liquidity";
export type ViewKey = "dashboard" | "factors" | "regimes" | "portfolio" | "experiments";

export type FactorSummary = {
  key: FactorKey;
  label: string;
  short: string;
  tone: string;
  description: string;
  return: number;
  volatility: number;
  sharpe: number;
  tStat: number;
  confidence: string;
  sparkline: number[];
};

export type PortfolioHolding = {
  ticker: string;
  name: string;
  sector: string;
  score: number;
  weight: number;
  change: number;
};

export type Experiment = {
  id: string;
  name: string;
  status: "Completed" | "Running" | "Draft";
  period: string;
  dataset: string;
  result: string;
};

export type ExperimentRun = {
  experiment_id: string;
  status: "draft" | "running" | "completed" | "blocked";
  dataset_version: string | null;
  last_completed_node: string | null;
  execution_trace: Array<{ node: string; status: string; outputs?: Record<string, unknown> }>;
  node_outputs: Record<string, Record<string, unknown>>;
  errors: Array<{ message: string }>;
};

export type ExperimentNodeRun = {
  experiment_id: string;
  node: string;
  status: string;
  outputs: Record<string, unknown>;
};

export type ExperimentCreatePayload = {
  name: string;
  start_date: string;
  end_date: string;
  factors: FactorKey[];
  portfolio_method: string;
  portfolio_size: number;
  rebalance_frequency: string;
  regime_count: number;
  bootstrap_iterations: number;
  newey_west_threshold: number;
  fundamental_availability_policy: string;
  fixed_reporting_lag_days: number;
};

export type ExperimentRecord = ExperimentCreatePayload & {
  id: string;
  status: string;
  dataset_version: string;
  created_at: string;
  completed_at: string | null;
  git_commit: string | null;
};

export type DatasetQuality = {
  dataset_id: string;
  structural_status: "passed" | "failed";
  price_universe_expansion: string;
  research_readiness: string;
  source_pdf_count: number;
  valid_dol_document_count: number;
  valid_document_rate: number;
  observation_count: number;
  tickers: string[];
  date_min: string;
  date_max: string;
  missing_liquidity_fields: Record<string, number>;
  carried_market_prices_by_ticker: Record<string, number>;
  unique_closes_by_ticker: Record<string, number>;
  longest_unchanged_close_run_by_ticker: Record<string, number>;
};

export type FundamentalsCompletion = {
  dataset_id: string;
  generated_at: string;
  universe_id: string;
  summary: {
    expected_issuer_periods: number;
    complete_issuer_periods: number;
    missing_issuer_periods: number;
    issuers_in_scope: number;
    issuers_with_complete_observations: number;
    remaining_issuers: string[];
    fiscal_periods: string[];
  };
  workflow: string[];
};

export type FactorEligibility = {
  factor: FactorKey;
  status: "eligible" | "preliminary" | "blocked";
  reasons: string[];
  metrics: Record<string, number | boolean | string>;
};

export type FactorRegression = {
  status: "blocked" | "preliminary" | "eligible";
  reason: string | null;
  observations: number;
  predictors: string[];
  newey_west_lags: number | null;
  alpha: number | null;
  alpha_std_error: number | null;
  alpha_t: number | null;
  alpha_p_value: number | null;
  r_squared: number | null;
  adjusted_r_squared: number | null;
  coefficients: Record<string, {
    coefficient: number;
    std_error: number;
    t_stat: number;
    p_value: number;
  }>;
  target_definition: string;
};

export type CharacteristicPortfolio = {
  status: "preliminary" | "eligible" | "blocked";
  coverage: {
    formation_months: number;
    months_with_size_spread: number;
    months_with_value_spread: number;
    groups: number;
    minimum_assets: number;
  };
  performance: Array<{
    formation_month: string;
    holding_month: string;
    size_spread_return: number | null;
    value_spread_return: number | null;
    size_small_count: number;
    size_big_count: number;
    value_high_count: number;
    value_low_count: number;
  }>;
  factors: Partial<Record<"size" | "value", {
    methodology: Record<string, string>;
    statistics: {
      statistics: Record<string, number | null> | null;
      newey_west_t: number | null;
      newey_west_lags: number | null;
      bootstrap: Record<string, number> | null;
      observations: number;
    };
  }>>;
};

export type PilotExperiment = {
  experiment_id: string;
  name: string;
  status: "completed_with_constraints";
  generated_at: string;
  dataset_version: string;
  reproducibility: {
    fingerprint: string;
    inputs: Record<string, { filename: string; bytes: number; sha256: string }>;
    configuration: Record<string, string | number>;
    software: { commit: string | null; dirty: boolean | null };
  };
  universe: {
    universe_id: string;
    name: string;
    selection_basis: string;
    securities: Array<{ ticker: string; company: string; sector: string }>;
  };
  price_dataset: string;
  fundamentals_dataset: string;
  coverage: {
    observations: number;
    tickers: number;
    dates: number;
    marked_returns: number;
    official_trade_returns: number;
    carried_price_rows: number;
    first_date: string;
    last_date: string;
  };
  market_input_coverage: {
    benchmark_observations: number;
    benchmark_months: number;
    risk_free_observations: number;
    risk_free_months: number;
    aligned_months: number;
    benchmark_code: string | null;
    risk_free_tenor: string | null;
    first_aligned_month: string | null;
    last_aligned_month: string | null;
  } | null;
  factor_eligibility: FactorEligibility[];
  characteristic_coverage: {
    observations: number;
    months: number;
    universe_tickers: number;
    point_in_time_observations: number;
    fundamental_tickers: number;
    size_eligible_observations: number;
    value_eligible_observations: number;
    actual_date_observations: number;
    estimated_date_observations: number;
  };
  characteristics: Array<Record<string, unknown>>;
  latest_characteristics: Array<{
    observation_month: string;
    ticker: string;
    close: number;
    fiscal_period: string | null;
    effective_from: string | null;
    effective_date_source: string | null;
    market_cap: number | null;
    book_to_market: number | null;
    size_rank: number | null;
    value_rank: number | null;
    size_eligible: boolean;
    value_eligible: boolean;
    size_exclusion_reason: string | null;
    value_exclusion_reason: string | null;
    source_id: string | null;
  }>;
  market_proxy_statistics: {
    marked_price: Record<string, number>;
    official_trade: Record<string, number>;
    annualised_return_difference: number;
  };
  market_proxy: Array<{
    observation_month: string;
    marked_equal_weight_return: number | null;
    official_equal_weight_return: number | null;
    marked_security_count: number;
    official_security_count: number;
  }>;
  market_factor: Array<{
    observation_month: string;
    benchmark_close: number;
    market_return: number | null;
    annual_rate_percent: number;
    risk_free_return: number;
    market_excess_return: number | null;
  }>;
  market_factor_statistics: Record<string, number> | null;
  factor_regressions: Partial<Record<FactorKey, FactorRegression>>;
  characteristic_portfolios: CharacteristicPortfolio;
  regime_analysis: {
    status: "blocked" | "eligible";
    reason: string | null;
    coverage: {
      monthly_endpoints: number;
      complete_market_returns: number;
      feature_observations: number;
      minimum_observations: number;
      states: number;
      volatility_window: number;
    };
    model: {
      algorithm: string;
      covariance_type: string;
      converged: boolean;
      iterations: number;
      log_likelihood: number;
      seed: number;
    } | null;
    timeline: Array<{
      observation_month: string;
      state: number;
      probabilities: number[];
    }>;
    statistics: Array<{
      state: number;
      mean_return: number;
      volatility: number;
      observations: number;
    }>;
    transition_matrix: number[][] | null;
  };
  momentum_portfolio: {
    status: "preliminary";
    methodology: Record<string, string | number>;
    coverage: {
      months: number;
      invested_months: number;
      holdings: number;
      marked_return_months: number;
      complete_official_return_months: number;
    };
    statistics: Record<string, number> | null;
    performance: Array<{
      observation_month: string;
      positions: number;
      turnover: number;
      transaction_cost: number;
      marked_gross_return: number | null;
      marked_net_return: number | null;
      official_gross_return: number | null;
      official_net_return: number | null;
      official_return_coverage: number | null;
    }>;
    holdings: Array<{
      observation_month: string;
      ticker: string;
      rank: number;
      formation_return: number;
      weight: number;
    }>;
  };
  latest_momentum: Array<{
    observation_month: string;
    ticker: string;
    momentum_return: number | null;
    rank: number | null;
  }>;
};
