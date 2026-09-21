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
import { getLatestDatasetQuality } from "@/lib/api";
import type { DatasetQuality, FactorKey, ViewKey } from "@/types/research";
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

function PortfolioView() {
  return <><div className="page-heading"><div><div className="eyebrow">RESEARCH / PORTFOLIO</div><h1>Model portfolio</h1><p className="lede">The top ten equal-weighted securities selected at the latest monthly rebalance.</p></div><button className="button button-primary"><BarChart3 size={15} /> Export results</button></div><div className="metric-grid portfolio-metrics"><MetricCard label="Portfolio value" value="₦12.46m" helper="from ₦10.0m initial" icon={TrendingUp} /><MetricCard label="Since inception" value="+24.6%" helper="Jan 2019 — Dec 2025" icon={ArrowUpRight} accent="var(--gold)" /><MetricCard label="Turnover" value="18.4%" helper="latest rebalance" icon={Activity} accent="var(--violet)" /><MetricCard label="Positions" value="10 / 183" helper="eligible universe" icon={Target} accent="var(--coral)" /></div><section className="section-block"><SectionHeader eyebrow="RANKED SECURITIES" title="Holdings & factor scores" action={<button className="button button-quiet"><SlidersHorizontal size={14} /> Configure</button>} /><div className="table-card full-table"><table><thead><tr><th>#</th><th>Security</th><th>Sector</th><th>Composite score</th><th>Weight</th><th>1M return</th><th>Action</th></tr></thead><tbody>{HOLDINGS.concat([{ ticker: "NB", name: "Nigerian Breweries", sector: "Consumer", score: 1.47, weight: 10, change: 1.2 }, { ticker: "ZENITHBANK", name: "Zenith Bank", sector: "Financials", score: 1.41, weight: 10, change: -1.1 }]).map((holding, index) => <tr key={holding.ticker}><td className="muted">{String(index + 1).padStart(2, "0")}</td><td><div className="security-cell"><span className="ticker-avatar">{holding.ticker.slice(0, 2)}</span><div><b>{holding.ticker}</b><small>{holding.name}</small></div></div></td><td>{holding.sector}</td><td><div className="score-bar"><span style={{ width: `${Math.min(100, holding.score * 42)}%` }} /><b>{holding.score.toFixed(2)}</b></div></td><td>{holding.weight.toFixed(1)}%</td><td className={holding.change >= 0 ? "positive" : "negative"}>{formatPercent(holding.change)}</td><td><button className="row-action"><MoreHorizontal size={16} /></button></td></tr>)}</tbody></table></div></section></>;
}

function ExperimentsView({ onNewExperiment }: { onNewExperiment: () => void }) {
  return <><div className="page-heading"><div><div className="eyebrow">RESEARCH / EXPERIMENTS</div><h1>Experiment registry</h1><p className="lede">Every run is reproducible. Configuration, dataset, software version, and outputs stay together.</p></div><button className="button button-primary" onClick={onNewExperiment}><Plus size={16} /> New experiment</button></div><div className="experiment-hero panel"><div className="experiment-hero-copy"><span className="eyebrow">ACTIVE RUN · EXP_01HXYZ</span><h2>Five-factor baseline</h2><p>All 13 research nodes completed successfully on dataset ngx_monthly_v3.</p><div className="progress-track"><span style={{ width: "100%" }} /></div><div className="run-meta"><span><Check size={13} /> Completed 11 Sep 2026, 14:00 UTC</span><span><Database size={13} /> 183 eligible securities</span></div></div><div className="run-score"><span>MODEL RETURN</span><strong>+24.6%</strong><small>1.42 Sharpe · 11.8% max drawdown</small></div></div><section className="section-block"><SectionHeader eyebrow="RUN HISTORY" title="Saved experiments" /><div className="experiment-table table-card"><table><thead><tr><th>Experiment</th><th>Status</th><th>Period</th><th>Dataset</th><th>Result</th><th /></tr></thead><tbody>{EXPERIMENTS.map((experiment) => <tr key={experiment.id}><td><b>{experiment.name}</b><small>{experiment.id}</small></td><td><StatusBadge status={experiment.status} /></td><td>{experiment.period}</td><td><span className="dataset-tag">{experiment.dataset}</span></td><td className="result-cell">{experiment.result}</td><td><button className="text-button">Open <ArrowUpRight size={14} /></button></td></tr>)}</tbody></table></div></section></>;
}

