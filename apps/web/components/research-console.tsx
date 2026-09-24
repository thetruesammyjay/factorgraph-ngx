"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Bell,
  BookOpen,
  BriefcaseBusiness,
  Check,
  ChevronDown,
  CircleHelp,
  Database,
  Download,
  FlaskConical,
  LayoutDashboard,
  Menu,
  MoreHorizontal,
  PanelLeftClose,
  Play,
  Plus,
  Settings2,
  SlidersHorizontal,
  Sparkles,
  Target,
  TrendingUp,
  Waves,
  X,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { EQUITY_CURVE, EXPERIMENTS, FACTORS, HOLDINGS, NAV_ITEMS, REGIME_TIMELINE } from "@/lib/constants";
import { createExperiment, getExperimentNodeRun, getExperimentExport, getExperimentManifest, getExperimentPlan, getExperimentRun, getLatestDatasetQuality, getLatestFundamentalsCompletion, getLatestPilotExperiment, listExperiments, runExperiment } from "@/lib/api";
import type { DatasetQuality, ExperimentBacktestOutput, ExperimentBenchmarkOutput, ExperimentCreatePayload, ExperimentManifest, ExperimentPlan, ExperimentPortfolioOutput, ExperimentRecord, ExperimentRun, ExperimentStockRankingOutput, FactorKey, FactorRegression, FundamentalsCompletion, PilotExperiment, ViewKey } from "@/types/research";
import { formatPercent } from "@/lib/utils";

const iconMap = { LayoutDashboard, Activity, Waves, BriefcaseBusiness, FlaskConical };

function LogoMark() {
  return <img className="brand-logo-image" src="/factorgraph-ngx.png" alt="FactorGraph NGX" />;
}

function MiniSparkline({ values, tone }: { values: number[]; tone: string }) {
  const points = values.map((value, index) => `${(index / (values.length - 1)) * 100},${60 - value}`).join(" ");
  return <svg className="mini-sparkline" viewBox="0 0 100 60" preserveAspectRatio="none" aria-hidden="true"><polyline points={points} fill="none" stroke={`var(--${tone})`} strokeWidth="2.4" vectorEffect="non-scaling-stroke" /></svg>;
}

function StatusBadge({ status }: { status: string }) {
  const className = status.toLowerCase().replace(" ", "-");
  return <span className={`status-badge ${className}`}><span className="status-dot" />{status}</span>;
}

function MetricCard({ label, value, helper, accent, icon: Icon }: { label: string; value: string; helper: string; accent?: string; icon: typeof TrendingUp }) {
  return <div className="metric-card" style={{ "--card-accent": accent ?? "var(--teal)" } as React.CSSProperties}>
    <div className="metric-head"><span>{label}</span><Icon size={15} /></div>
    <div className="metric-value">{value}</div>
    <div className="metric-helper">{helper}</div>
    <div className="metric-accent" />
  </div>;
}

function SectionHeader({ eyebrow, title, action }: { eyebrow: string; title: string; action?: React.ReactNode }) {
  return <div className="section-header"><div><div className="eyebrow">{eyebrow}</div><h2>{title}</h2></div>{action}</div>;
}

function DashboardView({ onNewExperiment, quality }: { onNewExperiment: () => void; quality: DatasetQuality | null }) {
  const [range, setRange] = useState("Full study");
  return <>
    <div className="page-heading">
      <div><div className="eyebrow">RESEARCH / OVERVIEW</div><h1>Good morning, Samuel.</h1><p className="lede">Your latest model run is complete. Here’s the signal across the Nigerian Exchange.</p></div>
      <button className="button button-primary" onClick={onNewExperiment}><Plus size={16} /> New experiment</button>
    </div>

    <div className="hero-grid">
      <div className="hero-card">
        <div className="hero-card-top"><div><span className="live-kicker"><span className="pulse" /> ACTIVE EXPERIMENT</span><h2>Five-factor baseline</h2><p>Regime-aware, liquidity-augmented model</p></div><button className="icon-button" aria-label="More experiment actions"><MoreHorizontal size={18} /></button></div>
        <div className="hero-number-row"><div><span className="hero-number">+24.6%</span><span className="hero-number-label">cumulative return</span></div><div className="hero-meta"><span>Jan 2019 — Dec 2025</span><span className="success-text"><ArrowUpRight size={14} /> +6.3 pts vs ASI</span></div></div>
        <div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><AreaChart data={EQUITY_CURVE} margin={{ top: 12, right: 2, left: -22, bottom: 0 }}>
          <defs><linearGradient id="modelFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#79e3ce" stopOpacity={0.26} /><stop offset="100%" stopColor="#79e3ce" stopOpacity={0} /></linearGradient></defs>
          <CartesianGrid vertical={false} stroke="rgba(255,255,255,.08)" strokeDasharray="2 6" />
          <XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fill: "#8b989b", fontSize: 10 }} interval={2} />
          <YAxis tickLine={false} axisLine={false} tick={{ fill: "#8b989b", fontSize: 10 }} tickFormatter={(v) => `${v}`} />
          <Tooltip contentStyle={{ background: "#192326", border: "1px solid #334044", borderRadius: 8, color: "#f2f5ef", fontSize: 12 }} itemStyle={{ color: "#79e3ce" }} formatter={(value: number) => [`${value.toFixed(1)}`, "Index"]} />
          <Area type="monotone" dataKey="model" stroke="#79e3ce" strokeWidth={2.5} fill="url(#modelFill)" />
          <Line type="monotone" dataKey="benchmark" stroke="#718083" strokeWidth={1.5} strokeDasharray="4 4" dot={false} />
        </AreaChart></ResponsiveContainer></div>
        <div className="chart-legend"><span><i className="legend-line model" /> Proposed model</span><span><i className="legend-line benchmark" /> NGX ASI</span><div className="range-tabs">{["1Y", "3Y", "Full study"].map((item) => <button key={item} className={range === item ? "active" : ""} onClick={() => setRange(item)}>{item}</button>)}</div></div>
      </div>
      <div className="research-rail">
        <div className="rail-heading"><span className="eyebrow">MODEL PULSE</span><span className="signal">LIVE</span></div>
        <div className="rail-state"><div className="state-orb"><Waves size={28} /></div><div><span className="rail-label">CURRENT REGIME</span><strong>Stable market</strong><span className="rail-sub">State 0 · 71% probability</span></div></div>
        <div className="rail-rows"><div><span>Market return</span><b>+1.84%</b></div><div><span>Rolling volatility</span><b>12.6%</b></div><div><span>State persistence</span><b>4.2 months</b></div></div>
        <div className="rail-foot"><span className="check-circle review"><Database size={12} /></span><span>{quality ? "Price expansion ready · liquidity input unavailable" : "Checking public-data validation"}</span></div>
      </div>
    </div>

    <div className="metric-grid"><MetricCard label="Universe" value="183" helper="eligible equities" icon={Target} accent="var(--gold)" /><MetricCard label="Model Sharpe" value="1.42" helper="vs 0.96 NGX ASI" icon={TrendingUp} accent="var(--teal)" /><MetricCard label="Max drawdown" value="−11.8%" helper="Jan 2020 — Mar 2020" icon={ArrowDownRight} accent="var(--coral)" /><MetricCard label="Last rebalance" value="02 Sep 25" helper="10 positions · equal weight" icon={SlidersHorizontal} accent="var(--violet)" /></div>

    <section className="section-block"><SectionHeader eyebrow="FACTOR VALIDATION" title="Five signals, one view" action={<button className="text-button" onClick={() => window.location.href = "/factors"}>Open factor lab <ArrowUpRight size={14} /></button>} />
      <div className="factor-grid">{FACTORS.map((factor) => <article className="factor-card" key={factor.key}><div className="factor-card-head"><div className={`factor-chip ${factor.tone}`}>{factor.short}</div><span className="factor-name">{factor.label}</span><span className="confidence-dot" title="Passed validation" /></div><div className="factor-return">{formatPercent(factor.return)} <span>annualised</span></div><MiniSparkline values={factor.sparkline} tone={factor.tone} /><div className="factor-stats"><span><b>{factor.sharpe.toFixed(2)}</b> Sharpe</span><span><b>{factor.tStat.toFixed(2)}</b> NW t-stat</span></div></article>)}</div>
    </section>

    <div className="two-column section-block"><section><SectionHeader eyebrow="PORTFOLIO / TOP RANKED" title="Current holdings" action={<button className="text-button" onClick={() => window.location.href = "/portfolio"}>View portfolio <ArrowUpRight size={14} /></button>} /><div className="table-card"><table><thead><tr><th>Security</th><th>Sector</th><th>Score</th><th>Weight</th><th>1M</th></tr></thead><tbody>{HOLDINGS.map((holding) => <tr key={holding.ticker}><td><div className="security-cell"><span className="ticker-avatar">{holding.ticker.slice(0, 2)}</span><div><b>{holding.ticker}</b><small>{holding.name}</small></div></div></td><td>{holding.sector}</td><td><b>{holding.score.toFixed(2)}</b></td><td>{holding.weight.toFixed(1)}%</td><td className={holding.change >= 0 ? "positive" : "negative"}>{formatPercent(holding.change)}</td></tr>)}</tbody></table></div></section><section><SectionHeader eyebrow="RUN HISTORY" title="Experiments" action={<button className="text-button" onClick={() => window.location.href = "/experiments"}>See all <ArrowUpRight size={14} /></button>} /><div className="experiment-list">{EXPERIMENTS.map((experiment) => <div className="experiment-row" key={experiment.id}><div className="experiment-icon"><FlaskConical size={16} /></div><div className="experiment-details"><b>{experiment.name}</b><span>{experiment.period} · {experiment.dataset}</span></div><div className="experiment-result"><StatusBadge status={experiment.status} /><strong>{experiment.result}</strong></div></div>)}</div></section></div>
  </>;
}

