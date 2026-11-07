"""Sandbox-only developer controls; part of the single public API."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def extend(spec,fixtures):
    patch=json.loads((ROOT/'data/sandbox-contract.json').read_text())
    spec['paths'].update(patch['paths'])
    spec['components']['schemas'].update(patch['schemas'])
    spec.setdefault('tags',[]).append({'name':'Sandbox','description':'Reproducible developer scenarios with synthetic data and money.'})
    result=[]
    for path,methods in patch['paths'].items():
        for method,operation in methods.items():
            operation['x-availability']='published_contract'
            operation['security']=[{'BearerAuth':[]}]
            media=operation.get('requestBody',{}).get('content',{}).get('application/json')
            request=media['schema']['$ref'].rsplit('/',1)[-1] if media else None
            if request:fixtures[request]=media['example']
            data=next(v for k,v in operation['responses'].items() if k.startswith('2'))['content']['application/json']['schema']['properties']['data']
            response=(data.get('items',data)).get('$ref','#/components/schemas/SandboxActionResult').rsplit('/',1)[-1]
            result.append({'id':operation['operationId'],'method':method.upper(),'path':path,'group':'Sandbox','response':response,'request':request,'many':data.get('type')=='array','scope':operation['x-required-scopes'][0]})
    return result
