#!/usr/bin/env python3
"""Cross-surface checks: published data model, source mappings, research and API."""
import hashlib
import json
import re
from pathlib import Path
from data_model_alignment import build_catalog, variants, nullable, deref, COMMON

ROOT=Path(__file__).resolve().parents[1]
spec=json.loads((ROOT/'openapi/amlok.json').read_text());schemas=spec['components']['schemas']
catalog=json.loads((ROOT/'downloads/data-model-field-catalog.json').read_text())
checks=0

def check(condition,message):
    global checks
    assert condition,message
    checks+=1

check(catalog==build_catalog(spec),'Catalog regeneration drift')
check(catalog['contractSha256']==hashlib.sha256((ROOT/'openapi/amlok.json').read_bytes()).hexdigest(),'Contract fingerprint')
fields=catalog['fields'];text=(ROOT/'data-model/field-dictionary.mdx').read_text()
parsed={p:(fid,kind,req=='Required',null=='Yes') for p,fid,kind,req,null in re.findall(r'#### `([^`]+)`\n\n\*\*([^*]+)\*\* · `([^`]+)` · (Required|Optional) · Nullable: (Yes|No)',text)}
check(len(parsed)==len(fields),'Dictionary omissions or duplicate paths')
for fid,field in fields.items():
    check(parsed.get(field['path'])==(fid,field['type'],field['required'],field['nullable']),field['path'])
    x=schemas[field['schema']];parts=field['schemaPointer'].strip('/').split('/')
    for p in parts[:-2]:x=x[p]
    check((parts[-1] in x.get('required',[]))==field['required'],fid+' required')
    prop=x['properties'][parts[-1]]
    check(nullable(prop,schemas)==field['nullable'],fid+' nullable')
    check(prop['x-field-id']==fid,fid+' schema ID')
for path in ['verification.subject_association_version','requirement.rejection','workflow_run.attempt','workflow_run.failure']:
    check(any(f['path']==path for f in fields.values()),'Missing previously undocumented field '+path)
check(fields['F0206']['required'] is False,'Read fields must not inherit creation requirements')
check('F0987' in fields and fields['F0987']['path']=='reconciliation_link.review_status','Correct field identity')
check(fields['F0002']['id']=='F0002','Common object identity')

resource_names=variants(spec)
check(len(resource_names)==len(set(resource_names)),'Distinct variants')
normalized_data=schemas['DataRecord']['properties']['normalized']
check(normalized_data['anyOf']==schemas['Evidence']['properties']['normalized']['anyOf'],'Data and Evidence variants differ')

def resolve(resource,path):
    name=next(iter(resource_names.values())) if resource=='common' else resource_names.get(resource)
    x=schemas.get(name,{})
    for part in path:
        x=deref(x,schemas)
        if 'anyOf' in x:x=deref(next(v for v in x['anyOf'] if v.get('type')!='null'),schemas)
        if x.get('type')=='array':x=deref(x['items'],schemas)
        x=x.get('properties',{}).get(part,{})
    return x

integrations=json.loads((ROOT/'data/integration-status.json').read_text())['integrations'];ids={i['id'] for i in integrations}
association_count=0
provider_coverage=(ROOT/'data-model/provider-coverage.mdx').read_text()
resource_coverage=(ROOT/'data-model/resource-coverage.mdx').read_text()
for item in integrations:
    path=ROOT/(item['href'].lstrip('/')+'.mdx');t=path.read_text()
    check('| Provider ID | '+item['id']+' |' in t,item['id']+' guide')
    label=item['status']+(' (Beta)' if item['beta'] else '')
    check('| Integration status | '+label+' |' in t,item['id']+' status')
    for coverage in [provider_coverage,resource_coverage]:check('id="'+item['id'].lower()+'"' in coverage,item['id']+' coverage')
    resources=re.findall(r'\[([^\]]+)\]\(/data-model/field-dictionary#',t)
    for resource in resources:
        check(resource.replace('\\','') in resource_names,item['id']+' resource '+resource);association_count+=1
    check(bool(item['markets']) and set(item['markets']) <= {'US','CA'},item['id']+' markets')

mapping_count=0
for block in re.findall(r'<Accordion title=.*?</Accordion>',(ROOT/'data-model/field-mappings.mdx').read_text(),re.S):
    row={k.strip():v.replace('\\','').strip() for k,v in re.findall(r'^\| ([^|]+) \| (.*?) \|$',block,re.M)}
    check(set(row['Provider IDs'].split('; '))<=ids,'Mapping provider')
    target=row['AMLOK target']
    if target=='invoice / bill (resource routing)':check(all(r in resource_names for r in ['invoice','bill']),'Routing variants')
    else:
        parts=target.replace('[]','').split('.');check(bool(resolve(parts[0],parts[1:])),'Unresolved mapping '+target)
    check('Adapter test status' in row and 'Source evidence' in row,'Mapping qualification')
    mapping_count+=1
check(association_count==2036,'Review provider association count')
check(mapping_count==71,'Review upstream mapping count')

et=(ROOT/'data-model/enumerations.mdx').read_text()
for name,sch in schemas.items():
    if name.startswith('NormalizedEnum_'):
        key=name.removeprefix('NormalizedEnum_')
        body=re.search(r'## `'+re.escape(key)+r'`\n(.*?)(?=\n## |\Z)',et,re.S)
        check(body is not None,key+' missing enum')
        check(re.findall(r'^\| `([^`]+)` \|$',body[1],re.M)==sch['enum'],key+' enum drift')

# Research correspondence only links real contract paths. No new wire fields.
paths={
 'Metric':['key','value','basis','inputs','coverage','calculation_version','window','currency'],
 'RiskPackage':['dimensions','analyses.reconciliations','verification','sources','evidence_set'],
 'DataRecord':['id','normalized','resource_id','record_version','source_payload'],
 'EvidenceSummary':['data_record_id'],
 'Borrower':['subject_id'],
 'Connection':['status','data_status'],
}
for name,field_paths in paths.items():
    for path in field_paths:
        x=schemas[name]
        for part in path.split('.'):
            x=deref(x,schemas);x=x.get('properties',{}).get(part,{})
        check(bool(x),name+'.'+path)
for path in ['data-foundations','record-model','financial-analysis','business-underwriting','consumer-underwriting','monitoring','data-points','entity-graph','model-card']:
    t=(ROOT/('research/'+path+'.mdx')).read_text()
    check('/data-model/api-alignment' in t,path+' research correspondence')
    check('not new API response fields' in t,path+' research boundary')
metrics=json.loads((ROOT/'downloads/underwriting-metric-catalog.json').read_text())
check({m['key'] for m in metrics['metrics']}==set(schemas['Metric']['properties']['key']['enum']),'Metric catalog/contract mismatch')
check('149' in (ROOT/'data-model/derived-attributes.mdx').read_text(),'Source/assessment distinction')
print(f'Data model alignment: {checks} checks; {len(fields)} source fields, {len(integrations)} providers, {association_count} resource associations and {mapping_count} mappings.')