function FactorsView() {
  const [selected, setSelected] = useState<FactorKey>("liquidity");
  const factor = FACTORS.find((item) => item.key === selected) ?? FACTORS[4];
  const factorChart = EQUITY_CURVE.map((point, index) => ({ month: point.month, return: 100 + factor.sparkline[index % factor.sparkline.length] - 30 }));
  return <><div className="page-heading"><div><div className="eyebrow">RESEARCH / FACTOR LAB</div><h1>Factor analytics</h1><p className="lede">Trace the return, risk, and statistical confidence of every signal in the model.</p></div><button className="button button-quiet"><Database size={15} /> Dataset v3.2</button></div><div className="factor-lab-layout"><div className="factor-selector">{FACTORS.map((item) => <button key={item.key} className={item.key === selected ? "selected" : ""} onClick={() => setSelected(item.key)}><span className={`factor-chip ${item.tone}`}>{item.short}</span><span><b>{item.label}</b><small>{item.description}</small></span><strong>{formatPercent(item.return)}</strong></button>)}</div><div className="factor-detail"><div className="detail-title"><div><span className="eyebrow">{factor.short} / VALIDATED SERIES</span><h2>{factor.label} factor</h2></div><StatusBadge status="Validated" /></div><div className="detail-metrics"><div><span>Annualised return</span><b>{formatPercent(factor.return)}</b></div><div><span>Volatility</span><b>{factor.volatility.toFixed(1)}%</b></div><div><span>Sharpe ratio</span><b>{factor.sharpe.toFixed(2)}</b></div><div><span>NW t-statistic</span><b>{factor.tStat.toFixed(2)}</b></div></div><div className="detail-chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={factorChart}><CartesianGrid vertical={false} stroke="rgba(255,255,255,.08)" strokeDasharray="2 6" /><XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fill: "#8b989b", fontSize: 10 }} interval={2} /><YAxis tickLine={false} axisLine={false} tick={{ fill: "#8b989b", fontSize: 10 }} /><Tooltip contentStyle={{ background: "#192326", border: "1px solid #334044", borderRadius: 8, color: "#f2f5ef", fontSize: 12 }} /><Line dataKey="return" stroke={`var(--${factor.tone})`} strokeWidth={2.5} dot={false} /></LineChart></ResponsiveContainer></div><div className="method-note"><BookOpen size={15} /><span><b>Method note:</b> {factor.description}. Results use point-in-time aligned observations and a Newey-West adjusted standard error.</span></div></div></div></>;
}

function RegimesView() {
  return <><div className="page-heading"><div><div className="eyebrow">RESEARCH / REGIME ENGINE</div><h1>Market regimes</h1><p className="lede">A three-state Gaussian HMM reads return and volatility together.</p></div><button className="button button-quiet"><Settings2 size={15} /> Model settings</button></div><div className="regime-grid"><div className="regime-main panel"><div className="panel-heading"><div><span className="eyebrow">STATE TIMELINE</span><h2>How the market has moved</h2></div><StatusBadge status="Converged" /></div><div className="timeline-strip">{REGIME_TIMELINE.map((item) => <div className={`timeline-block ${item.color}`} key={item.month}><span>{item.month}</span><b>{item.regime}</b></div>)}</div><div className="timeline-axis"><span>2019</span><span>2020</span><span>2021</span><span>2022</span><span>2023</span><span>2024</span><span>2025</span></div></div><div className="panel current-regime-panel"><span className="eyebrow">LATEST OBSERVATION</span><div className="big-regime"><span className="state-orb teal"><Waves size={26} /></span><div><h2>Stable market</h2><span>State 0 · 71% posterior probability</span></div></div><div className="regime-probabilities"><div><span>Stable</span><b>71%</b><i><em style={{ width: "71%" }} /></i></div><div><span>Expansion</span><b>19%</b><i><em className="gold" style={{ width: "19%" }} /></i></div><div><span>Stress</span><b>10%</b><i><em className="coral" style={{ width: "10%" }} /></i></div></div></div></div><section className="section-block"><SectionHeader eyebrow="REGIME DIAGNOSTICS" title="Three states, distinct behaviour" /><div className="diagnostic-grid"><div className="diagnostic-card stable"><span className="regime-pill">STATE 0 · STABLE</span><b>+1.84%</b><span>mean monthly return</span><div className="diagnostic-foot"><span>Volatility</span><strong>3.2%</strong><span>Persistence</span><strong>4.2 mo</strong></div></div><div className="diagnostic-card expansion"><span className="regime-pill">STATE 1 · EXPANSION</span><b>+3.11%</b><span>mean monthly return</span><div className="diagnostic-foot"><span>Volatility</span><strong>5.8%</strong><span>Persistence</span><strong>3.1 mo</strong></div></div><div className="diagnostic-card stress"><span className="regime-pill">STATE 2 · STRESS</span><b>−4.62%</b><span>mean monthly return</span><div className="diagnostic-foot"><span>Volatility</span><strong>11.7%</strong><span>Persistence</span><strong>1.8 mo</strong></div></div></div></section></>;
}

function LiveRegimesView({ pilot }: { pilot: PilotExperiment | null }) {
  if (!pilot) return <div className="panel"><p>Loading regime readiness…</p></div>;
  const analysis = pilot.regime_analysis;
  const coverage = analysis.coverage;
  return <>
    <div className="page-heading"><div><div className="eyebrow">RESEARCH / REGIME ENGINE</div><h1>Market regimes</h1><p className="lede">A three-state Gaussian HMM reads return and volatility together.</p></div><StatusBadge status={analysis.status === "eligible" ? "Eligible" : "Blocked"} /></div>
    <div className="metric-grid">
      <MetricCard label="Monthly endpoints" value={String(coverage.monthly_endpoints)} helper={`${coverage.minimum_observations} required`} icon={Activity} />
      <MetricCard label="Complete returns" value={String(coverage.complete_market_returns)} helper="market excess returns" icon={TrendingUp} accent="var(--gold)" />
      <MetricCard label="HMM features" value={String(coverage.feature_observations)} helper={`rolling ${coverage.volatility_window}-month volatility`} icon={Waves} accent="var(--violet)" />
      <MetricCard label="States" value={String(coverage.states)} helper="configured Gaussian states" icon={Target} accent="var(--coral)" />
    </div>
    {analysis.status === "blocked" ? <section className="section-block"><div className="panel method-note"><Database size={18} /><span><b>Regime estimation is blocked.</b> {analysis.reason ?? "The current data does not satisfy the regime gate."} No state labels or posterior probabilities are shown until the gate passes.</span></div></section> : <>
      <section className="section-block"><SectionHeader eyebrow="STATE TIMELINE" title="Estimated market states" /><div className="table-card full-table"><table><thead><tr><th>Month</th><th>State</th><th>Posterior probabilities</th></tr></thead><tbody>{analysis.timeline.map((point) => <tr key={point.observation_month}><td>{point.observation_month}</td><td><b>State {point.state}</b></td><td>{point.probabilities.map((probability) => `${(probability * 100).toFixed(1)}%`).join(" · ")}</td></tr>)}</tbody></table></div></section>
      <section className="section-block"><SectionHeader eyebrow="REGIME DIAGNOSTICS" title="Estimated state behaviour" /><div className="diagnostic-grid">{analysis.statistics.map((summary) => <div className="diagnostic-card" key={summary.state}><span className="regime-pill">STATE {summary.state}</span><b>{(summary.mean_return * 100).toFixed(2)}%</b><span>mean monthly return</span><div className="diagnostic-foot"><span>Volatility</span><strong>{(summary.volatility * 100).toFixed(2)}%</strong><span>Observations</span><strong>{summary.observations}</strong></div></div>)}</div></section>
    </>}
  </>;
}

