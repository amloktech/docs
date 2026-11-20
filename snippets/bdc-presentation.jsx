// Unlisted presentation for BDC. Mintlify supplies React hooks.
const bdcSlides = [
  ["The opportunity", "Capacity-based lending"],
  ["The challenge", "A fragmented picture. A moving risk."],
  ["Research", "AI research for better decisions."],
  ["Two products", "Insights and Signal"],
  ["The unified process", "Unified data. A stronger underwriting process."],
  ["After funding", "New signals. A continuous view of risk."],
  ["Embedded financing", "Turn each transaction into a financing opportunity."],
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

// Metric names and applicability from downloads/underwriting-metric-catalog.json (2026-11-12.1).
// Keep every catalog metric in its assigned dimension when this catalog changes.
const bdcMetricDimensions = [
  { key: "identity", label: "Identity and verification", metrics: [
    ["business_age_months","Business age",["business"]],
    ["verified_account_owner_ratio","Verified account ownership share",["business","person"]]
  ] },
  { key: "ownership_and_control", label: "Ownership and control", metrics: [
    ["ownership_disclosed_ratio","Disclosed ownership share",["business"]],
    ["related_party_balance_share","Related-party receivables share",["business"]],
    ["supported_guarantee_coverage","Supported guarantee coverage",["business"]]
  ] },
  { key: "cashflow", label: "Cash flow", metrics: [
    ["total_inflows","Posted inflows",["business","person"]],
    ["total_outflows","Posted outflows",["business","person"]],
    ["net_cash_flow","Net cash flow",["business","person"]],
    ["operating_cash_inflows","Operating receipts",["business","person"]],
    ["operating_cash_outflows","Operating cash payments",["business","person"]],
    ["operating_net_cash_flow","Net operating cash flow",["business","person"]],
    ["internal_transfer_inflows","Internal transfer inflows",["business","person"]],
    ["financing_inflows","Financing inflows",["business","person"]],
    ["positive_cashflow_month_share","Positive cash-flow months",["business","person"]],
    ["cashflow_volatility","Operating cash-flow volatility",["business","person"]],
    ["cashflow_change_90d","Operating cash-flow change",["business","person"]],
    ["posted_transaction_count","Posted transaction count",["business"]],
    ["operating_receipt_count","Operating receipt count",["business"]],
    ["owner_contribution_inflows","Owner capital contributions",["business"]],
    ["owner_distribution_outflows","Owner distributions",["business"]],
    ["debt_proceeds_inflows","Debt proceeds",["business"]],
    ["observed_debt_service","Observed debt-service payments",["business"]],
    ["bank_fee_outflows","Bank fees paid",["business"]],
    ["cash_withdrawal_outflows","Cash withdrawals",["business"]],
    ["payroll_outflows","Payroll paid",["business"]],
    ["inventory_purchase_outflows","Inventory purchases paid",["business"]],
    ["internal_transfer_outflows","Internal transfer outflows",["business"]],
    ["spending_to_receipts_ratio","Operating spending to receipts",["business"]],
    ["spending_to_receipts_change_90d","Change in spending to receipts",["business"]]
  ] },
  { key: "liquidity", label: "Liquidity", metrics: [
    ["unrestricted_cash","Unrestricted cash",["business","person"]],
    ["average_daily_balance","Average daily cash balance",["business","person"]],
    ["minimum_daily_balance","Minimum daily cash balance",["business","person"]],
    ["negative_balance_days","Days below zero",["business","person"]],
    ["cash_buffer_days","Cash buffer",["business","person"]],
    ["current_ratio","Current ratio",["business"]],
    ["quick_ratio","Quick ratio",["business"]],
    ["cash_ratio","Cash ratio",["business"]],
    ["balance_stddev","Daily balance variability",["business"]],
    ["balance_coefficient_of_variation","Relative daily balance variability",["business"]],
    ["maximum_daily_balance","Maximum daily cash balance",["business"]],
    ["median_daily_balance","Median daily cash balance",["business"]],
    ["low_balance_days","Days below the declared cash floor",["business"]],
    ["balance_change_90d","Cash balance change over 90 days",["business"]],
    ["cash_shock_count","Observed cash-shock episodes",["business"]],
    ["balance_recovery_days","Most recent cash-shock recovery",["business"]],
    ["unrecovered_cash_shock_count","Unrecovered cash-shock episodes",["business"]]
  ] },
  { key: "revenue_quality", label: "Revenue quality", metrics: [
    ["verified_revenue","Verified revenue",["business"]],
    ["recurring_revenue_share","Recurring revenue share",["business"]],
    ["revenue_growth_yoy","Revenue growth year over year",["business"]],
    ["revenue_growth_90d","Revenue growth over 90 days",["business"]],
    ["revenue_volatility","Monthly revenue volatility",["business"]],
    ["refund_amount_share","Refund amount share",["business"]],
    ["chargeback_amount_share","Chargeback amount share",["business"]],
    ["revenue_cash_realization","Revenue cash realization",["business"]],
    ["unverified_receipts_share","Unverified receipts share",["business"]],
    ["nonrecurring_revenue_share","Nonrecurring revenue share",["business"]],
    ["receipt_gap_mean_days","Mean interval between receipts",["business"]],
    ["receipt_gap_stddev_days","Receipt interval variability",["business"]],
    ["receipt_day_of_month_stddev","Receipt calendar-day variability",["business"]],
    ["zero_revenue_month_count","Months without recorded receipts",["business"]],
    ["operating_receipts_volatility","Operating receipts volatility",["business"]],
    ["operating_receipts_change_90d","Operating receipts change",["business"]],
    ["days_since_last_operating_receipt","Days since last observed receipt",["business"]],
    ["unclassified_receipt_share","Unclassified external receipts",["business"]]
  ] },
  { key: "profitability", label: "Profitability", metrics: [
    ["gross_profit","Gross profit",["business"]],
    ["gross_margin","Gross margin",["business"]],
    ["ebitda","EBITDA",["business"]],
    ["ebitda_margin","EBITDA margin",["business"]],
    ["operating_profit","Operating profit",["business"]],
    ["operating_margin","Operating margin",["business"]],
    ["net_profit","Net profit",["business"]],
    ["net_margin","Net margin",["business"]],
    ["free_cash_flow","Free cash flow",["business"]],
    ["return_on_assets","Return on assets",["business"]]
  ] },
  { key: "working_capital", label: "Working capital", metrics: [
    ["net_working_capital","Net working capital",["business"]],
    ["receivables_days","Receivable days",["business"]],
    ["payables_days","Payable days",["business"]],
    ["inventory_days","Inventory days",["business"]],
    ["cash_conversion_cycle","Cash conversion cycle",["business"]],
    ["ar_overdue_share","Overdue receivables share",["business"]],
    ["ar_90_plus_share","Receivables over 90 days past due",["business"]],
    ["ap_overdue_share","Overdue payables share",["business"]],
    ["inventory_turnover","Inventory turnover",["business"]]
  ] },
  { key: "leverage", label: "Debt and leverage", metrics: [
    ["total_debt","Total interest-bearing debt",["business","person"]],
    ["net_debt","Net debt",["business","person"]],
    ["debt_to_assets","Debt to assets",["business"]],
    ["debt_to_equity","Debt to equity",["business"]],
    ["net_debt_to_ebitda","Net debt to EBITDA",["business"]],
    ["credit_utilization","Revolving credit utilization",["business","person"]],
    ["short_term_debt_share","Debt due within one year",["business","person"]],
    ["debt_maturing_90d","Debt maturing within 90 days",["business","person"]],
    ["concurrent_financing_count","Observed active financing facilities",["business"]],
    ["new_financing_count_90d","Recently funded active facilities",["business"]],
    ["debt_to_operating_receipts","Debt to annual operating receipts",["business"]]
  ] },
  { key: "repayment_capacity", label: "Repayment capacity", metrics: [
    ["dscr","Cash-flow debt-service coverage",["business"]],
    ["fixed_charge_coverage","Fixed-charge coverage",["business"]],
    ["interest_coverage","Interest coverage",["business"]],
    ["existing_debt_service","Existing debt service",["business"]],
    ["proposed_debt_service","Proposed debt service",["business"]],
    ["total_debt_service","Total debt service",["business"]],
    ["residual_cash_after_debt","Cash after debt service",["business"]],
    ["debt_service_headroom","Debt-service headroom",["business"]],
    ["debt_payment_to_receipts","Debt payments to operating receipts",["business"]],
    ["debt_service_to_outflows","Debt-service share of outflows",["business"]]
  ] },
  { key: "concentration", label: "Concentration", metrics: [
    ["top_customer_share","Largest customer share",["business"]],
    ["top_five_customer_share","Top five customer share",["business"]],
    ["top_supplier_share","Largest supplier share",["business"]],
    ["top_channel_share","Largest sales channel share",["business"]],
    ["customer_hhi","Customer concentration index",["business"]],
    ["income_source_hhi","Income-source concentration index",["person"]]
  ] },
  { key: "collateral", label: "Collateral and security", metrics: [
    ["collateral_ltv","Loan to collateral value",["business","person"]],
    ["combined_ltv","Combined loan to value",["business","person"]],
    ["collateral_coverage","Collateral coverage",["business","person"]],
    ["eligible_receivables","Eligible borrowing-base receivables",["business"]],
    ["collateral_haircut_ratio","Collateral haircut",["business","person"]]
  ] },
  { key: "fraud_and_consistency", label: "Fraud and consistency", metrics: [
    ["reconciliation_break_share","Unreconciled value share",["business","person"]],
    ["duplicate_transaction_share","Duplicate transaction share",["business","person"]],
    ["document_contradiction_count","Document contradictions",["business","person"]],
    ["identity_mismatch_count","Unresolved identity mismatches",["business","person"]],
    ["declared_income_gap_ratio","Declared-to-verified income gap",["business","person"]]
  ] },
  { key: "income_and_affordability", label: "Income and affordability", metrics: [
    ["verified_gross_monthly_income","Verified gross monthly income",["person"]],
    ["verified_net_monthly_income","Verified net monthly income",["person"]],
    ["debt_to_income","Debt to income",["person"]],
    ["housing_to_income","Housing cost to income",["person"]],
    ["essential_monthly_spend","Essential monthly expenditure",["person"]],
    ["residual_monthly_income","Residual monthly income",["person"]],
    ["payment_to_income","Proposed payment to income",["person"]],
    ["liquid_reserve_months","Liquid reserve months",["person"]]
  ] },
  { key: "income_stability", label: "Income stability", metrics: [
    ["income_source_count","Verified income sources",["person"]],
    ["income_volatility","Monthly income volatility",["person"]],
    ["income_growth_yoy","Income growth year over year",["person"]],
    ["days_since_last_income","Days since last income",["person"]],
    ["income_interruption_days","Income interruption",["person"]],
    ["income_continuity_share","Income continuity",["person"]]
  ] },
  { key: "payment_behavior", label: "Payment behavior", metrics: [
    ["nsf_event_count","Insufficient-funds events",["business","person"]],
    ["overdraft_days","Overdraft days",["business","person"]],
    ["returned_payment_amount","Returned payment amount",["business","person"]],
    ["delinquent_obligation_count","Delinquent obligations",["business","person"]],
    ["maximum_days_past_due","Maximum days past due",["business","person"]],
    ["on_time_payment_share","On-time payment share",["business","person"]]
  ] },
  { key: "credit_history", label: "Credit history", metrics: [
    ["open_credit_obligation_count","Open credit obligations",["business","person"]],
    ["bureau_utilization","Reported revolving utilization",["business","person"]],
    ["recent_credit_inquiry_count","Recent credit inquiries",["business","person"]],
    ["severe_delinquency_count","Severe delinquency events",["business","person"]],
    ["public_record_event_count","Relevant public-record events",["business","person"]]
  ] },
  { key: "commerce_performance", label: "Commerce and subscriptions", metrics: [
    ["gross_sales","Gross sales",["business"]],
    ["net_sales","Net sales",["business"]],
    ["average_order_value","Average order value",["business"]],
    ["repeat_customer_share","Repeat customer share",["business"]],
    ["monthly_recurring_revenue","Monthly recurring revenue",["business"]],
    ["gross_revenue_retention","Gross revenue retention",["business"]],
    ["net_revenue_retention","Net revenue retention",["business"]],
    ["settlement_delay_days","Settlement delay",["business"]]
  ] },
  { key: "operating_resilience", label: "Operating resilience", metrics: [
    ["payroll_burden_share","Payroll burden",["business"]],
    ["payroll_growth_yoy","Payroll growth year over year",["business"]],
    ["inventory_stockout_share","Inventory stockout share",["business"]],
    ["fulfillment_on_time_share","On-time fulfillment share",["business"]],
    ["supplier_payment_delay_days","Supplier payment delay",["business"]],
    ["operating_outflows_change_90d","Operating payments change",["business"]]
  ] },
  { key: "tax_and_compliance", label: "Tax and statutory obligations", metrics: [
    ["tax_liability","Reported tax liability",["business"]],
    ["tax_overdue_amount","Overdue tax amount",["business"]],
    ["tax_payment_coverage","Tax payment coverage",["business"]],
    ["filing_coverage","Filing evidence coverage",["business"]]
  ] },
  { key: "financial_reporting_quality", label: "Financial reporting quality", metrics: [
    ["bank_accounting_match_share","Bank-to-books match share",["business"]],
    ["statement_balance_discrepancy","Balance-sheet discrepancy",["business"]],
    ["material_adjustment_share","Material accounting adjustments",["business"]],
    ["books_closing_lag_days","Books closing lag",["business"]]
  ] },
  { key: "data_quality", label: "Data quality and coverage", metrics: [
    ["observed_account_coverage","Declared-account coverage",["business","person"]],
    ["covered_history_days","Covered history",["business","person"]],
    ["stale_source_share","Stale required sources",["business","person"]],
    ["unclassified_transaction_share","Unclassified transactions",["business","person"]],
    ["reconciled_value_share","Reconciled financial value",["business","person"]]
  ] },
  { key: "forecasting_and_stress", label: "Forecasting and stress", metrics: [
    ["projected_minimum_cash","Projected minimum cash",["business","person"]],
    ["stress_dscr","Stressed debt-service coverage",["business"]],
    ["stress_residual_income","Stressed residual income",["person"]],
    ["liquidity_shortfall","Projected liquidity shortfall",["business","person"]],
    ["break_even_revenue_decline","Break-even revenue decline",["business"]]
  ] },
  { key: "relationship_risk", label: "Related-party and network exposure", metrics: [
    ["related_party_receipts_share","Related-party receipts share",["business"]],
    ["circular_flow_amount","Potential circular-flow amount",["business"]],
    ["connected_counterparty_share","Connected-counterparty exposure",["business"]]
  ] },
  { key: "monitoring_change", label: "Monitoring changes", metrics: [
    ["revenue_change_from_baseline","Revenue change from baseline",["business"]],
    ["liquidity_change_from_baseline","Liquidity change from baseline",["business","person"]],
    ["dscr_change_from_baseline","DSCR change from baseline",["business"]],
    ["obligation_growth_from_baseline","Debt change from baseline",["business","person"]]
  ] }
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
    <div className="bdc-ai-projection-heading"><h3>Financial intelligence across six dimensions.</h3><div className="bdc-ai-view-switch" role="group" aria-label="Comparison chart view"><button type="button" aria-pressed={chartView === "radar"} onClick={() => setChartView("radar")}>Radar</button><button type="button" aria-pressed={chartView === "dimensions"} onClick={() => setChartView("dimensions")}>By dimension</button></div></div>
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
const BdcMetricCatalog = () => {
  const [query, setQuery] = useState("");
  const [audience, setAudience] = useState("all");
  const search = query.trim().toLowerCase().replace(/[_-]+/g, " ");
  const visible = bdcMetricDimensions.map(dimension => ({
    ...dimension,
    metrics: dimension.metrics.filter(([key, label, borrowers]) =>
      (audience === "all" || borrowers.includes(audience)) &&
      (!search || `${dimension.label} ${key.replace(/_/g, " ")} ${label}`.toLowerCase().includes(search))
    )
  })).filter(dimension => dimension.metrics.length);
  const total = bdcMetricDimensions.reduce((sum, dimension) => sum + dimension.metrics.length, 0);
  const shown = visible.reduce((sum, dimension) => sum + dimension.metrics.length, 0);
  return <div className="bdc-metric-catalog">
    <div className="bdc-metric-intro">
      <div><h3>What the API assesses</h3><p>Financial, operational and risk measures used across underwriting and ongoing monitoring. Available values depend on borrower type, authorized sources and the evidence for each assessment.</p></div>
      <div className="bdc-metric-totals" aria-label={`${bdcMetricDimensions.length} dimensions and ${total} metrics in the API catalog`}><span><strong>{bdcMetricDimensions.length}</strong>dimensions</span><span><strong>{total}</strong>metrics</span></div>
    </div>
    <div className="bdc-metric-controls">
      <label className="bdc-metric-search"><span className="bdc-sr-only">Search metrics or dimensions</span><BdcIcon name="search" size={18} /><input type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder="Search metrics or dimensions" /></label>
      <div className="bdc-metric-audience" role="group" aria-label="Borrower type">{[["all", "All"], ["business", "Business"], ["person", "Consumer"]].map(([value, label]) => <button type="button" key={value} aria-pressed={audience === value} onClick={() => setAudience(value)}>{label}</button>)}</div>
    </div>
    <div className="bdc-metric-result-bar"><p role="status">{shown} {shown === 1 ? "metric" : "metrics"} across {visible.length} {visible.length === 1 ? "dimension" : "dimensions"}</p><a href="/api-reference/underwriting-dimensions" target="_blank" rel="noopener noreferrer">Full metric dictionary<BdcIcon name="arrow" size={14} /></a></div>
    <div className="bdc-metric-grid">{visible.map(dimension => <section className="bdc-metric-group" key={dimension.key} aria-labelledby={`bdc-metric-${dimension.key}`}><header><h4 id={`bdc-metric-${dimension.key}`}>{dimension.label}</h4><span aria-label={`${dimension.metrics.length} ${dimension.metrics.length === 1 ? "metric" : "metrics"}`}>{dimension.metrics.length}</span></header><ul>{dimension.metrics.map(([key, label]) => <li key={key}>{label}</li>)}</ul></section>)}</div>
    {!visible.length && <div className="bdc-metric-empty"><p>No metrics match this search.</p><button type="button" onClick={() => { setQuery(""); setAudience("all"); }}>Show all metrics</button></div>}
    <p className="bdc-metric-footnote">Each metric is defined with its calculation, units, observation window and evidence requirements. Missing or inapplicable values are identified explicitly. <a href="/api-reference/risk-package-methodology" target="_blank" rel="noopener noreferrer">View the assessment methodology</a>.</p>
  </div>;
};

const BdcResearch = () => {
  const [view, setView] = useState("metrics");
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
    <div className="bdc-research-actions"><div><button type="button" onClick={e => openDetails("landscape", e)}>AI comparison<BdcIcon name="arrow" size={16} /></button><button type="button" onClick={e => openDetails("metrics", e)}>Metrics and dimensions<BdcIcon name="arrow" size={16} /></button></div></div>
    <dialog className="bdc-research-dialog" data-view={view} ref={dialogRef} aria-labelledby="bdc-research-details-title" onClose={() => openerRef.current?.focus()} onClick={e => { if (e.target === e.currentTarget) closeDetails(); }}>
      <div className="bdc-research-dialog-header"><div><p className="bdc-eyebrow">AMLOK / Research</p><h2 id="bdc-research-details-title">{view === "landscape" ? "Financial AI comparison" : "Research details"}</h2></div><button type="button" onClick={closeDetails} aria-label="Close research details"><BdcIcon name="close" /></button></div>
      <div className="bdc-research-switch" role="group" aria-label="Research detail view"><button type="button" aria-pressed={view === "landscape"} onClick={() => setView("landscape")}>AI comparison</button><button type="button" aria-pressed={view === "metrics"} onClick={() => setView("metrics")}>Metrics and dimensions</button><button type="button" aria-pressed={view === "approach"} onClick={() => setView("approach")}>Research approach</button></div>
      <div hidden={view !== "landscape"}><BdcAIComparison /></div>
      <div hidden={view !== "metrics"}><BdcMetricCatalog /></div>
      <div hidden={view !== "approach"} className="bdc-research-approach"><p>Research focuses on financial understanding for full underwriting and ongoing monitoring. Each task has its own evidence, evaluation population and intended use.</p><div>{bdcResearchApproach.map(([title, summary, details]) => <section key={title}><h3>{title === "Models" ? "Model architecture" : title}</h3><dl>{details.map(([label, detail]) => <div key={label}><dt>{label}</dt><dd>{detail}</dd></div>)}</dl></section>)}</div><p className="bdc-research-detail-note">The headline figures are supplied AMLOK research results. The public research documentation describes separate structured-loan and financial-document baseline studies.</p><a href="/research" target="_blank" rel="noopener noreferrer">Explore the research documentation<BdcIcon name="arrow" size={16} /></a></div>
    </dialog>
  </div>;
};

// Embedded-financing concept only. Selection updates local presentation state, never a payment.
const bdcEmbeddedPlans = [
  { key: "bank", name: "Bank data", amount: 6000, rate: 8, evidence: "Your bank transactions and cash flow.", condition: "Use your existing bank data.", connections: false, monitoring: false },
  { key: "connected", name: "Connected business", amount: 8000, rate: 6, evidence: "Add sales, refunds and settlement evidence.", condition: "Connect Shopify and Stripe.", connections: true, monitoring: false },
  { key: "monitored", name: "Connected + monitored", amount: 10000, rate: 4, evidence: "The same sources, with ongoing visibility.", condition: "Allow monitoring for the 6-month financing term.", connections: true, monitoring: true }
];
const BdcAppHeader = () => <div className="bdc-bank-header"><img src="/images/demobdc/bdc-logo.svg" alt="BDC" width="61" height="32" /><span>Business payments</span><span className="bdc-bank-avatar" aria-hidden="true">NM</span></div>;
const BdcConnectionLogos = () => <span className="bdc-widget-connections"><span>Connect</span><span><img src="/images/demobdc/shopify.svg" alt="" />Shopify</span><span><img src="/images/demobdc/stripe.svg" alt="" />Stripe</span></span>;
const BdcEmbeddedFinance = () => {
  const [selected, setSelected] = useState("monitored");
  const offerRef = useRef(null);
  const plan = bdcEmbeddedPlans.find(item => item.key === selected);
  const amount = 15000;
  const financed = plan?.amount || 0;
  const monthlyRate = (plan?.rate || 0) / 1200;
  const instalment = plan ? financed * monthlyRate / (1 - Math.pow(1 + monthlyRate, -6)) : 0;
  const dollars = value => new Intl.NumberFormat("en-CA", { minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value);
  const cents = value => new Intl.NumberFormat("en-CA", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);
  return <div className="bdc-embedded-journey">
    <div className="bdc-journey-column">
      <div className="bdc-journey-step"><span>01</span><h3>A payment becomes an opportunity</h3><BdcIcon name="arrow" size={18} /></div>
      <div className="bdc-bank-screen">
        <BdcAppHeader />
        <div className="bdc-bank-body">
          <p className="bdc-bank-breadcrumb">Payments / New transfer</p>
          <h4>Send a payment</h4>
          <div className="bdc-transfer-payee"><span className="bdc-payee-symbol"><BdcIcon name="shop" size={22} /></span><div><strong>Maple Supply Co.</strong><small>Equipment deposit · Invoice 2084</small></div></div>
          <div className="bdc-transfer-amount"><span>Transfer amount</span><strong>$15,000<small>CAD</small></strong></div>
          <div className="bdc-transfer-account"><BdcIcon name="bank" size={17} /><span>Business account <strong>•• 4821</strong></span></div>
          <button type="button" className="bdc-pay-own" onClick={() => setSelected(null)}>Pay $15,000 from my account</button>
          <div className="bdc-finance-widget">
            <div className="bdc-widget-brand"><img src="/logo/amlok-logo-blue.svg" alt="AMLOK" /><span>Financing option</span></div>
            <h5>Keep more cash in your business.</h5>
            <p>Finance up to <strong>$10,000</strong> of this payment.<br />Rates starting at <strong>4.00% APR.</strong></p>
            <button type="button" onClick={() => { setSelected("monitored"); offerRef.current?.focus(); }}>Explore financing<BdcIcon name="arrow" size={15} /></button>
          </div>
        </div>
        <div className="bdc-bank-footer"><BdcIcon name="lock" size={12} />Northline Manufacturing Inc.</div>
      </div>
    </div>
    <div className="bdc-journey-column">
      <div className="bdc-journey-step"><span>02</span><h3>See a path to better terms</h3><BdcIcon name="arrow" size={18} /></div>
      <div className="bdc-bank-screen">
        <BdcAppHeader />
        <div className="bdc-bank-body bdc-options-body">
          <div className="bdc-finance-title"><div><p className="bdc-bank-breadcrumb">Financing / Your options</p><h4>Choose how to qualify</h4></div><img src="/logo/amlok-blue.svg" alt="AMLOK" /></div>
          <p className="bdc-offer-explainer">More evidence can support better terms.</p>
          <div className="bdc-embedded-options" role="group" aria-label="Illustrative financing options">
            {bdcEmbeddedPlans.map((offer, index) => <button key={offer.key} ref={index === 2 ? offerRef : undefined} type="button" aria-pressed={selected === offer.key} onClick={() => setSelected(offer.key)} className="bdc-embedded-option" aria-label={`Preview ${offer.name}: CAD ${dollars(offer.amount)} at ${offer.rate}% APR for 6 months`}>
              <span className="bdc-option-heading"><strong>{offer.name}</strong><span className="bdc-option-radio" aria-hidden="true">{selected === offer.key && <BdcIcon name="check" size={11} />}</span></span>
              <span className="bdc-option-terms"><strong>${dollars(offer.amount)}</strong><span>{offer.rate.toFixed(2)}% APR<span>6 months</span></span></span>
              <span className="bdc-option-evidence">{offer.evidence}</span>
              <span className="bdc-option-condition">{offer.connections ? <BdcConnectionLogos /> : <span className="bdc-existing-source"><BdcIcon name="bank" size={13} />Bank data</span>}{offer.monitoring && <span className="bdc-monitor-label"><BdcIcon name="flow" size={13} />Monitoring</span>}</span>
              <span className="bdc-option-requirement">{offer.condition}</span>
            </button>)}
          </div>
          <p className="bdc-options-consent">You choose which sources to connect and whether to permit monitoring. Terms depend on the assessment.</p>
        </div>
        <div className="bdc-bank-footer"><BdcIcon name="shield" size={12} />Assessed against the institution's lending policy</div>
      </div>
    </div>
    <div className="bdc-journey-column">
      <div className="bdc-journey-step"><span>03</span><h3>Pay with clarity and control</h3></div>
      <div className="bdc-bank-screen">
        <BdcAppHeader />
        <div className="bdc-bank-body bdc-confirm-body" aria-live="polite" aria-atomic="true">
          <div className="bdc-payment-success"><span><BdcIcon name="check" size={23} /></span><h4>Payment sent</h4><strong>$15,000 <small>CAD</small></strong><p>To Maple Supply Co.</p></div>
          <div className="bdc-payment-split"><div className="bdc-split-bar" aria-hidden="true"><span style={{width:`${financed/amount*100}%`}} /></div><dl><div><dt><i />Financed by BDC</dt><dd>${dollars(financed)}</dd></div><div><dt><i />From your account</dt><dd>${dollars(amount-financed)}</dd></div></dl></div>
          {plan ? <div className="bdc-confirm-financing"><div className="bdc-confirm-plan"><strong>Your financing</strong><span>{plan.name}</span></div><dl><div><dt>Annual percentage rate</dt><dd>{plan.rate.toFixed(2)}%</dd></div><div><dt>Repayment term</dt><dd>6 months</dd></div><div><dt>Est. monthly payment</dt><dd>${cents(instalment)}</dd></div></dl><p><BdcIcon name={plan.monitoring ? "flow" : "check"} size={14} />{plan.monitoring ? "Monitoring authorized for the financing term" : plan.connections ? "Shopify + Stripe used for this assessment" : "Assessed with bank data"}</p></div> : <div className="bdc-confirm-financing"><strong>Paid from your account</strong><p>No financing selected. No repayments.</p></div>}
          <div className="bdc-receipt-link"><BdcIcon name="document" size={15} />{plan ? "Payment receipt and financing terms" : "Payment receipt"}</div>
        </div>
        <div className="bdc-bank-footer">{plan ? "Financing by BDC" : "Payment confirmed"}<span>Powered by AMLOK</span></div>
      </div>
    </div>
  </div>;
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
  return <main id="demobdc-deck" className={`not-prose${current === 6 ? " bdc-embedded-active" : ""}`} ref={rootRef} aria-label="AMLOK presentation for BDC">
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

      <section className="bdc-slide bdc-research" hidden={current !== 2} aria-labelledby="bdc-title-2"><BdcHeading index={2} intro={<>Our Research Lab develops proprietary models, benchmarks and continuous-learning systems<br />for high-risk banking workflows - where general-purpose AI still falls short.</>} /><BdcResearch /></section>

      <section className="bdc-slide bdc-product-pathways-slide" hidden={current !== 3} aria-labelledby="bdc-title-3">
        <p className="bdc-eyebrow bdc-product-slide-label" id="bdc-title-3">04 / Two products</p>
        <div className="bdc-product-pathways">
          <div className="bdc-product-institutions">
            <div className="bdc-product-institution-title"><BdcIcon name="bank" size={28} /><h3>Financial institutions</h3></div>
            <ul aria-label="Institution types"><li>Banks</li><li>Neo-banks</li><li>Credit unions</li></ul>
          </div>
          <div className="bdc-product-branch" aria-hidden="true"><span /><span /></div>
          <div className="bdc-product-pair">
            <article className="bdc-product-card">
              <div className="bdc-product-card-top"><span>Before funding</span><BdcIcon name="search" size={32} /></div>
              <h3>Insights</h3>
              <h4>Deal underwriting</h4>
              <p>Understand the business, assess repayment capacity and evaluate the deal against your lending policies.</p>
              <div className="bdc-product-result"><BdcIcon name="document" size={19} /><span>An evidence-backed credit assessment</span></div>
            </article>
            <article className="bdc-product-card">
              <div className="bdc-product-card-top"><span>After funding</span><BdcIcon name="flow" size={32} /></div>
              <h3>Signal</h3>
              <h4>Portfolio monitoring</h4>
              <p>Follow changes in the business, reassess risk and capacity, and identify when your team should review.</p>
              <div className="bdc-product-result"><BdcIcon name="target" size={19} /><span>Timely signals for institution-led action</span></div>
            </article>
          </div>
        </div>
        <p className="bdc-product-principle">One risk engine. Your institution's policies and credit authority.</p>
      </section>

      <section className="bdc-slide bdc-unified" hidden={current !== 4} aria-labelledby="bdc-title-4">
        <BdcHeading index={4} />
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
              ["flow", "Assess revenue quality, liquidity and existing obligations"],
              ["shield", "Evaluate repayment capacity and resilience under stress"],
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

      <section className="bdc-slide bdc-unified bdc-signal" hidden={current !== 5} aria-labelledby="bdc-title-5">
        <BdcHeading index={5} intro="Signal compares new evidence with the funded baseline, so your team can see what changed and when to review." />
        <div className="bdc-signal-map">
          <div className="bdc-signal-inputs" aria-label="Monitored signals">
            {[
              ["flow", "Cash flow and liquidity", "Operating cash, balances, cash buffer and volatility."],
              ["shop", "Revenue and margin", "Sales trends, recurring receipts, costs and margins."],
              ["card", "Payments and new debt", "Missed payments, insufficient funds, refunds, disputes and new obligations."],
              ["target", "Capacity and covenants", "Debt-service coverage, repayment headroom and policy thresholds."],
              ["book", "Working capital and operations", "Overdue invoices, payables, inventory, payroll and settlement delays."],
              ["link", "Counterparty exposure", "Customer, supplier and channel concentration; related-party activity."],
              ["shield", "Collateral and obligations", "Collateral coverage, tax arrears and relevant public-record changes."],
              ["search", "Data health and consistency", "Stale feeds, lost permission, reconciliation gaps and conflicting records."]
            ].map(([icon, title, detail]) => <div key={title}><BdcIcon name={icon} size={21} /><div><h3>{title}</h3><p>{detail}</p></div></div>)}
          </div>
          <div className="bdc-unification-arrow"><BdcIcon name="arrow" size={30} /></div>
          <div className="bdc-unification-engine bdc-signal-engine">
            <p className="bdc-eyebrow">Signal / Portfolio monitoring</p>
            <h3>Know what changed.<br />Know why it matters.</h3>
            <div>{[
              ["document", "Compare new evidence with the funded baseline"],
              ["flow", "Reassess risk, capacity and repayment headroom"],
              ["target", "Apply lender-defined thresholds and policy context"],
              ["link", "Link alerts to source evidence, timing and severity"],
              ["search", "Separate financial changes from missing or stale data"],
              ["layers", "Deliver updated findings through APIs and webhooks"]
            ].map(([icon, title]) => <span key={title}><BdcIcon name={icon} size={19} />{title}</span>)}</div>
          </div>
        </div>
        <div className="bdc-unified-outcomes bdc-signal-outcomes">
          {[
            ["Detect", "Changes that warrant attention", "Surface deterioration, repayment stress and emerging exposures."],
            ["Reassess", "Improvement and headroom", "Recognize stronger cash flow, lower debt and changing financing capacity."],
            ["Prioritize", "Evidence for institution-led review", "Connect changed facts to the borrower, affected policies and supporting records."]
          ].map(([title, subtitle, body]) => <div key={title}><h3>{title}</h3><strong>{subtitle}</strong><p>{body}</p></div>)}
        </div>
        <BdcNote>Coverage and refresh depend on authorized sources. Change-driven reassessment is included in Signal. Your institution owns outreach and decisions; monitoring does not automatically reprice a facility.</BdcNote>
      </section>

      <section className="bdc-slide bdc-embedded" hidden={current !== 6} aria-labelledby="bdc-title-6"><BdcHeading index={6} intro="An embedded AMLOK widget underwrites at the point of payment, using the institution's policies and borrower-permissioned data." /><BdcEmbeddedFinance /><div className="bdc-embedded-caption"><p><strong>Research → Risk engine → In-flow financing</strong><span>The institution controls policy and approval. The business sees what can improve its offer.</span></p><small>BDC-branded concept, not an existing BDC product or offer. Illustrative CAD terms; subject to evidence, underwriting and approval. No live payments or connections.</small></div></section>

      <section className="bdc-slide bdc-closing" hidden={current !== 7} aria-labelledby="bdc-title-7"><p className="bdc-eyebrow">A focused next step</p><h2 id="bdc-title-7">Where could better evidence <br />change a <span>BDC decision?</span></h2><p className="bdc-closing-lead">Let's choose one real lending question<br />and design the smallest useful pilot around it.</p><BdcSteps items={[["Choose the product", "Where does incomplete evidence constrain the decision?"], ["Define the pathway", "Which verified fact could change an eligible offer?"], ["Agree the evaluation", "What would credit, product and operations need to see?"]]} /><div className="bdc-closing-bottom"><img src="/logo/amlok-logo-white.svg" alt="AMLOK" width="139" height="26" /><span>Infrastructure for financial risk intelligence</span></div></section>
    </div>
    <footer className="bdc-footer"><nav className="bdc-progress" aria-label="Slide navigation">{bdcSlides.map(([section, title], index) => <button key={title} type="button" aria-label={`Go to slide ${index + 1}: ${section}`} aria-current={current === index ? "step" : undefined} className={index <= current ? "bdc-passed" : ""} onClick={() => goTo(index)} title={`${index + 1}. ${title}`}><span /></button>)}</nav><div className="bdc-footer-row"><span className="bdc-footer-context">AMLOK / BDC <span>/ {bdcSlides[current][0]}</span></span><span className="bdc-key-hint">Use ← → to navigate</span><div className="bdc-pagination"><button type="button" onClick={() => goTo(current - 1)} disabled={current === 0} aria-label="Previous slide"><BdcIcon name="back" size={19} /></button><span><strong>{String(current + 1).padStart(2, "0")}</strong> / {bdcSlides.length}</span><button type="button" onClick={() => goTo(current + 1)} disabled={current === bdcSlides.length - 1} aria-label="Next slide"><BdcIcon name="arrow" size={19} /></button></div></div></footer>
    <dialog className="bdc-overview" ref={overviewRef} aria-labelledby="bdc-overview-title" onClick={e => { if (e.target === e.currentTarget) closeOverview(); }}><div className="bdc-overview-header"><div><p className="bdc-eyebrow">AMLOK / Prepared for BDC</p><h2 id="bdc-overview-title">Presentation overview</h2></div><button type="button" onClick={closeOverview} aria-label="Close slide overview"><BdcIcon name="close" /></button></div><div className="bdc-overview-grid">{bdcSlides.map(([section, title], i) => <button type="button" key={title} className={i === current ? "bdc-overview-current" : ""} aria-current={i === current ? "step" : undefined} onClick={() => { goTo(i); closeOverview(); }}><span className="bdc-eyebrow">{String(i + 1).padStart(2, "0")} / {section}</span><strong>{title}</strong><BdcIcon name="arrow" size={19} /></button>)}</div></dialog>
  </main>;
};
