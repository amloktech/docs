// Manual report snapshot. Update the review time and components together after checking the canonical report.
export const ServiceStatus = () => {
  const components = [
    ["Web application", "app.amlok.io"],
    ["API and background functions", "Application /api/* routes"],
    ["Database", "Cloudflare D1"],
    ["Authentication and sessions", "Application /api/auth/* routes"],
    ["AI chat", "Anthropic"],
    ["Email delivery", "Loops transactional email"],
    ["Identity verification", "Argos onboarding KYC"],
    ["Banking connections", "Flinks"],
    ["Billing", "Stripe subscriptions and Connect"],
  ];
  return <div className="amlok-service-status not-prose">
    <div className="ass-summary">
      <span className="ass-eyebrow">AMLOK WEB PLATFORM</span>
      <h2><span className="ass-dot" aria-hidden="true"/>All systems operational</h2>
      <p>No incidents reported in the latest reviewed status report.</p>
      <div className="ass-source"><span>Report reviewed <time dateTime="2026-10-23T20:44:00Z">October 23, 2026 at 20:44 UTC</time></span><a href="https://app.amlok.io/status" target="_blank" rel="noreferrer">View current status ↗</a></div>
    </div>
    <ul className="ass-components" aria-label="Reported component status">
      {components.map(([name, detail]) => <li key={name}><div><strong>{name}</strong><span>{detail}</span></div><span className="ass-state"><span className="ass-dot" aria-hidden="true"/>Operational</span></li>)}
    </ul>
  </div>;
};
