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
  research_readiness: string;
  source_pdf_count: number;
  observation_count: number;
  tickers: string[];
  date_min: string;
  date_max: string;
  missing_liquidity_fields: Record<string, number>;
  carried_market_prices_by_ticker: Record<string, number>;
  unique_closes_by_ticker: Record<string, number>;
  longest_unchanged_close_run_by_ticker: Record<string, number>;
};
