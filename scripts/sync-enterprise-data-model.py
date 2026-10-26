"""Keep public data-model prose aligned with generated enterprise schemas."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent

def sync():
    schemas = json.loads((ROOT/'openapi/amlok-v1.json').read_text())['components']['schemas']
    additions = {
        'verification': ['processing_context', 'stop_reason'],
        'lien_search': ['processing_context', 'stop_reason'],
        'document': ['stop_reason'],
        'monitor': ['blocked_reason', 'monitoring_period_id'],
        'workflow_run': ['product', 'input_manifest_id', 'initial_input_manifest_id', 'workload_id', 'billing_usage_id', 'monitoring_period_id', 'blocked_reason', 'stop_reason'],
        'risk_snapshot': ['workflow_run_id', 'application_id', 'billing_usage_id'],
    }
    descriptions = {
        'processing_context': 'Authorized parent Insights workflow or paid Signal monitoring period. This stage is included in the product and creates no separate charge.',
        'stop_reason': 'Why unfinished processing stopped: account cancellation, parent cancellation, or revoked consent. Null when no stop applies.',
        'product': 'Insights for full underwriting or its stages; Signal for monitoring and included reassessment.',
        'input_manifest_id': 'Immutable evidence manifest used for this run, including exact source record versions.',
        'initial_input_manifest_id': 'Initial immutable manifest retained when accepted missing evidence creates a successor for an unfinished run. Audit events identify every replacement; completed outputs remain immutable.',
        'workload_id': 'Read-only workload report with observed counts and agreed limits.',
        'billing_usage_id': 'The one successful product charge associated with the result. Null before charging, or for an included stage with no separate charge.',
        'monitoring_period_id': 'Shared borrower/business/workspace UTC calendar month. Null for Insights.',
        'workflow_run_id': 'Workflow that produced this assessment output.',
        'application_id': 'Associated underwriting application, when applicable.',
        'blocked_reason': 'Reason processing cannot continue. Null when unblocked. Inspect the enum and processing lifecycle before retrying.',
    }
    p=ROOT/'data-model/field-dictionary.mdx'; t=p.read_text()
    for field in ['document.legal_hold','workflow_run.approval_required']:
        t=re.sub(r'^#### `'+re.escape(field)+r'`\n.*?(?=^#### |^</Accordion>)','',t,flags=re.M|re.S)
    for resource, keys in additions.items():
        name=''.join(part.capitalize() for part in resource.split('_'))
        pattern=r'(<Accordion title="'+resource+r'"[^>]*>)(.*?)(</Accordion>)'
        def update(m):
            body=m[2]
            for key in keys:
                body=re.sub(r'^#### `'+resource+r'\.'+key+r'`\n.*?(?=^#### |\Z)','',body,flags=re.M|re.S)
                prop=schemas[name]['properties'][key]
                typ=prop.get('$ref','').split('/')[-1] or prop.get('type') or 'nullable'
                body+='\n#### `'+resource+'.'+key+'`\n\n**API contract field** · `'+str(typ)+'` · Required\n\n'+descriptions[key]+'\n\nSee [processing lifecycle](/api-reference/processing-lifecycle) and [evidence traceability](/api-reference/evidence-traceability).\n\n'
            count=len(re.findall(r'^#### ',body,re.M))
            opening=re.sub(r'description="\d+ fields"',f'description="{count} fields"',m[1])
            return opening+body+m[3]
        t=re.sub(pattern,update,t,flags=re.S)
    t=t.replace('One of the five AMLOK workflows.', 'One of four assessment workflow types within Insights or Signal.')
    t=t.replace('Requested document or approval category.', 'Requested evidence category.')
    t=t.replace('Run that triggered this one, such as Monitor re-entering Underwrite.', 'Parent assessment run. Signal reassessment remains included in Signal.')
    count=len(re.findall(r'^#### ',t,re.M))
    t=re.sub(r'\d+ field definitions',f'{count} field definitions',t)
    p.write_text(t)

    p=ROOT/'data-model/enumerations.mdx';t=p.read_text()
    for name in ['retention_action','resource_status']:
        t=re.sub(r'^## `'+name+r'`\n.*?(?=^## |\Z)','',t,flags=re.M|re.S)
    meanings={
        'queued':'Accepted; waiting for execution.', 'running':'Processing permitted evidence.',
        'waiting_for_data':'Required evidence is missing or under validation.',
        'waiting_for_credits':'Final output is withheld until the accepted run can be charged atomically.',
        'blocked_by_limit':'Paused before exceeding an agreed workload dimension.',
        'completed':'Finished successfully; output is available under the product rules.',
        'failed':'Terminated with a reported error.', 'cancelled':'Stopped; no further work or usage charge.',
        'blocked':'System-paused; inspect blocked_reason.', 'paused':'Paused by the customer.',
        'active':'Eligible to run within the paid monitoring period and agreed scope.',
        'open':'Fresh comparable evidence indicates an active risk condition.',
        'resolved':'Fresh comparable evidence shows the condition cleared. This is not institution acknowledgement.',
    }
    for name in ['workflow_status','monitor_status','alert_status','search_status','verification_status']:
        values=schemas['Enum_'+name]['enum']
        section='## `'+name+'`\n\n| Allowed value | Meaning / handling |\n| --- | --- |\n'
        section+=''.join('| `'+v+'` | '+meanings.get(v,'Assessment-specific state; preserve the underlying evidence and inspect result completeness.')+' |\n' for v in values)+'\n'
        t=re.sub(r'^## `'+name+r'`\n.*?(?=^## |\Z)',lambda _:section,t,flags=re.M|re.S)
    p.write_text(t)

    p=ROOT/'data-model/shared-types.mdx';t=p.read_text()
    marker='\n| `resume_cursor` |'
    if marker not in t:
        t=t.replace('\n## Change\n','\n| `resume_cursor` | `string`<br />Required | Durable change-feed position, including after an empty response. | `changes_after_sequence_42` |\n| `cursor_expires_at` | `datetime`<br />Required | Explicit expiry; create a new checkpoint and bootstrap after expiry. | `2026-11-01T14:00:00Z` |\n\n## Change\n')
        t+='\n| `sequence` | `integer`<br />Required | Monotonic workspace change sequence; filtered streams may contain gaps. | `42` |\n'
    t=t.replace('in the proposed contract','in this contract')
    if '## Processing and reporting helpers' not in t:
        t+='\n## Processing and reporting helpers\n\nCalculation jobs also return `processing_context` and nullable `stop_reason`. Product context, monitoring periods, workload reports, frozen manifests and billing records use dedicated schemas in the [OpenAPI download](/openapi/amlok-v1.json). See [product scope](/api-reference/products-and-endpoints), [workload reporting](/api-reference/workload-reporting), and [export formats](/api-reference/export-formats).\n'
    p.write_text(t)
    for file in ['data-model/start-here.mdx','data-model/entities.mdx']:
        p=ROOT/file;t=p.read_text()
        t=re.sub(r'\d+ field definitions',f'{count} field definitions',t)
        t=t.replace('Evidence or approval required to complete a workflow.','Evidence required to complete an assessment workflow.')
        t=t.replace('Loan contract and current servicing state.','Lender-supplied loan agreement and current repayment state.')
        t=t.replace('A servicing payment event and its allocation.','A lender-supplied repayment event and its allocation.')
        t=t.replace('| Resource fields | 941 |',f'| Resource fields | {count} |')
        t=re.sub(r'\| Field definitions \| \d+ \|',f'| Field definitions | {count} |',t)
        t=t.replace('| Shared-type fields | 134 |','| Source shared-type fields | 134 |')
        p.write_text(t)
    p=ROOT/'data-model/workflow-guide.mdx';t=p.read_text()
    if '## Product scope' not in t:
        t+='\n## Product scope\n\nVerification, lien searches, calculations and investigations are included stages of Insights or Signal. Stage requests require an authorized `processing_context`; they are not independently priced products. A Signal change-driven reassessment stays within its paid monthly period. Read [products and endpoint scope](/api-reference/products-and-endpoints) for the complete mapping.\n'
    p.write_text(t)

if __name__=='__main__':
    sync()
