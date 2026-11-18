// Unlisted presentation for BDC. Mintlify supplies React hooks.
const bdcSlides = [
  ["The opportunity", "Capacity-based lending"],
  ["The challenge", "A fragmented picture. A moving risk."],
  ["The unified process", "Unified data. A stronger underwriting process."],
  ["Research", "AI research for better decisions."],
  ["The permission", "Connect what matters, with clear permission."],
  ["After funding", "Keep the funded decision in view."],
  ["The full proposal", "From business evidence to responsible financing."],
  ["The controls", "Your policy. Your authority. Your borrower."],
  ["The pilot", "Start with one decision worth improving."],
  ["The conversation", "Where could better evidence change a decision?"]
];

const BdcIcon = ({ name, size = 22 }) => {
  const paths = {
    arrow: "M5 12h14m-6-6 6 6-6 6", back: "M19 12H5m6-6-6 6 6 6",
    grid: "M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z",
    expand: "M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5",
    print: "M6 9V3h12v6M6 18H3V9h18v9h-3M6 14h12v7H6z",
    close: "m6 6 12 12M6 18 18 6", check: "m5 12 4 4L19 6",
    bank: "m3 8 9-5 9 5M3 9h18M5 10v8m7-8v8m7-8v8M3 21h18",
    card: "M3 5h18v14H3zM3 10h18M6 15h4",
    shop: "M4 10v11h16V10M2 10l3-7h14l3 7M2 10h20M9 21v-7h6v7",
    book: "M4 3h16v18H4zM8 7h8M8 11h8M8 15h5",
    globe: "M3 12h18M12 3c-5 5-5 13 0 18 5-5 5-13 0-18M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18",
    flow: "M3 12h4l3-8 4 16 3-8h4",
    shield: "m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6zM8 12l3 3 5-6",
    link: "m9 15 6-6M7 14l-2 2a3 3 0 0 0 4 4l4-4M11 8l4-4a3 3 0 0 1 4 4l-2 2",
    document: "M5 3h10l4 4v14H5zM14 3v5h5M9 12h6M9 16h6",
    search: "M10 3a7 7 0 1 0 0 14 7 7 0 0 0 0-14m5 12 6 6",
    layers: "m12 3 10 5-10 5L2 8zM2 12l10 5 10-5M2 16l10 5 10-5",
    lock: "M5 10h14v11H5zM8 10V7a4 4 0 0 1 8 0v3",
    target: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18m0 5a4 4 0 1 0 0 8 4 4 0 0 0 0-8"
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[name] || paths.flow} /></svg>;
};
const BdcHeading = ({ index, intro }) => <header className="bdc-heading"><p className="bdc-eyebrow">{String(index + 1).padStart(2, "0")} / {bdcSlides[index][0]}</p><h2 id={`bdc-title-${index}`}>{bdcSlides[index][1]}</h2>{intro && <p className="bdc-intro">{intro}</p>}</header>;
const BdcNote = ({ children }) => <p className="bdc-note">{children}</p>;
const BdcSteps = ({ items, className = "" }) => <div className={`bdc-steps ${className}`}>{items.map(([title, body, detail], i) => <div key={title}><span className="bdc-index">{String(i + 1).padStart(2, "0")}</span><h3>{title}</h3><p>{body}</p>{detail && <small>{detail}</small>}</div>)}</div>;

