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
    const discount = input.useAgreedRates ? 0 : readNumber(input.discount, "discount", "Agreed discount", 0, 100, true);
    if (!input.enabled.insights && !input.enabled.signal) errors.products = "Select at least one product.";
    const discountBasisPoints = Math.round(discount * 100);
    const topUpAmount = readNumber(input.topUpAmount, "topUpAmount", "Top-up amount", 500, 100000000, true);
    const topUpThreshold = readNumber(input.autoPay ? input.topUpThreshold : "200", "topUpThreshold", "Automatic top-up threshold", 200, 100000000, true);
    const rows = [];
    for (const product of ["insights", "signal"]) {
      if (input.enabled[product] && !input.selectedTiers[product].some(Boolean)) errors.products = "Select at least one tier for each enabled product.";
      tiers.forEach((tier, index) => {
        const id = `${product}-${index}`;
        const label = `${product === "insights" ? "Insights" : "Signal"} ${tier.name} volume`;
        const active = input.enabled[product] && input.selectedTiers[product][index];
        const quantity = active ? readNumber(input.volumes[product][index], id, label, 50, 1000000, false) : 0;
        const unitCents = input.useAgreedRates && active
          ? Math.round(readNumber(input.agreedRates[product][index], `rate-${id}`, `${label} unit rate`, 0, 1000000, true) * 100)
          : tier[product];
        // Agreed rates are final effective rates. Do not apply the discount a second time.
        // Round the effective unit rate to cents first, then multiply the integer quantity.
        const effectiveUnitCents = Math.round(unitCents * (10000 - discountBasisPoints) / 10000);
        rows.push({ product, tier: tier.name, quantity, unitCents: effectiveUnitCents, cents: quantity * effectiveUnitCents });
      });
    }
    if (Object.keys(errors).length) return { valid: false, errors };
    const insightsCents = rows.filter((row) => row.product === "insights").reduce((sum, row) => sum + row.cents, 0);
    const signalCents = rows.filter((row) => row.product === "signal").reduce((sum, row) => sum + row.cents, 0);
    const monthlyCents = insightsCents + signalCents;
    const usageCents = monthlyCents * 12;
    const paymentCents = Math.round(commitment * 100) * 12;
    const topUpAmountCents = Math.round(topUpAmount * 100);
    const triggerCents = input.autoPay ? Math.round(topUpThreshold * 100) : 0;
    // Aggregate planning assumes prompt funding; the trigger is not a spending restriction.
    // With auto-pay off, estimate manual top-ups needed to fund the projected usage.
    const fundingGapCents = Math.max(0, usageCents + triggerCents - paymentCents);
    const topUpCents = Math.ceil(fundingGapCents / topUpAmountCents) * topUpAmountCents;
    const unusedCents = paymentCents + topUpCents - usageCents;
    return { valid: true, errors, rows, insightsCents, signalCents, monthlyCents, usageCents, paymentCents, topUpCents, unusedCents, fundingCents: paymentCents + topUpCents, commitment, discount };
  };
  // PRICING_MATH_END

  // VOLUME_PRESETS_START: preset selection never changes an exact typed quantity.
  const volumePresets = [50, 100, 200, 500, 1000, 5000];
  const customVolumePosition = volumePresets.length;
  const nearestVolumePreset = (raw) => {
    const value = Number(raw);
    if (value >= 10000) return customVolumePosition;
    if (!Number.isFinite(value) || value < 0) return 0;
    return volumePresets.reduce((closest, preset, index) => Math.abs(preset - value) < Math.abs(volumePresets[closest] - value) ? index : closest, 0);
  };
  // VOLUME_PRESETS_END

  const [enabled, setEnabled] = useState({ insights: true, signal: true });
  const [volumes, setVolumes] = useState({ insights: ["50", "50", "50"], signal: ["50", "50", "50"] });
  const [selectedTiers, setSelectedTiers] = useState({ insights: [true, false, false], signal: [true, false, false] });
  const [autoPay, setAutoPay] = useState(true);
  const [topUpAmount, setTopUpAmount] = useState("500");
  const [topUpThreshold, setTopUpThreshold] = useState("200");
  const [customVolumes, setCustomVolumes] = useState({});
  const [commitment, setCommitment] = useState("1000");
  const [discount, setDiscount] = useState("0");
  const [useAgreedRates, setUseAgreedRates] = useState(false);
  const [agreedRates, setAgreedRates] = useState({ insights: ["5", "15", "35"], signal: ["3", "5", "8"] });
  const estimate = calculatePricing({ enabled, volumes, selectedTiers, commitment, discount, useAgreedRates, agreedRates, autoPay, topUpAmount, topUpThreshold });
  const money = (cents) => `CAD ${(cents / 100).toLocaleString("en-CA", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const updateVolume = (product, index, value) => setVolumes((current) => ({ ...current, [product]: current[product].map((quantity, i) => i === index ? value : quantity) }));
  const chooseVolumePreset = (product, index, position) => {
    const id = `${product}-${index}`;
    setCustomVolumes((current) => ({ ...current, [id]: position === customVolumePosition }));
    // 10,000+ needs an exact quantity before it can produce a price.
    updateVolume(product, index, position === customVolumePosition ? (Number(volumes[product][index]) >= 10000 ? volumes[product][index] : "") : String(volumePresets[position]));
  };
  const typeVolume = (product, index, value) => {
    updateVolume(product, index, value);
    if (value !== "") setCustomVolumes((current) => ({ ...current, [`${product}-${index}`]: Number(value) >= 10000 }));
  };
  const reset = () => { setEnabled({ insights: true, signal: true }); setVolumes({ insights: ["50", "50", "50"], signal: ["50", "50", "50"] }); setSelectedTiers({ insights: [true, false, false], signal: [true, false, false] }); setAutoPay(true); setTopUpAmount("500"); setTopUpThreshold("200"); setCustomVolumes({}); setCommitment("1000"); setDiscount("0"); setUseAgreedRates(false); setAgreedRates({ insights: ["5", "15", "35"], signal: ["3", "5", "8"] }); };
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
      <p className="apc-volume-help" id="apc-volume-help">Select the tiers you use. Each selected volume starts at 50. Choose a slider preset or type an exact volume; for 10,000+, enter your exact quantity.</p>
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
                  const selected = selectedTiers[product.key][index];
                  const presetIndex = customVolumes[id] ? customVolumePosition : nearestVolumePreset(rawVolume);
                  const needsCustomVolume = customVolumes[id] && rawVolume === "";
                  const volumeLabel = `${product.name} ${tier.name} ${product.accessibleUnit}`;
                  return (
                    <div key={id} className="apc-tier">
                      <div className="apc-tier-heading"><label className="apc-tier-toggle"><input type="checkbox" checked={selected} onChange={(event) => setSelectedTiers((current) => ({ ...current, [product.key]: current[product.key].map((value, i) => i === index ? event.target.checked : value) }))} aria-label={`Include ${product.name} ${tier.name}`} /><strong>{tier.name}</strong></label><span>{useAgreedRates ? "Your agreed rate below" : `${money(tier[product.key])} / ${product.unit}`}</span></div>
                      <input id={`apc-${id}`} type="number" disabled={!selected} min="50" max="1000000" step="1" inputMode="numeric" placeholder={needsCustomVolume ? "10,000+" : undefined} value={rawVolume} onChange={(event) => typeVolume(product.key, index, event.target.value)} aria-label={volumeLabel} aria-invalid={Boolean(estimate.errors[id])} aria-describedby={`apc-volume-help${estimate.errors[id] ? ` apc-error-${id}` : ""}`} />
                      <div className="apc-slider-control">
                        <input type="range" disabled={!selected} min="0" max={customVolumePosition} step="1" value={presetIndex} onChange={(event) => chooseVolumePreset(product.key, index, Number(event.target.value))} aria-label={`${volumeLabel} preset`} aria-valuetext={needsCustomVolume ? "10,000 or more. Enter an exact volume in the number field." : `${Number(rawVolume || 0).toLocaleString("en-CA")} ${product.accessibleUnit}${volumePresets.includes(Number(rawVolume)) ? "" : ", custom volume"}`} aria-describedby="apc-volume-help" style={{ "--apc-slider-progress": `${presetIndex / customVolumePosition * 100}%` }} />
                        <div className="apc-slider-labels" aria-hidden="true">
                          {[...volumePresets, "10,000+"].map((value, position) => <span key={position} style={{ left: `${position / customVolumePosition * 100}%` }}>{typeof value === "number" ? value.toLocaleString("en-CA") : value}</span>)}
                        </div>
                      </div>
                      {estimate.errors[id] && <p id={`apc-error-${id}`} className="apc-error">{needsCustomVolume ? "Enter an exact volume of 10,000 or more, or choose a lower preset." : estimate.errors[id]}</p>}
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
                <input id="apc-discount" type="number" min="0" max="100" step="0.01" inputMode="decimal" value={discount} disabled={useAgreedRates} onChange={(event) => setDiscount(event.target.value)} aria-invalid={Boolean(estimate.errors.discount)} aria-describedby="apc-discount-help apc-error-discount" />
                <p id="apc-discount-help">{useAgreedRates ? "Your agreed rates already include discounts. No additional discount is applied." : "Optional. Applies equally to both products. No discount is assumed."}</p>
                <p id="apc-error-discount" className="apc-error">{estimate.errors.discount || ""}</p>
              </div>
            </div>
          </section>
          <section className="apc-panel apc-terms" aria-labelledby="apc-funding-title">
            <h2 id="apc-funding-title">Top-up planning</h2>
            <label className="apc-product-toggle"><input type="checkbox" checked={autoPay} onChange={(event) => setAutoPay(event.target.checked)} /><span>Estimate with automatic top-ups</span></label>
            <p>Configure actual payments in your client portal. This calculator does not collect payments.</p>
            <div className="apc-terms-grid">
              <div>
                <label htmlFor="apc-threshold">Automatic top-up threshold (CAD)</label>
                <input id="apc-threshold" type="number" min="200" max="100000000" step="0.01" value={topUpThreshold} disabled={!autoPay} onChange={(event) => setTopUpThreshold(event.target.value)} aria-invalid={Boolean(estimate.errors.topUpThreshold)} aria-describedby="apc-threshold-help" />
                <p id="apc-threshold-help">Starts at CAD 200.00. A trigger, not a balance floor.</p>
                {estimate.errors.topUpThreshold && <p className="apc-error">{estimate.errors.topUpThreshold}</p>}
              </div>
              <div>
                <label htmlFor="apc-topup">Top-up amount (CAD)</label>
                <input id="apc-topup" type="number" min="500" max="100000000" step="0.01" value={topUpAmount} onChange={(event) => setTopUpAmount(event.target.value)} aria-invalid={Boolean(estimate.errors.topUpAmount)} aria-describedby="apc-topup-help" />
                <p id="apc-topup-help">Minimum CAD 500.00. With auto-pay off, this estimates manual funding needed.</p>
                {estimate.errors.topUpAmount && <p className="apc-error">{estimate.errors.topUpAmount}</p>}
              </div>
            </div>
          </section>
          <section className="apc-panel apc-terms" aria-labelledby="apc-rates-title">
            <h2 id="apc-rates-title">Negotiated rates</h2>
            <label className="apc-product-toggle">
              <input type="checkbox" checked={useAgreedRates} onChange={(event) => setUseAgreedRates(event.target.checked)} />
              <span>Use my agreed unit rates</span>
            </label>
            <p>Enter final CAD rates from your agreement. Custom quotes keep the Standard, Advanced, or Complex tier assigned by AMLOK.</p>
            {useAgreedRates && <div className="apc-terms-grid">
              {products.filter((product) => enabled[product.key]).map((product) => tiers.map((tier, index) => {
                const id = `rate-${product.key}-${index}`;
                return <div key={id}>
                  <label htmlFor={`apc-${id}`}>{product.name} - {tier.name}</label>
                  <input id={`apc-${id}`} type="number" min="0" max="1000000" step="0.01" inputMode="decimal" value={agreedRates[product.key][index]} onChange={(event) => setAgreedRates((current) => ({ ...current, [product.key]: current[product.key].map((rate, i) => i === index ? event.target.value : rate) }))} aria-invalid={Boolean(estimate.errors[id])} aria-describedby={`apc-error-${id}`} />
                  <p>CAD / {product.unit}</p>
                  <p id={`apc-error-${id}`} className="apc-error">{estimate.errors[id] || ""}</p>
                </div>;
              }))}
            </div>}
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
              <p className="apc-explanation">{autoPay ? "Estimated top-ups use your selected trigger and amount. Credits below the trigger can still fund requests while a payment is pending." : "Auto-pay is off. Additional credits shown are manual funding needed to cover this estimate. Processing stops only when credits cannot cover the next billable operation."}</p>
              <p className="apc-footnote">The prepayment is counted once. Funding is an aggregate estimate with prompt settlement; actual request timing, reservations, and payment delays affect top-ups. Agreed rates or discounts change usage deductions, not your monthly minimum.</p>
            </div>
          ) : <p className="apc-invalid-summary">Complete the highlighted fields to see your estimate.</p>}
        </aside>
      </div>
      <p className="apc-sr-only" role="status" aria-live="polite" aria-atomic="true">{estimate.valid ? `Estimate updated. Monthly usage ${money(estimate.monthlyCents)}. Payment at signing or renewal ${money(estimate.paymentCents)}. Additional credits ${money(estimate.topUpCents)}. Unused credits ${money(estimate.unusedCents)}.` : "Estimate unavailable. Check the highlighted fields."}</p>
    </div>
  );
};
