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

export type FactorEligibility = {
  factor: FactorKey;
  status: "eligible" | "preliminary" | "blocked";
  reasons: string[];
  metrics: Record<string, number | boolean | string>;
};

export type PilotExperiment = {
  experiment_id: string;
  name: string;
  status: "completed_with_constraints";
  generated_at: string;
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
  factor_eligibility: FactorEligibility[];
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
  latest_momentum: Array<{
    observation_month: string;
    ticker: string;
    momentum_return: number | null;
    rank: number | null;
  }>;
};
