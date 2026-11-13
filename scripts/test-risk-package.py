"""Contract and financial interpretation regressions; not production model validation."""
from copy import deepcopy
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from risk_package_contract import semantic_errors
from risk_package_catalog import catalog
ROOT=Path(__file__).resolve().parent.parent
spec=json.loads((ROOT/'openapi/amlok.json').read_text());c=catalog();checks=0

def validator(name):return Draft202012Validator({'$ref':'#/components/schemas/'+name,'components':spec['components']},format_checker=FormatChecker())
def check(p):
 global checks
 errors=list(validator('RiskPackage').iter_errors(p));assert not errors,[(list(e.path),e.message) for e in errors][:5]
 assert not semantic_errors(p),semantic_errors(p);checks+=1

def reject(p,mutate):
 global checks
 bad=deepcopy(p);mutate(bad)
 assert list(validator('RiskPackage').iter_errors(bad)) or semantic_errors(bad),'Invalid result accepted';checks+=1

def metric(p,key):return next(m for d in p['dimensions'] for m in d['metrics'] if m['key']==key)
partial=json.loads((ROOT/'downloads/risk-package-example.json').read_text())
examples={name:json.loads((ROOT/('downloads/risk-package-'+name+'-example.json')).read_text()) for name in ['business','consumer','signal']}
for p in [partial,*examples.values()]:check(p)
b=examples['business'];person=examples['consumer']
assert len(c['metrics'])==184 and len(c['dimensions'])==24
assert metric(b,'dscr')['value']=='2.00'
assert metric(person,'debt_to_income')['value']=='0.25'
assert metric(partial,'dscr')['value'] is None
reject(b,lambda p:p['dimensions'].append(deepcopy(p['dimensions'][0])))
reject(b,lambda p:p['dimensions'][0]['metrics'].append(deepcopy(p['dimensions'][0]['metrics'][0])))
reject(b,lambda p:p['dimensions'][0]['metrics'].pop())
reject(b,lambda p:p['completeness'].update(available_metric_count=184))
reject(b,lambda p:metric(p,'dscr').update(value=None))
reject(partial,lambda p:metric(p,'dscr').update(value='0'))
reject(b,lambda p:metric(p,'dscr').update(unit='currency',currency='CAD'))
reject(b,lambda p:metric(p,'dscr').update(currency='CAD'))
reject(b,lambda p:metric(p,'dscr').update(calculation_version='unknown'))
reject(b,lambda p:metric(p,'dscr')['inputs'][0].update(value=None))
reject(b,lambda p:metric(p,'dscr')['coverage'].update(observed_days=366,expected_days=365))
reject(b,lambda p:metric(p,'dscr').update(evidence_ids=['unrelated_evidence']))
reject(b,lambda p:metric(p,'operating_cash_inflows').update(currency='USD'))
reject(b,lambda p:p['policy_results'][0].update(actual='9.00'))
reject(b,lambda p:p['policy_results'][0].update(result='fail'))
reject(b,lambda p:p['policy_results'][0].update(threshold='0.50'))
reject(b,lambda p:p['risk_policy']['definition']['rules'][0].update(calculation_version='changed-without-new-policy'))
reject(b,lambda p:metric(p,'dscr')['inputs'][1].update(value='0.00'))
reject(person,lambda p:metric(p,'debt_to_income')['inputs'][0].update(value='0.00'))
reject(b,lambda p:p['analyses']['reconciliations']['items'][0].update(residual='100.00'))
reject(b,lambda p:p['analyses']['reconciliations']['items'][0].update(tolerance='-1.00'))
reject(b,lambda p:p['analyses']['model_outputs'].update(reason=None))
reject(b,lambda p:p['analyses']['benchmarks'].update(status='partial',reason=None))
reject(person,lambda p:p['scope'].update(borrower_type='business'))
reject(examples['signal'],lambda p:p['analyses']['changes']['items'][0].update(comparable=False,reason='Different currency'))
reject(examples['signal'],lambda p:p['analyses']['changes']['items'][0].update(absolute_delta='1.00'))
reject(examples['signal'],lambda p:p['analyses']['changes']['items'][0].update(previous_value='0.00'))
# Probability, evidence-location and projection constraints reject misleading typed outputs.
model={'id':'model_synthetic','kind':'probability_of_default','value':'0.08','unit':'ratio','currency':None,'model_version':'synthetic-1','provider':'Synthetic only','target_definition':'Illustrative 90-day delinquency definition','horizon_months':12,'population':'Synthetic population','market':'CA','validation_reference':'Synthetic fixture, not validated production evidence','calibration_as_of':b['as_of'],'reason_codes':['synthetic'],'limitations':['Not a production score.']}
assert validator('RiskModelOutput').is_valid(model)
for change in [{'value':'1.1'},{'value':'-0.1'},{'currency':'CAD'},{'unit':'score'}]:assert not validator('RiskModelOutput').is_valid({**model,**change});checks+=1
assert not validator('EvidenceLocation').is_valid({'evidence_id':'ev','field_path':None,'document_id':None,'page':1,'quote':None});checks+=1
# Documentation and registry stay tied to policy discovery, public docs and exact units/versions.
f=json.loads((ROOT/'data/product-api-examples.json').read_text())
assert f['Configuration']['dimensions']==c['metrics']
assert json.loads((ROOT/'downloads/underwriting-metric-catalog.json').read_text())==c
page=(ROOT/'api-reference/underwriting-dimensions.mdx').read_text()
assert all('### '+m['key']+'\n' in page and m['calculation_version'] in page for m in c['metrics'])
summary={'dimensions':24,'metrics':184,'risk_contract_checks':checks,'backend_execution':'not_run','predictive_performance_validation':'not_run'}
(ROOT/'artifacts/risk-package-validation.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
