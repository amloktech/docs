import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
const source = readFileSync(new URL("../snippets/pricing-calculator.jsx", import.meta.url), "utf8");
const math = source.split("// PRICING_MATH_START:")[1].split("\n").slice(1).join("\n").split("// PRICING_MATH_END")[0];
const calculate = vm.runInNewContext("(() => { " + math + "; return calculatePricing; })()");
const presetCode = source.split("// VOLUME_PRESETS_START:")[1].split("\n").slice(1).join("\n").split("// VOLUME_PRESETS_END")[0];
const presetPosition = vm.runInNewContext("(() => { " + presetCode + "; return nearestVolumePreset; })()");
const baseline = () => ({ enabled: { insights: true, signal: true }, selectedTiers: { insights:[true,false,false],signal:[true,false,false] }, volumes: { insights:["50","50","50"], signal:["50","50","50"] }, commitment:"1000",discount:"0",autoPay:true,topUpAmount:"500",topUpThreshold:"200" });
let tests=0;
const test=(name,fn)=>{fn();tests++;console.log("PASS "+name);};
test("Opening example starts selected volumes at 50 and prepayment at CAD 12,000",()=>{
 const r=calculate(baseline());assert.equal(r.valid,true);assert.equal(r.monthlyCents,40000);assert.equal(r.paymentCents,1200000);assert.equal(r.unusedCents,720000);
});
test("Prepayment is not added twice",()=>{
 const i=baseline();i.volumes.insights[0]="100";i.volumes.signal[0]="200";
 const r=calculate(i);assert.equal(r.monthlyCents,110000);assert.equal(r.topUpCents,150000);assert.equal(r.fundingCents,1350000);assert.equal(r.unusedCents,30000);
});
test("Each product and tier uses its approved price",()=>{
 for(const [p,rates] of [["insights",[500,1500,3500]],["signal",[300,500,800]]]){
  for(let tier=0;tier<3;tier++){const i=baseline();i.enabled={insights:p==="insights",signal:p==="signal"};i.selectedTiers[p]=[false,false,false];i.selectedTiers[p][tier]=true;assert.equal(calculate(i).monthlyCents,50*rates[tier]);}
 }
});
test("Inactive tiers are excluded and do not need zero or valid dormant inputs",()=>{
 const i=baseline();i.volumes.insights[1]="";assert.equal(calculate(i).valid,true);
 i.selectedTiers.insights[1]=true;assert.equal(calculate(i).valid,false);
 i.selectedTiers.insights=[false,false,false];assert.equal(calculate(i).valid,false);
 i.enabled.insights=false;assert.equal(calculate(i).monthlyCents,15000);
});
test("Active volumes below 50 and malformed inputs are rejected",()=>{
 for(const value of ["0","1","49","","-1","50.5","1000001","Infinity","NaN","1e3"]){const i=baseline();i.volumes.insights[0]=value;assert.equal(calculate(i).valid,false,value);}
 for(const value of ["999","","1000.001","100000001"]){const i=baseline();i.commitment=value;assert.equal(calculate(i).valid,false,value);}
 for(const value of ["-1","100.01","101","","1.234"]){const i=baseline();i.discount=value;assert.equal(calculate(i).valid,false,value);}
});
test("Effective unit rate rounds first, half up, before multiplying volume",()=>{
 const i=baseline();i.enabled.signal=false;i.discount="33.33";const r=calculate(i);
 assert.equal(r.rows[0].unitCents,333);assert.equal(r.monthlyCents,16650);
 i.discount="33.30";assert.equal(calculate(i).rows[0].unitCents,334);
});
test("Discount changes usage but not the monthly minimum",()=>{
 const i=baseline();i.discount="10";const r=calculate(i);assert.equal(r.monthlyCents,36000);assert.equal(r.paymentCents,1200000);
});
test("Agreed effective rates are not discounted again",()=>{
 const i=baseline();i.useAgreedRates=true;i.discount="50";i.agreedRates={insights:["4.50","13.50","31.50"],signal:["2.50","4.00","7.00"]};
 const r=calculate(i);assert.equal(r.monthlyCents,35000);assert.equal(r.discount,0);
 i.agreedRates.insights[0]="4.555";assert.equal(calculate(i).valid,false);
});
test("No auto-pay allows all prepaid credits to be consumed",()=>{
 const i=baseline();i.enabled.signal=false;i.volumes.insights[0]="200";i.autoPay=false;
 let r=calculate(i);assert.equal(r.usageCents,1200000);assert.equal(r.topUpCents,0);assert.equal(r.unusedCents,0);
 i.autoPay=true;r=calculate(i);assert.equal(r.topUpCents,50000);assert.equal(r.unusedCents,50000);
});
test("Auto-pay trigger differs from a processing floor",()=>{
 const i=baseline();i.enabled.signal=false;i.volumes.insights[0]="197";
 assert.equal(calculate(i).topUpCents,50000);i.autoPay=false;
 assert.equal(calculate(i).topUpCents,0);assert.equal(calculate(i).unusedCents,18000);
});
test("Top-up amount and threshold are configurable with enforced minimums",()=>{
 const i=baseline();i.enabled.signal=false;i.volumes.insights[0]="200";i.topUpAmount="1000";
 assert.equal(calculate(i).topUpCents,100000);i.topUpAmount="499.99";assert.equal(calculate(i).valid,false);
 i.topUpAmount="500";i.topUpThreshold="199.99";assert.equal(calculate(i).valid,false);
 i.autoPay=false;assert.equal(calculate(i).valid,true);
});
test("Slider ends with only one 10,000+ option",()=>{
 [50,100,200,500,1000,5000].forEach((v,p)=>assert.equal(presetPosition(String(v)),p));
 for(const v of [10000,10001,1000000])assert.equal(presetPosition(String(v)),6);
});
test("Exact typed quantities are not snapped to preset values",()=>{
 for(const q of [175,10000,12500]){const i=baseline();i.enabled.signal=false;i.volumes.insights[0]=String(q);assert.equal(calculate(i).monthlyCents,q*500);}
});
test("No enabled product produces no estimate",()=>{
 const i=baseline();i.enabled={insights:false,signal:false};assert.equal(calculate(i).valid,false);
});
test("Maximum supported inputs remain exact integer cents",()=>{
 const i=baseline();i.selectedTiers={insights:[true,true,true],signal:[true,true,true]};i.volumes={insights:["1000000","1000000","1000000"],signal:["1000000","1000000","1000000"]};i.useAgreedRates=true;i.agreedRates={insights:["1000000","1000000","1000000"],signal:["1000000","1000000","1000000"]};
 const r=calculate(i);assert.equal(r.valid,true);for(const k of ["monthlyCents","usageCents","fundingCents","unusedCents"])assert.ok(Number.isSafeInteger(r[k]),k);
 assert.equal(r.fundingCents-r.usageCents,r.unusedCents);
});
console.log(tests+" pricing calculator checks passed.");
