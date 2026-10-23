"""Validate OpenAPI structure and every documented example without network calls."""
import ast
import json
import re
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from openapi_spec_validator import validate

root = Path(__file__).resolve().parent.parent
spec = json.loads((root/'openapi/amlok-v1.json').read_text())
validate(spec)
document = {'$schema':'https://json-schema.org/draft/2020-12/schema',**spec}
registry = Registry().with_resource('https://contract.example.com/openapi',Resource.from_contents(document))
errors=[]
counts={'operations':0,'requestExamples':0,'responseExamples':0,'pythonSamples':0}

def check(schema,value,label):
    wrapped={'$schema':'https://json-schema.org/draft/2020-12/schema',**schema,'components':spec['components']}
    validator=Draft202012Validator(wrapped,format_checker=FormatChecker())
    for error in validator.iter_errors(value): errors.append(label+' '+str(list(error.path))+': '+error.message)

for path,methods in spec['paths'].items():
    for method,operation in methods.items():
        counts['operations']+=1
        for media in operation.get('requestBody',{}).get('content',{}).values():
            check(media['schema'],media['example'],operation['operationId']+' request');counts['requestExamples']+=1
        for code,response in operation['responses'].items():
            if '$ref' in response:response=spec['components']['responses'][response['$ref'].split('/')[-1]]
            for media in response.get('content',{}).values():
                for name,example in media.get('examples',{}).items():
                    check(media['schema'],example['value'],operation['operationId']+' '+code+' '+name);counts['responseExamples']+=1
        for sample in operation['x-codeSamples']:
            if sample['lang']=='Python':ast.parse(sample['source']);counts['pythonSamples']+=1
        if operation.get('requestBody'):
            assert method in ['post','patch']
        assert 'x-contract-status' not in operation
        assert operation['security']==[{'BearerAuth':[]}]
        assert operation['x-required-scopes']

for name,webhook in spec['webhooks'].items():
    media=webhook['post']['requestBody']['content']['application/json']
    check(media['schema'],media['example'],'webhook '+name)
for name,schema in spec['components']['schemas'].items():Draft202012Validator.check_schema(schema)
if errors:
    print('\n'.join(errors));raise SystemExit(f'{len(errors)} invalid examples')
index=json.loads((root/'data/api-reference-index.json').read_text())
wallet_index=json.loads((root/'data/wallet-api-index.json').read_text())
assert counts['operations']==164+len(wallet_index)==len(index)
assert len({op['operationId'] for methods in spec['paths'].values() for op in methods.values()})==len(index)
assert spec['servers'][0]['url']=='https://api.example.com'
assert spec['info']['version']=='1.4.2'
assert '0.1.0-draft' not in json.dumps(spec)
assert '\u2014' not in json.dumps(spec,ensure_ascii=False)
out=root/'artifacts/api-schema-validation.json';out.write_text(json.dumps(counts,indent=2)+'\n')
print(json.dumps(counts))
