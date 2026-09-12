import type { FactorSummary, PortfolioHolding, Experiment } from "@/types/research";

export const NAV_ITEMS = [
  { label: "Overview", href: "/dashboard", icon: "LayoutDashboard" },
  { label: "Factor lab", href: "/factors", icon: "Activity" },
  { label: "Regimes", href: "/regimes", icon: "Waves" },
  { label: "Portfolio", href: "/portfolio", icon: "BriefcaseBusiness" },
  { label: "Experiments", href: "/experiments", icon: "FlaskConical" },
] as const;

export const FACTORS: FactorSummary[] = [
  { key: "market", label: "Market", short: "MKT", tone: "teal", description: "Excess return over the risk-free rate", return: 14.8, volatility: 12.1, sharpe: 1.22, tStat: 2.84, confidence: "9.2 — 20.4%", sparkline: [30, 34, 33, 38, 36, 41, 43, 45, 44, 50, 52, 57] },
  { key: "size", label: "Size", short: "SMB", tone: "gold", description: "Small-capitalisation premium", return: 6.4, volatility: 8.9, sharpe: 0.72, tStat: 1.96, confidence: "0.8 — 12.0%", sparkline: [40, 37, 42, 39, 45, 47, 43, 49, 50, 54, 52, 58] },
  { key: "value", label: "Value", short: "HML", tone: "coral", description: "High book-to-market premium", return: 9.7, volatility: 10.4, sharpe: 0.93, tStat: 2.31, confidence: "3.1 — 16.3%", sparkline: [50, 47, 45, 51, 49, 53, 57, 55, 61, 60, 66, 71] },
  { key: "momentum", label: "Momentum", short: "MOM", tone: "violet", description: "12–1 formation-period winners", return: 18.1, volatility: 15.7, sharpe: 1.15, tStat: 3.08, confidence: "10.4 — 25.8%", sparkline: [25, 29, 31, 30, 38, 42, 40, 48, 46, 55, 62, 69] },
  { key: "liquidity", label: "Liquidity", short: "LIQ", tone: "blue", description: "Turnover adjusted for illiquidity", return: 11.3, volatility: 9.6, sharpe: 1.18, tStat: 2.67, confidence: "5.7 — 16.9%", sparkline: [35, 38, 37, 42, 44, 43, 48, 47, 52, 56, 59, 63] },
];

export const HOLDINGS: PortfolioHolding[] = [
  { ticker: "DANGCEM", name: "Dangote Cement", sector: "Industrials", score: 1.84, weight: 10, change: 3.8 },
  { ticker: "BUACEMENT", name: "BUA Cement", sector: "Industrials", score: 1.72, weight: 10, change: 2.9 },
  { ticker: "SEPLAT", name: "Seplat Energy", sector: "Energy", score: 1.64, weight: 10, change: -0.7 },
  { ticker: "MTNN", name: "MTN Nigeria", sector: "Telecoms", score: 1.58, weight: 10, change: 4.2 },
  { ticker: "GTCO", name: "Guaranty Trust", sector: "Financials", score: 1.51, weight: 10, change: 1.8 },
];

export const EXPERIMENTS: Experiment[] = [
  { id: "exp_01HXYZ", name: "Five-factor baseline", status: "Completed", period: "Jan 2019 — Dec 2025", dataset: "ngx_monthly_v3", result: "+24.6%" },
  { id: "exp_01HWQ2", name: "Liquidity sensitivity", status: "Completed", period: "Jan 2020 — Dec 2025", dataset: "ngx_monthly_v3", result: "+19.2%" },
  { id: "exp_01HSB8", name: "Preliminary universe audit", status: "Running", period: "Jan 2019 — Jun 2025", dataset: "ngx_daily_v2", result: "—" },
];

export const EQUITY_CURVE = [
  { month: "Jan 19", model: 100, benchmark: 100 }, { month: "Jul 19", model: 106, benchmark: 104 },
  { month: "Jan 20", model: 111, benchmark: 108 }, { month: "Jul 20", model: 106, benchmark: 96 },
  { month: "Jan 21", model: 125, benchmark: 116 }, { month: "Jul 21", model: 133, benchmark: 121 },
  { month: "Jan 22", model: 139, benchmark: 128 }, { month: "Jul 22", model: 145, benchmark: 131 },
  { month: "Jan 23", model: 153, benchmark: 136 }, { month: "Jul 23", model: 162, benchmark: 142 },
  { month: "Jan 24", model: 175, benchmark: 151 }, { month: "Jul 24", model: 192, benchmark: 160 },
  { month: "Jan 25", model: 211, benchmark: 171 }, { month: "Dec 25", model: 224.6, benchmark: 181.2 },
];

export const REGIME_TIMELINE = [
  { month: "Jan 19", regime: "Stable", color: "teal" }, { month: "Jul 19", regime: "Stable", color: "teal" },
  { month: "Jan 20", regime: "Expansion", color: "gold" }, { month: "Jul 20", regime: "Stress", color: "coral" },
  { month: "Jan 21", regime: "Expansion", color: "gold" }, { month: "Jul 21", regime: "Expansion", color: "gold" },
  { month: "Jan 22", regime: "Stable", color: "teal" }, { month: "Jul 22", regime: "Stable", color: "teal" },
  { month: "Jan 23", regime: "Expansion", color: "gold" }, { month: "Jul 23", regime: "Expansion", color: "gold" },
  { month: "Jan 24", regime: "Expansion", color: "gold" }, { month: "Jul 24", regime: "Stable", color: "teal" },
  { month: "Jan 25", regime: "Stable", color: "teal" }, { month: "Dec 25", regime: "Stable", color: "teal" },
];