function PortfolioView() {
  return <><div className="page-heading"><div><div className="eyebrow">RESEARCH / PORTFOLIO</div><h1>Model portfolio</h1><p className="lede">The top ten equal-weighted securities selected at the latest monthly rebalance.</p></div><button className="button button-primary"><BarChart3 size={15} /> Export results</button></div><div className="metric-grid portfolio-metrics"><MetricCard label="Portfolio value" value="₦12.46m" helper="from ₦10.0m initial" icon={TrendingUp} /><MetricCard label="Since inception" value="+24.6%" helper="Jan 2019 — Dec 2025" icon={ArrowUpRight} accent="var(--gold)" /><MetricCard label="Turnover" value="18.4%" helper="latest rebalance" icon={Activity} accent="var(--violet)" /><MetricCard label="Positions" value="10 / 183" helper="eligible universe" icon={Target} accent="var(--coral)" /></div><section className="section-block"><SectionHeader eyebrow="RANKED SECURITIES" title="Holdings & factor scores" action={<button className="button button-quiet"><SlidersHorizontal size={14} /> Configure</button>} /><div className="table-card full-table"><table><thead><tr><th>#</th><th>Security</th><th>Sector</th><th>Composite score</th><th>Weight</th><th>1M return</th><th>Action</th></tr></thead><tbody>{HOLDINGS.concat([{ ticker: "NB", name: "Nigerian Breweries", sector: "Consumer", score: 1.47, weight: 10, change: 1.2 }, { ticker: "ZENITHBANK", name: "Zenith Bank", sector: "Financials", score: 1.41, weight: 10, change: -1.1 }]).map((holding, index) => <tr key={holding.ticker}><td className="muted">{String(index + 1).padStart(2, "0")}</td><td><div className="security-cell"><span className="ticker-avatar">{holding.ticker.slice(0, 2)}</span><div><b>{holding.ticker}</b><small>{holding.name}</small></div></div></td><td>{holding.sector}</td><td><div className="score-bar"><span style={{ width: `${Math.min(100, holding.score * 42)}%` }} /><b>{holding.score.toFixed(2)}</b></div></td><td>{holding.weight.toFixed(1)}%</td><td className={holding.change >= 0 ? "positive" : "negative"}>{formatPercent(holding.change)}</td><td><button className="row-action"><MoreHorizontal size={16} /></button></td></tr>)}</tbody></table></div></section></>;
}

function ExperimentsView({ onNewExperiment }: { onNewExperiment: () => void }) {
  return <><div className="page-heading"><div><div className="eyebrow">RESEARCH / EXPERIMENTS</div><h1>Experiment registry</h1><p className="lede">Every run is reproducible. Configuration, dataset, software version, and outputs stay together.</p></div><button className="button button-primary" onClick={onNewExperiment}><Plus size={16} /> New experiment</button></div><div className="experiment-hero panel"><div className="experiment-hero-copy"><span className="eyebrow">ACTIVE RUN · EXP_01HXYZ</span><h2>Five-factor baseline</h2><p>All 13 research nodes completed successfully on dataset ngx_monthly_v3.</p><div className="progress-track"><span style={{ width: "100%" }} /></div><div className="run-meta"><span><Check size={13} /> Completed 11 Sep 2026, 14:00 UTC</span><span><Database size={13} /> 183 eligible securities</span></div></div><div className="run-score"><span>MODEL RETURN</span><strong>+24.6%</strong><small>1.42 Sharpe · 11.8% max drawdown</small></div></div><section className="section-block"><SectionHeader eyebrow="RUN HISTORY" title="Saved experiments" /><div className="experiment-table table-card"><table><thead><tr><th>Experiment</th><th>Status</th><th>Period</th><th>Dataset</th><th>Result</th><th /></tr></thead><tbody>{EXPERIMENTS.map((experiment) => <tr key={experiment.id}><td><b>{experiment.name}</b><small>{experiment.id}</small></td><td><StatusBadge status={experiment.status} /></td><td>{experiment.period}</td><td><span className="dataset-tag">{experiment.dataset}</span></td><td className="result-cell">{experiment.result}</td><td><button className="text-button">Open <ArrowUpRight size={14} /></button></td></tr>)}</tbody></table></div></section></>;
}

const factorLabels: Record<FactorKey, string> = {
  market: "Market",
  size: "Size",
  value: "Value",
  momentum: "Momentum",
  liquidity: "Liquidity",
};

function PilotDashboardView({ pilot }: { pilot: PilotExperiment | null }) {
  if (!pilot) return <div className="panel"><p>Loading deterministic pilot results…</p></div>;
  const excessByMonth = new Map(
    pilot.market_factor.map((point) => [point.observation_month, point.market_excess_return]),
  );
  const chart = pilot.market_proxy.map((point) => ({
    month: point.observation_month.slice(5),
    marked: point.marked_equal_weight_return === null ? null : point.marked_equal_weight_return * 100,
    official: point.official_equal_weight_return === null ? null : point.official_equal_weight_return * 100,
    excess: excessByMonth.get(point.observation_month) == null ? null : excessByMonth.get(point.observation_month)! * 100,
  }));
  return <>
    <div className="page-heading"><div><div className="eyebrow">RESEARCH / PUBLIC-DATA PILOT</div><h1>Deterministic 2023–2024 experiment</h1><p className="lede">Observed returns, stale-price sensitivity, and factor gates from validated NGX documents.</p></div><StatusBadge status="Completed with constraints" /></div>
    <div className="metric-grid"><MetricCard label="Universe" value={String(pilot.coverage.tickers)} helper={`${pilot.coverage.dates} accepted dates`} icon={Target} accent="var(--gold)" /><MetricCard label="Marked returns" value={pilot.coverage.marked_returns.toLocaleString()} helper="close-to-close observations" icon={TrendingUp} /><MetricCard label="Trade returns" value={pilot.coverage.official_trade_returns.toLocaleString()} helper="official trade-to-trade" icon={Activity} accent="var(--violet)" /><MetricCard label="Carried prices" value={pilot.coverage.carried_price_rows.toLocaleString()} helper="explicitly flagged rows" icon={Database} accent="var(--coral)" /></div>
    <section className="section-block"><SectionHeader eyebrow="MARKET RETURNS" title="Official benchmark and universe proxies" /><div className="panel detail-chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={chart}><CartesianGrid vertical={false} stroke="rgba(255,255,255,.08)" strokeDasharray="2 6" /><XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fill: "#8b989b", fontSize: 10 }} /><YAxis tickLine={false} axisLine={false} tick={{ fill: "#8b989b", fontSize: 10 }} tickFormatter={(value) => `${value}%`} /><Tooltip contentStyle={{ background: "#192326", border: "1px solid #334044", borderRadius: 8 }} formatter={(value: number) => [`${value.toFixed(2)}%`]} /><Line dataKey="excess" name="NGX ASI excess return" stroke="#a78bfa" strokeWidth={2.5} dot={false} /><Line dataKey="marked" name="Marked-price proxy" stroke="#79e3ce" strokeWidth={2} dot={false} /><Line dataKey="official" name="Official-trade proxy" stroke="#d8b56a" strokeWidth={2} strokeDasharray="4 4" dot={false} /></LineChart></ResponsiveContainer></div></section>
    <section className="section-block"><SectionHeader eyebrow="FACTOR ELIGIBILITY" title="Evidence before calculation" /><div className="factor-grid">{pilot.factor_eligibility.map((factor) => <article className="factor-card" key={factor.factor}><div className="factor-card-head"><div className="factor-chip teal">{factor.factor.slice(0, 3).toUpperCase()}</div><span className="factor-name">{factorLabels[factor.factor]}</span></div><StatusBadge status={factor.status} /><div className="method-note"><BookOpen size={15} /><span>{factor.reasons.join(" · ")}</span></div></article>)}</div></section>
  </>;
}

