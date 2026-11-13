"""Generate the source model reference from the same schemas used by API reads.

Curated prose describes meaning; it cannot override wire types or presence rules.
"""
from collections import Counter, OrderedDict
from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://docs.amlok.io'
COMMON = ['id', 'object', 'subject_id', 'created_at', 'updated_at', 'observed_at', 'effective_at', 'record_version', 'deleted_at', 'source_refs', 'field_provenance', 'data_status', 'missing_fields', 'schema_version', 'client_reference', 'extensions']
OVERRIDES = {
    'alert.status': 'System-derived alert state. This evidence field is not an institution acknowledgement or review command.',
    'verification.subject_association_version': 'Version of the authorized related-subject association used by an included verification stage; null when not applicable.',
    'requirement.rejection': 'Structured reason submitted evidence did not satisfy the requirement; null when there is no rejection.',
    'workflow_run.attempt': 'Processing attempt number recorded in the evidence. Reading this value does not start or retry processing.',
    'workflow_run.failure': 'Structured processing failure preserved with the source record; null when no failure is recorded.',
}

def rows(tab):
    data = json.loads((ROOT/'data/api-contract-source.json').read_text())[tab]['values']
    return [dict(zip(data[0], row)) for row in data[1:] if row and row[0]]


def variants(spec):
    schemas = spec['components']['schemas']
    result = OrderedDict()
    for item in schemas['Evidence']['properties']['normalized']['anyOf'][0]['oneOf']:
        name = item['$ref'].rsplit('/', 1)[-1]
        resource = schemas[name]['properties']['object']['const']
        if resource != 'verification_assessment':
            result[resource] = name
    return result


def leaves(schema, prefix='', pointer='', parents_required=True):
    for key, value in schema.get('properties', {}).items():
        path = prefix+'.'+key if prefix else key
        ptr = pointer+'/properties/'+key
        required = key in schema.get('required', [])
        if 'properties' in value and 'x-field-id' not in value:
            yield from leaves(value, path, ptr, parents_required and required)
        else:
            yield path, value, required, parents_required, ptr


def annotate_fields(spec):
    """Restore dictionary IDs on refined schemas without changing accepted JSON."""
    originals = {r['Field path'].replace('[]',''):r for r in rows('Field Dictionary')}
    for resource, name in variants(spec).items():
        schema = spec['components']['schemas'][name]
        for path, field, required, _, _ in leaves(schema):
            canonical = ('common' if path.split('.')[0] in COMMON else resource)+'.'+path
            original = originals.get(canonical, {})
            field.setdefault('x-field-id', original.get('Field ID') or 'API:'+canonical)
            if not required and field.get('x-availability') == 'Required when resource exists':
                field['x-availability'] = 'Returned when available and authorized; a partial read record can omit this field.'
            if canonical in OVERRIDES:
                field['description'] = OVERRIDES[canonical]


def deref(schema, schemas):
    if '$ref' in schema:
        return {**schemas[schema['$ref'].rsplit('/',1)[-1]], **{k:v for k,v in schema.items() if k != '$ref'}}
    return schema


def nullable(schema, schemas):
    schema = deref(schema, schemas)
    return schema.get('type') == 'null' or 'null' in (schema.get('type') if isinstance(schema.get('type'),list) else []) or any(nullable(v, schemas) for v in schema.get('anyOf',[]) + schema.get('oneOf',[]))


def kind(schema, schemas):
    if '$ref' in schema:
        return schema['$ref'].rsplit('/',1)[-1]
    if 'const' in schema:
        return 'literal '+json.dumps(schema['const'])
    choices = schema.get('anyOf',[]) + schema.get('oneOf',[])
    if choices:
        return ' | '.join(dict.fromkeys(kind(v, schemas) for v in choices if v.get('type') != 'null')) or 'null'
    if schema.get('type') == 'array':
        return 'array<'+kind(schema.get('items',{}),schemas)+'>'
    return str(schema.get('type','object' if 'properties' in schema else 'JSON value'))