export function ResearchConsole({ view }: { view: ViewKey }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [toast, setToast] = useState("");
  const [quality, setQuality] = useState<DatasetQuality | null>(null);
  const [qualityError, setQualityError] = useState(false);
  useEffect(() => {
    getLatestDatasetQuality().then(setQuality).catch(() => setQualityError(true));
  }, []);
  const showToast = (message: string) => { setToast(message); window.setTimeout(() => setToast(""), 2800); };
  const handleNewExperiment = () => setModalOpen(true);
  const title = NAV_ITEMS.find((item) => item.href.includes(view))?.label ?? "Overview";
  return <div className="app-shell">
    <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}><div className="brand"><LogoMark /><button className="icon-button mobile-close" onClick={() => setSidebarOpen(false)}><X size={17} /></button></div><div className="workspace-switcher"><span className="workspace-avatar">SJ</span><div><b>Samuel Justin</b><small>Research workspace</small></div><ChevronDown size={15} /></div><nav><span className="nav-label">Workspace</span>{NAV_ITEMS.map((item) => { const Icon = iconMap[item.icon as keyof typeof iconMap]; const active = item.href === `/${view}` || (view === "dashboard" && item.href === "/dashboard"); return <a className={active ? "active" : ""} href={item.href} key={item.href} onClick={() => setSidebarOpen(false)}><Icon size={17} /><span>{item.label}</span>{item.label === "Experiments" && <span className="nav-count">3</span>}</a>; })}</nav><div className="sidebar-bottom"><div className={`data-health ${qualityError ? "unavailable" : "review"}`}><span className="health-dot" /><div><b>{qualityError ? "Data status unavailable" : quality ? "Price audit passed" : "Checking dataset"}</b><small>{quality ? `${quality.valid_dol_document_count} documents · liquidity blocked` : "Loading validation report"}</small></div></div><a href="#docs"><BookOpen size={16} /> Documentation</a><a href="#settings"><Settings2 size={16} /> Workspace settings</a></div></aside>
    <main className="main-content"><header className="topbar"><button className="icon-button menu-trigger" onClick={() => setSidebarOpen(true)} aria-label="Open navigation"><Menu size={19} /></button><div className="breadcrumb"><span>Workspace</span><span>/</span><b>{title}</b></div><div className="topbar-actions"><span className="demo-pill"><span /> Public-data pilot</span><button className="icon-button" aria-label="Help"><CircleHelp size={17} /></button><button className="icon-button" aria-label="Notifications"><Bell size={17} /><i className="notification-dot" /></button><div className="topbar-avatar">SJ</div></div></header><div className="page-body">{view === "dashboard" && <DashboardView onNewExperiment={handleNewExperiment} quality={quality} />}{view === "factors" && <FactorsView />}{view === "regimes" && <RegimesView />}{view === "portfolio" && <PortfolioView />}{view === "experiments" && <ExperimentsView onNewExperiment={handleNewExperiment} />}</div><footer className="site-footer"><span>NGX Research Console <i>·</i> academic research environment</span><span>Dataset <b>{quality?.dataset_id ?? "loading"}</b> <i>·</i> deterministic outputs only</span></footer></main>
    {modalOpen && <div className="modal-backdrop" role="dialog" aria-modal="true"><div className="modal"><div className="modal-head"><div><span className="eyebrow">NEW RESEARCH RUN</span><h2>Configure experiment</h2></div><button className="icon-button" onClick={() => setModalOpen(false)} aria-label="Close"><X size={18} /></button></div><label>Experiment name<input defaultValue="Five-factor baseline — copy" /></label><div className="form-grid"><label>Start date<input type="date" defaultValue="2019-01-01" /></label><label>End date<input type="date" defaultValue="2025-12-31" /></label></div><div className="form-grid"><label>Portfolio size<select defaultValue="10"><option>10 securities</option><option>20 securities</option><option>30 securities</option></select></label><label>Regime states<select defaultValue="3"><option>3 states</option><option>2 states</option><option>4 states</option></select></label></div><div className="factor-toggle-list"><span className="eyebrow">ENABLED FACTORS</span>{FACTORS.map((factor) => <div key={factor.key}><span className={`factor-chip ${factor.tone}`}>{factor.short}</span><b>{factor.label}</b><span className="toggle-on"><Check size={12} /></span></div>)}</div><div className="modal-actions"><button className="button button-quiet" onClick={() => setModalOpen(false)}>Cancel</button><button className="button button-primary" onClick={() => { setModalOpen(false); showToast("Experiment saved as draft"); }}><Play size={14} /> Create draft</button></div></div></div>}
    {toast && <div className="toast"><span className="check-circle"><Check size={13} /></span>{toast}</div>}
  </div>;
}