// Headline figures supplied by AMLOK for this presentation. The comparison remains proposed.
const bdcResearchComparison = [
  ["Cash-flow category coverage", 70, 88, "%"],
  ["Revenue settlement reconciliation", 75, 90, "%"],
  ["AML false-positive manual-review burden index", 100, 65, ""],
  ["Named counterparty coverage", 65, 86, "%"],
  ["Customer concentration coverage", 60, 84, "%"],
  ["Vendor concentration coverage", 60, 88, "%"],
  ["Debt-repayment miss rate", 4.4, 3.96, "%"],
  ["Debt-service coverage assessability", 70, 85, "%"],
  ["Working-capital cycle visibility", 65, 79, "%"],
  ["Graph relationship precision", 80, 95, "%"],
  ["60-day cash-flow forecast error", 20, 18.5, "%"],
  ["Transaction classification error", 2.8, 2.66, "%"]
];
const bdcResearchApproach = [
  ["Disciplines", "Evaluation, financial language, temporal reasoning, entity relationships and model governance.", [
    ["Evaluation and calibration", "Measure extraction, reconciliation, forecasting and risk signals on task-specific cohorts, with uncertainty and matched baselines."],
    ["Financial language", "Interpret descriptors and document fields in their financial context, including counterparty roles, transaction purpose and bilingual evidence."],
    ["Temporal reasoning", "Represent cash movements and obligations over time, preserving the evidence available at each decision date."],
    ["Entity and event relationships", "Resolve businesses, counterparties and related records without counting one economic event several times."],
    ["Model governance", "Track data provenance, model versions, limitations and the human review required for consequential decisions."]
  ]],
  ["Capabilities", "Document extraction, transaction interpretation, reconciliation, capacity analysis and change detection.", [
    ["Documents and transactions", "Extract structured evidence and interpret financial activity while retaining source references and unresolved fields."],
    ["Connected financial evidence", "Reconcile orders, invoices, payments, settlements and bank entries across authorized systems."],
    ["Relationships and obligations", "Map supported entity links, existing financing, counterparties and customer or supplier concentrations."],
    ["Risk and repayment capacity", "Calculate cash flow, working capital and debt-service measures using versioned formulas and reconciled inputs."],
    ["Post-funding intelligence", "Compare new evidence with the funded baseline and identify changes that warrant institution-led review."]
  ]],
  ["Models", "Specialist language models, temporal event encoders, entity graphs and financial calculation layers.", [
    ["Transaction-language models", "Represent descriptor meaning, purpose and counterparty candidates with supporting evidence spans."],
    ["Temporal event encoders", "Combine amounts, categories, timestamps, source coverage and missingness to study financial behavior."],
    ["Evidence-backed entity graphs", "Represent typed, time-scoped relationships between businesses, facilities, counterparties and economic events."],
    ["Task-specific models and calculations", "Use separate risk, forecasting and change-detection tasks, alongside deterministic financial calculations and grounded explanations."]
  ]],
  ["Philosophy", "Measure the financial task. Validate changes. Keep evidence and institutional judgment connected.", [
    ["Evaluate the decision task", "Judge quality through financial evidence, cohort definitions and operational tradeoffs, rather than a general-purpose benchmark alone."],
    ["Learn through controlled review", "Use authorized analyst feedback to identify improvements; validate changes with historical replay and held-out evaluation before release."],
    ["Keep the institution in control", "Make assumptions, evidence and uncertainty reviewable. The institution owns policy, final approval and intervention."]
  ]]
];
const bdcResearchLogos = [
  ["CIBC", "https://us.cibc.com/content/dam/global-assets/logos/cibc-logos/no-tagline/cibc-logo-colour-142x36.svg"],
  ["Vancity", "https://amlok.io/vancity-logo.svg"],
  ["ATB", "https://amlok.io/atb-logo.svg"],
  ["Laurentian Bank", "https://amlok.io/laurentian-bank-white.svg"],
  ["Trez Capital", "https://www.trezcapital.com/wp-content/themes/trezcapital/img/trez-logo.svg"],
  ["Desjardins", "https://www.desjardins.com/content/dam/images/logos/commun/logo-desjardins-en.svg"],
  ["Canada Drives", "https://www.canadadrives.ca/img/logo/cd-logo-black2x.png"],
  ["goeasy", "https://images.ctfassets.net/fh625txf4dd5/tKuZ2ppr4fF5b5MT2YWfZ/a2cb4fc1d68cf44a1f6553b9b2ad9dc6/goeasy-logo.svg"],
  ["Clearco", "https://cdn.prod.website-files.com/65fde10e62e6a7603e9221cc/660190120ed591c2ca6658f4_clearco-logo-black.webp"],
  ["Romspen", "https://www.romspen.com/wp-content/themes/romspen/dist/assets/img/romspen-logo-color.svg"],
  ["Lendefied", "https://www.lendefied.com/wp-content/uploads/2024/01/Lendefied.gif"]
];
// Qualitative product-scope comparison. Do not convert these descriptions into benchmark scores.
const bdcAIProviders = [
  {
    name: "AMLOK", product: "Insights + Signal", kind: "Connected risk platform",
    cells: [
      ["Connected business evidence", "Banking, payments, commerce, accounting and public records."],
      ["Risk and repayment capacity", "Reconciled evidence, entity relationships and underwriting findings."],
      ["Baseline + reassessment", "Signal follows new evidence and reassesses the funded business."],
      ["Workspace API", "Agreed workflows; the lender retains credit authority."]
    ],
    note: "AMLOK's documented product scope. Data coverage and processing depend on the agreed workflow and authorized sources.",
    sources: [["Insights", "/pricing/insights"], ["Signal", "/pricing/signal"], ["Entity graph", "/research/entity-graph"]]
  },
  {
    name: "OpenAI", product: "GPT family", kind: "General-purpose models",
    cells: [
      ["Documents + tool data", "PDF text and images, files and developer-connected systems."],
      ["Interpretation + reasoning", "Document analysis and application-defined tool outputs."],
      ["Application-defined", "A developer can connect models to a monitoring workflow.*"],
      ["Model API + tools", "The application executes its custom functions and actions."]
    ],
    note: "This column describes model/API building blocks, not every OpenAI product. File inputs and function calling support custom applications; they do not establish a shared lending-performance score.",
    sources: [["File inputs", "https://developers.openai.com/api/docs/guides/file-inputs"], ["Function calling", "https://developers.openai.com/api/docs/guides/function-calling"]]
  },
  {
    name: "Anthropic", product: "Claude family", kind: "General-purpose models",
    cells: [
      ["Documents + tool data", "PDFs, connected sources and financial-data integrations."],
      ["Financial-analysis workflows", "Document interpretation, modeling and research workflows."],
      ["Application-defined", "A developer can connect models to a monitoring workflow.*"],
      ["Model API + tools", "Tool integrations and financial-services workflows."]
    ],
    note: "Claude combines general-purpose document understanding and tools with financial-services workflows. This is a scope comparison, not a judgment of its underwriting accuracy.",
    sources: [["PDF support", "https://platform.claude.com/docs/en/build-with-claude/pdf-support"], ["Tool use", "https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview"], ["Financial services", "https://www.anthropic.com/news/advancing-claude-for-financial-services"]]
  },
  {
    name: "RBC Borealis", product: "ATOM", kind: "Transaction foundation model",
    cells: [
      ["Financial-event sequences", "RBC transaction data and other financial events."],
      ["Behavior + credit capacity", "Temporal representations, predictions and personalization."],
      ["Forecasting + alerts", "NOMI cash-flow forecasts and payment-error warnings."],
      ["RBC applications", "Institution-specific deployment described by RBC."]
    ],
    note: "ATOM is a financial foundation model for asynchronous event sequences. Its documented RBC applications are not equivalent to a third-party lender API or a common AMLOK benchmark.",
    sources: [["ATOM research and applications", "https://rbcborealis.com/applications/atom/"]]
  },
  {
    name: "Prism Data", product: "CashScore + Insights + Pulse", kind: "Cash-flow analytics platform",
    cells: [
      ["Structured bank activity", "Transactions and balances; statement data must be structured first."],
      ["Scores + cash-flow attributes", "CashScore and consumer/SMB income, debt and capacity signals."],
      ["Continuous cash-flow signals", "Pulse tracks changing financial conditions and obligations."],
      ["Analytics APIs", "Attributes and scores feed lender models, rules and workflows."]
    ],
    note: "Prism documents both consumer and SMB cash-flow analysis and continuous monitoring. SMB bank-statement data must be extracted into a supported format before processing.",
    sources: [["SMB Intelligence", "https://www.prismdata.com/smb-intelligence/"], ["CashScore", "https://www.prismdata.com/cashscore/"], ["Pulse", "https://www.prismdata.com/pulse/"]]
  },
  {
    name: "Trust Science", product: "T°Score + CashFlow+", kind: "Credit decisioning platform",
    cells: [
      ["Bureau + alternative data", "Credit signals, borrower information and bank activity."],
      ["Credit + income assessment", "Explainable scores, reason codes and cash-flow insights."],
      ["Portfolio re-underwriting", "Portfolio credit-quality analysis is described; cadence is not specified."],
      ["Lender decisioning platform", "Credit Bureau+, scoring and bank-data intelligence."]
    ],
    note: "Trust Science describes consumer credit scoring, cash-flow analysis and portfolio re-underwriting. The reviewed source does not specify a continuous monitoring cadence; this does not establish absence of that capability.",
    sources: [["Platform and portfolio services", "https://trustscience.com/"], ["T°Score", "https://trustscience.com/t-score"], ["CashFlow+", "https://trustscience.com/cashflow"]]
  }
];
// Internal scenario estimates requested for planning, not observed benchmark scores.
// Missing values must stay null; never connect a line across an unassessed dimension.
const bdcAIDimensions = [
  ["Document", "understanding"], ["Transaction", "semantics"], ["Cross-source", "reconciliation"],
  ["Entity and", "obligation graph"], ["Risk and", "repayment capacity"], ["Continuous", "reassessment"]
];
const bdcAIProjections = [
  { name: "AMLOK", product: "Target profile", color: "#052698", dash: undefined, scores: [4, 5, 5, 5, 5, 5], assumption: "Target fit for the proposed complete workflow: source-linked extraction, banking and business-system evidence, entity relationships and Signal reassessment. These are planning targets, not observed scores." },
  { name: "OpenAI", product: "GPT family", color: "#d17823", dash: "10 5", scores: [5, 4, 3, 3, 4, 2], assumption: "General-purpose document and reasoning strengths, with lender-specific orchestration assumed for reconciliation, graph persistence and continuous reassessment. This is an internal scenario estimate." },
  { name: "Anthropic", product: "Claude family", color: "#8758b8", dash: "2 5", scores: [5, 4, 3, 3, 4, 2], assumption: "The same planning profile as OpenAI: strong document/reasoning fit, with configured financial workflows and tools. The available evidence does not justify a numerical distinction between these families." },
  { name: "RBC ATOM", product: "Transaction model", color: "#008b9a", dash: "12 4 2 4", scores: [null, 5, null, null, 4, 4], assumption: "Transaction-centered projection from ATOM's published credit-capacity, forecasting and alert use cases. Document extraction, cross-system reconciliation and entity-graph fit remain unassessed." },
  { name: "Prism Data", product: "CashScore / Insights / Pulse", color: "#c34370", dash: "6 4", scores: [2, 5, 2, null, 5, 5], assumption: "Bank cash-flow analysis and monitoring drive the projection. External document conversion and banking-only consolidation limit the assumed fit to the broader cross-system workflow. Entity-graph fit remains unassessed." },
  { name: "Trust Science", product: "T°Score / CashFlow+", color: "#557644", dash: "14 6", scores: [null, 4, null, null, 5, 4], assumption: "Credit scoring, income analysis and portfolio re-underwriting drive the projection. The monitoring cadence is unspecified. Document, cross-system reconciliation and entity-graph fit remain unassessed." }
];
const BdcAIComparison = () => {
  const [chartView, setChartView] = useState("radar");
  const [visible, setVisible] = useState([true, true, true, true, true, true]);
  const [focused, setFocused] = useState(null);
  const radarPoint = (index, score, radius = 172) => {
    const angle = -Math.PI / 2 + index * Math.PI / 3;
    return [410 + Math.cos(angle) * radius * score / 5, 236 + Math.sin(angle) * radius * score / 5];
  };
  const linePoint = (index, score) => [110 + index * 157, 300 - score * 48];
  const position = chartView === "radar" ? radarPoint : linePoint;
  const series = bdcAIProjections.map((profile, seriesIndex) => visible[seriesIndex] ? <g key={profile.name} className="bdc-ai-series" opacity={focused === null || focused === seriesIndex ? 1 : .15}>
    {seriesIndex === 0 && chartView === "radar" && <polygon points={profile.scores.map((score, index) => radarPoint(index, score).join(",")).join(" ")} fill={profile.color} fillOpacity=".055" />}
    {profile.scores.map((score, index) => {
      const next = index + 1 < profile.scores.length ? index + 1 : chartView === "radar" ? 0 : null;
      if (next === null || score === null || profile.scores[next] === null) return null;
      const from = position(index, score), to = position(next, profile.scores[next]);
      return <line key={`line-${index}`} x1={from[0]} y1={from[1]} x2={to[0]} y2={to[1]} stroke={profile.color} strokeWidth={seriesIndex === 0 ? 3.5 : seriesIndex === 1 ? 3 : 2.5} strokeDasharray={profile.dash} strokeLinecap="round" />;
    })}
    {profile.scores.map((score, index) => {
      if (score === null) return null;
      const point = position(index, score);
      return <circle key={`point-${index}`} cx={point[0]} cy={point[1]} r={seriesIndex === 0 ? 5 : 3.5} fill={seriesIndex === 0 ? profile.color : "#fff"} stroke={profile.color} strokeWidth="2"><title>{profile.name}: {bdcAIDimensions[index].join(" ")} - projected fit {score}/5</title></circle>;
    })}
  </g> : null);
  return <div className="bdc-ai-comparison">
    <div className="bdc-ai-projection-heading"><div><span className="bdc-ai-projection-tag">Projected comparison</span><h3>Financial intelligence across six dimensions.</h3><p>Projected workflow fit - 0 to 5 planning scale.</p></div><div className="bdc-ai-view-switch" role="group" aria-label="Comparison chart view"><button type="button" aria-pressed={chartView === "radar"} onClick={() => setChartView("radar")}>Radar</button><button type="button" aria-pressed={chartView === "dimensions"} onClick={() => setChartView("dimensions")}>By dimension</button></div></div>
    <div className="bdc-ai-projection-layout">
      <div className={`bdc-ai-projection-plot ${chartView === "dimensions" ? "bdc-ai-projection-wide" : ""}`} role="region" aria-label="Projected comparison graphic" tabIndex={0}>
        <svg viewBox={chartView === "radar" ? "0 0 820 475" : "0 0 1010 390"} role="img" aria-labelledby="bdc-ai-chart-title bdc-ai-chart-description">
          <title id="bdc-ai-chart-title">Projected workflow fit for AMLOK, OpenAI, Anthropic, RBC ATOM, Prism Data and Trust Science</title>
          <desc id="bdc-ai-chart-description">Internal planning estimates, not measured model performance. All series use a 0 to 5 fit rubric. Missing values are unassessed and remain gaps. The score table and assumptions are available below the chart.</desc>
          {chartView === "radar" ? <g>
            {[1, 2, 3, 4, 5].map(level => <g key={level}><polygon points={bdcAIDimensions.map((_, index) => radarPoint(index, level).join(",")).join(" ")} className="bdc-ai-radar-ring" /><text x="418" y={236 - level * 172 / 5 + 4} className="bdc-ai-scale-label">{level}</text></g>)}
            {bdcAIDimensions.map((label, index) => { const edge = radarPoint(index, 5), text = radarPoint(index, 5, 210); const align = index === 0 || index === 3 ? "middle" : index < 3 ? "start" : "end"; return <g key={label[0]}><line x1="410" y1="236" x2={edge[0]} y2={edge[1]} className="bdc-ai-radar-spoke" /><text x={text[0]} y={text[1] - 6} textAnchor={align} className="bdc-ai-axis-title"><tspan x={text[0]}>{label[0]}</tspan><tspan x={text[0]} dy="18">{label[1]}</tspan></text></g>; })}
          </g> : <g>
            {[0, 1, 2, 3, 4, 5].map(level => <g key={level}><line x1="85" y1={linePoint(0, level)[1]} x2="920" y2={linePoint(0, level)[1]} className="bdc-ai-radar-spoke" /><text x="68" y={linePoint(0, level)[1] + 4} textAnchor="end" className="bdc-ai-scale-label">{level}</text></g>)}
            {bdcAIDimensions.map((label, index) => <text key={label[0]} x={linePoint(index, 0)[0]} y="335" textAnchor="middle" className="bdc-ai-axis-title"><tspan x={linePoint(index, 0)[0]}>{label[0]}</tspan><tspan x={linePoint(index, 0)[0]} dy="18">{label[1]}</tspan></text>)}
          </g>}
          {series}
        </svg>
      </div>
      <aside className="bdc-ai-projection-legend"><p>Compared approaches</p><div role="group" aria-label="Visible comparison series">{bdcAIProjections.map((profile, index) => <button type="button" key={profile.name} aria-pressed={visible[index]} onClick={() => setVisible(current => current.map((item, i) => i === index ? !item : item))} onMouseEnter={() => setFocused(index)} onMouseLeave={() => setFocused(null)} onFocus={() => setFocused(index)} onBlur={() => setFocused(null)}><svg width="32" height="12" viewBox="0 0 32 12" aria-hidden="true"><line x1="1" y1="6" x2="31" y2="6" stroke={profile.color} strokeWidth="2.5" strokeDasharray={profile.dash} /><circle cx="16" cy="6" r="3" fill="#fff" stroke={profile.color} strokeWidth="1.5" /></svg><span><strong>{profile.name}</strong><small>{profile.product}</small></span></button>)}</div><button type="button" className="bdc-ai-show-all" onClick={() => { setVisible([true, true, true, true, true, true]); setFocused(null); }}>Show all</button><small className="bdc-ai-legend-help">Select to show or hide. Hover to highlight.<br />Gaps = unassessed, not zero.</small></aside>
    </div>
    <p className="bdc-ai-projection-caption">Internal planning estimates, not measured model performance. AMLOK is a target profile; the other profiles are scenario assumptions. Equal scores can overlap.</p>
    <details className="bdc-ai-projection-method"><summary>Planning scores and assumptions</summary><p>This is a subjective fit rubric for the defined workflow, not accuracy, probability or a normalized benchmark. 5 = target end-to-end fit; 4 = strong fit with configuration; 3 = partial fit requiring substantial integration; 2 = limited direct fit; 1 = minimal direct fit; 0 = no fit in the scenario. A blank value is unassessed. There is no aggregate score or estimated confidence interval.</p><div className="bdc-ai-matrix-scroll"><table className="bdc-ai-score-table"><caption className="bdc-sr-only">Projected workflow-fit scores, not measured benchmark results</caption><thead><tr><th scope="col">Approach</th>{bdcAIDimensions.map(label => <th scope="col" key={label[0]}>{label.join(" ")}</th>)}</tr></thead><tbody>{bdcAIProjections.map(profile => <tr key={profile.name}><th scope="row">{profile.name}</th>{profile.scores.map((score, index) => <td key={index}>{score === null ? <abbr title="Unassessed">-</abbr> : score}</td>)}</tr>)}</tbody></table></div><div className="bdc-ai-assumptions">{bdcAIProjections.map(profile => <section key={profile.name}><h4>{profile.name}</h4><p>{profile.assumption}</p></section>)}</div></details>
  <details className="bdc-ai-table-details"><summary>Read the full provider comparison</summary><div className="bdc-ai-matrix-scroll" role="region" aria-label="AI approaches comparison matrix" tabIndex={0}>
    <table className="bdc-ai-matrix"><caption className="bdc-sr-only">Published capabilities of AMLOK, OpenAI, Anthropic, RBC ATOM, Prism Data and Trust Science. This is not a performance ranking.</caption>
      <thead><tr><th scope="col">Comparison<br />dimension</th>{bdcAIProviders.map((provider, i) => <th scope="col" key={provider.name} className={i === 0 ? "bdc-ai-amlok" : undefined}><strong>{provider.name}</strong><span>{provider.product}</span><small>{provider.kind}</small></th>)}</tr></thead>
      <tbody>{[["layers", "Data inputs"], ["search", "Financial outputs"], ["flow", "Ongoing intelligence"], ["link", "Integration model"]].map(([icon, label], index) => <tr key={label}><th scope="row"><BdcIcon name={icon} size={19} /><span>{label}</span></th>{bdcAIProviders.map((provider, i) => <td key={provider.name} className={i === 0 ? "bdc-ai-amlok" : undefined}><strong>{provider.cells[index][0]}</strong><span>{provider.cells[index][1]}</span></td>)}</tr>)}</tbody>
    </table>
  </div></details>
  <details className="bdc-ai-sources"><summary>Sources and comparison scope</summary><div>{bdcAIProviders.map(provider => <section key={provider.name}><h4>{provider.name}</h4><p>{provider.note}</p><ul>{provider.sources.map(([label, href]) => <li key={href}><a href={href} target="_blank" rel="noopener noreferrer">{label}<BdcIcon name="arrow" size={12} /></a></li>)}</ul></section>)}</div></details>
  <a className="bdc-ai-protocol" href="/research/frontier-benchmark" target="_blank" rel="noopener noreferrer">How a measured performance comparison is evaluated<BdcIcon name="arrow" size={14} /></a>
</div>;
};
const BdcResearch = () => {
  const [view, setView] = useState("comparison");
  const dialogRef = useRef(null), openerRef = useRef(null);
  const openDetails = (next, event) => { openerRef.current = event.currentTarget; setView(next); dialogRef.current?.showModal(); };
  const closeDetails = () => dialogRef.current?.close();
  return <div className="bdc-research-content">
    <div className="bdc-research-corpus">
      <p className="bdc-eyebrow">AMLOK-reported research</p>
      <dl className="bdc-research-metrics">{[["275,019", "Closed deals studied"], ["6,322,690", "Metadata records"], ["1,300", "Average data points per business"]].map(([value, label]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
      <div className="bdc-research-logos" role="group" aria-label="Financial institutions represented in the research">
        <span className="bdc-research-td" role="img" aria-label="TD Bank"><img src="https://www.td.com/content/dam/tdb/images/navigation-header-and-footer/td-logo-desktop.png" alt="" aria-hidden="true" /><span aria-hidden="true">Bank</span></span>
        {bdcResearchLogos.map(([name, src]) => <img key={name} src={src} alt={name} />)}
      </div>
    </div>
    <div className="bdc-research-findings" aria-label="AMLOK-reported research findings">{[["40% → 82%", "Assessable information"], ["60-85%", "Unreadable transaction value resolved"], ["25-45%", "Signal-bearing defaults flagged"], ["6-8 weeks", "Earlier distress detection"]].map(([value, label]) => <div key={label}><strong>{value}</strong><p>{label}</p></div>)}</div>
    <dl className="bdc-research-functions">{bdcResearchApproach.find(([title]) => title === "Capabilities")[2].map(([title, description]) => <div key={title}><dt>{title}</dt><dd>{description}</dd></div>)}</dl>
    <div className="bdc-research-actions"><div><button type="button" onClick={e => openDetails("landscape", e)}>AI comparison<BdcIcon name="arrow" size={16} /></button><button type="button" onClick={e => openDetails("comparison", e)}>12 comparison measures<BdcIcon name="arrow" size={16} /></button></div></div>
    <dialog className="bdc-research-dialog" data-view={view} ref={dialogRef} aria-labelledby="bdc-research-details-title" onClose={() => openerRef.current?.focus()} onClick={e => { if (e.target === e.currentTarget) closeDetails(); }}>
      <div className="bdc-research-dialog-header"><div><p className="bdc-eyebrow">AMLOK / Research</p><h2 id="bdc-research-details-title">{view === "landscape" ? "Financial AI comparison" : "Research details"}</h2></div><button type="button" onClick={closeDetails} aria-label="Close research details"><BdcIcon name="close" /></button></div>
      <div className="bdc-research-switch" role="group" aria-label="Research detail view"><button type="button" aria-pressed={view === "landscape"} onClick={() => setView("landscape")}>AI comparison</button><button type="button" aria-pressed={view === "comparison"} onClick={() => setView("comparison")}>Proposed comparison</button><button type="button" aria-pressed={view === "approach"} onClick={() => setView("approach")}>Research approach</button></div>
      <div hidden={view !== "landscape"}><BdcAIComparison /></div>
      <div hidden={view !== "comparison"} className="bdc-research-comparison">
        <h3>Connected-data validation</h3><p>Proposed comparison from the AMLOK research summary. Values are approximate; relative change is calculated as (AMLOK - baseline) / baseline.</p>
        <div className="bdc-research-table-scroll" role="region" aria-label="Scrollable proposed comparison" tabIndex={0}><table><caption className="bdc-sr-only">Proposed connected-data comparison across 12 measurement dimensions</caption><thead><tr><th scope="col">Measurement dimension</th><th scope="col">Baseline</th><th scope="col">AMLOK (proposed)</th><th scope="col">Relative change</th></tr></thead><tbody>{bdcResearchComparison.map(([label, baseline, amlok, unit]) => { const delta = (amlok - baseline) / baseline * 100; return <tr key={label}><th scope="row">{label}</th><td>{baseline.toFixed(2)}{unit}</td><td>≈{amlok.toFixed(2)}{unit}</td><td>≈{delta > 0 ? "+" : ""}{delta.toFixed(2)}%</td></tr>; })}</tbody></table></div>
        <p className="bdc-research-detail-note">The AML measure is a normalized manual-review burden index (baseline = 100), not verification accuracy, review time or cost. Percentage change is distinct from a percentage-point difference.</p>
      </div>
      <div hidden={view !== "approach"} className="bdc-research-approach"><p>Research focuses on financial understanding for full underwriting and ongoing monitoring. Each task has its own evidence, evaluation population and intended use.</p><div>{bdcResearchApproach.map(([title, summary, details]) => <section key={title}><h3>{title === "Models" ? "Model architecture" : title}</h3><dl>{details.map(([label, detail]) => <div key={label}><dt>{label}</dt><dd>{detail}</dd></div>)}</dl></section>)}</div><p className="bdc-research-detail-note">The headline figures are supplied AMLOK research results. The public research documentation describes separate structured-loan and financial-document baseline studies.</p><a href="/research" target="_blank" rel="noopener noreferrer">Explore the research documentation<BdcIcon name="arrow" size={16} /></a></div>
    </dialog>
  </div>;
};

const BdcPermission = () => {
  const [provider, setProvider] = useState("Stripe");
  const [monitoring, setMonitoring] = useState(false);
  const sources = [
    { name: "Stripe", icon: "card", records: "Payments, refunds, disputes and payouts", purpose: "Assess net receipts and settlement patterns" },
    { name: "Shopify", icon: "shop", records: "Orders, sales, cancellations and returns", purpose: "Understand sales quality and return patterns" },
    { name: "Accounting", icon: "book", records: "Invoices, invoice payments, receivables and payables", purpose: "Assess collections, payment terms and operating commitments" }
  ];
  const source = sources.find(item => item.name === provider);
  return <div className="bdc-demo"><div className="bdc-demo-bar"><span><BdcIcon name="lock" size={18} />Data permission preview</span><span className="bdc-tag">Demo only</span></div><div className="bdc-permission-body"><p className="bdc-mini-label">Choose a relevant source</p><div className="bdc-provider-switch" role="group" aria-label="Example data source">{sources.map(item => <button key={item.name} type="button" onClick={() => setProvider(item.name)} aria-pressed={provider === item.name}><BdcIcon name={item.icon} size={19} />{item.name}</button>)}</div><dl className="bdc-permission-list"><div><dt>Records</dt><dd>{source.records}</dd></div><div><dt>Purpose</dt><dd>{source.purpose}</dd></div><div><dt>Access</dt><dd>Read-only. No movement of money or changes to source records.</dd></div><div><dt>History</dt><dd>12-month example, subject to available history and permissions</dd></div></dl><label className="bdc-consent"><input type="checkbox" checked={monitoring} onChange={e => setMonitoring(e.target.checked)} /><span><strong>Include ongoing monitoring</strong><small>Separate from this assessment. Scope, duration and refresh schedule are agreed with the lender.</small></span></label><p className="bdc-permission-state" role="status">{monitoring ? "Preview: assessment + ongoing monitoring" : "Preview: assessment only"}</p></div></div>;
};

export const BdcPresentation = () => {
  const [current, setCurrent] = useState(0);
  const [fullscreen, setFullscreen] = useState(false);
  const [notice, setNotice] = useState("");
  const rootRef = useRef(null), stageRef = useRef(null), overviewRef = useRef(null), overviewButtonRef = useRef(null);
  const goTo = useCallback(index => {
    const next = Math.max(0, Math.min(bdcSlides.length - 1, index));
    setCurrent(next);
    window.history.replaceState(null, "", `#slide-${String(next + 1).padStart(2, "0")}`);
    if (stageRef.current) stageRef.current.scrollTop = 0;
  }, []);
  const closeOverview = () => { overviewRef.current?.close(); overviewButtonRef.current?.focus(); };
  useEffect(() => {
    const readHash = () => { const match = window.location.hash.match(/^#slide-(\d{1,2})$/); if (match) setCurrent(Math.max(0, Math.min(bdcSlides.length - 1, Number(match[1]) - 1))); };
    readHash(); window.addEventListener("hashchange", readHash);
    const onFullscreen = () => setFullscreen(Boolean(document.fullscreenElement));
    document.addEventListener("fullscreenchange", onFullscreen);
    return () => { window.removeEventListener("hashchange", readHash); document.removeEventListener("fullscreenchange", onFullscreen); };
  }, []);
  useEffect(() => {
    const onKey = e => {
      if (e.altKey || e.ctrlKey || e.metaKey || overviewRef.current?.open || e.target?.closest("input,select,textarea,[contenteditable=true],.bdc-provider-switch,.bdc-research-dialog")) return;
      if (["ArrowRight", "PageDown", "ArrowLeft", "PageUp", "Home", "End"].includes(e.key)) e.preventDefault();
      if (e.key === "ArrowRight" || e.key === "PageDown") goTo(current + 1);
      if (e.key === "ArrowLeft" || e.key === "PageUp") goTo(current - 1);
      if (e.key === "Home") goTo(0);
      if (e.key === "End") goTo(bdcSlides.length - 1);
    };
    document.addEventListener("keydown", onKey); return () => document.removeEventListener("keydown", onKey);
  }, [current, goTo]);
  const toggleFullscreen = async () => {
    try { if (document.fullscreenElement) await document.exitFullscreen(); else if (rootRef.current?.requestFullscreen) await rootRef.current.requestFullscreen(); else setNotice("Use your browser's full-screen option on this device."); }
    catch { setNotice("Use your browser's full-screen option on this device."); }
  };
  return <main id="demobdc-deck" className="not-prose" ref={rootRef} aria-label="AMLOK presentation for BDC">
    <header className="bdc-topbar"><a href="#slide-01" onClick={e => { e.preventDefault(); goTo(0); }} aria-label="AMLOK presentation, first slide"><img src="/logo/amlok-logo-blue.svg" alt="AMLOK" width="139" height="26" /></a><div className="bdc-meeting-label">Prepared for BDC<span>Capacity-based lending</span></div><div className="bdc-toolbar"><button ref={overviewButtonRef} type="button" onClick={() => overviewRef.current?.showModal()} aria-label="Open slide overview" title="Slide overview"><BdcIcon name="grid" size={18} /><span>Overview</span></button><button type="button" onClick={() => window.print()} aria-label="Print or save presentation as PDF" title="Print or save PDF"><BdcIcon name="print" size={18} /></button><button type="button" onClick={toggleFullscreen} aria-label={fullscreen ? "Exit full screen" : "Enter full screen"} title="Full screen"><BdcIcon name="expand" size={18} /></button></div></header>
    <div className="bdc-sr-only" aria-live="polite">Slide {current + 1} of {bdcSlides.length}: {bdcSlides[current][1]}</div>
    {notice && <div className="bdc-notice" role="status">{notice}<button type="button" onClick={() => setNotice("")} aria-label="Dismiss message"><BdcIcon name="close" size={16} /></button></div>}
    <div className="bdc-stage" ref={stageRef}>
      <section className="bdc-slide bdc-cover" hidden={current !== 0} aria-labelledby="bdc-title-0"><div className="bdc-cover-copy"><p className="bdc-eyebrow">AMLOK / A conversation with BDC</p><h1 id="bdc-title-0">Risk is a movie,<br /><span>not a photo.</span></h1><p className="bdc-cover-subtitle">Capacity-based lending<br />for Canadian businesses.</p><p className="bdc-cover-description">Understand business risk and repayment capacity.<br />Identify the evidence that could change the offer.<br />Follow the business after funding.</p><div className="bdc-cover-meta"><span>Deal underwriting</span><span>Portfolio monitoring</span><span>Risk intelligence</span></div></div><div className="bdc-lifecycle-art" aria-label="Evidence connects underwriting, funding and monitoring"><div className="bdc-art-kicker">A continuous view of capacity</div><div className="bdc-orbit" /><div className="bdc-orbit bdc-orbit-small" /><svg className="bdc-art-line" viewBox="0 0 500 320" fill="none" aria-hidden="true"><path d="M10 252C82 252 90 160 165 175S248 80 320 100 401 53 490 45" stroke="white" strokeWidth="2" /><path d="M10 270C88 270 105 200 170 216S258 142 322 148 411 101 490 96" stroke="white" strokeOpacity=".2" strokeWidth="2" strokeDasharray="5 7" /><circle cx="165" cy="175" r="8" fill="white" /><circle cx="320" cy="100" r="8" fill="white" /><circle cx="490" cy="45" r="8" fill="white" /></svg>{[["search", "Understand", "Verified evidence"], ["target", "Assess", "Supported capacity"], ["flow", "Follow", "Changes over time"]].map(([icon, label, title], i) => <div className={`bdc-art-node bdc-node-${i}`} key={label}><BdcIcon name={icon} /><span>{label}<strong>{title}</strong></span></div>)}<span className="bdc-art-foot">From origination to renewal</span></div></section>

      <section className="bdc-slide bdc-challenge" hidden={current !== 1} aria-labelledby="bdc-title-1">
        <BdcHeading index={1} intro="The gaps span the evidence, the assessment of repayment capacity and the ability to follow the business after funding." />
        <div className="bdc-challenge-columns">
          {[
            ["layers", "Fragmented evidence", [
              ["Disconnected sources", "Institution, banking, accounting, payment and commerce records use different formats, identifiers and periods."],
              ["Repeated manual work", "Collection, extraction and reconciliation repeat. Transfers, loan proceeds, one-off receipts and duplicates obscure operating cash."],
              ["An unclear decision path", "Missing evidence, lending criteria and human-review exceptions need to connect to the offer and the next borrower request."]
            ]],
            ["target", "Uncertain repayment capacity", [
              ["Different cash cycles", "Retail: settlements, fees, returns. Services: invoice terms, overdue collections. Manufacturing: inventory, production, supplier terms."],
              ["More than revenue", "Recurring cash, receivables, payables, debt, advances and operating commitments define available capacity."],
              ["Downside and dependencies", "Cash timing, seasonality, customer or supplier concentration, weaker demand and higher costs shape repayment headroom."]
            ]],
            ["flow", "Limited continuity", [
              ["Snapshots age", "Sales, liquidity and new financing change between assessment, funding and renewal."],
              ["Deterioration or improvement is missed", "Stress can precede a missed payment. Stronger cash flow or lower debt can warrant a fresh capacity review."],
              ["Alerts need context", "Link changes to the funded baseline, source evidence and policy. Distinguish missing data from financial distress."]
            ]]
          ].map(([icon, title, items], i) => <div className="bdc-challenge-column" key={title}><div className="bdc-challenge-column-header"><BdcIcon name={icon} size={23} /><span>{String(i + 1).padStart(2, "0")}</span></div><h3>{title}</h3><div className="bdc-challenge-points">{items.map(([label, detail]) => <div key={label}><strong>{label}</strong><p>{detail}</p></div>)}</div></div>)}
        </div>
        <div className="bdc-challenge-impact"><strong>The consequence</strong><p>Slower decisions, more borrower effort, misjudged risk and capacity, and missed opportunities to intervene or reassess.</p></div>
      </section>

      <section className="bdc-slide bdc-unified" hidden={current !== 2} aria-labelledby="bdc-title-2">
        <BdcHeading index={2} />
        <div className="bdc-unification-map">
          <div className="bdc-unification-sources" aria-label="Connected data sources">
            {[
              ["bank", "Financial institution", "Applications, facilities, repayments"],
              ["flow", "Banking", "Transactions, balances, obligations"],
              ["card", "Payments and commerce", "Orders, payouts, returns, refunds"],
              ["book", "Accounting and operations", "Financials, invoices, payables, inventory"],
              ["globe", "Public context", "Entity and business records"]
            ].map(([icon, title, detail]) => <div key={title}><BdcIcon name={icon} size={19} /><span><strong>{title}</strong><small>{detail}</small></span></div>)}
          </div>
          <div className="bdc-unification-arrow"><BdcIcon name="arrow" size={30} /></div>
          <div className="bdc-unification-engine">
            <p className="bdc-eyebrow">AMLOK Insights / One unified process</p>
            <h3>A verified business picture</h3>
            <div>{[
              ["link", "Resolve entities and map relationships"],
              ["layers", "Normalize and reconcile activity across sources"],
              ["search", "Identify duplicates, inconsistencies and missing evidence"],
              ["document", "Link findings to source records and lender policy"]
            ].map(([icon, title]) => <span key={title}><BdcIcon name={icon} size={17} />{title}</span>)}</div>
          </div>
        </div>
        <div className="bdc-unified-outcomes">
          {[
            ["Faster", "Automate manual underwriting work", "Reduce document review, data gathering, reconciliation and repetitive application checks."],
            ["Consistent", "Policy-aligned decisions", "Apply the same lending criteria across applications, channels and reviewers, with human review of exceptions."],
            ["Traceable", "Full decision lineage", "Connect each recommendation to its source data, policy rules, supporting evidence and recorded human actions."]
          ].map(([title, subtitle, body]) => <div key={title}><h3>{title}</h3><strong>{subtitle}</strong><p>{body}</p></div>)}
        </div>
        <BdcNote>Business-system access is borrower-permissioned. Your institution retains final credit authority.</BdcNote>
      </section>

      <section className="bdc-slide bdc-research" hidden={current !== 3} aria-labelledby="bdc-title-3"><BdcHeading index={3} intro={<>Our Research Lab develops proprietary models, benchmarks and continuous-learning systems<br />for high-risk banking workflows — where general-purpose AI still falls short.</>} /><BdcResearch /></section>

      <section className="bdc-slide" hidden={current !== 4} aria-labelledby="bdc-title-4"><BdcHeading index={4} /><div className="bdc-permission-layout"><div className="bdc-consent-story"><p className="bdc-eyebrow">Borrower-controlled access</p><h3>A specific purpose.<br />A clear scope.<br />A separate choice.</h3><ul>{["Explain the underwriting question.", "Show which records will be accessed.", "Separate assessment from ongoing monitoring.", "Explain disconnection and its implications."].map(t => <li key={t}><BdcIcon name="check" size={17} />{t}</li>)}</ul><p>Refresh depends on the source, permissions and agreed synchronization schedule. A disconnected source is a coverage issue, not proof of financial distress.</p></div><BdcPermission /></div><BdcNote>Interactive preview only. These controls do not connect accounts or record actual borrower consent.</BdcNote></section>

      <section className="bdc-slide" hidden={current !== 5} aria-labelledby="bdc-title-5"><BdcHeading index={5} intro="AMLOK Signal monitors changes and reassesses the business against the evidence behind the funded decision." /><div className="bdc-monitor-flow"><div className="bdc-baseline"><p className="bdc-eyebrow">Funded baseline</p><BdcIcon name="document" size={35} /><h3>Preserve the rationale</h3><p>Approved assumptions, financial evidence, conditions and policy context.</p></div><div className="bdc-monitor-events"><p className="bdc-eyebrow">Illustrative change signals</p>{[["flow", "Cash generation changes", "Compare receipts, costs and liquidity."], ["layers", "Risk and capacity shift", "Review new debt, concentrations or stronger repayment headroom."], ["link", "Evidence becomes unavailable", "Flag incomplete coverage separately."]].map(([icon, title, text]) => <div key={title}><BdcIcon name={icon} size={19} /><span><strong>{title}</strong>{text}</span></div>)}</div><div className="bdc-intervention"><p className="bdc-eyebrow">Lender review</p><h3>Know when <br />to look closer.</h3><p>Prioritize risk, capacity and renewal reviews with changed facts and affected assumptions.</p><span className="bdc-tag">Institution-led intervention</span></div></div><BdcNote>Signal includes change-driven reassessment. The institution handles borrower outreach and action in its own systems. Monitoring does not automatically reprice a signed facility.</BdcNote></section>

      <section className="bdc-slide bdc-proposal" hidden={current !== 6} aria-labelledby="bdc-title-6">
        <BdcHeading index={6} intro="A proposed Credit Capacity experience that connects underwriting, financing choices and post-funding intelligence." />
        <div className="bdc-proposal-flow">
          {[
            ["layers", "Connect evidence", "Institution data, permissioned business systems and relevant public context."],
            ["link", "Understand the business", "Reconcile activity, map relationships and surface missing or conflicting evidence."],
            ["search", "Assess risk and capacity", "Evaluate cash flow, obligations, concentrations and downside scenarios."],
            ["target", "Test financing options", "Apply lender rules to amount, price, term, repayment structure and conditions."],
            ["flow", "Reassess over time", "Track the funded baseline and identify changes that warrant review."]
          ].map(([icon, title, detail], i) => <div key={title}><div className="bdc-proposal-step"><span>{String(i + 1).padStart(2, "0")}</span><BdcIcon name={icon} size={22} /></div><h3>{title}</h3><p>{detail}</p></div>)}
        </div>
        <div className="bdc-product-summary"><div><p className="bdc-eyebrow">AMLOK Insights</p><strong>Full underwriting</strong><span>Evidence, risk, capacity and decision support.</span></div><div><p className="bdc-eyebrow">AMLOK Signal</p><strong>Monitoring and reassessment</strong><span>New information and changing business conditions.</span></div></div>
        <div className="bdc-challenge-impact"><BdcIcon name="shield" size={21} /><strong>The institution stays in control</strong><p>Policy, final approval, borrower relationships and intervention.</p></div>
        <BdcNote>Delivered through existing lending workflows using APIs, webhooks and traceable evidence. Technical discovery confirms integration scope.</BdcNote>
      </section>

      <section className="bdc-slide" hidden={current !== 7} aria-labelledby="bdc-title-7"><BdcHeading index={7} intro="Define the boundaries before introducing any borrower-facing financing pathway." /><div className="bdc-control-grid">{[["shield", "Credit and commercial control", "You own product eligibility, risk appetite, pricing rules, delegated authority and final approval."], ["lock", "Permission and purpose", "Access the minimum relevant information with defined purposes, retention and monitoring scope."], ["document", "Traceable assessments", "Keep source evidence, data freshness, assumptions and policy context available for review."], ["target", "Controlled action", "Route findings to your teams. Your institution owns outreach, agreements, funding and intervention."]].map(([icon, title, body]) => <div key={title}><BdcIcon name={icon} size={30} /><h3>{title}</h3><p>{body}</p></div>)}</div><div className="bdc-control-bottom"><strong>Evidence informs. Your institution decides.</strong><span>Validate privacy, security, model risk and operational requirements during discovery.</span></div></section>

      <section className="bdc-slide" hidden={current !== 8} aria-labelledby="bdc-title-8"><BdcHeading index={8} intro="A proposed BDC pilot: one financing product, one policy question and one or two relevant data sources." /><BdcSteps className="bdc-phases" items={[["Define", "Select a decision that verified evidence could change.", "Agree the rules, cohort, access and success measures."], ["Evaluate", "Review authorized historical cases using information available at decision time.", "Compare against the existing process without future-data leakage."], ["Pilot", "Run in shadow mode, then introduce a limited live experience after lender approval.", "Add monitoring only within the agreed scope and permissions."]]} /><div className="bdc-measurement"><p className="bdc-eyebrow">Measure the contribution</p><div>{["Incremental verified insight", "Analyst time and rework", "Borrower completion", "Policy-consistent decisions"].map(t => <span key={t}>{t}</span>)}</div></div><BdcNote>Success targets are agreed before the pilot. Credit outcomes require an appropriate observation period; no performance improvement is assumed.</BdcNote></section>

      <section className="bdc-slide bdc-closing" hidden={current !== 9} aria-labelledby="bdc-title-9"><p className="bdc-eyebrow">A focused next step</p><h2 id="bdc-title-9">Where could better evidence <br />change a <span>BDC decision?</span></h2><p className="bdc-closing-lead">Let's choose one real lending question<br />and design the smallest useful pilot around it.</p><BdcSteps items={[["Choose the product", "Where does incomplete evidence constrain the decision?"], ["Define the pathway", "Which verified fact could change an eligible offer?"], ["Agree the evaluation", "What would credit, product and operations need to see?"]]} /><div className="bdc-closing-bottom"><img src="/logo/amlok-logo-white.svg" alt="AMLOK" width="139" height="26" /><span>Infrastructure for financial risk intelligence</span></div></section>
    </div>
    <footer className="bdc-footer"><nav className="bdc-progress" aria-label="Slide navigation">{bdcSlides.map(([section, title], index) => <button key={title} type="button" aria-label={`Go to slide ${index + 1}: ${section}`} aria-current={current === index ? "step" : undefined} className={index <= current ? "bdc-passed" : ""} onClick={() => goTo(index)} title={`${index + 1}. ${title}`}><span /></button>)}</nav><div className="bdc-footer-row"><span className="bdc-footer-context">AMLOK / BDC <span>/ {bdcSlides[current][0]}</span></span><span className="bdc-key-hint">Use ← → to navigate</span><div className="bdc-pagination"><button type="button" onClick={() => goTo(current - 1)} disabled={current === 0} aria-label="Previous slide"><BdcIcon name="back" size={19} /></button><span><strong>{String(current + 1).padStart(2, "0")}</strong> / {bdcSlides.length}</span><button type="button" onClick={() => goTo(current + 1)} disabled={current === bdcSlides.length - 1} aria-label="Next slide"><BdcIcon name="arrow" size={19} /></button></div></div></footer>
    <dialog className="bdc-overview" ref={overviewRef} aria-labelledby="bdc-overview-title" onClick={e => { if (e.target === e.currentTarget) closeOverview(); }}><div className="bdc-overview-header"><div><p className="bdc-eyebrow">AMLOK / Prepared for BDC</p><h2 id="bdc-overview-title">Presentation overview</h2></div><button type="button" onClick={closeOverview} aria-label="Close slide overview"><BdcIcon name="close" /></button></div><div className="bdc-overview-grid">{bdcSlides.map(([section, title], i) => <button type="button" key={title} className={i === current ? "bdc-overview-current" : ""} aria-current={i === current ? "step" : undefined} onClick={() => { goTo(i); closeOverview(); }}><span className="bdc-eyebrow">{String(i + 1).padStart(2, "0")} / {section}</span><strong>{title}</strong><BdcIcon name="arrow" size={19} /></button>)}</div></dialog>
  </main>;
};
