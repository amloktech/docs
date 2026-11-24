export const DefinitionTable = ({ version }) => {
  const [catalog, setCatalog] = useState(null);
  const [error, setError] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const [query, setQuery] = useState("");
  const [type, setType] = useState("all");
  const [category, setCategory] = useState("all");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const tableRef = useRef(null);
  const normalize = (value) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setCatalog(null);
    setError(false);
    fetch(`/downloads/definition-table.json?v=${encodeURIComponent(version)}`, { signal: controller.signal })
      .then((response) => { if (!response.ok) throw new Error("Catalog unavailable"); return response.json(); })
      .then((data) => {
        if (data.schema_version !== 1 || !Array.isArray(data.rows) || !Array.isArray(data.text)) throw new Error("Unsupported catalog");
        const rows = data.rows.map((row) => {
          const explanation = row.meaning.map((index) => {
            if (typeof data.text[index] !== "string") throw new Error("Incomplete definition");
            return data.text[index];
          }).join(" ");
          return { ...row, explanation, search: normalize([row.type, row.key, row.name, row.category, row.unit, row.context, row.period, explanation].join(" ")) };
        });
        if (active) setCatalog({ ...data, rows });
      })
      .catch((cause) => { if (active && cause.name !== "AbortError") setError(true); });
    return () => { active = false; controller.abort(); };
  }, [version, attempt]);

  const categories = useMemo(() => catalog ? Array.from(new Set(catalog.rows.filter((row) => type === "all" || row.type === type).map((row) => row.category))).sort() : [], [catalog, type]);
  const filtered = useMemo(() => {
    const search = normalize(query);
    const terms = search.split(/\s+/).filter(Boolean);
    const candidates = catalog ? catalog.rows.filter((row) => (type === "all" || row.type === type) && (category === "all" || row.category === category)) : [];
    const exact = search ? candidates.filter((row) => normalize(row.key) === search) : [];
    return exact.length ? exact : candidates.filter((row) => terms.every((term) => row.search.includes(term)));
  }, [catalog, query, type, category]);
  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  const offset = (currentPage - 1) * pageSize;
  const visible = filtered.slice(offset, offset + pageSize);
  const hasFilters = query !== "" || type !== "all" || category !== "all";
  const chooseType = (value) => { setType(value); setCategory("all"); setPage(1); };
  const reset = () => { setQuery(""); chooseType("all"); };
  const movePage = (value) => { setPage(value); if (tableRef.current) tableRef.current.scrollTop = 0; };
  const headlineTypes = [["Dimension", "Dimensions"], ["Metric", "Metrics"], ["Attribute", "Attributes"], ["Category", "Categories"], ["Group", "Groups"]];

  return (
    <div className="amlok-definitions not-prose" aria-busy={!catalog && !error}>
      {error ? <div className="amlok-definitions-notice" role="alert"><strong>The catalog could not load.</strong><p>Try again, or use the metric and category references linked below.</p><button type="button" onClick={() => setAttempt(attempt + 1)}>Retry loading</button></div> : !catalog ? <div className="amlok-definitions-notice" role="status">Loading definitions...</div> : <>
        <div className="amlok-definitions-totals" aria-label="Filter by definition type">
          {headlineTypes.map(([value, label]) => <button type="button" key={value} aria-pressed={type === value} onClick={() => chooseType(type === value ? "all" : value)}><span>{label}</span><strong>{catalog.counts[value].toLocaleString("en-CA")}</strong></button>)}
        </div>
        <div className="amlok-definitions-filters">
          <div><label htmlFor="definition-search">Search definitions</label><input id="definition-search" type="search" placeholder="Name, API key or concept..." value={query} onChange={(event) => { setQuery(event.target.value); setPage(1); }} aria-controls="definition-table" autoComplete="off" /></div>
          <div><label htmlFor="definition-type">Type</label><select id="definition-type" value={type} onChange={(event) => chooseType(event.target.value)} aria-controls="definition-table"><option value="all">All types</option>{Object.keys(catalog.counts).map((value) => <option key={value} value={value}>{value} ({catalog.counts[value].toLocaleString("en-CA")})</option>)}</select></div>
          <div><label htmlFor="definition-category">Dimension or category</label><select id="definition-category" value={category} onChange={(event) => { setCategory(event.target.value); setPage(1); }} aria-controls="definition-table"><option value="all">All dimensions and categories</option>{categories.map((value) => <option key={value} value={value}>{value}</option>)}</select></div>
        </div>
        <div className="amlok-definitions-results"><p role="status" aria-live="polite" aria-atomic="true">{filtered.length ? `Showing ${(offset + 1).toLocaleString("en-CA")}-${Math.min(offset + pageSize, filtered.length).toLocaleString("en-CA")} of ${filtered.length.toLocaleString("en-CA")} definitions` : "No matching definitions"}</p>{hasFilters && <button type="button" onClick={reset}>Clear filters</button>}</div>
        <div ref={tableRef} className="amlok-definitions-scroll" role="region" aria-label="Definition results" tabIndex={0}>
          <table id="definition-table">
            <caption className="amlok-definitions-sr">API definitions, explanations, categories and units</caption>
            <thead><tr><th scope="col">Name and API key</th><th scope="col">Type</th><th scope="col">Dimension / category</th><th scope="col">What it represents</th><th scope="col">Unit</th></tr></thead>
            <tbody>{visible.map((row) => <tr key={`${row.type}:${row.key}`}>
              <th scope="row"><span className="amlok-definitions-name">{row.name}</span><code>{row.key}</code></th>
              <td><span className="amlok-definitions-type">{row.type}</span></td>
              <td>{row.category}</td>
              <td><p>{row.explanation}</p>{(row.context || row.period) && <div className="amlok-definitions-context">{row.context && <span>{row.context}</span>}{row.period && <span>{row.period}</span>}</div>}</td>
              <td>{row.unit ? <code>{row.unit}</code> : <span aria-label="Not applicable">-</span>}</td>
            </tr>)}{!visible.length && <tr><td colSpan={5} className="amlok-definitions-empty"><strong>No matching definitions</strong><p>Try another term or clear your filters.</p><button type="button" onClick={reset}>Clear filters</button></td></tr>}</tbody>
          </table>
        </div>
        {filtered.length > 0 && <div className="amlok-definitions-pagination"><label htmlFor="definition-page-size">Rows per page <select id="definition-page-size" value={pageSize} onChange={(event) => { setPageSize(Number(event.target.value)); setPage(1); }}><option value={10}>10</option><option value={25}>25</option><option value={50}>50</option></select></label><span>Page {currentPage.toLocaleString("en-CA")} of {totalPages.toLocaleString("en-CA")}</span><div><button type="button" disabled={currentPage === 1} onClick={() => movePage(currentPage - 1)} aria-label="Previous definitions page">Previous</button><button type="button" disabled={currentPage === totalPages} onClick={() => movePage(currentPage + 1)} aria-label="Next definitions page">Next</button></div></div>}
      </>}
    </div>
  );
};