def build_catalog(spec):
    schemas = spec['components']['schemas']; resources = variants(spec)
    prose = json.loads((ROOT/'data/data-model-descriptions.json').read_text())
    entity_rows = {r['Resource']:r for r in rows('Entities')}
    fields = OrderedDict(); objects = OrderedDict()
    first_name = next(iter(resources.values()))
    for resource,name in [('common',first_name), *resources.items()]:
        schema = schemas[name]; objects[resource] = {'schema':name, 'category':entity_rows.get(resource,{}).get('Category','Platform'), 'description':entity_rows.get(resource,{}).get('Record meaning',schema.get('description',''))}
        for path,field,required,parent_required,pointer in leaves(schema):
            is_common = path.split('.')[0] in COMMON
            if (resource == 'common') != is_common:continue
            canonical = resource+'.'+path; entry = prose.get(canonical,{})
            actual = deepcopy(field)
            if canonical == 'common.object':
                actual = {'type':'string','enum':list(resources), 'x-field-id':'F0002'}
            resolved = deref(actual,schemas)
            display = canonical + ('[]' if resolved.get('type') == 'array' else '')
            field_id = actual['x-field-id']
            assert field_id not in fields, field_id
            details = dict(entry.get('details',{}))
            if actual.get('x-availability'):
                details['Availability'] = actual['x-availability']
            details['Presence'] = ('Required' if required else 'Optional')+' within its containing object. '+('All containing objects are required.' if parent_required else 'A containing object is optional; absence is not JSON null.')
            if 'enum' in resolved:details['Allowed values'] = ', '.join(map(str,resolved['enum']))
            details['Schema'] = name+pointer
            fields[field_id] = {'id':field_id,'path':display,'resource':resource,'schema':name,'schemaPointer':pointer,'type':kind(actual,schemas),'required':required,'parentRequired':parent_required,'nullable':nullable(actual,schemas),'description':OVERRIDES.get(canonical) or actual.get('description') or entry.get('description') or 'Read-only '+path.replace('_',' ')+' from the normalized record.','details':details,'docsUrl':BASE+'/data-model/field-dictionary#'+resource.replace('_','-')}
    return {'contractSha256':hashlib.sha256((json.dumps(spec,indent=2)+'\n').encode()).hexdigest(), 'version':spec['info']['version'], 'resources':objects,'fields':fields}


def page(path,title,description,body):
    (ROOT/(path+'.mdx')).write_text('---\ntitle: '+json.dumps(title)+'\ndescription: '+json.dumps(description)+'\nkeywords: ["AMLOK", "data model", "API contract"]\n---\n\n'+body.strip()+'\n')


def managed(path, body):
    p=ROOT/(path+'.mdx');text=p.read_text();begin='{/* BEGIN API MODEL ALIGNMENT */}';end='{/* END API MODEL ALIGNMENT */}'
    block=begin+'\n'+body.strip()+'\n'+end
    if begin in text:text=re.sub(re.escape(begin)+r'.*?'+re.escape(end),lambda _:block,text,flags=re.S)
    else:
        front,rest=text.split('---',2)[1:]
        text='---'+front+'---\n\n'+block+'\n\n'+rest.lstrip()
    p.write_text(text)


def escape(value):
    return str(value).replace('|','&#124;').replace('<','&lt;').replace('>','&gt;').replace('\n',' ')


