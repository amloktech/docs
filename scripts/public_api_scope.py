"""Approved public assessment scope, applied without modifying the workbook."""
REMOVED_RESOURCES = {'case', 'task', 'communication', 'payment_promise'}
REMOVED_OPERATION_IDS = {'EP161', 'EP162'} | {f'EP{i:03}' for i in [*range(119, 127), *range(152, 158)]}
REMOVED_EVENTS = {'deletion.completed', 'case.updated', 'task.updated', 'communication.updated'}
REMOVED_ENUMS = {'case_status', 'task_status', 'communication_channel', 'communication_status', 'approval_status'}
REMOVED_FIELDS = {'alert.case_id', 'workflow_run.task_ids[]'}

def public_rows(name, records):
    for record in records:
        for key, value in record.items():
            if isinstance(value, str):
                record[key] = value.replace("Produced assessments, checks, cases or reports.", "Produced assessments, checks, risk findings or reports.").replace("Verify, Underwrite, Monitor, Service or Investigate", "Verify, Underwrite, Monitor or Investigate")
    if name == 'Entities':
        return [r for r in records if r['Resource'] not in REMOVED_RESOURCES]
    if name == 'Field Dictionary':
        return [r for r in records if r['Resource'] not in REMOVED_RESOURCES and r['Field path'] not in REMOVED_FIELDS]
    if name == 'Enumerations':
        return [r for r in records if r['Enum'] not in REMOVED_ENUMS and not (r['Enum'] == 'workflow_type' and r['Allowed value'] == 'service')]
    if name == 'API Endpoints':
        return [r for r in records if r['Operation ID'] not in REMOVED_OPERATION_IDS]
    if name == 'Events':
        return [r for r in records if r['Event key'] not in REMOVED_EVENTS]
    return records

def public_example(value):
    if isinstance(value, list):
        return [public_example(v) for v in value]
    if isinstance(value, dict):
        drop = {'case_id'} if value.get('object') == 'alert' else {'task_ids'} if value.get('object') == 'workflow_run' else set()
        return {k: public_example(v) for k, v in value.items() if k not in drop}
    return value
