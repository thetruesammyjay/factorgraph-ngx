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

