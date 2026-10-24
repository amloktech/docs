"""Build the API reference from the read-only workbook snapshot.

Run with Python 3. Request refinements are recorded as design decisions; this generator does not implement or call an AMLOK API.
"""
from pathlib import Path
from collections import defaultdict
from copy import deepcopy
import json
import re
from pprint import pformat

ROOT = Path(__file__).resolve().parent.parent
SOURCE = json.loads((ROOT / 'data/api-contract-source.json').read_text())
VERSION = '1.4.2'
NOW = '2026-10-23T14:00:00Z'
SOURCE_URL = 'https://docs.google.com/spreadsheets/d/14pU2PLv9JDda8gAa1367hipa2oJQB260fIJthevrp10/edit'

def rows(name):
    values = SOURCE[name]['values']
    return [dict(zip(values[0], row + [None] * (len(values[0]) - len(row)))) for row in values[1:] if row and row[0]]

def write(path, value):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value.replace('0.1.0-draft', VERSION).replace('\u2014', '-').replace('\u2013', '-') + ('\n' if not value.endswith('\n') else ''))

def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2)

def pascal(name):
    return ''.join(x.capitalize() for x in name.split('_'))

def ref(name):
    return {'$ref': '#/components/schemas/' + name}

def nullable(schema):
    return {'anyOf': [schema, {'type': 'null'}]}

def object_schema(properties=None, required=None, **kw):
    out = {'type': 'object', 'properties': properties or {}}
    if required: out['required'] = required
    out.update(kw)
    return out

ENTITIES = {r['Resource']: r for r in rows('Entities') if r['Resource'] != 'common'}
FIELDS = defaultdict(list)
for r in rows('Field Dictionary'): FIELDS[r['Resource']].append(r)
SHARED = defaultdict(list)
for r in rows('Shared Types'): SHARED[r['Type']].append(r)
ENUMS = defaultdict(list)
for r in rows('Enumerations'): ENUMS[r['Enum']].append(r['Allowed value'])
OPS = rows('API Endpoints')
PARAMS = rows('API Parameters')
EVENTS = rows('Events')
ERRORS = rows('Error Codes')
SCHEMAS = {f'Enum_{k}': {'type': 'string', 'enum': v} for k, v in ENUMS.items()}
EXAMPLES = {}
REFINEMENTS = [
    'Lien-search search_type is normalized to name, identifier, vin or serial. The identifier field is required for non-name searches.',
    'The partial account-balance example supplies required date_basis as unknown because source observation timing is not available.',
    'Response-only helper objects (jobs, download links, webhook destinations and replay receipts) use the common data/meta envelope; ChangePage already contains its envelope.',
    'A new connection returns its Action beside data and meta. The Action is not a persistent connection field.',
    'Request schemas reject unknown properties. PATCH requests require at least one supplied property and do not support null clearing.',
    'Request fields listed only in endpoint prose receive explicit types and requiredness here.',
    'Webhook registration description is optional. Creation includes a one-time secret; destination list responses exclude that property entirely.',
    'Provider capability discovery accepts country, resource_type, limit and cursor. Changes accepts resource_types, limit and cursor, and never uses provider cursors.',
    'Generic status and subject filters apply only when the resource has those fields. Source-connection filtering is restricted to source-backed resources.',
    'ResponseMeta.data_status describes response completeness; newly accepted asynchronous work uses pending. Creation examples do not fabricate completed results.',
    'Page.next_cursor is explicitly nullable, as required by the pagination rule. Shared optional fields permit null where the normalization rule requires missing-value representation.',
    'Multipart document upload is the documented ingestion route. No unlisted pre-signed-upload endpoint is invented.',
    'The workbook describes key administration, signing-secret rotation, approval IDs and frozen input manifests but does not define management endpoints for them. Provisioning remains an onboarding dependency.',
]

def type_schema(t):
    if '|null' in t: return nullable(type_schema(t.replace('|null', '')))
    if t.startswith('array<'): return {'type': 'array', 'items': type_schema(t[6:-1])}
    if t.startswith('enum:'): return ref('Enum_' + t[5:])
    if t in SHARED: return ref(t)
    if t == 'decimal': return {'type': 'string', 'pattern': r'^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$', 'description': 'Exact decimal string in major units. Do not use binary floating-point arithmetic.'}
    if t in ['id', 'string']: return {'type': 'string'}
    if t in ['integer', 'boolean']: return {'type': t}
    if t in ['date', 'datetime']: return {'type': 'string', 'format': 'date' if t == 'date' else 'date-time'}
    if t == 'JSON': return {'type': 'object', 'additionalProperties': True}
    raise ValueError('Unknown type ' + str(t))