function LiveFactorsView({ pilot, completion }: { pilot: PilotExperiment | null; completion: FundamentalsCompletion | null }) {
  if (!pilot) return <div className="panel">Loading factor gates…</div>;
  const eligibleCharacteristics = pilot.latest_characteristics.filter((row) => row.size_eligible);
  const regressionEntries = (Object.entries(pilot.factor_regressions) as [FactorKey, FactorRegression][]).filter(([, result]) => Boolean(result));
  const displayStatistic = (value: number | null) => value === null ? "—" : value.toFixed(3);
  const characteristicPortfolio = pilot.characteristic_portfolios;
  const recentPortfolio = characteristicPortfolio.performance.slice(-6);
  return <><div className="page-heading"><div><div className="eyebrow">RESEARCH / FACTOR GATES</div><h1>Factor eligibility</h1><p className="lede">A factor is calculated only when its observed inputs satisfy the declared gate.</p></div></div><div className="factor-selector">{pilot.factor_eligibility.map((factor) => <div className="panel" key={factor.factor}><div className="detail-title"><h2>{factorLabels[factor.factor]}</h2><StatusBadge status={factor.status} /></div><div className="method-note"><BookOpen size={15} /><span>{factor.reasons.join(" · ")}</span></div></div>)}</div>
    {completion && <section className="section-block"><SectionHeader eyebrow="FUNDAMENTALS COMPLETION" title="Point-in-time evidence queue" /><div className="factor-grid"><article className="factor-card"><span className="eyebrow">ISSUER-PERIOD TASKS</span><div className="factor-return">{completion.summary.complete_issuer_periods}<span> approved of {completion.summary.expected_issuer_periods}</span></div><div className="method-note"><Database size={15} /><span>{completion.summary.missing_issuer_periods} tasks remain blocked</span></div></article><article className="factor-card"><span className="eyebrow">ISSUERS COVERED</span><div className="factor-return">{completion.summary.issuers_with_complete_observations}<span> of {completion.summary.issuers_in_scope}</span></div><div className="method-note"><Target size={15} /><span>Complete observations across the declared universe</span></div></article><article className="factor-card"><span className="eyebrow">REMAINING ISSUERS</span><div className="method-note"><BookOpen size={15} /><span>{completion.summary.remaining_issuers.join(" · ")}</span></div></article></div></section>}
    <section className="section-block"><SectionHeader eyebrow="POINT-IN-TIME SNAPSHOT" title={`${eligibleCharacteristics.length} issuers with Size inputs`} /><div className="table-card full-table"><table><thead><tr><th>Issuer</th><th>Effective from</th><th>Market cap</th><th>Size rank</th><th>Book-to-market</th><th>Value rank</th><th>Availability</th></tr></thead><tbody>{eligibleCharacteristics.map((row) => <tr key={row.ticker}><td><b>{row.ticker}</b><small>FY {row.fiscal_period ?? "unavailable"}</small></td><td>{row.effective_from}</td><td>{row.market_cap === null ? "—" : `₦${(row.market_cap / 1_000_000_000).toFixed(1)}bn`}</td><td>{row.size_rank === null ? "—" : `#${row.size_rank}`}</td><td>{row.book_to_market === null ? "Excluded" : row.book_to_market.toFixed(3)}</td><td>{row.value_rank === null ? "—" : `#${row.value_rank}`}</td><td><StatusBadge status={row.effective_date_source === "ACTUAL_PUBLICATION_DATE" ? "Actual date" : "Estimated date"} /></td></tr>)}</tbody></table></div><div className="method-note"><BookOpen size={15} /><span>{pilot.characteristic_coverage.fundamental_tickers} of {pilot.characteristic_coverage.universe_tickers} issuers currently have point-in-time fundamentals. Rankings are descriptive snapshots; SMB and HML return portfolios remain preliminary until coverage improves.</span></div></section>
    <section className="section-block"><SectionHeader eyebrow="REGRESSION DIAGNOSTICS" title="Market-exposure diagnostics" /><div className="table-card full-table"><table><thead><tr><th>Factor return</th><th>Status</th><th>Observations</th><th>Alpha</th><th>Alpha t-stat</th><th>R²</th><th>Interpretation</th></tr></thead><tbody>{regressionEntries.map(([factor, result]) => <tr key={factor}><td><b>{factorLabels[factor]}</b><small>{result.target_definition}</small></td><td><StatusBadge status={result.status} /></td><td>{result.observations}</td><td>{displayStatistic(result.alpha)}</td><td>{displayStatistic(result.alpha_t)}</td><td>{displayStatistic(result.r_squared)}</td><td>{result.reason ?? "HAC regression available"}</td></tr>)}</tbody></table></div><div className="method-note"><BookOpen size={15} /><span>Coefficients use the aligned monthly market excess return and Newey-West standard errors. Pilot samples remain descriptive until the declared evidence and sample-size gates pass.</span></div></section>
    <section className="section-block"><SectionHeader eyebrow="PORTFOLIO SORTS" title="Size and Value spreads" /><div className="factor-grid">{(["size", "value"] as const).map((factor) => { const result = characteristicPortfolio.factors[factor]; const summary = result?.statistics.statistics; return <article className="factor-card" key={factor}><div className="factor-card-head"><div className={`factor-chip ${factor === "size" ? "gold" : "violet"}`}>{factor === "size" ? "SMB" : "HML"}</div><span className="factor-name">{factorLabels[factor]}</span><StatusBadge status={characteristicPortfolio.status} /></div><div className="factor-return">{summary?.mean_return == null ? "—" : formatPercent(summary.mean_return * 100)} <span>mean monthly spread</span></div><div className="factor-stats"><span><b>{result?.statistics.newey_west_t == null ? "—" : result.statistics.newey_west_t.toFixed(2)}</b> NW t-stat</span><span><b>{result?.statistics.observations ?? 0}</b> observations</span></div></article>; })}</div><div className="table-card full-table"><table><thead><tr><th>Formation</th><th>Holding</th><th>Size spread</th><th>Value spread</th><th>Size count</th><th>Value count</th></tr></thead><tbody>{recentPortfolio.map((row) => <tr key={`${row.formation_month}-${row.holding_month}`}><td>{row.formation_month}</td><td>{row.holding_month}</td><td>{row.size_spread_return == null ? "—" : formatPercent(row.size_spread_return * 100)}</td><td>{row.value_spread_return == null ? "—" : formatPercent(row.value_spread_return * 100)}</td><td>{row.size_small_count}/{row.size_big_count}</td><td>{row.value_high_count}/{row.value_low_count}</td></tr>)}</tbody></table></div><div className="method-note"><BookOpen size={15} /><span>{characteristicPortfolio.coverage.months_with_size_spread} Size and {characteristicPortfolio.coverage.months_with_value_spread} Value holding months currently have complete spreads. These are preliminary while point-in-time fundamentals coverage is incomplete.</span></div></section>
  </>;
}

function BlockedResearchView({ title, reason }: { title: string; reason: string }) {
  return <><div className="page-heading"><div><div className="eyebrow">RESEARCH / COVERAGE GATE</div><h1>{title}</h1><p className="lede">{reason}</p></div><StatusBadge status="Blocked" /></div><div className="panel method-note"><Database size={18} /><span>The platform will enable this view after the required canonical inputs pass validation.</span></div></>;
}

