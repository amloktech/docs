"""KYC/KYB schema, dictionary and semantic contract checks; no provider execution."""
from copy import deepcopy
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from verification_contract import semantic_errors, SECTIONS
ROOT=Path(__file__).resolve().parent.parent
spec=json.loads((ROOT/'openapi/amlok.json').read_text());checks=0

def validator(name):return Draft202012Validator({'$ref':'#/components/schemas/'+name,'components':spec['components']},format_checker=FormatChecker())
def check(a):
 global checks
 errors=list(validator('VerificationAssessment').iter_errors(a))
 assert not errors,[(list(e.path),e.message) for e in errors][:5]
 assert not semantic_errors(a),semantic_errors(a);checks+=1

def reject(a,mutate):
 global checks
 bad=deepcopy(a);mutate(bad)
 assert list(validator('VerificationAssessment').iter_errors(bad)) or semantic_errors(bad),'Invalid verification accepted';checks+=1

b=json.loads((ROOT/'downloads/verification-business-example.json').read_text())
p=json.loads((ROOT/'downloads/verification-consumer-example.json').read_text())
for a in [b,p]:check(a)
for kind in ['example','business-example','consumer-example','signal-example']:
 package=json.loads((ROOT/('downloads/risk-package-'+kind+'.json')).read_text())
 check(package['verification']);assert package['borrower_id']==package['verification']['borrower_id']
 assert package['as_of']>=package['verification']['as_of']
record=json.loads((ROOT/'downloads/verification-data-record-example.json').read_text())
assert validator('DataRecord').is_valid(record)
assert record['resource_id']==record['normalized']['id'] and record['resource_type']==record['normalized']['object']
assert record['record_version']==record['normalized']['record_version']
assert record['normalized']['subject_id']==record['normalized']['assessment']['subject_id']
assert record['normalized']['subject_id']!=record['borrower_id'];checks+=1
reject(b,lambda a:a.update(status='complete',outcome='passed'))
reject(b,lambda a:a['checks']['items'][0].update(state='pending',outcome='passed'))
reject(b,lambda a:a['ownership']['items'][0].update(effective_share='0.65'))
reject(b,lambda a:a['ownership']['items'][0].update(voting_share='1.01'))
reject(b,lambda a:a['ownership']['items'][0].update(economic_share_min='0.9',economic_share_max='0.5'))
reject(b,lambda a:a['ownership_resolution'].update(status='complete',unknown_share='0'))
reject(b,lambda a:a['ownership_resolution'].update(unknown_share='0.25'))
reject(b,lambda a:a['businesses']['items'][0]['provenance'].update(evidence=[]))
reject(b,lambda a:a['businesses']['items'][0]['provenance'].update(source_id='missing'))
reject(b,lambda a:a['sources'].append(deepcopy(a['sources'][0])))
reject(b,lambda a:a['field_comparisons']['items'][1].update(provided='not actually missing'))
reject(b,lambda a:a['source_scores']['items'][0]['score'].update(value=1000))
reject(b,lambda a:a['source_scores']['items'][0]['score'].update(scale_min=100,scale_max=0))
reject(b,lambda a:a['sources'][0]['coverage'].update(status='complete'))
reject(b,lambda a:a['businesses']['items'][0].update(missing_fields=[]))
reject(p,lambda a:a['identity_documents']['items'][0]['identifier'].update(value='unmasked'))
reject(p,lambda a:a['screenings']['items'][0].update(result='no_match'))
reject(p,lambda a:a['screenings']['items'][0].update(result='confirmed_match'))
reject(p,lambda a:a['screenings']['items'][0].update(returned_hit_count=2))
reject(p,lambda a:a['screenings']['items'][0]['hits'][0].update(disposition='confirmed'))
clean=deepcopy(p);x=clean['screenings']['items'][0];x.update(result='no_match',hits=[],reported_hit_count=0,returned_hit_count=0);check(clean)
reject(clean,lambda a:a['screenings']['items'][0].update(state='pending'))
reject(clean,lambda a:a['screenings']['items'][0]['coverage'].update(status='partial'))
reject(clean,lambda a:a['screenings']['items'][0].update(screened_at=None))
unknown=deepcopy(b);unknown['source_scores']['items'][0]['score'].update(value=None,scale_min=None,scale_max=None,label='source qualitative rating');check(unknown)
# Exact generated dictionary IDs and fields, including nested inline objects.
catalog=json.loads((ROOT/'downloads/verification-field-catalog.json').read_text())
assert {x['key'] for x in catalog['sections']}==set(SECTIONS)
assert len(catalog['fields'])>750
for fid,field in catalog['fields'].items():
 assert fid=='VERIFY:'+field['path']
 assert field['description'] and field['docsUrl'].startswith('https://docs.amlok.io/api-reference/verification-fields#')
 assert '### '+field['docsUrl'].split('#')[1] in (ROOT/'api-reference/verification-fields.mdx').read_text().lower()
checks+=len(catalog['fields'])
mapping=json.loads((ROOT/'implementation/verification-source-mapping.json').read_text())
for row in mapping['mappings']:
 for target in row['targets']:
  name,field=target.split('.')
  assert field in spec['components']['schemas'][name]['properties'],target
 checks+=1
summary={'verification_contract_checks':checks,'sections':len(SECTIONS),'dictionary_fields':len(catalog['fields']),'mapping_groups':len(mapping['mappings']),'provider_execution':'not_run'}
(ROOT/'artifacts/verification-validation.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