def example_value(t, raw=None, key='', optional=False):
    if raw == 'null' or raw is None:
        if optional: return None
    if t.endswith('|null'):
        return example_value(t[:-5], raw, key, optional)
    if raw not in [None, '', 'null']:
        if t in ['integer', 'boolean'] or t.startswith('array<') or t in SHARED or t == 'JSON':
            try: return json.loads(str(raw))
            except (ValueError, TypeError): pass
        elif t.startswith('enum:'):
            if raw in ENUMS[t[5:]]: return raw
        elif t == 'decimal':
            if re.fullmatch(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?', str(raw)): return str(raw)
        else: return str(raw)
    if t.startswith('array<'): return []
    if t.startswith('enum:'): return ENUMS[t[5:]][0]
    if t in SHARED: return deepcopy(EXAMPLES.get(t, {}))
    return {'integer': 1, 'boolean': False, 'datetime': NOW, 'date': '2026-10-01', 'decimal': '100.00', 'JSON': {}}.get(t, 'res_example' if t == 'id' else key + '_example')

for name, definitions in SHARED.items():
    props, required, example = {}, [], {}
    for r in definitions:
        key = r['Field'].replace('[]', '')
        s = type_schema(r['Data type'])
        if r['Presence'] == 'Optional' and '|null' not in r['Data type']: s = nullable(s)
        if name == 'Page' and key == 'next_cursor': s = nullable({'type': 'string'})
        s['description'] = r['Definition']
        props[key] = s
        if r['Presence'] == 'Required': required.append(key)
        if r['Presence'] != 'Conditional': example[key] = example_value(r['Data type'], r['Example'], key, r['Presence'] == 'Optional')
    SCHEMAS[name] = object_schema(props, required)
    EXAMPLES[name] = example

EXAMPLES['Page'] = {'next_cursor': None, 'has_more': False, 'limit': 100}
EXAMPLES['ResponseMeta'] = {'request_id': 'req_example', 'schema_version': VERSION, 'generated_at': NOW, 'data_status': 'partial'}
EXAMPLES['ChangePage'] = {'data': [EXAMPLES['Change']], 'page': EXAMPLES['Page'], 'meta': EXAMPLES['ResponseMeta']}
EXAMPLES['WebhookEvent']['data'] = {'status': 'in_review'}
SCHEMAS['Page']['properties']['limit'].update(minimum=1, maximum=200)
SCHEMAS['MoneyInput'] = object_schema({'amount': type_schema('decimal'), 'currency': {'type': 'string', 'pattern': '^[A-Z]{3}$'}}, ['amount', 'currency'], additionalProperties=False)
SCHEMAS['WebhookEndpointPublic'] = deepcopy(SCHEMAS['WebhookEndpoint'])
del SCHEMAS['WebhookEndpointPublic']['properties']['secret']
SCHEMAS['WebhookEndpointPublic']['additionalProperties'] = False
SCHEMAS['WebhookEndpointCreated'] = deepcopy(SCHEMAS['WebhookEndpoint'])
SCHEMAS['WebhookEndpointCreated']['required'].append('secret')
EXAMPLES['WebhookEndpointPublic'] = deepcopy(EXAMPLES['WebhookEndpoint'])
EXAMPLES['WebhookEndpointCreated'] = {**deepcopy(EXAMPLES['WebhookEndpoint']), 'secret': 'synthetic_webhook_secret_replace_on_provisioning'}
SCHEMAS['WebhookEvent']['properties']['type'] = {'type': 'string', 'enum': [e['Event key'] for e in EVENTS]}

def add_field(schema, example, parts, leaf, value, required):
    key = parts[0].replace('[]', '')
    if len(parts) == 1:
        schema['properties'][key] = leaf
        example[key] = value
    else:
        if key not in schema['properties']: schema['properties'][key] = object_schema()
        example.setdefault(key, {})
        add_field(schema['properties'][key], example[key], parts[1:], leaf, value, required)
    if required and key not in schema.setdefault('required', []): schema['required'].append(key)

for name in ['common', *ENTITIES]:
    s, example = object_schema(), {}
    for r in FIELDS[name]:
        parts = r['Field path'].split('.')[1:]
        leaf = type_schema(r['Data type'])
        if r['Nullable'] == 'Yes': leaf = nullable(leaf)
        leaf['description'] = r['Definition'] + ' ' + (r['Normalization / validation'] or '')
        leaf['x-field-id'] = r['Field ID']
        leaf['x-classification'] = r['Classification']
        leaf['x-availability'] = r['Availability']
        val = example_value(r['Data type'], r['Example value'], parts[-1].replace('[]', ''), r['Nullable'] == 'Yes')
        add_field(s, example, parts, leaf, val, r['Required'] == 'Required')
    if name == 'common':
        SCHEMAS['ResourceMetadata'], EXAMPLES['ResourceMetadata'] = s, example
        continue
    common = deepcopy(SCHEMAS['ResourceMetadata'])
    common['properties'].update(s['properties'])
    common['required'] = list(dict.fromkeys(common['required'] + s.get('required', [])))
    common['properties']['object'] = {'type': 'string', 'const': name}
    common['title'] = name
    common['description'] = ENTITIES[name]['Record meaning'] + ' Population depends on source and tenant entitlement.'
    SCHEMAS[pascal(name)] = common
    example = {**deepcopy(EXAMPLES['ResourceMetadata']), **example}
    example.update(id=name + '_example', object=name, subject_id='biz_example', created_at=NOW, updated_at=NOW, record_version=1, source_refs=[], data_status='partial', missing_fields=[], schema_version=VERSION)
    example.pop('field_provenance', None)
    for key in ['observed_at', 'effective_at', 'deleted_at', 'extensions']: example.pop(key, None)
    EXAMPLES[pascal(name)] = example

# Preserve the workbook's worked examples where supplied.
WORKED = rows('Examples')
for r in WORKED:
    response = json.loads(r['Response JSON'])
    data = response.get('data')
    record = data[0] if isinstance(data, list) and data else data
    if isinstance(record, dict) and record.get('object') in ENTITIES:
        EXAMPLES[pascal(record['object'])] = deepcopy(record)
EXAMPLES['AccountBalance']['date_basis'] = 'unknown'

RESOURCE_BY_PATH = {r['Collection endpoint']: name for name, r in ENTITIES.items()}
GROUPS = {name: r['Category'] for name, r in ENTITIES.items()}
SOURCE_BACKED = {name for name, r in ENTITIES.items() if r['Category'] in ['Banking', 'Payments', 'Commerce', 'Accounting', 'Inventory', 'Lending', 'Liens', 'Identity'] and name not in ['document','verification','lien_search']}
PREFIXES = {'business':'biz','person':'per','connection':'cnn','consent':'con','sync_job':'syn','verification':'ver','document':'doc','bank_account':'bka','bank_transaction':'btx','lien_search':'lis','workflow_run':'wfr','monitor':'mon','task':'tsk','case':'case','communication':'com','application':'app'}

COMMANDS = {
 'EP135': ('legal_name', 'client_reference registration_number incorporation_country'),
 'EP136': ('given_name family_name', 'email phone residence_country'),
 'EP137': ('subject_id subject_type purposes scopes policy_version evidence_document_id', ''),
 'EP138': ('reason', ''),
 'EP139': ('subject_id provider_id products consent_id redirect_uri', ''),
 'EP140': ('resources', 'from to'),
 'EP141': ('reason', ''),
 'EP142': ('subject_id verification_type workflow_version', 'return_url'),
 'EP143': ('subject_id debtor_name debtor_type search_type jurisdictions', 'identifier'),
 'EP144': ('file subject_id document_type', 'period_start period_end'),
 'EP145': ('purpose', ''),
 'EP146': ('applicant_entity_id product_type requested_amount', 'purpose requested_term_months'),
 'EP147': ('subject_id workflow_type workflow_version input_resource_ids', 'application_id loan_id'),
 'EP148': ('subject_id keys window_start window_end input_manifest_id', ''),
 'EP150': ('subject_id baseline_snapshot_id resource_types attribute_keys cadence ruleset_version', ''),
 'EP151': ('', 'status cadence attribute_keys ruleset_version'),
 'EP152': ('subject_id case_type', 'alert_ids application_id loan_id'),
 'EP153': ('', 'status assigned_to resolution_code resolution_notes'),
 'EP154': ('subject_id task_type', 'case_id workflow_run_id due_at'),
 'EP155': ('expected_record_version approval_reason', ''),
 'EP156': ('subject_id recipient_entity_id channel template_id', 'case_id subject body'),
 'EP157': ('approval_id expected_record_version', ''),
 'EP158': ('url event_types', 'description'),
 'EP160': ('event_id', ''),
 'EP161': ('subject_id reason scope', ''),
}
FALLBACK = {
 'reason': ('string', 'Requested by the authorized institution.'),
 'purpose': ('string', 'credit_assessment'),
 'expected_record_version': ('integer', '3'),
 'approval_reason': ('string', 'Authorized reviewer approved the exact task payload.'),
 'event_id': ('id', 'evt_example'),
 'resource_type': ('string', 'bank_transaction'),
 'description': ('string', 'Application events for the underwriting service'),
 'identifier': ('string', 'REG-EXAMPLE'),
 'file': ('string', 'statement-2026-09.pdf'),
 'requested_term_months': ('integer', '36'),
}

def request_schema(op, resource):
    required_text, optional_text = COMMANDS[op['Operation ID']]
    required, optional = required_text.split(), optional_text.split()
    definitions = {r['Parameter']: r for r in PARAMS if r['Location'] == 'body' and r['Applies to'] == op['Method'] + ' ' + op['Path']}
    resource_fields = {r['Field path'].split('.', 1)[1].replace('[]', ''): r for r in FIELDS.get(resource, []) + FIELDS['common']}
    properties, example = {}, {}
    for key in required + optional:
        r = definitions.get(key)
        f = resource_fields.get(key)
        if r: t, raw, desc = r['Type'], r['Example'], r['Definition / validation']
        elif f: t, raw, desc = f['Data type'], f['Example value'], f['Definition']
        elif key in FALLBACK: t, raw = FALLBACK[key]; desc = 'Request field from the endpoint contract.'
        else: raise ValueError(f'No request field definition: {op["Operation ID"]} {key}')
        s = type_schema(t)
        if t == 'Money': s = ref('MoneyInput')
        if t in ['string','id']: s['minLength'] = 1
        if t.startswith('array<') and key in required: s['minItems'] = 1
        if key in ['redirect_uri','return_url','url']: s.update(format='uri', pattern='^https://')
        if key == 'file': s = {'type': 'string', 'format': 'binary'}
        if key == 'verification_type': s = {'type': 'string', 'enum': ['kyc','kyb']}
        if key == 'search_type': s = {'type': 'string', 'enum': ['name','identifier','vin','serial']}
        if key == 'expected_record_version': s.update(minimum=1)
        if key == 'event_types': s['items'] = {'type': 'string', 'enum': [e['Event key'] for e in EVENTS]}
        if key == 'resources' or key == 'resource_types': s['items'] = {'type': 'string', 'enum': list(ENTITIES)}
        s['description'] = desc
        properties[key] = s
        if key in required or (key in optional and raw not in [None, '', 'null']):
            example[key] = example_value(t, raw, key)
    s = object_schema(properties, required, additionalProperties=False)
    if op['Operation ID'] == 'EP143':
        s['allOf'] = [{'if':{'properties':{'search_type':{'enum':['identifier','vin','serial']}},'required':['search_type']},'then':{'required':['identifier']}}]
    if op['Method'] == 'PATCH':
        s['minProperties'] = 1
        example = {'status': 'paused'} if resource == 'monitor' else {'status': 'in_progress', 'assigned_to': 'user_reviewer_example'}
    if op['Operation ID'] == 'EP135': example = {'legal_name':'Example Manufacturing Inc.','client_reference':'app-1029','incorporation_country':'CA'}
    if op['Operation ID'] == 'EP136': example = {'given_name':'Alex','family_name':'Example','email':'alex@example.com'}
    if op['Operation ID'] == 'EP144': example = {'file':'statement-2026-09.pdf','subject_id':'biz_example','document_type':'bank_statement','period_start':'2026-09-01','period_end':'2026-09-30'}
    if op['Operation ID'] == 'EP143': example.pop('identifier', None)
    if op['Operation ID'] == 'EP151': example = {'status':'paused'}
    if op['Operation ID'] == 'EP154': example.update(task_type='review_evidence')
    if op['Operation ID'] == 'EP156': example.update(channel='email', subject='Additional evidence requested', body='Please upload your latest financial statement through your secure portal.')
    return s, example

def parameter(name, location, t, description, required=False, example=None, **extra):
    p = {'name':name, 'in':location, 'required':required, 'description':description, 'schema':type_schema(t)}
    if example is not None: p['example'] = example
    p['schema'].update(extra)
    return p

def op_parameters(op, resource):
    method, path = op['Method'], op['Path']
    p = [parameter('X-Request-ID','header','string','Optional caller correlation ID; the response includes AMLOK request_id.',example='client-request-example')]
    if '{id}' in path: p.append(parameter('id','path','id','Tenant-visible resource identifier.',True,(PREFIXES.get(resource,resource or 'res')+'_example')))
    if method == 'POST': p.append(parameter('Idempotency-Key','header','string','Reuse for retries of the same intended command and identical payload. Retention: 24 hours.',True,'idem_example_1001'))
    if method == 'PATCH': p.append(parameter('If-Match','header','string','Current quoted record version returned as ETag. A stale version returns 412.',True,'"3"'))
    if method != 'GET': return p
    list_route = '{id}' not in path
    if list_route:
        p += [parameter('limit','query','integer','Page size. Default 100, maximum 200.',example=100,minimum=1,maximum=200,default=100),parameter('cursor','query','string','Opaque AMLOK cursor. Preserve the original filters.',example='cur_example')]
    if resource and list_route:
        p += [parameter('subject_id','query','id','Filter to one authorized business or person where applicable.',example='biz_example'),parameter('updated_from','query','datetime','Inclusive normalized update time.'),parameter('updated_to','query','datetime','Exclusive normalized update time.')]
        if resource in SOURCE_BACKED: p.append(parameter('connection_id','query','id','Filter one authorized source connection.',example='cnn_example'))
        status_field = next((r for r in FIELDS[resource] if r['Field path'] == resource+'.status'),None)
        if status_field: p.append(parameter('status','query',status_field['Data type'],'Filter by this resource status.'))
    if resource:
        p += [parameter('fields','query','string','Comma-separated relative fields. Required identity and metadata remain.',example='id,object,updated_at'),parameter('include','query','string','Comma-separated optional expansions: provenance, missing_fields. No unrestricted graph traversal.',example='provenance')]
    for r in PARAMS:
        if r['Location'] != 'query' or r['Applies to'].startswith(('All ','Resources ','Source-backed ')): continue
        applies = r['Applies to'].replace('GET ', '').split('; ')
        if path in applies:
            if r['Parameter'] not in [x['name'] for x in p]:
                p.append(parameter(r['Parameter'],'query',r['Type'],r['Definition / validation'],r['Required']=='Required',example_value(r['Type'],r['Example'],r['Parameter']) if r['Example'] else None))
    if path == '/v1/providers':
        p.append(parameter('resource_type','query','string','Return capabilities for one resource type.',example='bank_transaction',enum=list(ENTITIES)))
    return p

def meta(status='partial'):
    return {**deepcopy(EXAMPLES['ResponseMeta']), 'data_status':status}

def envelope(schema, data, list_response=False):
    if list_response: return object_schema({'data':{'type':'array','items':schema},'page':ref('Page'),'meta':ref('ResponseMeta')},['data','page','meta']), {'data':[data],'page':deepcopy(EXAMPLES['Page']),'meta':meta()}
    return object_schema({'data':schema,'meta':ref('ResponseMeta')},['data','meta']), {'data':data,'meta':meta()}

def title_for(op, resource):
    path = op['Path']
    if op['Operation ID']=='EP149':return 'Retrieve attribute calculation'
    if op['Operation ID']=='EP162':return 'Retrieve deletion request'
    noun = path.split('/')[2].replace('-', ' ')
    if op['Method'] == 'GET': return ('Retrieve ' if '{id}' in path else 'List ') + (resource.replace('_',' ') if '{id}' in path and resource else noun)
    custom = {'EP138':'Revoke consent','EP139':'Create connection','EP140':'Start connection sync','EP141':'Disconnect connection','EP142':'Start verification','EP143':'Start lien search','EP144':'Upload document','EP145':'Create document download link','EP147':'Start workflow run','EP148':'Calculate attributes','EP155':'Approve task','EP156':'Create communication draft','EP157':'Send approved communication','EP158':'Create webhook endpoint','EP160':'Replay webhook event','EP161':'Create deletion request'}
    return custom.get(op['Operation ID'],('Update ' if op['Method']=='PATCH' else 'Create ')+(resource.replace('_',' ') if resource else noun))

def samples(op, params, request, example_id):
    path = op['Path'].replace('{id}',example_id)
    is_multipart = op['Operation ID']=='EP144'
    curl = ['curl --request '+op['Method']+' --fail-with-body --max-time 30 \\', '  "${AMLOK_API_BASE_URL}'+path+'" \\', '  --header "Authorization: Bearer ${AMLOK_API_KEY}" \\', '  --header "Accept: application/json"']
    headers = {'Authorization':'Bearer <AMLOK_API_KEY>','Accept':'application/json'}
    if op['Method']=='POST': headers['Idempotency-Key']='idem_example_1001'
    if op['Method']=='PATCH': headers['If-Match']='"3"'
    if request and not is_multipart: headers['Content-Type']='application/json'
    for k,v in headers.items():
        if k not in ['Authorization','Accept']: curl[-1]+=' \\';curl.append("  --header '"+k+': '+v+"'")
    if request:
        if is_multipart:
            for k,v in request.items(): curl[-1]+=' \\';curl.append("  --form '"+k+'='+('@'+v if k=='file' else str(v))+"'")
        else: curl[-1]+=' \\';curl.append("  --data '"+dump(request)+"'")
    py_headers = {k:v for k,v in headers.items() if k!='Authorization'}
    python = 'import os\nimport requests\n\nbase_url = os.environ["AMLOK_API_BASE_URL"].rstrip("/")\nheaders = '+pformat(py_headers, width=60, sort_dicts=False)+'\nheaders["Authorization"] = "Bearer " + os.environ["AMLOK_API_KEY"]\n'
    if is_multipart:
        python += '\nwith open("statement-2026-09.pdf", "rb") as file:\n    response = requests.post(\n        base_url + "'+path+'", headers=headers,\n        files={"file": ("statement-2026-09.pdf", file, "application/pdf")},\n        data='+pformat({k:v for k,v in request.items() if k!='file'}, width=60, sort_dicts=False)+',\n        timeout=30, allow_redirects=False,\n    )\n'
    else:
        python += '\nresponse = requests.request(\n    "'+op['Method']+'", base_url + "'+path+'",\n    headers=headers, timeout=30, allow_redirects=False'+(',\n    json='+pformat(request, width=60, sort_dicts=False) if request else '')+',\n)\n'
    python += 'response.raise_for_status()\nprint(response.json())'
    js = ('import { readFile } from "node:fs/promises";\n' if is_multipart else '')+'\nconst baseUrl = process.env.AMLOK_API_BASE_URL;\nconst apiKey = process.env.AMLOK_API_KEY;\nif (!baseUrl || !apiKey) throw new Error("Configure AMLOK_API_BASE_URL and AMLOK_API_KEY");\nconst headers = '+dump({k:v for k,v in headers.items() if k!='Authorization'})+';\nheaders.Authorization = `Bearer ${apiKey}`;\n'
    if is_multipart:
        js += 'const body = new FormData();\nbody.set("file", new Blob([await readFile("statement-2026-09.pdf")], { type: "application/pdf" }), "statement-2026-09.pdf");\n'
        for k,v in request.items():
            if k!='file': js+='body.set('+json.dumps(k)+', '+json.dumps(v)+');\n'
    js += 'const response = await fetch(baseUrl.replace(/\\/$/, "") + "'+path+'", {\n  method: "'+op['Method']+'", headers,\n  redirect: "error", signal: AbortSignal.timeout(30000),\n'+('  body'+('' if is_multipart else ': JSON.stringify('+dump(request)+')')+',\n' if request else '')+'});\nif (!response.ok) throw new Error(`AMLOK returned HTTP ${response.status}`);\nconsole.log(await response.json());'
    return [{'lang':'Shell','label':'cURL','source':'\n'.join(curl)},{'lang':'Python','source':python},{'lang':'JavaScript','label':'Node.js','source':js}]

SPEC = {'openapi':'3.1.0','info':{'title':'AMLOK API','version':VERSION,'description':'API reference for AMLOK 1.4.2, with example requests and responses. Configure your institution-issued environment URL before making requests.','x-source-workbook':SOURCE_URL},'servers':[{'url':'https://api.example.com','description':'Set the server URL to your institution-issued AMLOK environment URL.'}],'security':[{'BearerAuth':[]}],'paths':{},'components':{'securitySchemes':{'BearerAuth':{'type':'http','scheme':'bearer','bearerFormat':'API key','description':'Server-to-server API key scoped to one institution tenant and environment. Do not use in public browser code.'}},'schemas':SCHEMAS},'tags':[]}
SCHEMAS['ErrorEnvelope'] = object_schema({'error':ref('Error'),'meta':ref('ResponseMeta')},['error','meta'])
OP_INDEX = []
NAV_GROUPS = defaultdict(list)
POSTMAN_GROUPS = defaultdict(list)

for op in OPS:
    oid, path, method = op['Operation ID'],op['Path'],op['Method']
    collection = '/'.join(path.split('/')[:3])
    resource = RESOURCE_BY_PATH.get(collection)
    group = GROUPS.get(resource, 'Platform')
    if path.startswith('/v1/webhook'): group='Webhooks'
    if path.startswith('/v1/deletion'): group='Privacy'
    if path.startswith('/v1/attribute-calculations'): group='Risk'
    title = title_for(op, resource)
    slug = title.lower().replace(' ', '-')
    if oid=='EP164': title='Read change feed';slug='read-change-feed'
    page = f'api-reference/endpoints/{group.lower()}/{slug}'
    params = op_parameters(op, resource)
    request, req_schema = None, None
    if oid in COMMANDS: req_schema,request=request_schema(op,resource)
    response_type = op['Response schema']
    list_response = response_type.startswith('List<')
    if response_type.startswith(('Single<','List<')):
        name = response_type.split('<')[1].split('>')[0]
        schema_name = pascal(name) if name in ENTITIES else name
        if name=='WebhookEndpoint':schema_name='WebhookEndpointPublic'
        response_schema,response_example=envelope(ref(schema_name),deepcopy(EXAMPLES[schema_name]),list_response)
    elif response_type=='ChangePage': response_schema,response_example=ref('ChangePage'),deepcopy(EXAMPLES['ChangePage'])
    else:
        schema_name='WebhookEndpointCreated' if response_type=='WebhookEndpoint' else response_type
        response_schema,response_example=envelope(ref(schema_name),deepcopy(EXAMPLES[schema_name]))
    data=response_example.get('data')
    if request and isinstance(data,dict):
        for key,value in request.items():
            if resource and key in SCHEMAS[pascal(resource)]['properties'] and key!='file':data[key]=deepcopy(value)
        if oid in ['EP135','EP136']:data['source_refs']=[{'provider_id':'CLIENT','retrieved_at':NOW}]
        if oid=='EP135':data.update(is_registry_sourced=False,registry_retrieved_at=None,legal_status=None)
        if oid=='EP138':data.update(status='revoked',revoked_at=NOW)
        if oid=='EP139':
            data.update(status='pending',data_status='pending',provider_tenant_id=None,institution_id=None,institution_name=None,history_available_from=None,sync_cursor=None,last_successful_sync_at=None,error_code=None,reauth_required_at=None)
            response_example['meta']=meta('pending')
            response_schema['properties']['action']=ref('Action');response_schema['required'].append('action')
            response_example['action']={'type':'authorize_connection','url':'https://connect.example.com/session','expires_at':'2026-10-23T14:15:00Z'}
        if oid=='EP141':data['status']='revoked'
        if oid=='EP142':data.update(status='not_started',hosted_url='https://verify.example.com/session')
        if op['Execution']=='Asynchronous':
            response_example['meta']=meta('pending')
            if resource:data['data_status']='pending'
            if 'status' in data and oid!='EP142': data['status']='queued'
            if oid=='EP144':data['extraction_status']='pending'
            for k in ['started_at','completed_at','sent_at','delivered_at']:
                if k in data:data[k]=None
            for k in ['records_added','records_updated','records_removed','coverage_start','coverage_end']:
                if k in data:data[k]=None
        if oid=='EP156':data.update(status='draft',sent_at=None,delivered_at=None,approval_id=None)
        if oid=='EP155':data.update(approval_status='approved',status='queued',approved_at=NOW,approved_by='user_reviewer_example',completed_at=None)
    if list_response and resource=='connection':data[0]['error_code']=None
    example_id=next((p['example'] for p in params if p['in']=='path'),'res_example')
    if isinstance(data,dict) and resource:data['id']=example_id if '{id}' in path and not path.endswith('/sync') else PREFIXES.get(resource,resource)+'_example'
    if method=='PATCH' or oid=='EP155':data['record_version']=4
    desc = op['Purpose']+'\n\nRequired scope: `'+op['Scope']+'`. '+op['Constraints']
    operation={'operationId':oid,'summary':title,'description':desc,'tags':[group],'parameters':params,'security':[{'BearerAuth':[]}],'x-required-scopes':[op['Scope']],'x-codeSamples':samples(op,params,request,example_id),'responses':{}}
    if req_schema:
        req_name=oid+'Request';SCHEMAS[req_name]=req_schema
        operation['requestBody']={'required':True,'content':{'multipart/form-data' if oid=='EP144' else 'application/json':{'schema':ref(req_name),'example':request}}}
    success=op['Success HTTP']
    success_headers={'X-Request-ID':{'description':'AMLOK response correlation identifier.','schema':{'type':'string'},'example':'req_example'}}
    if resource in ['monitor','case'] and not list_response:success_headers['ETag']={'description':'Quoted record version for an If-Match update.','schema':{'type':'string'},'example':'"'+str(data['record_version'])+'"'}
    operation['responses'][success]={'description':op['Purpose']+(' Accepted work is not yet complete.' if op['Execution']=='Asynchronous' else ''),'headers':success_headers,'content':{'application/json':{'schema':response_schema,'examples':{'synthetic':{'summary':'Synthetic '+title.lower(),'value':response_example}}}}}
    relevant=[e for e in ERRORS if e['HTTP status'] not in ['409','412','422'] or (e['HTTP status']=='409' and method=='POST') or (e['HTTP status']=='412' and (method=='PATCH' or oid in ['EP155','EP157'])) or (e['HTTP status']=='422' and method!='GET')]
    for e in relevant:
        code=e['HTTP status'];example={'error':{'code':e['Code'],'message':e['Meaning'],'retryable':e['Retryable']=='Yes','request_id':'req_example'},'meta':meta('complete')}
        response=operation['responses'].setdefault(code,{'description':'Request failed. Inspect error.code and error.retryable.','headers':deepcopy(success_headers),'content':{'application/json':{'schema':ref('ErrorEnvelope'),'examples':{}}}})
        response['headers'].pop('ETag',None)
        if code=='429':response['headers']['Retry-After']={'description':'Delay in seconds or an HTTP-date. The example is illustrative, not a contractual quota.','schema':{'type':'string'},'example':'30'}
        response['content']['application/json']['examples'][e['Code']]={'summary':e['Code'],'value':example}
    for code in list(operation['responses']):
        if code!=success:
            component_name='Error'+code
            SPEC['components'].setdefault('responses',{})[component_name]=operation['responses'][code]
            operation['responses'][code]={'$ref':'#/components/responses/'+component_name}
    SPEC['paths'].setdefault(path,{})[method.lower()]=operation
    NAV_GROUPS[group].append(page)
    notes='\n'
    notes+='**Required scope:** `'+op['Scope']+'` · **Execution:** '+op['Execution'].lower()+'.\n\n'+op['Constraints']+'\n'
    if resource:notes+='\n[Data dictionary](/data-model/field-dictionary#'+resource.replace('_','-')+') · [Response conventions](/api-reference/response-format) · [Errors](/api-reference/errors)\n'
    if op['Execution']=='Asynchronous':
        polling={'EP140':'/v1/sync-jobs/{id}','EP148':'/v1/attribute-calculations/{id}','EP161':'/v1/deletion-requests/{id}'}.get(oid,collection+'/{id}')
        if oid!='EP160':notes+='\nPoll `GET '+polling+'` with the returned resource ID, or consume the relevant webhook. A successful submission does not mean the work completed.\n'
    if op['Event']!='None':notes+='\n**Lifecycle event:** `'+op['Event']+'`. See [webhook delivery and verification](/api-reference/webhooks).\n'
    write(page+'.mdx','---\ntitle: '+json.dumps(title)+'\nopenapi: '+json.dumps('/openapi/amlok-v1.json '+method+' '+path)+'\nplayground: simple\n---\n'+notes)
    item={'name':title,'request':{'method':method,'header':[{'key':'Accept','value':'application/json'}],'url':{'raw':'{{base_url}}'+path.replace('{id}',example_id),'host':['{{base_url}}'],'path':path.replace('{id}',example_id).lstrip('/').split('/')},'description':desc}}
    if method=='POST':item['request']['header'].append({'key':'Idempotency-Key','value':'{{idempotency_key}}'})
    if method=='PATCH':item['request']['header'].append({'key':'If-Match','value':'{{record_etag}}'})
    if request:
        if oid=='EP144':item['request']['body']={'mode':'formdata','formdata':[{'key':k,'type':'file','src':[]} if k=='file' else {'key':k,'type':'text','value':str(v)} for k,v in request.items()]}
        else:item['request']['header'].append({'key':'Content-Type','value':'application/json'});item['request']['body']={'mode':'raw','raw':dump(request),'options':{'raw':{'language':'json'}}}
    item['response']=[{'name':'Synthetic '+success,'originalRequest':deepcopy(item['request']),'status':{'200':'OK','201':'Created','202':'Accepted'}[success],'code':int(success),'header':[{'key':'Content-Type','value':'application/json'}],'body':dump(response_example)}]
    POSTMAN_GROUPS[group].append(item)
    OP_INDEX.append({'id':oid,'method':method,'path':path,'title':title,'scope':op['Scope'],'group':group,'page':page,'resource':resource,'request':request,'response':response_example,'success':success})

from wallet_contract import extend
WALLET_OPS = extend(globals())

SPEC['tags']=[{'name':g,'description':g+' operations.'} for g in NAV_GROUPS]
SPEC['webhooks']={'resourceEvent':{'post':{'summary':'AMLOK resource event','description':'Signed at-least-once delivery. Verify the exact raw body before parsing.','security':[],'parameters':[parameter('X-AMLOK-Signature','header','string','HMAC-SHA256 of timestamp + period + raw body. Tolerance: 300 seconds.',True,'t=1792764000,v1=<hex_digest>')],'requestBody':{'required':True,'content':{'application/json':{'schema':ref('WebhookEvent'),'example':EXAMPLES['WebhookEvent']}}},'responses':{'200':{'description':'Acknowledged after durable acceptance.'}}}}}

write('openapi/amlok-v1.json',dump(SPEC))
write('downloads/amlok-api.postman_collection.json',dump({'info':{'name':'AMLOK API 1.4.2','description':'Example requests for AMLOK 1.4.2. Configure an institution-issued URL and secret locally. Use a new idempotency key for a new action and reuse it only for retries of that action.','schema':'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'},'auth':{'type':'bearer','bearer':[{'key':'token','value':'{{api_key}}','type':'string'}]},'variable':[{'key':'base_url','value':''},{'key':'api_key','value':''},{'key':'idempotency_key','value':'replace-with-stable-key-for-one-intended-action'},{'key':'record_etag','value':'"3"'}],'item':[{'name':g,'item':items} for g,items in POSTMAN_GROUPS.items()]}))
write('data/api-reference-index.json',dump(OP_INDEX))
write('artifacts/api-design-refinements.json',dump(REFINEMENTS))
GUIDES=['overview','quickstart','authentication','environments','response-format','pagination','idempotency','errors','rate-limits','async-jobs','webhooks','event-catalog','documents','versioning','security','workflows','examples','downloads','onboarding']
config=json.loads((ROOT/'docs.json').read_text())
api_tab=next(tab for tab in config['navigation']['tabs'] if tab['tab']=='API Reference')
ESSENTIAL_GROUPS = [('Requests and responses', 'arrow-right-arrow-left', ['response-format', 'pagination', 'idempotency']), ('Reliability', 'shield-check', ['errors', 'rate-limits', 'async-jobs']), ('Events and webhooks', 'webhook', ['webhooks', 'event-catalog']), ('Build your integration', 'blocks', ['workflows', 'documents', 'examples', 'downloads', 'onboarding']), ('Billing and wallets', 'wallet', ['wallets', 'consumption-reporting']), ('Security and versioning', 'lock', ['security', 'versioning'])]
api_tab['groups'] = [
    {'group': 'Get started', 'pages': ['api-reference/' + p for p in GUIDES[:4]]},
    {'group': 'Endpoints', 'pages': [{'group': g, 'expanded': False, 'pages': pages} for g, pages in NAV_GROUPS.items()]},
    {'group': 'Essentials', 'pages': [{'group': name, 'icon': icon, 'expanded': False, 'pages': ['api-reference/' + p for p in pages]} for name, icon, pages in ESSENTIAL_GROUPS]},
]
# Keep wallet endpoints navigable as the operation count grows.
endpoint_groups = api_tab['groups'][1]['pages']
for section in endpoint_groups:
    if section['group'] == 'Wallets':
        sections = defaultdict(list)
        for op in WALLET_OPS:
            if op['group'] != 'Wallets': continue
            path = op['path']
            category = ('Transfers' if path.startswith('/v1/wallet-transfers') else
                        'Withdrawals and payouts' if path.startswith(('/v1/wallet-withdrawals','/v1/wallet-payouts')) else
                        'Refunds' if path.startswith('/v1/wallet-refunds') else
                        'Approvals' if path.startswith('/v1/wallet-approvals') else
                        'Closure' if path.startswith('/v1/wallet-closures') else
                        'Quotes' if path.startswith('/v1/wallet-quotes') else
                        'Funding and destinations' if path.startswith(('/v1/wallet-sessions','/v1/wallet-payment-methods','/v1/wallet-top-ups')) or path.endswith('/auto-top-up') else
                        'Balances and ledger')
            sections[category].append(op['page'])
        section['pages'] = [{'group':name,'expanded':False,'pages':pages} for name,pages in sections.items()]
    elif section['group'] == 'Billing':
        section['pages'] = [
            {'group':'Usage and reporting','expanded':False,'pages':[op['page'] for op in WALLET_OPS if op['path'].startswith('/v1/billing/')]},
            {'group':'Agreement cancellation','expanded':False,'pages':[op['page'] for op in WALLET_OPS if op['path'].startswith('/v1/agreement-')]},
        ]
config['api']={'playground':{'display':'simple'},'examples':{'languages':['curl','python','javascript']}}
write('docs.json',dump(config))
print(dump({'operations':len(OP_INDEX),'resources':len(ENTITIES),'schemas':len(SCHEMAS),'events':len(SCHEMAS['WebhookEvent']['properties']['type']['enum']),'guides':len(GUIDES),'sourceFields':sum(map(len,FIELDS.values()))}))
