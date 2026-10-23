// Mintlify provides React hooks. Keep this component self-contained for its MDX sandbox.
export const PricingCalculator = () => {
  // PRICING_MATH_START: exercised directly by scripts/test-pricing-calculator.mjs.
  const tiers = [
    { name: "Standard", insights: 500, signal: 300 },
    { name: "Advanced", insights: 1500, signal: 500 },
    { name: "Complex", insights: 3500, signal: 800 },
  ];
  const calculatePricing = (input) => {
    const errors = {};
    const readNumber = (raw, id, label, min, max, decimals) => {
      const value = String(raw).trim();
      const format = decimals ? /^\d+(\.\d{1,2})?$/ : /^\d+$/;
      const number = Number(value);
      if (!format.test(value) || !Number.isFinite(number) || number < min || number > max) {
        errors[id] = `${label}: enter ${decimals ? "a number with up to 2 decimal places" : "a whole number"} from ${min.toLocaleString("en-CA")} to ${max.toLocaleString("en-CA")}.`;
        return 0;
      }
      return number;
    };
    const commitment = readNumber(input.commitment, "commitment", "Monthly minimum", 1000, 100000000, true);
    const discount = readNumber(input.discount, "discount", "Agreed discount", 0, 100, true);
    if (!input.enabled.insights && !input.enabled.signal) errors.products = "Select at least one product.";
    const discountBasisPoints = Math.round(discount * 100);
    const rows = [];
    for (const product of ["insights", "signal"]) {
      tiers.forEach((tier, index) => {
        const id = `${product}-${index}`;
        const label = `${product === "insights" ? "Insights" : "Signal"} ${tier.name} volume`;
        const quantity = input.enabled[product] ? readNumber(input.volumes[product][index], id, label, 0, 1000000, false) : 0;
        // Round each monthly product/tier subtotal to cents, then project 12 equal months.
        rows.push({ product, tier: tier.name, quantity, unitCents: tier[product], cents: Math.round(quantity * tier[product] * (10000 - discountBasisPoints) / 10000) });
      });
    }
    if (Object.keys(errors).length) return { valid: false, errors };
    const insightsCents = rows.filter((row) => row.product === "insights").reduce((sum, row) => sum + row.cents, 0);
    const signalCents = rows.filter((row) => row.product === "signal").reduce((sum, row) => sum + row.cents, 0);
    const monthlyCents = insightsCents + signalCents;
    const usageCents = monthlyCents * 12;
    const paymentCents = Math.round(commitment * 100) * 12;
    const topUpCents = Math.max(0, usageCents - paymentCents);
    const unusedCents = Math.max(0, paymentCents - usageCents);
    return { valid: true, errors, rows, insightsCents, signalCents, monthlyCents, usageCents, paymentCents, topUpCents, unusedCents, fundingCents: paymentCents + topUpCents, commitment, discount };
  };
  // PRICING_MATH_END

  // VOLUME_PRESETS_START: preset selection never changes an exact typed quantity.
  const volumePresets = [0, 50, 100, 200, 500, 1000, 5000, 10000];
  const nearestVolumePreset = (raw) => {
    const value = Number(raw);
    if (value > 10000) return 8;
    if (!Number.isFinite(value) || value < 0) return 0;
    return volumePresets.reduce((closest, preset, index) => Math.abs(preset - value) < Math.abs(volumePresets[closest] - value) ? index : closest, 0);
  };
  // VOLUME_PRESETS_END

  const [enabled, setEnabled] = useState({ insights: true, signal: true });
  const [volumes, setVolumes] = useState({ insights: ["100", "0", "0"], signal: ["200", "0", "0"] });
  const [customVolumes, setCustomVolumes] = useState({});
  const [commitment, setCommitment] = useState("1000");
  const [discount, setDiscount] = useState("0");
  const estimate = calculatePricing({ enabled, volumes, commitment, discount });
  const money = (cents) => `CAD ${(cents / 100).toLocaleString("en-CA", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const updateVolume = (product, index, value) => setVolumes((current) => ({ ...current, [product]: current[product].map((quantity, i) => i === index ? value : quantity) }));
  const chooseVolumePreset = (product, index, position) => {
    const id = `${product}-${index}`;
    setCustomVolumes((current) => ({ ...current, [id]: position === 8 }));
    // 10,000+ needs an exact quantity before it can produce a price.
    updateVolume(product, index, position === 8 ? (Number(volumes[product][index]) > 10000 ? volumes[product][index] : "") : String(volumePresets[position]));
  };
  const typeVolume = (product, index, value) => {
    updateVolume(product, index, value);
    if (value !== "") setCustomVolumes((current) => ({ ...current, [`${product}-${index}`]: Number(value) > 10000 }));
  };
  const reset = () => { setEnabled({ insights: true, signal: true }); setVolumes({ insights: ["100", "0", "0"], signal: ["200", "0", "0"] }); setCustomVolumes({}); setCommitment("1000"); setDiscount("0"); };
  const products = [
    { key: "insights", name: "AMLOK Insights", description: "Completed underwritings per month", unit: "underwriting", accessibleUnit: "underwritings per month" },
    { key: "signal", name: "AMLOK Signal", description: "Active monitored accounts each month", unit: "account / month", accessibleUnit: "active accounts per month" },
  ];

  return (
    <div className="amlok-pricing-calc not-prose">
      <div className="apc-toolbar">
        <span className="apc-badge">CAD estimates · 12-month view</span>
        <button type="button" onClick={reset} className="apc-reset">Reset example</button>
      </div>
      <p className="apc-volume-help" id="apc-volume-help">Choose a slider preset or type an exact volume. For 10,000+, enter your volume in the number field.</p>
      <div className="apc-layout">
        <div className="apc-inputs">
          {products.map((product) => (
            <section className="apc-panel" key={product.key} aria-labelledby={`apc-${product.key}-title`}>
              <div className="apc-product-header">
                <label className="apc-product-toggle">
                  <input type="checkbox" checked={enabled[product.key]} onChange={(event) => setEnabled({ ...enabled, [product.key]: event.target.checked })} aria-label={`Include ${product.name}`} />
                  <span id={`apc-${product.key}-title`}>{product.name}</span>
                </label>
                <p>{product.description}</p>
              </div>
              <fieldset disabled={!enabled[product.key]} className="apc-tiers">
                <legend className="apc-sr-only">{product.name} monthly volumes by complexity</legend>
                {tiers.map((tier, index) => {
                  const id = `${product.key}-${index}`;
                  const rawVolume = volumes[product.key][index];
                  const presetIndex = customVolumes[id] ? 8 : nearestVolumePreset(rawVolume);
                  const needsCustomVolume = customVolumes[id] && rawVolume === "";
                  const volumeLabel = `${product.name} ${tier.name} ${product.accessibleUnit}`;
                  return (
                    <div key={id} className="apc-tier">
                      <label htmlFor={`apc-${id}`}><strong>{tier.name}</strong><span>{money(tier[product.key])} / {product.unit}</span></label>
                      <input id={`apc-${id}`} type="number" min="0" max="1000000" step="1" inputMode="numeric" placeholder={needsCustomVolume ? "10,001+" : undefined} value={rawVolume} onChange={(event) => typeVolume(product.key, index, event.target.value)} aria-label={volumeLabel} aria-invalid={Boolean(estimate.errors[id])} aria-describedby={`apc-volume-help${estimate.errors[id] ? ` apc-error-${id}` : ""}`} />
                      <div className="apc-slider-control">
                        <input type="range" min="0" max="8" step="1" value={presetIndex} onChange={(event) => chooseVolumePreset(product.key, index, Number(event.target.value))} aria-label={`${volumeLabel} preset`} aria-valuetext={needsCustomVolume ? "More than 10,000. Enter an exact volume in the number field." : `${Number(rawVolume || 0).toLocaleString("en-CA")} ${product.accessibleUnit}${volumePresets.includes(Number(rawVolume)) ? "" : ", custom volume"}`} aria-describedby="apc-volume-help" style={{ "--apc-slider-progress": `${presetIndex / 8 * 100}%` }} />
                        <div className="apc-slider-labels" aria-hidden="true">
                          {[...volumePresets, "10,000+"].map((value, position) => <span key={position} className={position % 2 ? "apc-tick-low" : undefined} style={{ left: `${position / 8 * 100}%` }}>{typeof value === "number" ? value.toLocaleString("en-CA") : value}</span>)}
                        </div>
                      </div>
                      {estimate.errors[id] && <p id={`apc-error-${id}`} className="apc-error">{needsCustomVolume ? "Enter an exact volume above 10,000, or choose a lower preset." : estimate.errors[id]}</p>}
                    </div>
                  );
                })}
              </fieldset>
            </section>
          ))}
          {estimate.errors.products && <p className="apc-error" role="alert">{estimate.errors.products}</p>}
          <section className="apc-panel apc-terms" aria-labelledby="apc-terms-title">
            <h2 id="apc-terms-title">Your commitment and discount</h2>
            <div className="apc-terms-grid">
              <div>
                <label htmlFor="apc-commitment">Minimum monthly commitment (CAD)</label>
                <input id="apc-commitment" type="number" min="1000" max="100000000" step="0.01" inputMode="decimal" value={commitment} onChange={(event) => setCommitment(event.target.value)} aria-invalid={Boolean(estimate.errors.commitment)} aria-describedby="apc-commitment-help apc-error-commitment" />
                <p id="apc-commitment-help">Starts at CAD 1,000. Paid annually at signing and each renewal.</p>
                <p id="apc-error-commitment" className="apc-error">{estimate.errors.commitment || ""}</p>
              </div>
              <div>
                <label htmlFor="apc-discount">Agreed unit-rate discount (%)</label>
                <input id="apc-discount" type="number" min="0" max="100" step="0.01" inputMode="decimal" value={discount} onChange={(event) => setDiscount(event.target.value)} aria-invalid={Boolean(estimate.errors.discount)} aria-describedby="apc-discount-help apc-error-discount" />
                <p id="apc-discount-help">Optional. Applies equally to both products. No discount is assumed.</p>
                <p id="apc-error-discount" className="apc-error">{estimate.errors.discount || ""}</p>
              </div>
            </div>
          </section>
        </div>
        <aside className="apc-summary" aria-labelledby="apc-estimate-title">
          <h2 id="apc-estimate-title">Your estimate</h2>
          {estimate.valid ? (
            <div>
              <div className="apc-hero-amount"><span>Estimated monthly usage</span><strong data-testid="monthly-usage">{money(estimate.monthlyCents)}</strong><span>Deducted from your shared credit wallet</span></div>
              <dl className="apc-breakdown">
                <div><dt>Insights / month</dt><dd data-testid="insights-monthly">{money(estimate.insightsCents)}</dd></div>
                <div><dt>Signal / month</dt><dd data-testid="signal-monthly">{money(estimate.signalCents)}</dd></div>
                <div className="apc-total-row"><dt>Usage over 12 months</dt><dd data-testid="usage-12-months">{money(estimate.usageCents)}</dd></div>
              </dl>
              <div className="apc-payment"><span>Payment at signing or renewal</span><strong data-testid="payment-due">{money(estimate.paymentCents)}</strong><p>{money(Math.round(estimate.commitment * 100))} monthly minimum × 12</p></div>
              <dl className="apc-breakdown">
                <div><dt>Additional credits needed</dt><dd data-testid="additional-credits">{money(estimate.topUpCents)}</dd></div>
                <div><dt>Projected unused credits</dt><dd data-testid="unused-credits">{money(estimate.unusedCents)}</dd></div>
                <div className="apc-total-row"><dt>Total funding over 12 months</dt><dd data-testid="total-funding">{money(estimate.fundingCents)}</dd></div>
              </dl>
              <p className="apc-explanation">{estimate.topUpCents > 0 ? "Estimated usage exceeds prepaid credits. Purchase additional credits as needed, or agree to automatic top-ups." : "The prepaid credits cover this usage estimate. Unused credits remain available while your account stays active."}</p>
              <p className="apc-footnote">The payment funds your usage wallet. It is counted once in total funding. A unit-rate discount reduces usage deductions, not your monthly minimum.</p>
            </div>
          ) : <p className="apc-invalid-summary">Complete the highlighted fields to see your estimate.</p>}
        </aside>
      </div>
      <p className="apc-sr-only" role="status" aria-live="polite" aria-atomic="true">{estimate.valid ? `Estimate updated. Monthly usage ${money(estimate.monthlyCents)}. Payment at signing or renewal ${money(estimate.paymentCents)}. Additional credits ${money(estimate.topUpCents)}. Unused credits ${money(estimate.unusedCents)}.` : "Estimate unavailable. Check the highlighted fields."}</p>
    </div>
  );
};
