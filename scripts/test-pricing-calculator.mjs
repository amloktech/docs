import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

// Run the exact pure calculation used by the Mintlify component, without React or a DOM.
const source = readFileSync(new URL("../snippets/pricing-calculator.jsx", import.meta.url), "utf8");
const math = source.split("// PRICING_MATH_START:")[1].split("\n").slice(1).join("\n").split("// PRICING_MATH_END")[0];
const calculate = vm.runInNewContext(`(() => { ${math}; return calculatePricing; })()`);
const presetCode = source.split("// VOLUME_PRESETS_START:")[1].split("\n").slice(1).join("\n").split("// VOLUME_PRESETS_END")[0];
const presetPosition = vm.runInNewContext(`(() => { ${presetCode}; return nearestVolumePreset; })()`);
const baseline = () => ({ enabled: { insights: true, signal: true }, volumes: { insights: ["100", "0", "0"], signal: ["200", "0", "0"] }, commitment: "1000", discount: "0" });
let tests = 0;
const test = (name, run) => { run(); tests++; console.log(`PASS ${name}`); };

test("Mixed monthly usage consumes credits without adding the prepayment twice", () => {
  const r = calculate(baseline());
  assert.equal(r.valid, true);
  assert.equal(r.monthlyCents, 110000);
  assert.equal(r.paymentCents, 1200000);
  assert.equal(r.usageCents, 1320000);
  assert.equal(r.topUpCents, 120000);
  assert.equal(r.unusedCents, 0);
  assert.equal(r.fundingCents, 1320000);
});
test("Each of the six approved rates is used independently", () => {
  for (const [product, prices] of [["insights", [500, 1500, 3500]], ["signal", [300, 500, 800]]]) {
    for (let i = 0; i < 3; i++) {
      const input = baseline(); input.volumes = { insights: ["0", "0", "0"], signal: ["0", "0", "0"] }; input.volumes[product][i] = "1";
      assert.equal(calculate(input).monthlyCents, prices[i]);
    }
  }
});
test("Published mixed-portfolio example exactly consumes CAD 12,000", () => {
  const input = baseline(); input.volumes.insights = ["50", "10", "0"];
  const r = calculate(input); assert.equal(r.usageCents, 1200000); assert.equal(r.topUpCents, 0); assert.equal(r.unusedCents, 0);
});
test("Below-minimum usage leaves credits available", () => {
  const input = baseline(); input.enabled.insights = false; input.volumes.signal = ["300", "0", "0"];
  const r = calculate(input); assert.equal(r.usageCents, 1080000); assert.equal(r.unusedCents, 120000); assert.equal(r.fundingCents, 1200000);
});
test("Discount applies to usage, never the monthly minimum", () => {
  const input = baseline(); input.discount = "10";
  const r = calculate(input); assert.equal(r.monthlyCents, 99000); assert.equal(r.paymentCents, 1200000); assert.equal(r.unusedCents, 12000);
});
test("A larger commitment changes prepayment but not consumption", () => {
  const input = baseline(); input.commitment = "2000";
  const r = calculate(input); assert.equal(r.paymentCents, 2400000); assert.equal(r.monthlyCents, 110000); assert.equal(r.unusedCents, 1080000);
});
test("Zero usage does not erase the commitment", () => {
  const input = baseline(); input.volumes = { insights: ["0", "0", "0"], signal: ["0", "0", "0"] };
  const r = calculate(input); assert.equal(r.monthlyCents, 0); assert.equal(r.fundingCents, 1200000); assert.equal(r.unusedCents, 1200000);
});
test("Fractional discount rounds monthly line totals to cents", () => {
  const input = baseline(); input.enabled.signal = false; input.volumes.insights = ["1", "0", "0"]; input.discount = "33.33";
  const r = calculate(input); assert.equal(r.monthlyCents, 333); assert.equal(r.usageCents, 3996);
});
test("Invalid and incomplete fields do not produce a misleading estimate", () => {
  for (const value of ["", "-1", "1.5", "1000001", "Infinity", "NaN", "1e3"]) {
    const input = baseline(); input.volumes.insights[0] = value; assert.equal(calculate(input).valid, false, value);
  }
  for (const value of ["999", "", "-1000", "1000.001", "100000001"]) {
    const input = baseline(); input.commitment = value; assert.equal(calculate(input).valid, false, value);
  }
  for (const value of ["-1", "101", "", "1.234"]) {
    const input = baseline(); input.discount = value; assert.equal(calculate(input).valid, false, value);
  }
});
test("Disabled products contribute nothing and their dormant fields do not block estimates", () => {
  const input = baseline(); input.enabled.insights = false; input.volumes.insights[0] = "invalid";
  const r = calculate(input); assert.equal(r.valid, true); assert.equal(r.monthlyCents, 60000);
  input.enabled.signal = false; assert.equal(calculate(input).valid, false);
});
test("Maximum inputs remain safe integer cents, with balanced funding", () => {
  const input = baseline(); input.volumes = { insights: ["1000000", "1000000", "1000000"], signal: ["1000000", "1000000", "1000000"] }; input.commitment = "100000000";
  const r = calculate(input); assert.equal(r.valid, true);
  for (const key of ["monthlyCents", "usageCents", "paymentCents", "topUpCents", "unusedCents", "fundingCents"]) assert.ok(Number.isSafeInteger(r[key]), key);
  assert.equal(r.fundingCents - r.usageCents, r.unusedCents);
});
test("Slider presets end with a single 10,000+ position", () => {
  [0, 50, 100, 200, 500, 1000, 5000].forEach((volume, position) => assert.equal(presetPosition(String(volume)), position));
  assert.equal(presetPosition("10000"), 7);
  assert.equal(presetPosition("10001"), 7);
  assert.equal(presetPosition("1000000"), 7);
});
test("Exact typed volumes are priced without snapping or capping to slider presets", () => {
  for (const quantity of [175, 10000, 12500]) {
    const input = baseline(); input.enabled.signal = false; input.volumes.insights = [String(quantity), "0", "0"];
    const r = calculate(input); assert.equal(r.monthlyCents, quantity * 500); assert.equal(r.usageCents, quantity * 500 * 12);
  }
});
console.log(`${tests} pricing calculator checks passed.`);
