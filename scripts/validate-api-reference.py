"""Validate the authoritative OpenAPI, all examples and current reference links."""
import ast
import json
import re
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from openapi_spec_validator import validate
ROOT=Path(__file__).resolve().parent.parent
spec=json.loads((ROOT/'openapi/amlok.json').read_text())
validate(spec)
counts={'operations':0,'request_examples':0,'response_examples':0,'python_samples':0}
errors=[]
def check(schema,value,label):
    validator=Draft202012Validator({**schema,'components':spec['components']},format_checker=FormatChecker())
    for e in validator.iter_errors(value):errors.append(label+' '+str(list(e.path))+': '+e.message)
for path,methods in spec['paths'].items():
    assert path.startswith('/v1/')
    for method,op in methods.items():
        counts['operations']+=1
        for media in op.get('requestBody',{}).get('content',{}).values():
            check(media['schema'],media['example'],op['operationId']+' request');counts['request_examples']+=1
        for status,response in op['responses'].items():
            for media in response.get('content',{}).values():
                assert 'example' in media,(path,status)
                check(media['schema'],media['example'],op['operationId']+' '+status);counts['response_examples']+=1
        for sample in op['x-codeSamples']:
            if sample['lang']=='Python':ast.parse(sample['source']);counts['python_samples']+=1
for name,schema in spec['components']['schemas'].items():Draft202012Validator.check_schema(schema)
webhook=spec['webhooks']['resourceEvent']['post']['requestBody']['content']['application/json']
check(webhook['schema'],webhook['example'],'webhook')
index=json.loads((ROOT/'data/api-reference-index.json').read_text())
assert len(index)==counts['operations']==57
assert spec['info']['version']=='1.0.0'
assert spec['x-availability']=='published_contract'
assert {i['id'] for i in index}=={o['operationId'] for methods in spec['paths'].values() for o in methods.values()}
for item in index:
    content=(ROOT/(item['page']+'.mdx')).read_text()
    assert '/openapi/amlok.json '+item['method']+' '+item['path'] in content
    assert 'Legacy v1 endpoint' not in content
# Every endpoint in the primary navigation belongs to the single contract, exactly once.
c=json.loads((ROOT/'docs.json').read_text())
tab=next(t for t in c['navigation']['tabs'] if t['tab'].lower()=='api reference')
def navpages(value):
    if isinstance(value,str):yield value
    elif isinstance(value,list):
        for x in value:yield from navpages(x)
    elif isinstance(value,dict):
        yield from navpages(value.get('pages',[]));yield from navpages(value.get('groups',[]))
nav=list(navpages(tab));endpoints=[p for p in nav if p.startswith('api-reference/endpoints/')]
assert len(endpoints)==57 and set(endpoints)=={i['page'] for i in index}
for p in nav:assert (ROOT/(p+'.mdx')).exists(),p
for p in (ROOT/'api-reference').glob('*.mdx'):
    text=p.read_text()
    assert not re.search(r'`(?:GET|POST|PATCH|DELETE|PUT) /v2/',text),p
    for link in re.findall(r'\]\((/api-reference/endpoints/[^)#]+)',text):
        assert link[1:] in endpoints,(p,link)
if errors:raise SystemExit('\n'.join(errors))
(ROOT/'artifacts/api-validation.json').write_text(json.dumps(counts,indent=2)+'\n')
print(json.dumps(counts))

# Exclusivity: every published endpoint page and client request is current.
assert {p.name for p in (ROOT/'openapi').glob('*.json')} == {'amlok.json'}
assert not (ROOT/'legacy').exists()
assert {str(p.relative_to(ROOT).with_suffix('')) for p in (ROOT/'api-reference/endpoints').rglob('*.mdx')} == set(endpoints)
collection=json.loads((ROOT/'downloads/amlok-api.postman_collection.json').read_text())
assert len(collection['item'])==len(index)
assert {(i['request']['method'], '/'+'/'.join(i['request']['url']['path']).replace('{{record_id}}','{id}')) for i in collection['item']} == {(i['method'],i['path']) for i in index}
