"""Generate the customer verification guide and field dictionary from the contract."""
from copy import deepcopy
import json
from pathlib import Path
import re
from verification_contract import SECTIONS, VERSION
from verification_examples import examples, normalized_record
ROOT=Path(__file__).resolve().parents[1]

def write_guides(spec,f,index):
 from current_api_guides import page
 s=spec['components']['schemas'];sample=examples(s)
 def save(path,data):(ROOT/path).write_text(json.dumps(data,indent=2)+'\n')
 fields={}
 def kind(p):
  if '$ref' in p:return p['$ref'].split('/')[-1]
  if 'anyOf' in p:return ' | '.join(kind(x) for x in p['anyOf'])
  if p.get('type')=='array':return kind(p['items'])+'[]'
  t=p.get('type');return ' | '.join(t) if isinstance(t,list) else t or ('string' if 'const' in p else 'object')
 body='''These definitions describe `risk_package.verification` and the same assessment at `normalized.assessment` when `normalized.object` is `verification_assessment`. The [KYC and KYB guide](/api-reference/verification) explains retrieval, status, evidence and authorization. Every section is present even when no result is available.\n\nAll values in the [business example](/downloads/verification-business-example.json) and [consumer example](/downloads/verification-consumer-example.json) are synthetic. The [machine-readable dictionary](/downloads/verification-field-catalog.json) uses the exact field IDs imported by console Data Lookup.\n\n'''
 def properties(schema,prefix):
  for key,p in schema.get('properties',{}).items():
   path=prefix+'.'+key
   yield path,p,key in schema.get('required',[])
   yield from properties(p,path)
  if 'items' in schema:yield from properties(schema['items'],prefix+'[]')
  for variant in schema.get('anyOf',[])+schema.get('oneOf',[]):yield from properties(variant,prefix)
 for name,sch in s.items():
  if not name.startswith('Verification') and name!='NormalizedVerificationAssessment':continue
  if not sch.get('properties'):continue
  body+='## '+name+'\n\n'+sch.get('description','Typed verification response object.')+'\n\n'
  for path,p,required in properties(sch,name):
   fid=p['x-field-id'];heading=re.sub(r'[.\[\]]+','-',path).strip('-');anchor=heading.lower();nullable=any(x.get('type')=='null' for x in p.get('anyOf',[])) or (isinstance(p.get('type'),list) and 'null' in p['type'])
   details={'Origin':'Normalized authorized verification and registry evidence.','Classification':'Identity/compliance evidence; source licensing and purpose apply.','Normalization / validation':p.get('description',''),'Version':VERSION}
   if fid in fields:continue
   fields[fid]={'id':fid,'path':path,'type':kind(p),'required':required,'nullable':nullable,'description':p['description'],'details':details,'docsUrl':'https://docs.amlok.io/api-reference/verification-fields#'+anchor}
   body+='### '+heading+'\n\n`'+path.split('.',1)[1]+'` · `'+kind(p)+'` · '+('Required' if required else 'Optional')+' · Nullable: '+('Yes' if nullable else 'No')+'\n\n'+p['description']+'\n\n'
   if p.get('enum'):body+='Allowed values: '+', '.join('`'+str(v)+'`' for v in p['enum'])+'.\n\n'
   if p.get('format'):body+='Format: `'+p['format']+'`.\n\n'
   if '$ref' in p and p['$ref'].split('/')[-1] in s and s[p['$ref'].split('/')[-1]].get('properties'):body+='See ['+p['$ref'].split('/')[-1]+'](#'+p['$ref'].split('/')[-1].lower()+').\n\n'
 save('downloads/verification-field-catalog.json',{'version':VERSION,'sections':[{'key':k,'schema':v[0],'label':v[1],'description':v[2]} for k,v in SECTIONS.items()],'fields':fields})
 for name,a in sample.items():save('downloads/verification-'+name+'-example.json',a)
 for name in ['business','consumer','signal']:
  path='downloads/risk-package-'+name+'-example.json'
  package=json.loads((ROOT/path).read_text());assessment=deepcopy(sample['consumer' if name=='consumer' else 'business'])
  old=assessment['borrower_id'];new=package['borrower_id']
  assessment=json.loads(json.dumps(assessment).replace('"'+old+'"','"'+new+'"'))
  package['verification']=assessment;package['evidence_set']['count']+=1
  package['document_ids']=list(dict.fromkeys(package['document_ids']+[d['document_id'] for d in assessment['documents']]))
  save(path,package)

 a=sample['business'];record={'id':'dr_verification_synthetic','borrower_id':a['borrower_id'],'connection_id':None,'integration_id':None,'resource_type':'verification_assessment','resource_id':a['id'],'record_version':1,'ingested_at':a['as_of'],'source_as_of':a['as_of'],'access':'available','access_reason':None,'normalized':normalized_record(a),'source_payload':{'status':'not_retained','value':None,'reason':'This synthetic aggregate links to source records; it is not a raw provider payload.'},'document_ids':[d['document_id'] for d in a['documents'] if d['access']=='available']}
 save('downloads/verification-data-record-example.json',record)
 page('api-reference/verification-fields','Verification field dictionary','Types, meanings, normalization and evidence rules for KYC and KYB response fields.',body)
 page('api-reference/verification','KYC and KYB results','Retrieve normalized identity, business, ownership, screening and registry evidence through the AMLOK API.',GUIDE+'\n\n## Result sections\n\n| Section | Contents |\n| --- | --- |\n'+'\n'.join('| `'+k+'` | '+v[2]+' |' for k,v in SECTIONS.items())+'\n\n## Field definitions and examples\n\n- [Complete verification field dictionary](/api-reference/verification-fields)\n- [Machine-readable field catalog](/downloads/verification-field-catalog.json)\n- [Synthetic business verification](/downloads/verification-business-example.json)\n- [Synthetic consumer verification](/downloads/verification-consumer-example.json)\n- [Synthetic data record](/downloads/verification-data-record-example.json)\n')
 nav=json.loads((ROOT/'docs.json').read_text());tab=next(t for t in nav['navigation']['tabs'] if t['tab'].lower()=='api reference');group=next(g for g in tab['groups'] if g['group']=='Product guides');pos=group['pages'].index('api-reference/risk-package')+1;group['pages'][pos:pos]=['api-reference/verification','api-reference/verification-fields'];save('docs.json',nav)
 for path,text in {
  'api-reference/risk-package.mdx':'\n## KYC and KYB evidence\n\n`verification` contains the normalized identity, business, ownership, screening and source-report results. It uses the [verification response](/api-reference/verification), including explicit missing checks, field comparisons and document references. `analyses.verifications` remains a concise summary of checks; detailed verification observations and source outcomes are in `verification`. A financial metric or within-policy recommendation never overrides an unresolved identity or compliance requirement.\n',
  'api-reference/data-access.mdx':'\n## Verification assessments\n\nUse `resource_type=verification_assessment` to retrieve authorized KYC/KYB results. The typed object at `normalized.assessment` is the same [verification structure](/api-reference/verification) used in risk packages. Related parties, coverage and reports retain their exact source versions. This derived resource can have null connection and integration IDs because it combines multiple sources.\n',
  'api-reference/evidence-traceability.mdx':'\n## Verification source records and reports\n\n[Verification results](/api-reference/verification) point to immutable evidence and data-record versions. `source_path` identifies the permitted source field; `document_id` and one-based `page` identify a source report location. Registry, extracted and declared facts retain different provenance. Signed source URLs are not durable IDs: request an authorized AMLOK download link for the document.\n',
  'api-reference/downloads.mdx':'\n## KYC and KYB reference\n\nUse the [verification field catalog](/downloads/verification-field-catalog.json), [business example](/downloads/verification-business-example.json), [consumer example](/downloads/verification-consumer-example.json) and [data-record example](/downloads/verification-data-record-example.json) with the [KYC/KYB guide](/api-reference/verification). These examples are synthetic.\n',
 }.items():
  p=ROOT/path;p.write_text(p.read_text()+text)

