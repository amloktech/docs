// Unlisted presentation for BDC. Mintlify supplies React hooks.
const bdcSlides = [
  ["The opportunity", "Capacity-based lending"],
  ["The challenge: evidence", "More data. Still an incomplete credit picture."],
  ["The challenge: capacity", "Repayment capacity sits beneath the headline numbers."],
  ["The challenge: continuity", "Risk changes between credit reviews."],
  ["The evidence", "One business. A connected financial picture."],
  ["The assessment", "Size financing around repayment capacity."],
  ["The next question", "Ask for evidence that can change the decision."],
  ["The borrower experience", "Make the path to financing clear."],
  ["The permission", "Connect what matters, with clear permission."],
  ["After funding", "Keep the funded decision in view."],
  ["The integration", "An intelligence layer in your lending operation."],
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

const BdcOffers = () => {
  const [selected, setSelected] = useState(0);
  const offers = [
    ["Current evidence", "Indicative option", "175,000", "14.50%", "document", "Based on the information already reviewed.", "Confirm eligibility, complete credit review, and satisfy the lender's final conditions."],
    ["Connected evidence", "Conditional alternative", "250,000", "12.50%", "link", "Connect relevant Stripe or Shopify records.", "Authorize an eligible source. The evidence must resolve the identified policy condition and support the alternative terms."],
    ["Ongoing visibility", "Conditional alternative", "250,000", "11.50%", "flow", "Add separately authorized ongoing monitoring.", "Meet the connected-evidence conditions and the lender's approved monitoring terms. Monitoring alone does not qualify a borrower for better terms."]
  ];
  return <div className="bdc-demo"><div className="bdc-demo-bar"><span><BdcIcon name="bank" size={18} />Your business financing</span><span className="bdc-tag">Illustrative interface</span></div><div className="bdc-offers" role="group" aria-label="Illustrative financing options">{offers.map(([name, label, amount, rate, icon, detail], i) => <button type="button" key={name} aria-pressed={selected === i} className={`bdc-offer ${selected === i ? "bdc-selected" : ""}`} onClick={() => setSelected(i)}><span className="bdc-offer-name"><BdcIcon name={icon} size={19} />{name}<span className="bdc-radio" /></span><span className="bdc-offer-status">{label}</span><span className="bdc-amount"><small>Up to CAD</small>{amount}</span><span className="bdc-offer-terms"><strong>{rate}</strong> fixed annual rate<span>36-month term</span></span><span className="bdc-offer-detail">{detail}</span></button>)}</div><div className="bdc-conditions" aria-live="polite"><span className="bdc-eyebrow">What must be true</span><p>{offers[selected][6]}</p></div></div>;
};

const BdcPermission = () => {
  const [provider, setProvider] = useState("Stripe");
  const [monitoring, setMonitoring] = useState(false);
  return <div className="bdc-demo"><div className="bdc-demo-bar"><span><BdcIcon name="lock" size={18} />Data permission preview</span><span className="bdc-tag">Demo only</span></div><div className="bdc-permission-body"><p className="bdc-mini-label">Choose a relevant source</p><div className="bdc-provider-switch" role="group" aria-label="Example data source">{["Stripe", "Shopify"].map(name => <button key={name} type="button" onClick={() => setProvider(name)} aria-pressed={provider === name}><BdcIcon name={name === "Stripe" ? "card" : "shop"} />{name}{provider === name && <BdcIcon name="check" size={17} />}</button>)}</div><dl className="bdc-permission-list"><div><dt>Records</dt><dd>{provider === "Stripe" ? "Payments, refunds, disputes and payouts" : "Orders, sales, cancellations and returns"}</dd></div><div><dt>Purpose</dt><dd>{provider === "Stripe" ? "Assess net receipts and settlement patterns" : "Understand sales quality and return patterns"}</dd></div><div><dt>Access</dt><dd>Read-only. No movement of money or order changes.</dd></div><div><dt>History</dt><dd>12-month example, subject to available history and permissions</dd></div></dl><label className="bdc-consent"><input type="checkbox" checked={monitoring} onChange={e => setMonitoring(e.target.checked)} /><span><strong>Include ongoing monitoring</strong><small>Separate from this assessment. Scope, duration and refresh schedule are agreed with the lender.</small></span></label><p className="bdc-permission-state" role="status">{monitoring ? "Preview: assessment + ongoing monitoring" : "Preview: assessment only"}</p></div></div>;
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
      if (e.altKey || e.ctrlKey || e.metaKey || overviewRef.current?.open || e.target?.closest("input,select,textarea,[contenteditable=true],.bdc-offers,.bdc-provider-switch")) return;
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
      <section className="bdc-slide bdc-cover" hidden={current !== 0} aria-labelledby="bdc-title-0"><div className="bdc-cover-copy"><p className="bdc-eyebrow">AMLOK / A conversation with BDC</p><h1 id="bdc-title-0">Risk is a movie,<br /><span>not a photo.</span></h1><p className="bdc-cover-subtitle">Capacity-based lending<br />for Canadian businesses.</p><p className="bdc-cover-description">Understand what a business can repay.<br />Identify the evidence that could change the offer.<br />Follow the business after funding.</p><div className="bdc-cover-meta"><span>Deal underwriting</span><span>Portfolio monitoring</span><span>Risk intelligence</span></div></div><div className="bdc-lifecycle-art" aria-label="Evidence connects underwriting, funding and monitoring"><div className="bdc-art-kicker">A continuous view of capacity</div><div className="bdc-orbit" /><div className="bdc-orbit bdc-orbit-small" /><svg className="bdc-art-line" viewBox="0 0 500 320" fill="none" aria-hidden="true"><path d="M10 252C82 252 90 160 165 175S248 80 320 100 401 53 490 45" stroke="white" strokeWidth="2" /><path d="M10 270C88 270 105 200 170 216S258 142 322 148 411 101 490 96" stroke="white" strokeOpacity=".2" strokeWidth="2" strokeDasharray="5 7" /><circle cx="165" cy="175" r="8" fill="white" /><circle cx="320" cy="100" r="8" fill="white" /><circle cx="490" cy="45" r="8" fill="white" /></svg>{[["search", "Understand", "Verified evidence"], ["target", "Assess", "Supported capacity"], ["flow", "Follow", "Changes over time"]].map(([icon, label, title], i) => <div className={`bdc-art-node bdc-node-${i}`} key={label}><BdcIcon name={icon} /><span>{label}<strong>{title}</strong></span></div>)}<span className="bdc-art-foot">From origination to renewal</span></div></section>

      <section className="bdc-slide bdc-challenge" hidden={current !== 1} aria-labelledby="bdc-title-1">
        <BdcHeading index={1} intro="A responsible offer needs a verified, current view of revenue, obligations and cash available for repayment." />
        <div className="bdc-challenge-grid">
          {[
            ["layers", "Fragmented sources", "Applications, statements, accounting, payments and commerce records use different formats, identifiers and reporting periods."],
            ["search", "Ambiguous transactions", "Transfers, borrowed funds and one-off credits can obscure operating receipts. The same activity can appear across several sources."],
            ["flow", "Financial snapshots that age", "Accounts and credit history provide context, but may not show recent sales changes, cash pressure or new financing."],
            ["document", "Repeated manual review", "Collecting documents, extracting fields, reconciling totals and chasing inconsistencies consume time before the credit assessment."],
            ["shield", "Policy and evidence gaps", "A recommendation must connect to the applicable lending criteria, source evidence and exceptions that require human judgment."],
            ["target", "An unclear path forward", "Borrowers need to know which missing facts could change an offer. Lenders need to avoid requesting more data without a decision purpose."]
          ].map(([icon, title, body], i) => <div key={title}><div className="bdc-challenge-card-top"><BdcIcon name={icon} size={21} /><span>{String(i + 1).padStart(2, "0")}</span></div><h3>{title}</h3><p>{body}</p></div>)}
        </div>
        <div className="bdc-challenge-impact"><strong>The consequence</strong><p>Slower decisions, more borrower effort and a greater risk of misjudging both credit risk and lending capacity.</p></div>
      </section>

      <section className="bdc-slide bdc-challenge" hidden={current !== 2} aria-labelledby="bdc-title-2">
        <BdcHeading index={2} intro="Revenue, balances and credit history each answer part of the question. Debt service depends on how cash is earned, consumed and timed." />
        <div className="bdc-capacity-challenge">
          <div className="bdc-record-chain"><p className="bdc-eyebrow">One economic event. Several records.</p><h3>Follow the cash<br />through the business.</h3>
            <ol>{[["shop", "Sale recorded", "Orders, invoices and returns"], ["card", "Processor payout", "Fees, refunds, disputes and timing"], ["bank", "Bank settlement", "Cash received and available balances"]].map(([icon, title, body]) => <li key={title}><BdcIcon name={icon} size={21} /><span><strong>{title}</strong><small>{body}</small></span></li>)}</ol>
            <p className="bdc-chain-note">Gross sales, net receipts and cash available for repayment measure different things.</p>
          </div>
          <div className="bdc-capacity-questions">
            {[
              ["Revenue quality", "Which inflows recur? Separate trading receipts from transfers, loan proceeds, owner funding and exceptional income."],
              ["Total commitments", "What is already owed? Identify debt service, advances, payroll and other recurring obligations across accounts."],
              ["Liquidity and timing", "When is cash tight? Review seasonality, low balances, returned payments and the gap between collections and expenses."],
              ["Downside resilience", "What happens when conditions change? Assess headroom under lower sales, higher refunds or customer concentration."]
            ].map(([title, body]) => <div key={title}><h3>{title}</h3><p>{body}</p></div>)}
          </div>
        </div>
        <BdcNote>Incomplete evidence can undersize financing for a viable business or overstate what it can safely service. The assessment needs both risk and capacity.</BdcNote>
      </section>

      <section className="bdc-slide bdc-challenge" hidden={current !== 3} aria-labelledby="bdc-title-3">
        <BdcHeading index={3} intro="After funding, the original decision needs a link to new evidence and the assumptions it depended on." />
        <div className="bdc-snapshot"><div className="bdc-file"><BdcIcon name="document" size={35} /><strong>The funded decision</strong><span>A baseline to keep in view</span></div><div className="bdc-snapshot-track"><div className="bdc-timeline-labels"><span>Assessment</span><span>Funding</span><span>Renewal</span></div><svg viewBox="0 0 700 130" fill="none" aria-hidden="true"><path d="M0 75H700" stroke="#bdc9e4" strokeDasharray="5 7" /><path d="M0 75 70 75 105 38 145 95 200 55 250 61 295 17 355 66 400 40 440 98 485 78 540 105 585 58 645 70 700 29" stroke="#052698" strokeWidth="3" /></svg><span className="bdc-mini-label">Illustrative lifecycle: sales, liquidity, financing and obligations evolve</span></div></div>
        <BdcSteps items={[["Deterioration can surface late", "Falling receipts, new debt or liquidity pressure may emerge between scheduled reviews, before a missed payment."], ["Improvement can go unnoticed", "Stronger cash generation or reduced obligations may warrant a fresh capacity assessment or renewal review."], ["Alerts need decision context", "A change needs a baseline, supporting evidence and policy relevance. Missing data must stay distinct from financial distress."]]} />
        <div className="bdc-challenge-impact"><strong>The institutional challenge</strong><p>Assess consistently, recognize meaningful change and give the right team an auditable reason to review.</p></div>
      </section>

      <section className="bdc-slide" hidden={current !== 4} aria-labelledby="bdc-title-4"><BdcHeading index={4} intro="Combine the institution's knowledge with borrower-permissioned operating records and relevant public context." /><div className="bdc-evidence-map"><div className="bdc-source-list">{[["bank", "Financial institution", "Application, facilities, repayments"], ["flow", "Banking", "Cash movements, balances, obligations"], ["card", "Payments and commerce", "Stripe, Shopify and relevant business systems"], ["book", "Accounting", "Invoices, receivables, expenses, financials"], ["globe", "Public context", "Relevant entity and business records"]].map(([icon, name, body]) => <div key={name}><BdcIcon name={icon} /><span><strong>{name}</strong><small>{body}</small></span></div>)}</div><div className="bdc-map-arrow"><BdcIcon name="arrow" size={34} /></div><div className="bdc-engine"><p className="bdc-eyebrow">AMLOK Insights</p><h3>A reconciled<br />business view</h3><div className="bdc-engine-steps">{[["layers", "Normalize records"], ["link", "Resolve entities and relationships"], ["check", "Reconcile the same economic activity"], ["document", "Keep evidence and provenance"]].map(([icon, title]) => <span key={title}><BdcIcon name={icon} size={18} />{title}</span>)}</div><p className="bdc-engine-note">One sale can appear in commerce, payments and banking. It must not become three separate revenues.</p></div></div></section>

      <section className="bdc-slide" hidden={current !== 5} aria-labelledby="bdc-title-5"><BdcHeading index={5} intro="Translate verified financial and operating evidence into the financing a business can responsibly service." /><div className="bdc-capacity-grid"><div className="bdc-capacity-core"><p className="bdc-eyebrow">Repayment capacity</p><h3>Cash available<br />to service debt.</h3><div className="bdc-equation"><span>Recurring operating inflows</span><span>Less operating outflows and commitments</span><strong>Assess headroom for proposed debt</strong></div><p>Evaluate existing debt and the proposed facility together, across the lender's chosen scenarios.</p></div><div className="bdc-capacity-signals">{[["Cash generation", "Recurring receipts, margins, cash conversion"], ["Debt service", "Existing obligations and coverage"], ["Resilience", "Seasonality, volatility, downside scenarios"], ["Dependencies", "Customer, channel and supplier concentration"]].map(([title, body]) => <div key={title}><h3>{title}</h3><p>{body}</p></div>)}</div></div><div className="bdc-policy-strip"><BdcIcon name="shield" /><strong>Apply lender policy</strong>{["Eligibility", "Amount", "Price", "Term", "Security and conditions"].map(s => <span key={s}>{s}</span>)}</div><BdcNote>Capacity informs the decision alongside the lender's risk appetite, collateral requirements and approval authority.</BdcNote></section>

      <section className="bdc-slide" hidden={current !== 6} aria-labelledby="bdc-title-6"><BdcHeading index={6} intro="A targeted evidence request starts with a specific policy question." /><div className="bdc-question"><p className="bdc-eyebrow">Example underwriting question</p><h3>Do reported sales convert into consistent, usable cash?</h3></div><BdcSteps className="bdc-four" items={[["Identify the gap", "Net receipts and settlement patterns need verification."], ["Request the source", "Stripe for payment and payout evidence; Shopify for sales and returns."], ["Test the evidence", "Reconcile with bank receipts, refunds and relevant costs."], ["Reassess the option", "Apply the same lender-approved rules to the verified facts."]]} /><div className="bdc-outcomes"><span className="bdc-mini-label">Possible outcomes</span>{["Different terms", "Same terms", "More evidence needed", "Credit review"].map(t => <span key={t}>{t}</span>)}</div><BdcNote>Connecting a source never guarantees approval, more financing or a lower rate. Request only the evidence relevant to the decision.</BdcNote></section>

      <section className="bdc-slide" hidden={current !== 7} aria-labelledby="bdc-title-7"><BdcHeading index={7} intro="Show what current evidence supports and what must be true for an alternative." /><BdcOffers /><BdcNote>Illustrative CAD amounts and terms, not BDC offers or approved pricing. Conditional options require verified evidence, lender policy eligibility and final approval.</BdcNote></section>

      <section className="bdc-slide" hidden={current !== 8} aria-labelledby="bdc-title-8"><BdcHeading index={8} /><div className="bdc-permission-layout"><div className="bdc-consent-story"><p className="bdc-eyebrow">Borrower-controlled access</p><h3>A specific purpose.<br />A clear scope.<br />A separate choice.</h3><ul>{["Explain the underwriting question.", "Show which records will be accessed.", "Separate assessment from ongoing monitoring.", "Explain disconnection and its implications."].map(t => <li key={t}><BdcIcon name="check" size={17} />{t}</li>)}</ul><p>Refresh depends on the source, permissions and agreed synchronization schedule. A disconnected source is a coverage issue, not proof of financial distress.</p></div><BdcPermission /></div><BdcNote>Interactive preview only. These controls do not connect accounts or record actual borrower consent.</BdcNote></section>

      <section className="bdc-slide" hidden={current !== 9} aria-labelledby="bdc-title-9"><BdcHeading index={9} intro="AMLOK Signal monitors changes and reassesses the business against the evidence behind the funded decision." /><div className="bdc-monitor-flow"><div className="bdc-baseline"><p className="bdc-eyebrow">Funded baseline</p><BdcIcon name="document" size={35} /><h3>Preserve the rationale</h3><p>Approved assumptions, financial evidence, conditions and policy context.</p></div><div className="bdc-monitor-events"><p className="bdc-eyebrow">Illustrative change signals</p>{[["flow", "Cash generation changes", "Compare receipts, costs and liquidity."], ["layers", "Risk concentration shifts", "Review customer or channel dependencies."], ["link", "Evidence becomes unavailable", "Flag incomplete coverage separately."]].map(([icon, title, text]) => <div key={title}><BdcIcon name={icon} size={19} /><span><strong>{title}</strong>{text}</span></div>)}</div><div className="bdc-intervention"><p className="bdc-eyebrow">Lender review</p><h3>Know when <br />to look closer.</h3><p>Prioritize review with the changed facts, supporting evidence and affected assumptions.</p><span className="bdc-tag">Institution-led intervention</span></div></div><BdcNote>Signal includes change-driven reassessment. The institution handles borrower outreach and action in its own systems. Monitoring does not automatically reprice a signed facility.</BdcNote></section>

      <section className="bdc-slide" hidden={current !== 10} aria-labelledby="bdc-title-10"><BdcHeading index={10} intro="Keep the borrower relationship and lending infrastructure. Add connected financial intelligence." /><div className="bdc-architecture"><div className="bdc-institution-layer"><p className="bdc-eyebrow">Institution systems</p><div><span>Application and origination</span><span>Credit review and policy</span><span>Portfolio and relationship teams</span></div></div><div className="bdc-api-bridge"><span />API, webhooks and evidence-backed outputs<span /></div><div className="bdc-products"><div><BdcIcon name="search" size={27} /><p className="bdc-eyebrow">AMLOK Insights</p><h3>Full underwriting</h3><p>Build the evidence base, assess repayment capacity and support the credit decision.</p></div><div><BdcIcon name="flow" size={27} /><p className="bdc-eyebrow">AMLOK Signal</p><h3>Continuous assessment</h3><p>Monitor new information and reassess changes using the existing business context.</p></div></div><div className="bdc-shared"><BdcIcon name="layers" />Shared foundation<span>Connections</span><span>Normalized records</span><span>Entity relationships</span><span>Evidence lineage</span></div></div><BdcNote>Proposed Credit Capacity experience: lender-authorized financing pathways built around Insights and Signal. Technical discovery confirms deployment and integration scope.</BdcNote></section>

      <section className="bdc-slide" hidden={current !== 11} aria-labelledby="bdc-title-11"><BdcHeading index={11} intro="Define the boundaries before introducing any borrower-facing financing pathway." /><div className="bdc-control-grid">{[["shield", "Credit and commercial control", "You own product eligibility, risk appetite, pricing rules, delegated authority and final approval."], ["lock", "Permission and purpose", "Access the minimum relevant information with defined purposes, retention and monitoring scope."], ["document", "Traceable assessments", "Keep source evidence, data freshness, assumptions and policy context available for review."], ["target", "Controlled action", "Route findings to your teams. Your institution owns outreach, agreements, funding and intervention."]].map(([icon, title, body]) => <div key={title}><BdcIcon name={icon} size={30} /><h3>{title}</h3><p>{body}</p></div>)}</div><div className="bdc-control-bottom"><strong>Evidence informs. Your institution decides.</strong><span>Validate privacy, security, model risk and operational requirements during discovery.</span></div></section>

      <section className="bdc-slide" hidden={current !== 12} aria-labelledby="bdc-title-12"><BdcHeading index={12} intro="A proposed BDC pilot: one financing product, one policy question and one or two relevant data sources." /><BdcSteps className="bdc-phases" items={[["Define", "Select a decision that verified evidence could change.", "Agree the rules, cohort, access and success measures."], ["Evaluate", "Review authorized historical cases using information available at decision time.", "Compare against the existing process without future-data leakage."], ["Pilot", "Run in shadow mode, then introduce a limited live experience after lender approval.", "Add monitoring only within the agreed scope and permissions."]]} /><div className="bdc-measurement"><p className="bdc-eyebrow">Measure the contribution</p><div>{["Incremental verified insight", "Analyst time and rework", "Borrower completion", "Policy-consistent decisions"].map(t => <span key={t}>{t}</span>)}</div></div><BdcNote>Success targets are agreed before the pilot. Credit outcomes require an appropriate observation period; no performance improvement is assumed.</BdcNote></section>

      <section className="bdc-slide bdc-closing" hidden={current !== 13} aria-labelledby="bdc-title-13"><p className="bdc-eyebrow">A focused next step</p><h2 id="bdc-title-13">Where could better evidence <br />change a <span>BDC decision?</span></h2><p className="bdc-closing-lead">Let's choose one real lending question<br />and design the smallest useful pilot around it.</p><BdcSteps items={[["Choose the product", "Where does incomplete evidence constrain the decision?"], ["Define the pathway", "Which verified fact could change an eligible offer?"], ["Agree the evaluation", "What would credit, product and operations need to see?"]]} /><div className="bdc-closing-bottom"><img src="/logo/amlok-logo-white.svg" alt="AMLOK" width="139" height="26" /><span>Infrastructure for financial risk intelligence</span></div></section>
    </div>
    <footer className="bdc-footer"><nav className="bdc-progress" aria-label="Slide navigation">{bdcSlides.map(([section, title], index) => <button key={title} type="button" aria-label={`Go to slide ${index + 1}: ${section}`} aria-current={current === index ? "step" : undefined} className={index <= current ? "bdc-passed" : ""} onClick={() => goTo(index)} title={`${index + 1}. ${title}`}><span /></button>)}</nav><div className="bdc-footer-row"><span className="bdc-footer-context">AMLOK / BDC <span>/ {bdcSlides[current][0]}</span></span><span className="bdc-key-hint">Use ← → to navigate</span><div className="bdc-pagination"><button type="button" onClick={() => goTo(current - 1)} disabled={current === 0} aria-label="Previous slide"><BdcIcon name="back" size={19} /></button><span><strong>{String(current + 1).padStart(2, "0")}</strong> / {bdcSlides.length}</span><button type="button" onClick={() => goTo(current + 1)} disabled={current === bdcSlides.length - 1} aria-label="Next slide"><BdcIcon name="arrow" size={19} /></button></div></div></footer>
    <dialog className="bdc-overview" ref={overviewRef} aria-labelledby="bdc-overview-title" onClick={e => { if (e.target === e.currentTarget) closeOverview(); }}><div className="bdc-overview-header"><div><p className="bdc-eyebrow">AMLOK / Prepared for BDC</p><h2 id="bdc-overview-title">Presentation overview</h2></div><button type="button" onClick={closeOverview} aria-label="Close slide overview"><BdcIcon name="close" /></button></div><div className="bdc-overview-grid">{bdcSlides.map(([section, title], i) => <button type="button" key={title} className={i === current ? "bdc-overview-current" : ""} aria-current={i === current ? "step" : undefined} onClick={() => { goTo(i); closeOverview(); }}><span className="bdc-eyebrow">{String(i + 1).padStart(2, "0")} / {section}</span><strong>{title}</strong><BdcIcon name="arrow" size={19} /></button>)}</div></dialog>
  </main>;
};
