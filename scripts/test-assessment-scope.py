"""Check that public contracts expose assessment signals, not borrower servicing."""
import json
import re
from pathlib import Path
from jsonschema import Draft202012Validator
from public_api_scope import REMOVED_OPERATION_IDS, REMOVED_RESOURCES, REMOVED_EVENTS, REMOVED_ENUMS

ROOT = Path(__file__).resolve().parent.parent
spec = json.loads((ROOT / 'openapi/amlok-v1.json').read_text())
source = json.loads((ROOT / 'data/api-contract-source.json').read_text())
index = json.loads((ROOT / 'data/api-reference-index.json').read_text())
schemas = spec['components']['schemas']
operations = {op['operationId']: (path, method) for path, methods in spec['paths'].items() for method, op in methods.items()}
checks = 0

def check(ok, message):
    global checks
    assert ok, message
    checks += 1

for oid in REMOVED_OPERATION_IDS:
    check(oid not in operations, f'Removed operation returned: {oid}')
for route in ['cases', 'tasks', 'communications', 'payment-promises']:
    check(not any(p.startswith('/v1/' + route) for p in spec['paths']), f'Servicing route returned: {route}')
for resource in REMOVED_RESOURCES:
    name = ''.join(word.capitalize() for word in resource.split('_'))
    check(name not in schemas and name + 'Read' not in schemas, f'Servicing schema returned: {name}')
for name in REMOVED_ENUMS:
    check('Enum_' + name not in schemas, f'Servicing enum returned: {name}')
for name in REMOVED_EVENTS:
    check(name not in spec['webhooks'], f'Servicing event returned: {name}')
check('case_id' not in schemas['Alert']['properties'], 'Alert refers to removed case')
check('task_ids' not in schemas['WorkflowRun']['properties'], 'Workflow refers to removed tasks')
check(set(schemas['Enum_workflow_type']['enum']) == {'verify', 'underwrite', 'monitor', 'investigate'}, 'Unexpected workflow types')
request = spec['paths']['/v1/workflow-runs']['post']['requestBody']['content']['application/json']
validator = Draft202012Validator({'components': spec['components'], **request['schema']})
payload = dict(request['example'], workflow_type='service')
check(not validator.is_valid(payload), 'Servicing request accepted by contract')
for workflow in ['verify', 'underwrite', 'monitor', 'investigate']:
    candidate=dict(payload,workflow_type=workflow)
    if workflow!='underwrite':candidate['processing_context']={'product':'insights','workflow_run_id':'wfr_example'}
    check(validator.is_valid(candidate), 'Authorized assessment workflow rejected: ' + workflow)
for path in ['/v1/loans', '/v1/repayments', '/v1/monitors', '/v1/alerts', '/v1/risk-snapshots', '/v1/documents', '/v1/requirements', '/v1/audit-events', '/v1/billing/credits', '/v1/billing/consumption']:
    check('get' in spec['paths'][path], 'Missing assessment/reporting read: ' + path)

# Every retained workbook operation keeps its original identity and route.
values = source['API Endpoints']['values']
for row in values[1:]:
    op = dict(zip(values[0], row))
    if op['Operation ID'] in REMOVED_OPERATION_IDS:
        continue
    check(operations[op['Operation ID']] == (op['Path'], op['Method'].lower()), 'Workbook operation identity changed')

for p in [*ROOT.glob('api-reference/**/*.mdx'), *ROOT.glob('data-model/*.mdx'), *ROOT.glob('integrations/**/*.mdx')]:
    text = p.read_text()
    check('@@EP' not in text, f'Unresolved operation placeholder: {p}')
    for anchor in ['case', 'task', 'communication', 'payment-promise']:
        check(not re.search(r'/data-model/(?:entities|field-dictionary)#' + anchor + r'[)"\s]', text), f'Removed resource link: {p}')
    for target in re.findall(r'\]\((/[^)\s]+)\)|href="(/[^"\s]+)"', text):
        path = (target[0] or target[1]).split('#')[0].split('?')[0]
        if not path or path == '/':
            continue
        local = ROOT / path.lstrip('/')
        check(local.is_file() or local.with_suffix('.mdx').is_file() or (local / 'index.mdx').is_file(), f'Broken internal path in {p}: {path}')
    for match in re.finditer(r'/data-model/(entities|field-dictionary)#([\w-]+)', text):
        target = (ROOT / 'data-model' / (match[1] + '.mdx')).read_text()
        check(f'id="{match[2]}"' in target or f'## {match[2].capitalize()}' in target, f'Broken data-model anchor in {p}: {match[0]}')

def nav_pages(node):
    if isinstance(node, list):
        for item in node:
            if isinstance(item, str):
                yield item
            else:
                yield from nav_pages(item)
    elif isinstance(node, dict):
        for key in ['navigation', 'tabs', 'groups', 'pages']:
            yield from nav_pages(node.get(key, []))

for page in nav_pages(json.loads((ROOT / 'docs.json').read_text())):
    check((ROOT / (page + '.mdx')).is_file(), 'Missing navigation page: ' + page)
check(len(index) == len(operations) == 180 + len(json.loads((ROOT/'data/integration-api-index.json').read_text())), 'Operation count mismatch')
check(len(re.findall(r'^#### ', (ROOT / 'data-model/field-dictionary.mdx').read_text(), re.M)) == 957, 'Field count mismatch')
check(len(re.findall(r'<Accordion title=', (ROOT / 'data-model/entities.mdx').read_text())) == 64, 'Resource count mismatch')
result = {'checks': checks, 'operations': len(operations), 'removedServicingOperations': 14, 'scope': 'Documentation and API contract; no backend calls.'}
(ROOT / 'artifacts/assessment-scope-validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