GUIDE='''
AMLOK returns one normalized verification structure for business and consumer underwriting. It combines authorized identity checks, registry facts, related parties, ownership, screening, supporting documents, questionnaire declarations and source-specific observations. You receive the results and their evidence; AMLOK coordinates the underlying providers. `borrower_id` identifies the API borrower, while `subject_id` identifies its business or person entity returned by Get borrower. Related-party observations carry their own authorized subject IDs.

## Retrieve the results

| Need | Operation | Response location |
| --- | --- | --- |
| Verification used in an underwriting or monitoring result | [Get risk package](/api-reference/endpoints/results/get-risk-package) | `data.verification` |
| Current collected verification records independently of a package | [List data records](/api-reference/endpoints/data/list-data-records), with `borrower_id` and `resource_type=verification_assessment` | `data[].normalized.assessment` |
| Exact immutable verification version | [Get data record](/api-reference/endpoints/data/get-data-record) | `data.normalized.assessment` |
| Frozen verification evidence used by a package | [List evidence](/api-reference/endpoints/evidence/list-evidence), then [Get evidence](/api-reference/endpoints/evidence/get-evidence) | `data.normalized.assessment` when the resource is a verification assessment; source records retain their own resource type |
| Source reports, corporate profiles, articles and supporting files | [List documents](/api-reference/endpoints/evidence/list-documents), [Get document](/api-reference/endpoints/evidence/get-document), [Download document](/api-reference/endpoints/evidence/download-document) | Document metadata and short-lived download links |
| Changes and rescreening | [Data changes](/api-reference/endpoints/data/list-data-changes), [events](/api-reference/event-catalog) and [Signal monitoring](/api-reference/monitoring-design) | Immutable new record versions, packages and alerts |

Use the existing endpoint scopes and source entitlements. Related-person access must remain associated with the authorized business or consumer purpose. A configuration change or new source result creates a new record; it does not overwrite an earlier assessment. The source providers are not separate public AMLOK APIs or borrower-configurable integrations.

For example, retrieve `GET /v1/data/records?borrower_id=bor_synthetic&resource_type=verification_assessment`, follow all pages, and save the returned data-change cursor. The [pagination guide](/api-reference/pagination) defines snapshot and cursor expiry. A result must include all authorized source observations without silent truncation. Large original reports and provider payloads use their evidence/data records and document references rather than embedding file bytes in the assessment.

## Read status before values

- `status` describes assessment completeness. `outcome` describes verification, not creditworthiness or a lending decision.
- Each section has its own `status`, `reason`, `explanation` and `coverage`. An empty section never proves there were no risks or no owners.
- Each check has an execution `state` and an `outcome`. Pending, failed, skipped and not-requested checks are not passes. Keep original source decisions and any override with its reason and timestamp.
- `field_comparisons` preserves submitted and observed values, normalization, match scores and thresholds. `not_submitted`, `not_checked` and `source_unavailable` differ from `not_matched`.
- A registry candidate, active registration, identity document or extracted name does not independently prove a verified business, a verified owner or good standing.
- Sections are required, and scalar fields are nullable where their sources may omit them. Each null observation field has a `missing_fields` entry with its relative JSON pointer and reason. Unknown is never converted to zero, false or a clean result.

## Ownership and corporate records

People and legal entities can both own shares. `relationships` records roles such as director, agent for service, officer, parent and signatory. One party can have several roles; a service agent is not automatically a director or owner.

`economic_share` and `voting_share` are separate fractions from 0 to 1. A source value of 2.366% voting shares becomes `voting_share: "0.02366"`; it does not establish economic ownership. Preserve the original wording in `reported_interest`. Ranges keep their lower and upper bounds. Indirect `effective_share` requires a fully evidenced chain; missing parents or ownership information leave it null with an unresolved reason. Do not force partial holdings to total 100% or assume that a corporate shareholder is the ultimate natural-person owner.

`ownership_resolution` states the ownership basis and unresolved subjects. Known/unknown fractions use the same explicit denominator, reconcile to one when both are supplied, and remain null when the source does not support a denominator. Complete ownership requires all required interests and chains to be resolved, not merely all returned rows processed.

Registry facts retain multiple registration numbers, countries and subdivisions, legal forms, names, address roles, annual-return years and filing dates. Active registration and overdue returns can coexist. `corporate_structure` retains share classes, voting, dividend, redemption and liquidation provisions, transfer restrictions, director limits and sourced articles. Documents may contain facts absent from the JSON report; those extracted facts carry document/page provenance and a `document_extracted` basis.

## Screening and provider scores

Screening returns all authorized candidate hits, the datasets actually searched, source freshness, reported and returned counts, and review disposition. A potential name match is not a confirmed sanctions match, a finding of fraud or proof of wrongdoing. Confirmed matches and false positives require documented review provenance.

`no_match` requires a completed screening, complete coverage of the explicitly requested scope, zero reported/returned hits and a screening timestamp. Failed sources, missing datasets and unknown coverage produce `inconclusive` or `not_screened`. A source's subscription billing date is never used as a rescreening timestamp.

Provider scores retain their original numeric value, rating, scale, direction and method when known. Unknown bounds remain null. Identity similarity, business risk ratings, liveness confidence and fraud indicators are not interchangeable and are not AMLOK default probabilities. A TIN/EIN/BN/VAT check confirms only the stated identifier/name or format result; it does not prove taxes were paid or that there is no tax debt.

## Evidence, access and source-specific fields

Every populated observation has a source, basis, observation/retrieval time and exact evidence or data-record reference. Field-specific provenance preserves differences and conflicting observations instead of silently selecting a convenient value. Source URLs are only public registry references; controlled files use AMLOK document IDs. Download authorization and source licensing are rechecked when accessed.

`source_payload` on the existing Data API preserves permitted provider-native detail. `supplemental_facts` holds allowlisted scalar facts with names, types, meanings, units and source paths when a stable shared field does not apply. These are not permission bypasses: the same purpose, licensing, redaction and retention rules apply to normalized fields, source payloads, reports and exports.

Personal identifiers are masked by default; full disclosure requires explicit entitlement and purpose. Identity/compliance attributes are not implicit inputs to lending eligibility or capacity metrics. Default responses exclude raw biometric templates and capture media, credentials and secret session URLs, cross-customer identities, private personal social profiles, and unnecessary protected characteristics. Liveness and face checks return their results and evidence references. Original identity documents remain subject to document-specific authorization; a result reference never grants access by itself.

## Availability and normalization

Coverage depends on the actual source product, jurisdiction, consent and entitlement. A provider's capability catalog does not mean every check ran. Country codes normalize to ISO alpha-2 only when verified; region and identifier schemes retain their meaning. Dates with unknown day or month remain unavailable as full dates, with the original partial value retained as a permitted supplemental fact. Amounts retain currency; no assumed currency or conversion of unknown amounts to zero.

Regulatory datasets with no returned rows remain explicitly scoped observations. If a source does not distinguish a completed no-hit search from an unqueried registry, mark coverage unknown/unavailable rather than manufacturing a clean result. Unmapped provider statuses remain inconclusive with the original status and warning. New source-specific fields require review before promotion into the public dictionary.
'''
