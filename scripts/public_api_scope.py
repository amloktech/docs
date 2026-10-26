"""Approved public assessment scope, applied without modifying the workbook."""
REMOVED_RESOURCES = {'case', 'task', 'communication', 'payment_promise'}
REMOVED_OPERATION_IDS = {'EP161', 'EP162'} | {f'EP{i:03}' for i in [*range(119, 127), *range(152, 158)]}
REMOVED_EVENTS = {'deletion.completed', 'case.updated', 'task.updated', 'communication.updated'}
REMOVED_ENUMS = {'case_status', 'task_status', 'communication_channel', 'communication_status', 'approval_status', 'retention_action', 'resource_status'}
REMOVED_FIELDS = {'alert.case_id', 'workflow_run.task_ids[]', 'workflow_run.approval_required', 'document.legal_hold'}

def public_rows(name, records):
    for record in records:
        for key, value in record.items():
            if isinstance(value, str):
                record[key] = value.replace("Produced assessments, checks, cases or reports.", "Produced assessments, checks, risk findings or reports.").replace("Verify, Underwrite, Monitor, Service or Investigate", "Verify, Underwrite, Monitor or Investigate").replace('One of the five AMLOK workflows.', 'One of four assessment workflow types.').replace('No external action without scoped institutional authorization.', 'AMLOK returns evidence and assessment results. The institution performs all borrower outreach and intervention in its own systems.').replace('in the proposed contract', 'in this contract').replace('Evidence or approval required to complete a workflow.', 'Evidence required to complete an assessment workflow.').replace('Requested document or approval category.', 'Requested evidence category.')
    if name == 'Entities':
        return [r for r in records if r['Resource'] not in REMOVED_RESOURCES]
    if name == 'Field Dictionary':
        return [r for r in records if r['Resource'] not in REMOVED_RESOURCES and r['Field path'] not in REMOVED_FIELDS]
    if name == 'Enumerations':
        return [r for r in records if r['Enum'] not in REMOVED_ENUMS and not (r['Enum'] == 'workflow_type' and r['Allowed value'] == 'service') and not (r['Enum'] == 'workflow_status' and r['Allowed value'] == 'waiting_for_approval')]
    if name == 'API Endpoints':
        return [r for r in records if r['Operation ID'] not in REMOVED_OPERATION_IDS]
    if name == 'Events':
        return [r for r in records if r['Event key'] not in REMOVED_EVENTS]
    return records

def public_example(value):
    if isinstance(value, list):
        return [public_example(v) for v in value]
    if isinstance(value, dict):
        drop = {'case_id'} if value.get('object') == 'alert' else {'task_ids','approval_required'} if value.get('object') == 'workflow_run' else {'legal_hold'} if value.get('object') == 'document' else set()
        return {k: public_example(v) for k, v in value.items() if k not in drop}
    return value