def write_guides(spec):
    catalog=build_catalog(spec);schemas=spec['components']['schemas']; fields=catalog['fields'];objects=catalog['resources']
    (ROOT/'downloads/data-model-field-catalog.json').write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n')
    body='''These are the exact source-normalized fields returned inside `DataRecord.normalized` and `Evidence.normalized`. The [OpenAPI contract](/openapi/amlok.json) defines their wire schemas; the [API correspondence](/data-model/api-alignment) separates these records from public product resources and research concepts.

**Required** means present within its containing object. A nested required field can still be absent when its parent is optional. **Nullable** means JSON null is accepted; omission and null are different. Missing or restricted evidence never becomes zero, false or a completed no-hit result. Source records can be partial; inspect `data_status` and `missing_fields`.

Resource prefixes are dictionary context. `bank_transaction.amount.amount` is `data.normalized.amount.amount` on Get data record. Arrays use `[]` in dictionary paths. Common fields live at that same normalized object level, not under a `common` property. The detailed `verification_assessment` resource has its own [verification field dictionary](/api-reference/verification-fields), including its metadata.

Download the [machine-readable source dictionary](/downloads/data-model-field-catalog.json). It includes schema locations and the contract fingerprint used by console Data Lookup. Shared nested types resolve through [shared types](/data-model/shared-types) and OpenAPI.

'''
    current_category=None
    for resource,info in objects.items():
        if info['category'] != current_category:
            if current_category is not None:body+='</AccordionGroup>\n\n'
            current_category=info['category'];body+='## '+current_category+'\n\n<AccordionGroup>\n\n'
        selected=[v for v in fields.values() if v['resource']==resource]
        body+='<Accordion title="'+resource+'" id="'+resource.replace('_','-')+'" description="'+str(len(selected))+' fields">\n\n'
        for f in selected:
            body+='#### `'+f['path']+'`\n\n**'+f['id']+'** · `'+f['type']+'` · '+('Required' if f['required'] else 'Optional')+' · Nullable: '+('Yes' if f['nullable'] else 'No')+'\n\n'+f['description']+'\n\n'
            for k,v in f['details'].items():body+='- **'+k+':** '+escape(v)+'\n'
            body+='\n'
        body+='</Accordion>\n\n'
    body+='</AccordionGroup>\n'
    page('data-model/field-dictionary','Source field dictionary',f'{len(fields):,} source-normalized definitions with API types, presence, nullability, provenance and coverage rules.',body)

    body='''AMLOK uses different schemas for public product state and source-normalized observations. A normalized `connection` or `monitor` record is evidence; it is not the `Connection` or `Monitor` returned by its product endpoint. Use the schema matching the response path. No endpoint or second API is introduced by these evidence names.

## Product response states

| Response schema and field | Allowed values |
| --- | --- |
'''
    for name in ['Connection','Consent','Origination','Monitor','MonitoringRun','Alert','Export','DataRecord']:
        for field in ['status','data_status','access']:
            val=schemas[name].get('properties',{}).get(field,{})
            if 'enum' in val:body+='| `'+name+'.'+field+'` | '+', '.join('`'+v+'`' for v in val['enum'])+' |\n'
    body+='\n## Source-normalized enums\n\nThe sections below use exact `NormalizedEnum_*` schemas from OpenAPI. These are field values, not webhook event names. Public notifications use the [event catalog](/api-reference/event-catalog). Values for research labels remain in the research dataset definition.\n\n'
    for name,sch in schemas.items():
        if name.startswith('NormalizedEnum_'):
            key=name.removeprefix('NormalizedEnum_');body+='## `'+key+'`\n\nSchema: `'+name+'`.\n\n| Allowed value |\n| --- |\n'+''.join('| `'+str(v)+'` |\n' for v in sch['enum'])+'\n'
    page('data-model/enumerations','Enumerations','Exact product and normalized evidence enums, with distinct state vocabularies for their corresponding API schemas.',body)

    body='''Source-normalized records are grouped by evidence domain. The counts below describe the [source dictionary](/data-model/field-dictionary), not the number of endpoints or populated fields on one borrower. Shared `common` metadata is counted once. Detailed verification fields and risk metrics are separate definitions linked from the [model index](/data-model/start-here).

| Domain | Normalized source resources | Dictionary fields |
| --- | --- | --- |
'''
    for category in dict.fromkeys(v['category'] for v in objects.values()):
        res=[k for k,v in objects.items() if v['category']==category]
        count=sum(f['resource'] in res for f in fields.values())
        body+='| '+category+' | '+str(len([r for r in res if r!='common']))+' | '+str(count)+' |\n'
    body+='\n`verification_assessment` adds one typed aggregate with 25 observation sections under `normalized.assessment`. Financial results use the 24 [risk dimensions](/api-reference/underwriting-dimensions). Source domains, assessment dimensions and research feature families serve different purposes and do not share a one-to-one count.\n'
    page('data-model/domains','Domains','Source evidence domains, current schema counts and their relationship to verification assessments and risk-package dimensions.',body)

    # Reconcile counts after the enterprise guide generator writes the entry point.
    verification=json.loads((ROOT/'downloads/verification-field-catalog.json').read_text());metrics=json.loads((ROOT/'downloads/underwriting-metric-catalog.json').read_text());integrations=json.loads((ROOT/'data/integration-status.json').read_text())['integrations']
    count=len(fields);verification_count=len(verification['fields'])
    p=ROOT/'data-model/start-here.mdx';t=p.read_text().replace('957 field definitions',f'{count:,} field definitions').replace('1,817 separately identified',f'{count+verification_count:,} separately identified').replace('original source dictionary','source dictionary');p.write_text(t)
    managed('data-model/start-here','''Use [API correspondence](/data-model/api-alignment) to follow integration capabilities, normalized records, product responses and research definitions without confusing their identifiers or statuses.''')
    managed('data-model/entities','''The API currently exposes **63 source-normalized resource variants plus `verification_assessment`**, for **64 evidence variants**. Shared `common` metadata belongs to the 63 source variants; the verification aggregate has separately documented metadata. These are representations inside Data/Evidence responses, not 64 collection endpoints. Product `Borrower`, `Origination`, `Monitor`, `Connection`, `Document` and `RiskPackage` have their own response schemas. See [API correspondence](/data-model/api-alignment).''')
    p=ROOT/'data-model/entities.mdx';p.write_text(p.read_text().replace('Every top-level resource inherits `common` metadata.', 'Each of the 63 source-normalized variants inherits `common` metadata.'))
    managed('data-model/derived-attributes','''The 56 definitions below describe source-derived attributes and analytical building blocks. They are not the selectable `Metric.key` catalog for risk packages. Use the **184 [underwriting metrics](/api-reference/underwriting-dimensions)** across 24 dimensions for `RiskPackage.dimensions[].metrics[]` and configuration. Similar names are not interchangeable: match formula, unit, window, population and calculation version. For example, observed `debt_service_cash_paid` does not establish the complete contractual denominator for `dscr`.''')
    managed('data-model/relationships','''These joins describe normalized source records. Resolve API-facing relationships through `Borrower.subject_id`, `DataRecord.resource_id` plus `record_version`, and `Evidence.record.data_record_id`. Do not substitute `DataRecord.id` for a normalized logical ID. A shared name such as `monitor`, `connection` or `document` does not make its source schema identical to the product resource. See [API correspondence](/data-model/api-alignment).''')
    managed('data-model/coverage-considerations','''Catalog status, schema support and observed borrower coverage are separate. The 238 integration entries include 22 Active integrations and 216 In Review entries. Preserve each entry's Beta and market labels from the [catalog](/integrations/status). Resource associations describe potential authorized data, not proof that all associated fields are implemented, entitled or returned. Detailed upstream field mappings cover a subset of provider/resource pairs; the absence of a mapping does not justify inventing a native field.''')
    managed('data-model/field-mappings','''The 71 mappings below describe selected upstream fields, not every field exposed by every provider. Their normalized targets resolve against the current API schemas. Integration status and market coverage come from the [catalog](/integrations/status); mapping source evidence and adapter-test status remain separate. `common.*` targets belong directly to the normalized object. Resource-routing mappings select the appropriate normalized variant; they are not JSON property paths.''')
    managed('data-model/normalization-rules','''Read the current [source dictionary](/data-model/field-dictionary) for exact presence and nullability. The retained normalized-definition revision is distinct from `meta.schema_version` and the public contract revision. Source records are available through both [Data](/api-reference/data-access) and [Evidence](/api-reference/evidence-traceability). Source-derived observations, aggregate verification and risk-package metrics have different typed representations; use [API correspondence](/data-model/api-alignment).''')
    p=ROOT/'data-model/normalization-rules.mdx';t=p.read_text().replace('An empty array means the requested collection was queried and is known empty.','An empty array alone does not prove a completed query or no-hit result. Interpret it with data_status, missing_fields, source coverage and, for verification, the section status.').replace('Shared Types expands every reusable nested object.','OpenAPI defines every reusable nested object. Shared Types links the source helper schemas and product response types.').replace('accessed through the evidence endpoints','accessed through Data and Evidence endpoints').replace('Every top-level resource inherits common fields.', 'The 63 source-normalized variants inherit common fields. The verification aggregate defines its own metadata.');p.write_text(t)

    alignment=f'''The API reference, Data Model and console Data Lookup describe one public API. Use this correspondence to choose the correct resource and interpret integration and research coverage. There are **{len(json.loads((ROOT/'data/api-reference-index.json').read_text()))} public operations**, **64 normalized evidence variants**, **{count:,} source field definitions**, **{verification_count:,} detailed verification fields**, and **{len(metrics['metrics'])} risk metrics**. These are different counts; none guarantees a populated value for every borrower.

## From authorized source to API result

| Need | API operation or representation | Meaning |
| --- | --- | --- |
| Register the institution's applicant | `POST /v1/borrowers`, `Borrower.subject_id` | Institution-supplied identity, not a verified conclusion |
| Launch a configured Hub | `POST /v1/embedding-sessions` | Borrower-bound authorization journey; configuration stays in the console |
| Inspect connection health | `Connection.status`, `data_status`, source freshness | Authorization and collection progress are separate |
| Retrieve collected and enriched records | `DataRecord.normalized`, `resource_type`, `resource_id`, `record_version` | Typed source observation or derived record, independently of an assessment |
| Retrieve permitted provider-native details | `DataRecord.source_payload` | Source payload availability and licensing are explicit; never credentials or unrelated data |
| Submit underwriting inputs | `POST /v1/originations` | Application, documents, exact product/policy versions and connection scope |
| Read underwriting and monitoring results | `RiskPackage.dimensions`, `analyses`, `verification`, policy results | Immutable assessment with explicit limitations and evidence |
| Verify the exact evidence used | `Evidence.record.data_record_id`, `Evidence.normalized` | Frozen input version, not an automatic substitute with the latest record |
| Retrieve reports and original files | `Document` and authorized document download | Access and disclosure rules apply to files as well as normalized fields |
| Monitor a funded exposure | `Monitor`, `MonitoringRun`, `Alert` and deal snapshots | New observations and packages preserve the baseline and earlier versions |
| Reconcile billing | Billing summary, transactions, payments, usage and exports | Institution workspace funding and consumption, distinct from a borrower's normalized payment records |

Use [Data access](/api-reference/data-access), [evidence traceability](/api-reference/evidence-traceability), [large results](/api-reference/large-results) and the [endpoint reference](/api-reference/overview) for exact request and response shapes.

## Names do not imply identical schemas

`Connection.status` is product state, while `normalized.object=connection` describes source evidence with `NormalizedEnum_connection_status`. Likewise, normalized `consent`, `document`, `monitor`, `alert`, `application` and `risk_snapshot` are not replacements for their product response schemas. Use [enumerations](/data-model/enumerations) for the correct vocabulary. Read-only processing identifiers are provenance, not orchestration commands.

`DataRecord.id` identifies an immutable data version. `normalized.id` and `DataRecord.resource_id` identify the logical normalized record. `Borrower.id` and its business/person `subject_id` are also distinct. Exact data-record IDs connect frozen evidence to those versions.

## Integration coverage

The [integration catalog](/integrations/status) has **238 entries: 22 Active and 216 In Review**. Preserve country, Beta, product and entitlement conditions. The **2,036 provider-to-resource associations** describe candidate data coverage. The **71 documented field mappings** cover selected upstream paths; they are not a complete adapter conformance certificate for all 238 entries. All referenced normalized resources belong to the current contract.

Internal verification and registry sources supplement borrower-connected integrations. They are not additional customer-selectable Hub integrations. Their authorized results use the [KYC/KYB model](/api-reference/verification), source records, evidence and document references. No provider's entire API is promised, and denied or unavailable information stays explicit.

## Workspace billing agreements

Financial institution billing is separate from a borrower's normalized payment or accounting records. `GET /v1/billing/summary` returns `pricing` with six product/complexity rates and `commitment` (monthly minimum, quarterly/annual cadence and prepayment). `GET /v1/billing/usage` returns the historical tier, effective unit rate, amount, rate version, assessment rationale and linked transaction for each charge. Transactions carry the actual wallet movement and optional `charge_details`.

Amlok assesses complexity; request and record volumes do not select the price. Monetary values are exact two-decimal CAD strings. Historical records preserve their original terms. See [consumption reporting](/api-reference/consumption-reporting) and [billing](/console/billing).

## Financial and verification definitions

The [source dictionary](/data-model/field-dictionary) documents normalized fields and partial-source behavior. The [verification dictionary](/api-reference/verification-fields) documents 25 detailed observation sections. The [risk metric catalog](/api-reference/underwriting-dimensions) documents 24 dimension families and 184 approved metric keys. The 56 [source-derived attribute definitions](/data-model/derived-attributes) are supporting calculations, not an alternative risk metric enum.

An observed debit is not the complete debt obligation; a provider score is not an AMLOK-calibrated probability; a search candidate is not a verified identity. Preserve calculation version, metric basis, units, period, missing reasons and evidence. An empty collection needs its query/coverage status before it can mean no results.

## Research correspondence

| Research concept | Product representation | Boundary |
| --- | --- | --- |
| Source identity and revisions | `DataRecord`, normalized `source_refs`, `field_provenance` | Research pseudonyms and training manifests are not new API fields |
| Economic reconciliation | normalized `reconciliation_link`, `RiskPackage.analyses.reconciliations` | Linked order, invoice, payment and deposit observations remain distinct |
| Financial features | `Metric.key`, `value`, `basis`, `inputs`, `coverage`, `calculation_version` | Only catalog keys are API metrics; proposed features require separate definition |
| Business/consumer study populations | Borrower type and metric applicability | Public-company or business benchmarks do not establish consumer performance |
| Identity and source reliability | `RiskPackage.verification` and metric/source coverage | A documented capability is not proof that a check completed |
| Change detection | Monitoring runs, immutable packages, alerts and the Data change feed | Model evaluation events are not webhook event names |
| Training and evaluation | Research datasets, labels and reproducibility artifacts | Consent to connect does not authorize shared training; benchmark results do not become borrower facts |

Read the [research data foundations](/research/data-foundations), [record model](/research/record-model), [financial analysis](/research/financial-analysis) and [evaluation](/research/evaluation). Proposed research models and measured public-data experiments remain distinct from the API contract and production performance claims.
'''
    page('data-model/api-alignment','API correspondence','Trace integration coverage, normalized fields, risk-package results and research concepts to their exact roles in the public API.',alignment)
    config=json.loads((ROOT/'docs.json').read_text())
    group=next(g for g in config['navigation']['tabs'][0]['groups'] if g['group']=='Data Model')
    if 'data-model/api-alignment' not in group['pages']:group['pages'].insert(1,'data-model/api-alignment')
    (ROOT/'docs.json').write_text(json.dumps(config,indent=2)+'\n')
    for path in ['data-foundations','record-model','financial-analysis','business-underwriting','consumer-underwriting','monitoring','data-points','entity-graph','model-card']:
        managed('research/'+path,'''## Correspondence with the public API

This research describes study methods, candidate representations and evaluation evidence. Use [API correspondence](/data-model/api-alignment) for exact product schemas and [the risk metric catalog](/api-reference/underwriting-dimensions) for exposed metric keys. Research-only pseudonyms, labels, embeddings and training manifests are not new API response fields. Measured research results do not establish an individual borrower's verification, credit outcome or production model performance.''')
    shared=[]
    names=set()
    def collect(x):
        if isinstance(x,dict):
            if '$ref' in x:
                n=x['$ref'].rsplit('/',1)[-1]
                if n.startswith('Normalized') and n not in names:
                    names.add(n);collect(schemas[n])
            for k,v in x.items():
                if k!='$ref':collect(v)
        elif isinstance(x,list):
            for v in x:collect(v)
    for n in variants(spec).values():collect(schemas[n])
    for n in sorted(names):
        if 'properties' in schemas[n] and not n.endswith('Read'):
            shared.append('### `'+n+'`\n\n'+(schemas[n].get('description') or 'Nested source helper used by normalized evidence.')+'\n\n| Field | Type | Required | Nullable |\n| --- | --- | --- | --- |\n'+''.join('| `'+k+'` | `'+kind(v,schemas).replace('|','\\|')+'` | '+('Yes' if k in schemas[n].get('required',[]) else 'No')+' | '+('Yes' if nullable(v,schemas) else 'No')+' |\n' for k,v in schemas[n]['properties'].items()))
    managed('data-model/shared-types','''## Source helper types

These helper schemas belong inside source-normalized records. Requiredness is relative to the containing object. Product response types such as `Money`, `Metric`, `Connection` and `Document` remain separate. OpenAPI carries all nested constraints and enum references.

'''+ '\n\n'.join(shared))
    return catalog