function MomentumPortfolioView({ pilot }: { pilot: PilotExperiment | null }) {
  if (!pilot) return <div className="panel"><p>Loading momentum pilot…</p></div>;
  const portfolio = pilot.momentum_portfolio;
  const invested = portfolio.performance.filter((point) => point.marked_net_return !== null);
  const latestMonth = portfolio.holdings.at(-1)?.observation_month;
  const latestHoldings = portfolio.holdings.filter((row) => row.observation_month === latestMonth);
  const chart = invested.map((point) => ({
    month: point.observation_month.slice(5),
    net: point.marked_net_return! * 100,
    official: point.official_net_return === null ? null : point.official_net_return * 100,
  }));
  return <>
    <div className="page-heading"><div><div className="eyebrow">RESEARCH / MOMENTUM PILOT</div><h1>12–1 momentum portfolio</h1><p className="lede">An eligible monthly-rebalanced pilot using 11 compounded return months, skipping the latest month before each holding period.</p></div><StatusBadge status="Eligible" /></div>
    <div className="metric-grid"><MetricCard label="Invested months" value={String(portfolio.coverage.invested_months)} helper={`${portfolio.coverage.months} observed months`} icon={Activity} /><MetricCard label="Holdings" value={String(portfolio.coverage.holdings)} helper="security-month positions" icon={Target} accent="var(--gold)" /><MetricCard label="Official coverage" value={String(portfolio.coverage.complete_official_return_months)} helper="complete return months" icon={Database} accent="var(--violet)" /><MetricCard label="Transaction cost" value={`${portfolio.methodology.transaction_cost_bps} bps`} helper="applied to turnover" icon={TrendingUp} accent="var(--coral)" /></div>
    <section className="section-block"><SectionHeader eyebrow="NET RETURNS" title="Marked-price and official-trade sensitivity" /><div className="panel detail-chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={chart}><CartesianGrid vertical={false} stroke="rgba(255,255,255,.08)" strokeDasharray="2 6" /><XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fill: "#8b989b", fontSize: 10 }} /><YAxis tickLine={false} axisLine={false} tick={{ fill: "#8b989b", fontSize: 10 }} tickFormatter={(value) => `${value}%`} /><Tooltip contentStyle={{ background: "#192326", border: "1px solid #334044", borderRadius: 8 }} formatter={(value: number) => [`${value.toFixed(2)}%`]} /><Line dataKey="net" name="Marked net return" stroke="#79e3ce" strokeWidth={2.5} dot={false} /><Line dataKey="official" name="Official-trade sensitivity" stroke="#d8b56a" strokeWidth={2} strokeDasharray="4 4" dot={false} /></LineChart></ResponsiveContainer></div></section>
    <section className="section-block"><SectionHeader eyebrow="LATEST REBALANCE" title={latestMonth ?? "No eligible holdings"} /><div className="factor-grid">{latestHoldings.map((holding) => <article className="factor-card" key={holding.ticker}><div className="factor-card-head"><div className="factor-chip teal">#{holding.rank}</div><span className="factor-name">{holding.ticker}</span></div><b>{(holding.weight * 100).toFixed(0)}% weight</b><div className="method-note"><TrendingUp size={15} /><span>{(holding.formation_return * 100).toFixed(2)}% formation return</span></div></article>)}</div></section>
  </>;
}

function PilotExperimentsViewContent({ pilot, onNewExperiment }: { pilot: PilotExperiment | null; onNewExperiment: () => void }) {
  return <><div className="page-heading"><div><div className="eyebrow">RESEARCH / EXPERIMENTS</div><h1>Experiment registry</h1><p className="lede">Computed results remain linked to their input datasets and eligibility decisions.</p></div><button className="button button-primary" onClick={onNewExperiment}><Plus size={16} /> New experiment</button></div>{pilot && <><div className="experiment-hero panel"><div className="experiment-hero-copy"><span className="eyebrow">{pilot.experiment_id}</span><h2>{pilot.name}</h2><p>{pilot.coverage.observations.toLocaleString()} price observations · {pilot.factor_eligibility.filter((factor) => factor.status === "blocked").length} blocked factor</p><div className="run-meta"><span><Check size={13} /> Completed with constraints</span><span><Database size={13} /> {pilot.dataset_version}</span></div></div><div className="run-score"><span>RESEARCH STATUS</span><strong>Auditable</strong><small>No blocked factor is reported as a result</small></div></div><section className="section-block"><SectionHeader eyebrow="REPRODUCIBILITY" title="Content-addressed experiment" /><div className="method-note"><Database size={15} /><span>Fingerprint <b>{pilot.reproducibility.fingerprint.slice(0, 16)}</b> · Git <b>{pilot.reproducibility.software.commit?.slice(0, 12) ?? "unavailable"}</b> · {Object.keys(pilot.reproducibility.inputs).length} hashed inputs · worktree {pilot.reproducibility.software.dirty ? "contained uncommitted changes" : "clean"}</span></div></section></>}</>;
}

const GRAPH_RUN_CONFIG: ExperimentCreatePayload = {
  name: "Inspectable graph run",
  start_date: "2023-01-03",
  end_date: "2024-12-31",
  factors: ["market", "size", "value", "momentum", "liquidity"],
  portfolio_method: "equal_weight",
  portfolio_size: 10,
  rebalance_frequency: "monthly",
  regime_count: 3,
  bootstrap_iterations: 1000,
  newey_west_threshold: 2.5,
  fundamental_availability_policy: "actual_or_fixed_lag",
  fixed_reporting_lag_days: 90,
};

function LegacyExecutableGraphRunPanel() {
  const [run, setRun] = useState<ExperimentRun | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const execute = async () => {
    setPending(true);
    setError(null);
    try {
      const experiment = await createExperiment(GRAPH_RUN_CONFIG);
      setRun(await runExperiment(experiment.id));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Research graph failed");
    } finally {
      setPending(false);
    }
  };
  return <section className="section-block"><SectionHeader eyebrow="EXECUTABLE RESEARCH GRAPH" title="Inspectable node run" action={<button className="button button-primary" onClick={execute} disabled={pending}><Play size={14} /> {pending ? "Running graphâ€¦" : "Run graph"}</button>} />{error && <div className="panel method-note"><Database size={16} /><span>{error}</span></div>}{run && <><div className="table-card full-table"><table><thead><tr><th>Order</th><th>Node</th><th>Status</th></tr></thead><tbody>{run.execution_trace.map((step, index) => <tr key={`${step.node}-${index}`}><td>{String(index + 1).padStart(2, "0")}</td><td><b>{step.node}</b></td><td><StatusBadge status={step.status} /></td></tr>)}</tbody></table></div><div className="method-note"><Database size={15} /><span>Run <b>{run.experiment_id}</b> Â· dataset <b>{run.dataset_version ?? "unassigned"}</b> Â· last completed node <b>{run.last_completed_node ?? "none"}</b></span></div></>}{!run && !pending && !error && <div className="panel method-note"><Play size={16} /><span>Run the graph to execute and inspect every deterministic research node in order.</span></div>}</section>;
}

function ExecutableGraphRunPanel() {
  const [run, setRun] = useState<ExperimentRun | null>(null);
  const [plan, setPlan] = useState<ExperimentPlan | null>(null);
  const [pending, setPending] = useState(false);
  const [detailPending, setDetailPending] = useState(false);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [selectedOutput, setSelectedOutput] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const execute = async () => {
    setPending(true);
    setError(null);
    setSelectedNode(null);
    setSelectedOutput(null);
    try {
      const experiment = await createExperiment(GRAPH_RUN_CONFIG);
      const nextPlan = await getExperimentPlan(experiment.id);
      setPlan(nextPlan);
      setRun(await runExperiment(experiment.id));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Research graph failed");
    } finally {
      setPending(false);
    }
  };
  const inspectNode = async (node: string) => {
    if (!run) return;
    setSelectedNode(node);
    setDetailPending(true);
    setError(null);
    try {
      const detail = await getExperimentNodeRun(run.experiment_id, node);
      setSelectedOutput(detail.outputs);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Graph node output is unavailable");
      setSelectedOutput(null);
    } finally {
      setDetailPending(false);
    }
  };
  return <section className="section-block"><SectionHeader eyebrow="EXECUTABLE RESEARCH GRAPH" title="Inspectable node run" action={<button className="button button-primary" onClick={execute} disabled={pending}><Play size={14} /> {pending ? "Preparing and running..." : "Run graph"}</button>} />{error && <div className="panel method-note"><Database size={16} /><span>{error}</span></div>}{plan && <div className="panel method-note"><Database size={15} /><span><b>Preflight plan</b> · dataset <b>{plan.dataset_version}</b> · {plan.planned_nodes.length} planned nodes · factors {plan.requested_factors.map((factor) => `${factor} (${plan.factor_statuses[factor]})`).join(" · ")} · {plan.constraints.length ? `${plan.constraints.length} constraint${plan.constraints.length === 1 ? "" : "s"}` : "no constraints"} · fingerprint <b>{plan.run_fingerprint.slice(0, 16)}</b></span></div>}{run && <><div className="table-card full-table"><table><thead><tr><th>Order</th><th>Node</th><th>Status</th><th>Evidence</th></tr></thead><tbody>{run.execution_trace.map((step, index) => <tr key={`${step.node}-${index}`}><td>{String(index + 1).padStart(2, "0")}</td><td><b>{step.node}</b></td><td><StatusBadge status={step.status} /></td><td><button className="text-button" onClick={() => inspectNode(step.node)} disabled={detailPending && selectedNode === step.node}>{detailPending && selectedNode === step.node ? "Loading..." : "Inspect"}</button></td></tr>)}</tbody></table></div>{selectedNode && <div className="panel method-note"><Database size={15} /><span><b>{selectedNode}</b> output summary</span><pre>{JSON.stringify(selectedOutput ?? {}, null, 2)}</pre></div>}<div className="method-note"><Database size={15} /><span>Run <b>{run.experiment_id}</b> · dataset <b>{run.dataset_version ?? "unassigned"}</b> · last completed node <b>{run.last_completed_node ?? "none"}</b></span></div></>}{!run && !pending && !error && <div className="panel method-note"><Play size={16} /><span>Run the graph to execute and inspect every deterministic research node in order.</span></div>}</section>;
}

function ManifestExportPanel() {
  const [manifest, setManifest] = useState<ExperimentManifest | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const registry = await listExperiments();
        const latest = registry.items.find((item) => item.status !== "draft") ?? registry.items[0];
        if (!latest) return;
        const next = await getExperimentManifest(latest.id);
        if (active) {
          setManifest(next);
          setError(null);
        }
      } catch (reason) {
        if (active) setError(reason instanceof Error ? reason.message : "Experiment manifest is unavailable");
      }
    };
    load();
    const timer = window.setInterval(load, 3000);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);
  const download = () => {
    if (!manifest) return;
    const blob = new Blob([JSON.stringify(manifest, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${manifest.experiment_id}-manifest.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  };
  return <section className="section-block"><SectionHeader eyebrow="REPRODUCIBILITY MANIFEST" title="Latest run record" action={<button className="button button-quiet" onClick={download} disabled={!manifest}><Database size={14} /> Download JSON</button>} />{error && <div className="panel method-note"><Database size={16} /><span>{error}</span></div>}{manifest ? <div className="panel method-note"><Database size={16} /><span><b>{manifest.experiment_id}</b> Â· {manifest.execution.node_count} nodes Â· {manifest.status} Â· fingerprint <b>{manifest.run_fingerprint?.slice(0, 16) ?? "pending"}</b></span></div> : !error && <div className="panel method-note"><Database size={16} /><span>Run an experiment to populate its reproducibility manifest.</span></div>}</section>;
}

function ExperimentPortfolioResults({ run }: { run: ExperimentRun }) {
  const output = run.node_outputs.historical_backtest as ExperimentBacktestOutput | undefined;
  const percent = (value: number | null | undefined) =>
    value == null ? "—" : `${(value * 100).toFixed(2)}%`;
  const statistic = (value: number | null | undefined) =>
    value == null ? "—" : value.toFixed(2);
  const characteristicRows = (["size", "value"] as const).flatMap((factor) => {
    const result = output?.characteristic_factors?.[factor];
    const details = result?.statistics?.statistics;
    if (!result) return [];
    const interval = result.statistics?.bootstrap;
    return [{
      name: `${factor[0].toUpperCase()}${factor.slice(1)} spread`,
      observations: result.statistics?.observations ?? details?.observations ?? null,
      annualized: details?.annualised_return,
      volatility: details?.volatility,
      sharpe: details?.sharpe,
      neweyWest: result.statistics?.newey_west_t,
      interval: interval ? `${percent(interval.lower)} to ${percent(interval.upper)}` : "—",
    }];
  });
  const momentum = output?.momentum_statistics;
  const rows = [
    ...characteristicRows,
    ...(momentum ? [{
      name: "Momentum net",
      observations: momentum.observations ?? null,
      annualized: momentum.annualised_return,
      volatility: momentum.volatility,
      sharpe: momentum.sharpe,
      neweyWest: null,
      interval: "—",
    }] : []),
  ];

  return <section className="section-block">
    <div className="detail-title"><div><span className="eyebrow">RUN-SPECIFIC PERFORMANCE</span><h2>Portfolio statistics</h2></div></div>
    {rows.length ? <div className="table-card full-table"><table><thead><tr><th>Strategy</th><th>Months</th><th>Annualized return</th><th>Annualized volatility</th><th>Sharpe</th><th>Newey-West t</th><th>Monthly mean 95% bootstrap CI</th></tr></thead><tbody>{rows.map((row) => <tr key={row.name}><td><b>{row.name}</b></td><td>{row.observations ?? "—"}</td><td>{percent(row.annualized)}</td><td>{percent(row.volatility)}</td><td>{statistic(row.sharpe)}</td><td>{statistic(row.neweyWest)}</td><td>{row.interval}</td></tr>)}</tbody></table></div> : <div className="method-note"><Database size={15} /><span>No requested portfolio has performance statistics in this run.</span></div>}
    <div className="method-note"><Database size={15} /><span>Momentum return is net of the configured trading-cost estimate. Size and Value are next-month long-short spread returns; their confidence intervals cover the monthly mean.</span></div>
  </section>;
}

function ExperimentPortfolioSeries({ run }: { run: ExperimentRun }) {
  const output = run.node_outputs.portfolio_construction as ExperimentPortfolioOutput | undefined;
  const characteristic = output?.characteristic_portfolios;
  const momentum = output?.momentum_portfolio;
  const monthly = new Map<string, { month: string; size: number | null; value: number | null; momentum: number | null }>();
  const monthlyRow = (month: string) => {
    const current = monthly.get(month) ?? { month, size: null, value: null, momentum: null };
    monthly.set(month, current);
    return current;
  };
  for (const row of characteristic?.performance ?? []) {
    if (typeof row.holding_month !== "string") continue;
    const current = monthlyRow(row.holding_month);
    current.size = typeof row.size_spread_return === "number" ? row.size_spread_return : null;
    current.value = typeof row.value_spread_return === "number" ? row.value_spread_return : null;
  }
  for (const row of momentum?.performance ?? []) {
    if (typeof row.observation_month !== "string") continue;
    const current = monthlyRow(row.observation_month);
    current.momentum = typeof row.marked_net_return === "number" ? row.marked_net_return : null;
  }
  const chart = [...monthly.values()]
    .filter((row) => row.size != null || row.value != null || row.momentum != null)
    .sort((left, right) => left.month.localeCompare(right.month));
  const holdings = [
    ...(characteristic?.holdings ?? []).flatMap((row) =>
      typeof row.ticker === "string" && typeof row.holding_month === "string"
        ? [{
            month: row.holding_month,
            factor: typeof row.factor === "string" ? row.factor : "—",
            ticker: row.ticker,
            bucket: typeof row.portfolio === "string" ? row.portfolio : "—",
            signal: typeof row.characteristic === "number" ? row.characteristic : null,
            weight: null as number | null,
          }]
        : [],
    ),
    ...(momentum?.holdings ?? []).flatMap((row) =>
      typeof row.ticker === "string" && typeof row.observation_month === "string"
        ? [{
            month: row.observation_month,
            factor: "momentum",
            ticker: row.ticker,
            bucket: typeof row.rank === "number" ? `rank ${row.rank}` : "selected",
            signal: typeof row.formation_return === "number" ? row.formation_return : null,
            weight: typeof row.weight === "number" ? row.weight : null,
          }]
        : [],
    ),
  ].sort((left, right) => left.month.localeCompare(right.month) || left.factor.localeCompare(right.factor) || left.ticker.localeCompare(right.ticker));
  const percent = (value: unknown) =>
    typeof value === "number" ? `${(value * 100).toFixed(2)}%` : "—";
  const formationSignal = (factor: string, value: number | null) => {
    if (value == null) return "—";
    return factor === "momentum"
      ? percent(value)
      : value.toLocaleString(undefined, { maximumFractionDigits: 4 });
  };

  return <section className="section-block">
    <div className="detail-title"><div><span className="eyebrow">MONTHLY RESEARCH OUTPUT</span><h2>Portfolio returns and holdings</h2></div></div>
    {chart.length ? <><div className="panel detail-chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={chart} margin={{ top: 12, right: 18, left: 5, bottom: 0 }}><CartesianGrid vertical={false} stroke="rgba(22,51,0,.10)" strokeDasharray="3 5" /><XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fill: "#718083", fontSize: 10 }} /><YAxis tickLine={false} axisLine={false} tick={{ fill: "#718083", fontSize: 10 }} tickFormatter={percent} /><Tooltip formatter={(value: number) => [percent(value), "Monthly return"]} contentStyle={{ background: "#fffdf7", border: "1px solid #dfe4d9", borderRadius: 8 }} /><Line dataKey="size" name="Size spread" stroke="#8b6dd1" strokeWidth={2} dot={false} connectNulls={false} /><Line dataKey="value" name="Value spread" stroke="#219a82" strokeWidth={2} dot={false} connectNulls={false} /><Line dataKey="momentum" name="Momentum net" stroke="#c08c2e" strokeWidth={2} dot={false} connectNulls={false} /></LineChart></ResponsiveContainer></div><div className="chart-legend"><span><i className="legend-line" style={{ background: "#8b6dd1" }} /> Size spread</span><span><i className="legend-line" style={{ background: "#219a82" }} /> Value spread</span><span><i className="legend-line" style={{ background: "#c08c2e" }} /> Momentum net</span></div></> : <div className="method-note"><Database size={15} /><span>This saved run has no captured monthly portfolio return rows. Rerun the experiment to create them.</span></div>}
    {holdings.length > 0 && <details className="panel"><summary className="method-note">Security-level holdings · {holdings.length} records</summary><div className="table-card full-table"><table><thead><tr><th>Month</th><th>Factor</th><th>Ticker</th><th>Portfolio</th><th>Formation signal or characteristic</th><th>Weight</th></tr></thead><tbody>{holdings.map((row, index) => <tr key={`${row.month}-${row.factor}-${row.ticker}-${index}`}><td>{row.month}</td><td>{row.factor}</td><td><b>{row.ticker}</b></td><td>{row.bucket}</td><td>{formationSignal(row.factor, row.signal)}</td><td>{percent(row.weight)}</td></tr>)}</tbody></table></div></details>}
    <div className="method-note"><Database size={15} /><span>Returns are grouped by holding month. Momentum formation signals are returns; Size uses market capitalization and Value uses book-to-market. Formation signals and selected holdings are saved with the experiment so the portfolio can be audited.</span></div>
  </section>;
}

function ExperimentStockRankings({ run }: { run: ExperimentRun }) {
  const output = run.node_outputs.stock_ranking as ExperimentStockRankingOutput | undefined;
  const factors = Object.entries(output?.factors ?? {}) as [
    FactorKey,
    NonNullable<ExperimentStockRankingOutput["factors"][FactorKey]>,
  ][];
  const formatScore = (factor: FactorKey, score: number) => {
    if (factor === "momentum") return `${(score * 100).toFixed(2)}%`;
    return factor === "size"
      ? score.toLocaleString(undefined, { notation: "compact", maximumFractionDigits: 2 })
      : score.toFixed(4);
  };

  return <section className="section-block">
    <div className="detail-title"><div><span className="eyebrow">POINT-IN-TIME CROSS SECTION</span><h2>Selected-month factor rankings</h2></div><span className="dataset-tag">{output?.observation_month ?? "No month"}</span></div>
    {factors.length ? factors.map(([factor, result]) => <details className="panel" key={factor}><summary className="method-note"><b>{factor[0].toUpperCase() + factor.slice(1)}</b> · {result.selected_securities} of {result.eligible_securities} selected at portfolio size {output?.portfolio_size}<span style={{ marginLeft: "auto" }}><StatusBadge status={result.status} /></span></summary>{result.reason && <div className="method-note">{result.reason}</div>}{result.rankings.length > 0 && <div className="table-card full-table"><table><thead><tr><th>Rank</th><th>Ticker</th><th>Factor characteristic</th><th>Selection</th></tr></thead><tbody>{result.rankings.map((row) => <tr key={`${factor}-${row.ticker}`}><td>{row.rank}</td><td><b>{row.ticker}</b></td><td>{formatScore(factor, row.score)}</td><td>{row.selected ? "Selected" : "Outside portfolio size"}</td></tr>)}</tbody></table></div>}</details>) : <div className="method-note"><Database size={15} /><span>Stock rankings were not captured in this saved run.</span></div>}
    <div className="method-note"><Database size={15} /><span>{output?.ranking_scope ?? "Each factor is ranked independently; unlike scores are not combined into a stock recommendation."}</span></div>
  </section>;
}

function ExperimentBenchmarkResults({ run }: { run: ExperimentRun }) {
  const benchmark = run.node_outputs.benchmark_comparison as ExperimentBenchmarkOutput | undefined;
  const entries = Object.entries(benchmark?.regressions ?? {}) as [
    "size" | "value" | "momentum",
    NonNullable<ExperimentBenchmarkOutput["regressions"]["size"]>,
  ][];
  const percent = (value: number | null | undefined) =>
    value == null ? "—" : `${(value * 100).toFixed(2)}%`;
  const statistic = (value: number | null | undefined, digits = 2) =>
    value == null ? "—" : value.toFixed(digits);

  return <section className="section-block">
    <div className="detail-title"><div><span className="eyebrow">RUN-SPECIFIC DIAGNOSTICS</span><h2>Benchmark regression</h2></div><span className="dataset-tag">{benchmark?.benchmark_code ?? "Benchmark unavailable"}</span></div>
    {entries.length ? <div className="table-card full-table"><table><thead><tr><th>Portfolio</th><th>Status</th><th>Months</th><th>Monthly alpha</th><th>Market beta</th><th>Alpha t-stat</th><th>R²</th></tr></thead><tbody>{entries.map(([factor, result]) => <tr key={factor}><td><b>{factor[0].toUpperCase() + factor.slice(1)}</b><small>{result.target_definition}</small></td><td><StatusBadge status={result.status} />{result.reason && <small>{result.reason}</small>}</td><td>{result.observations}</td><td>{percent(result.alpha)}</td><td>{statistic(result.coefficients.market_excess_return?.coefficient)}</td><td>{statistic(result.alpha_t)}</td><td>{percent(result.r_squared)}</td></tr>)}</tbody></table></div> : <div className="method-note"><Database size={15} /><span>No selected portfolio has a benchmark regression in this run.</span></div>}
    <div className="method-note"><Database size={15} /><span>Market <b>{benchmark?.benchmark_code ?? "NGX ASI"}</b> · risk-free <b>{benchmark?.risk_free_tenor ?? "91D T-bill"}</b> · alpha and beta use Newey-West HAC errors. Momentum is compared after its matched risk-free return is deducted.</span></div>
  </section>;
}

function LiveExperimentHistory() {
  const [items, setItems] = useState<ExperimentRecord[]>([]);
  const [selected, setSelected] = useState<{ manifest: ExperimentManifest; run: ExperimentRun } | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [nodeOutput, setNodeOutput] = useState<Record<string, unknown> | null>(null);
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [nodePending, setNodePending] = useState(false);
  const [exportPending, setExportPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const registry = await listExperiments();
        if (active) setItems(registry.items);
      } catch {
        if (active) setItems([]);
      }
    };
    load();
    const timer = window.setInterval(load, 3000);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);
  const openRun = async (experimentId: string) => {
    setPendingId(experimentId);
    setError(null);
    setSelectedNode(null);
    setNodeOutput(null);
    try {
      const [manifest, run] = await Promise.all([
        getExperimentManifest(experimentId),
        getExperimentRun(experimentId),
      ]);
      setSelected({ manifest, run });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Saved experiment could not be opened");
    } finally {
      setPendingId(null);
    }
  };
  const inspectNode = async (node: string) => {
    if (!selected) return;
    setSelectedNode(node);
    setNodePending(true);
    setError(null);
    try {
      const detail = await getExperimentNodeRun(selected.run.experiment_id, node);
      setNodeOutput(detail.outputs);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Saved node output is unavailable");
      setNodeOutput(null);
    } finally {
      setNodePending(false);
    }
  };
  const downloadBundle = async () => {
    if (!selected) return;
    setExportPending(true);
    setError(null);
    try {
      const bundle = await getExperimentExport(selected.manifest.experiment_id);
      const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${selected.manifest.experiment_id}-audit-bundle.json`;
      anchor.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Experiment audit bundle is unavailable");
    } finally {
      setExportPending(false);
    }
  };
  return <section className="section-block"><SectionHeader eyebrow="LIVE RUN HISTORY" title="API experiment registry" />{error && <div className="panel method-note"><Database size={15} /><span>{error}</span></div>}{items.length ? <div className="table-card full-table"><table><thead><tr><th>Experiment</th><th>Status</th><th>Dataset</th><th>Created</th><th /></tr></thead><tbody>{items.map((item) => <tr key={item.id}><td><b>{item.name}</b><small>{item.id}</small></td><td><StatusBadge status={item.status} /></td><td>{item.dataset_version}</td><td>{new Date(item.created_at).toLocaleString()}</td><td><button className="text-button" onClick={() => openRun(item.id)} disabled={pendingId === item.id}>{pendingId === item.id ? "Loading..." : "Inspect"}</button></td></tr>)}</tbody></table></div> : <div className="panel method-note"><Database size={16} /><span>No API-created experiments are available yet.</span></div>}{selected && <div className="panel section-block"><div className="detail-title"><div><span className="eyebrow">SAVED EXPERIMENT</span><h2>{selected.manifest.name}</h2><small>{selected.manifest.experiment_id} · {selected.manifest.dataset_version}</small></div><div className="topbar-actions"><button className="button button-quiet" onClick={downloadBundle} disabled={exportPending}><Download size={14} /> {exportPending ? "Preparing..." : "Download audit bundle"}</button><button className="button button-quiet" onClick={() => setSelected(null)}>Close</button></div></div><div className="method-note"><Database size={15} /><span>Status <b>{selected.run.status}</b> · fingerprint <b>{selected.manifest.run_fingerprint?.slice(0, 16) ?? "pending"}</b> · {selected.manifest.execution.node_count} completed nodes</span></div>{selected.manifest.constraints.length > 0 && <div className="method-note"><BookOpen size={15} /><span>{selected.manifest.constraints.map((item) => `${item.factor}: ${item.status} (${item.reasons.join(", ")})`).join(" · ")}</span></div>}<details><summary>Experiment configuration</summary><pre>{JSON.stringify(selected.manifest.configuration, null, 2)}</pre></details><ExperimentStockRankings run={selected.run} /><ExperimentPortfolioResults run={selected.run} /><ExperimentPortfolioSeries run={selected.run} /><ExperimentBenchmarkResults run={selected.run} />{selected.run.execution_trace.length > 0 && <div className="table-card full-table"><table><thead><tr><th>Order</th><th>Node</th><th>Status</th><th>Output</th></tr></thead><tbody>{selected.run.execution_trace.map((step) => <tr key={step.node}><td>{String(step.sequence).padStart(2, "0")}</td><td><b>{step.node}</b></td><td><StatusBadge status={step.status} /></td><td><button className="text-button" onClick={() => inspectNode(step.node)} disabled={nodePending && selectedNode === step.node}>{nodePending && selectedNode === step.node ? "Loading..." : "Inspect"}</button></td></tr>)}</tbody></table></div>}{selectedNode && <div className="method-note"><Database size={15} /><span><b>{selectedNode}</b> stored output</span><pre>{JSON.stringify(nodeOutput ?? {}, null, 2)}</pre></div>}</div>}</section>;
}

function PilotExperimentsView({ pilot, onNewExperiment }: { pilot: PilotExperiment | null; onNewExperiment: () => void }) {
  return <><PilotExperimentsViewContent pilot={pilot} onNewExperiment={onNewExperiment} /><ExecutableGraphRunPanel /><ManifestExportPanel /><LiveExperimentHistory /></>;
}

const NEW_EXPERIMENT_DEFAULT: ExperimentCreatePayload = {
  name: "NGX public data study",
  start_date: "2023-01-03",
  end_date: "2024-12-31",
  factors: ["market", "size", "value", "momentum", "liquidity"],
  portfolio_method: "equal_weight",
  portfolio_size: 10,
  rebalance_frequency: "monthly",
  regime_count: 3,
  bootstrap_iterations: 1000,
  newey_west_threshold: 2.5,
  fundamental_availability_policy: "actual_or_fixed_lag",
  fixed_reporting_lag_days: 90,
};

function NewExperimentModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [configuration, setConfiguration] = useState<ExperimentCreatePayload>(NEW_EXPERIMENT_DEFAULT);
  const [plan, setPlan] = useState<ExperimentPlan | null>(null);
  const [run, setRun] = useState<ExperimentRun | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const update = <K extends keyof ExperimentCreatePayload>(key: K, value: ExperimentCreatePayload[K]) => {
    setConfiguration((current) => ({ ...current, [key]: value }));
  };
  const toggleFactor = (factor: FactorKey) => {
    const factors = configuration.factors.includes(factor)
      ? configuration.factors.filter((item) => item !== factor)
      : [...configuration.factors, factor];
    update("factors", factors);
  };
  const prepare = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      const experiment = await createExperiment(configuration);
      setPlan(await getExperimentPlan(experiment.id));
      onCreated();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Experiment plan could not be prepared");
    } finally {
      setPending(false);
    }
  };
  const execute = async () => {
    if (!plan) return;
    setPending(true);
    setError(null);
    try {
      setRun(await runExperiment(plan.experiment_id));
      onCreated();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Experiment could not be run");
    } finally {
      setPending(false);
    }
  };

  return <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="new-experiment-title"><div className="modal">
    <div className="modal-head"><div><span className="eyebrow">NEW RESEARCH RUN</span><h2 id="new-experiment-title">{run ? "Run complete" : plan ? "Review preflight plan" : "Configure experiment"}</h2></div><button className="icon-button" onClick={onClose} aria-label="Close"><X size={18} /></button></div>
    {!plan && <form onSubmit={prepare}>
      <label>Experiment name<input required maxLength={200} value={configuration.name} onChange={(event) => update("name", event.target.value)} /></label>
      <div className="form-grid"><label>Start date<input required type="date" value={configuration.start_date} onChange={(event) => update("start_date", event.target.value)} /></label><label>End date<input required type="date" value={configuration.end_date} onChange={(event) => update("end_date", event.target.value)} /></label></div>
      <div className="form-grid"><label>Portfolio size<select value={configuration.portfolio_size} onChange={(event) => update("portfolio_size", Number(event.target.value))}><option value={10}>10 securities</option><option value={20}>20 securities</option><option value={30}>30 securities</option></select></label><label>Regime states<select value={configuration.regime_count} onChange={(event) => update("regime_count", Number(event.target.value))}><option value={2}>2 states</option><option value={3}>3 states</option><option value={4}>4 states</option></select></label></div>
      <div className="factor-toggle-list"><span className="eyebrow">ENABLED FACTORS</span>{FACTORS.map((factor) => <div key={factor.key} role="checkbox" aria-checked={configuration.factors.includes(factor.key)} tabIndex={0} onClick={() => toggleFactor(factor.key)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") toggleFactor(factor.key); }}><span className={`factor-chip ${factor.tone}`}>{factor.short}</span><b>{factor.label}</b><span className={configuration.factors.includes(factor.key) ? "toggle-on" : "toggle-off"}>{configuration.factors.includes(factor.key) ? <Check size={12} /> : null}</span></div>)}</div>
      {error && <div className="panel method-note"><Database size={15} /><span>{error}</span></div>}
      <div className="modal-actions"><button type="button" className="button button-quiet" onClick={onClose}>Cancel</button><button type="submit" className="button button-primary" disabled={pending || configuration.factors.length === 0}><Play size={14} /> {pending ? "Preparing plan..." : "Create and review plan"}</button></div>
    </form>}
    {plan && !run && <><div className="panel method-note"><Database size={15} /><span><b>{plan.name}</b> · dataset <b>{plan.dataset_version}</b> · {plan.planned_nodes.length} graph nodes · {plan.analysis_window.start_month}–{plan.analysis_window.end_month} monthly · {plan.analysis_window.market_months} market months · fingerprint <b>{plan.run_fingerprint.slice(0, 16)}</b></span></div><div className="factor-grid">{plan.requested_factors.map((factor) => <article className="factor-card" key={factor}><span className="eyebrow">{factor}</span><StatusBadge status={plan.factor_statuses[factor]} />{plan.constraints.filter((item) => item.factor === factor).map((item) => <p className="method-note" key={item.factor}>{item.reasons.join(" · ")}</p>)}</article>)}</div>{error && <div className="panel method-note"><Database size={15} /><span>{error}</span></div>}<div className="modal-actions"><button className="button button-quiet" onClick={onClose}>Close</button><button className="button button-primary" onClick={execute} disabled={pending}><Play size={14} /> {pending ? "Running graph..." : "Run this experiment"}</button></div></>}
    {run && <><div className="panel method-note"><Database size={15} /><span><b>{run.status}</b> · {run.execution_trace.length} nodes recorded · dataset <b>{run.dataset_version ?? "unassigned"}</b> · fingerprint <b>{run.run_fingerprint?.slice(0, 16) ?? "unavailable"}</b></span></div>{run.constraints.length > 0 && <div className="method-note"><BookOpen size={15} /><span>Constraints: {run.constraints.map((item) => `${item.factor}: ${item.status}`).join(" · ")}</span></div>}<div className="modal-actions"><button className="button button-primary" onClick={onClose}>Done</button></div></>}
  </div></div>;
}

function ApiLoadError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return <section className="panel method-note" role="alert">
    <Database size={18} />
    <div>
      <b>Could not load the research data</b>
      <p>{message}</p>
      <p>Check that the FastAPI server is running and that <code>NEXT_PUBLIC_API_URL</code> points to its API root.</p>
      <button type="button" className="button button-quiet" onClick={onRetry}>Retry</button>
    </div>
  </section>;
}

export function ResearchConsole({ view }: { view: ViewKey }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [toast, setToast] = useState("");
  const [quality, setQuality] = useState<DatasetQuality | null>(null);
  const [pilot, setPilot] = useState<PilotExperiment | null>(null);
  const [completion, setCompletion] = useState<FundamentalsCompletion | null>(null);
  const [qualityError, setQualityError] = useState<string | null>(null);
  const [pilotError, setPilotError] = useState<string | null>(null);
  const [reloadCount, setReloadCount] = useState(0);
  useEffect(() => {
    let active = true;
    setQualityError(null);
    setPilotError(null);
    getLatestDatasetQuality()
      .then((result) => { if (active) setQuality(result); })
      .catch((error: unknown) => {
        if (!active) return;
        setQualityError(error instanceof Error ? error.message : "Dataset quality report is unavailable.");
      });
    getLatestPilotExperiment()
      .then((result) => { if (active) setPilot(result); })
      .catch((error: unknown) => {
        if (!active) return;
        setPilot(null);
        setPilotError(error instanceof Error ? error.message : "Pilot experiment report is unavailable.");
      });
    getLatestFundamentalsCompletion().then((result) => { if (active) setCompletion(result); }).catch(() => { if (active) setCompletion(null); });
    return () => { active = false; };
  }, [reloadCount]);
  const retryLoad = () => setReloadCount((count) => count + 1);
  const showToast = (message: string) => { setToast(message); window.setTimeout(() => setToast(""), 2800); };
  const handleNewExperiment = () => setModalOpen(true);
  const title = NAV_ITEMS.find((item) => item.href.includes(view))?.label ?? "Overview";
  return <div className="app-shell">
    <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}><div className="brand"><LogoMark /><button className="icon-button mobile-close" onClick={() => setSidebarOpen(false)}><X size={17} /></button></div><div className="workspace-switcher"><span className="workspace-avatar">SJ</span><div><b>Samuel Justin</b><small>Research workspace</small></div><ChevronDown size={15} /></div><nav><span className="nav-label">Workspace</span>{NAV_ITEMS.map((item) => { const Icon = iconMap[item.icon as keyof typeof iconMap]; const active = item.href === `/${view}` || (view === "dashboard" && item.href === "/dashboard"); return <a className={active ? "active" : ""} href={item.href} key={item.href} onClick={() => setSidebarOpen(false)}><Icon size={17} /><span>{item.label}</span>{item.label === "Experiments" && <span className="nav-count">3</span>}</a>; })}</nav><div className="sidebar-bottom"><div className={`data-health ${qualityError ? "unavailable" : "review"}`}><span className="health-dot" /><div><b>{qualityError ? "Data status unavailable" : quality ? "Price audit passed" : "Checking dataset"}</b>{quality ? <small>{quality.valid_dol_document_count} documents · liquidity blocked</small> : qualityError ? <button type="button" className="text-button" title={qualityError} onClick={retryLoad}>Retry validation report</button> : <small>Loading validation report</small>}</div></div><a href="#docs"><BookOpen size={16} /> Documentation</a><a href="#settings"><Settings2 size={16} /> Workspace settings</a></div></aside>
    <main className="main-content"><header className="topbar"><button className="icon-button menu-trigger" onClick={() => setSidebarOpen(true)} aria-label="Open navigation"><Menu size={19} /></button><div className="breadcrumb"><span>Workspace</span><span>/</span><b>{title}</b></div><div className="topbar-actions"><span className="demo-pill"><span /> Public-data pilot</span><button className="icon-button" aria-label="Help"><CircleHelp size={17} /></button><button className="icon-button" aria-label="Notifications"><Bell size={17} /><i className="notification-dot" /></button><div className="topbar-avatar">SJ</div></div></header><div className="page-body">{pilotError && view !== "experiments" ? <ApiLoadError message={pilotError} onRetry={retryLoad} /> : <>{view === "dashboard" && <PilotDashboardView pilot={pilot} />}{view === "factors" && <LiveFactorsView pilot={pilot} completion={completion} />}{view === "regimes" && <LiveRegimesView pilot={pilot} />}{view === "portfolio" && <MomentumPortfolioView pilot={pilot} />}{view === "experiments" && <>{pilotError && <ApiLoadError message={pilotError} onRetry={retryLoad} />}<PilotExperimentsView pilot={pilot} onNewExperiment={handleNewExperiment} /></>}</>}</div><footer className="site-footer"><span>NGX Research Console <i>·</i> academic research environment</span><span>Dataset <b>{quality?.dataset_id ?? (qualityError ? "unavailable" : "loading")}</b> <i>·</i> deterministic outputs only</span></footer></main>
    {modalOpen && <NewExperimentModal onClose={() => setModalOpen(false)} onCreated={() => showToast("Experiment saved to the registry")} />}
    {toast && <div className="toast"><span className="check-circle"><Check size={13} /></span>{toast}</div>}
  </div>;
}
