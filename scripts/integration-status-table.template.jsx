// Generated data is inserted by scripts/sync-integration-status.mjs.
// Mintlify provides React hooks in its MDX environment.
export const IntegrationStatusTable = () => {
  const integrations = /* INTEGRATION_DATA */ [];
  const [query, setQuery] = useState("");
  const [market, setMarket] = useState("all");
  const [status, setStatus] = useState("all");
  const [page, setPage] = useState(1);
  const pageSize = 25;
  const normalize = (value) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
  const search = normalize(query);
  const filtered = integrations.filter((integration) => {
    const matchesSearch = !search || normalize([integration.name, integration.id, ...integration.aliases].join(" ")).includes(search);
    const matchesMarket = market === "all" || integration.markets.includes(market);
    return matchesSearch && matchesMarket && (status === "all" || integration.status === status);
  });
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  const offset = (currentPage - 1) * pageSize;
  const visible = filtered.slice(offset, offset + pageSize);
  const activeCount = integrations.filter((integration) => integration.status === "Active").length;
  const reviewCount = integrations.filter((integration) => integration.status === "In Review").length;
  const statusClasses = { "In Review": "review", "On Roadmap": "roadmap", "In Progress": "progress", Active: "active" };
  const hasFilters = query !== "" || market !== "all" || status !== "all";
  const reset = () => { setQuery(""); setMarket("all"); setStatus("all"); setPage(1); };
  const selectStatus = (value) => { setStatus(value); setPage(1); };

  return (
    <div className="amlok-status not-prose">
      <div className="amlok-status-summary" aria-label="Catalog totals">
        <button type="button" onClick={reset} aria-pressed={!hasFilters} className="amlok-status-metric">
          <span>All integrations</span><strong>{integrations.length}</strong>
        </button>
        <button type="button" onClick={() => selectStatus("Active")} aria-pressed={status === "Active"} className="amlok-status-metric">
          <span>Active <span className="amlok-status-beta">Beta</span></span><strong>{activeCount}</strong>
        </button>
        <button type="button" onClick={() => selectStatus("In Review")} aria-pressed={status === "In Review"} className="amlok-status-metric">
          <span>In Review</span><strong>{reviewCount}</strong>
        </button>
      </div>

      <div className="amlok-status-filters">
        <div className="amlok-status-search">
          <label htmlFor="integration-search">Search integrations</label>
          <div className="amlok-status-search-input">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" /><path d="m16 16 5 5" /></svg>
            <input id="integration-search" type="search" placeholder="Search by name..." value={query} onChange={(event) => { setQuery(event.target.value); setPage(1); }} aria-controls="integration-status-table" autoComplete="off" />
          </div>
        </div>
        <div className="amlok-status-select">
          <label htmlFor="integration-market">Market</label>
          <select id="integration-market" value={market} onChange={(event) => { setMarket(event.target.value); setPage(1); }} aria-controls="integration-status-table">
            <option value="all">All markets</option><option value="US">US</option><option value="CA">CA</option>
          </select>
        </div>
        <div className="amlok-status-select">
          <label htmlFor="integration-status">Status</label>
          <select id="integration-status" value={status} onChange={(event) => selectStatus(event.target.value)} aria-controls="integration-status-table">
            <option value="all">All statuses</option><option value="In Review">In Review</option><option value="On Roadmap">On Roadmap</option><option value="In Progress">In Progress</option><option value="Active">Active</option>
          </select>
        </div>
      </div>

      <div className="amlok-status-results">
        <p role="status" aria-live="polite" aria-atomic="true">{filtered.length === 0 ? "No integrations found" : `Showing ${offset + 1}-${Math.min(offset + pageSize, filtered.length)} of ${filtered.length} integrations`}</p>
        {hasFilters && <button type="button" className="amlok-status-reset" onClick={reset}>Clear filters</button>}
      </div>

      <div className="amlok-status-table-wrap">
        <table id="integration-status-table">
          <caption className="amlok-status-sr-only">Integration availability by name, market, and development status. Active integrations marked Beta are available in beta.</caption>
          <thead><tr><th scope="col">Integration name</th><th scope="col">Market</th><th scope="col">Status</th></tr></thead>
          <tbody>
            {visible.map((integration) => (
              <tr key={integration.id}>
                <th scope="row"><a href={integration.href}>{integration.name}<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true"><path d="M7 17 17 7M7 7h10v10" /></svg></a><span className="amlok-status-category">{integration.category}</span></th>
                <td><span className="amlok-status-markets">{integration.markets.map((value) => <span key={value} className="amlok-status-market">{value}</span>)}</span></td>
                <td><span className="amlok-status-badges"><span className={`amlok-status-badge amlok-status-${statusClasses[integration.status]}`}><span aria-hidden="true" className="amlok-status-dot" />{integration.status}</span>{integration.beta && <span className="amlok-status-beta">Beta</span>}</span></td>
              </tr>
            ))}
            {!visible.length && <tr><td colSpan={3} className="amlok-status-empty"><strong>No matching integrations</strong><span>Try another name or change your filters.</span><button type="button" className="amlok-status-reset" onClick={reset}>Clear filters</button></td></tr>}
          </tbody>
        </table>
      </div>

      {filtered.length > 0 && <div className="amlok-status-pagination" aria-label="Integration results pagination">
        <span>Page {currentPage} of {totalPages}</span>
        <div><button type="button" aria-label="Previous results page" disabled={currentPage === 1} onClick={() => setPage(currentPage - 1)}>Previous</button><button type="button" aria-label="Next results page" disabled={currentPage === totalPages} onClick={() => setPage(currentPage + 1)}>Next</button></div>
      </div>}
    </div>
  );
};
