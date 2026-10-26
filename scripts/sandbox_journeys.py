"""Build a separate, chained Postman acceptance collection from the product journeys."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent.parent

def generate():
    def request(name,method,path,script,body=None,pre=None):
        r={'name':name,'request':{'method':method,'url':'{{base_url}}'+path,'header':[{'key':'Accept','value':'application/json'}]},'event':[]}
        if body:
            r['request']['header'] += [{'key':'Content-Type','value':'application/json'},{'key':'Idempotency-Key','value':'{{journey_action_key}}'}]
            r['request']['body']={'mode':'raw','raw':json.dumps(body,indent=2),'options':{'raw':{'language':'json'}}}
        r['event'].append({'listen':'test','script':{'type':'text/javascript','exec':('''
function requireThat(ok, message) {
  pm.test(message, () => pm.expect(Boolean(ok)).to.equal(true));
  if (!ok) { pm.execution.setNextRequest(null); throw new Error(message); }
}
requireThat(pm.response.code >= 200 && pm.response.code < 300, "Successful response required; reconcile saved action key on errors");
const response = pm.response.json(); const d = response.data;
'''+script).strip().splitlines()}})
        if pre:r['event'].append({'listen':'prerequest','script':{'type':'text/javascript','exec':pre.strip().splitlines()}})
        return r
    folders=[]
    for product in ['insights','signal']:
        prefix=product.capitalize()
        items=[request(prefix+' configuration','GET','/v1/configuration', '''
requireThat(d.environment === "sandbox", "Sandbox only");
pm.collectionVariables.set("sandbox_verified", "yes");
pm.collectionVariables.set("journey_config", JSON.stringify(d));
pm.collectionVariables.set("poll_count", "0");
''',pre='pm.collectionVariables.unset("sandbox_verified");'),
        request(prefix+' fixture','GET','/v1/sandbox/scenarios?limit=200',f'''
const fixture = d.find(x => x.id === "{product}_success");
requireThat(Boolean(fixture), "Provision or reset the {product} fixture through the portal");
pm.collectionVariables.set("journey_fixture", JSON.stringify(fixture));
pm.collectionVariables.set("journey_subject", fixture.subject_id);
pm.collectionVariables.set("journey_application", fixture.application_id || "");
pm.collectionVariables.set("journey_manifest", fixture.input_manifest_id || "");
pm.collectionVariables.set("journey_baseline", fixture.baseline_snapshot_id || "");
pm.collectionVariables.set("journey_workflow_version", fixture.workflow_version);
pm.collectionVariables.set("journey_ruleset", fixture.ruleset_version);
pm.collectionVariables.set("journey_cadence", fixture.cadence);
const cfg = JSON.parse(pm.collectionVariables.get("journey_config"));
const rules = cfg.rulesets.find(x => x.id === fixture.ruleset_version);
if (rules) {{ pm.collectionVariables.set("journey_resources", JSON.stringify(rules.resource_types)); pm.collectionVariables.set("journey_attributes", JSON.stringify(rules.attribute_keys)); }}
'''),
        request(prefix+' readiness','GET','/v1/subjects/{{journey_subject}}/readiness?product='+product, '''
requireThat(d.status !== "blocked", "Evidence readiness must not be blocked");
if (d.status !== "ready") {
 const n = Number(pm.collectionVariables.get("poll_count") || 0) + 1;
 pm.collectionVariables.set("poll_count", String(n));
 requireThat(n <= 60, "Readiness polling deadline; resume later without a new action");
 pm.execution.setNextRequest(pm.info.requestName);
} else { pm.collectionVariables.set("poll_count", "0"); }
''')]
        if product=='insights':
            body={'subject_id':'{{journey_subject}}','workflow_type':'underwrite','workflow_version':'{{journey_workflow_version}}','application_id':'{{journey_application}}','input_manifest_id':'{{journey_manifest}}','input_resource_ids':['{{journey_application}}']}
            path='/v1/workflow-runs';oid='EP147'
            accepted='pm.collectionVariables.set("journey_run", d.id);'
        else:
            body={'subject_id':'{{journey_subject}}','baseline_snapshot_id':'{{journey_baseline}}','resource_types':['REPLACE_RESOURCES'],'attribute_keys':['REPLACE_ATTRIBUTES'],'cadence':'{{journey_cadence}}','ruleset_version':'{{journey_ruleset}}'}
            path='/v1/monitors';oid='EP150';accepted='pm.collectionVariables.set("journey_monitor", d.id);'
        pre=f'''
const subject = pm.collectionVariables.get("journey_subject");
const name = "{product}_key_" + subject;
if (!pm.collectionVariables.get(name)) pm.collectionVariables.set(name, pm.variables.replaceIn("{{{{$guid}}}}"));
pm.collectionVariables.set("journey_action_key", pm.collectionVariables.get(name));
pm.collectionVariables.set("journey_operation_id", "{oid}");
pm.collectionVariables.set("journey_target_path", "{path}");
'''
        if product=='signal':pre+='''
const body = JSON.parse(pm.variables.replaceIn(pm.request.body.raw));
body.resource_types = JSON.parse(pm.collectionVariables.get("journey_resources"));
body.attribute_keys = JSON.parse(pm.collectionVariables.get("journey_attributes"));
pm.request.body.update(JSON.stringify(body));
'''
        items.append(request(prefix+' submit','POST',path,accepted,body,pre))
        if product=='insights':
            items += [request('Insights completion','GET','/v1/workflow-runs/{{journey_run}}', '''
requireThat(!["failed", "cancelled", "blocked_by_limit", "waiting_for_data", "waiting_for_credits"].includes(d.status), "Workflow must not be blocked; inspect failure and use the recovery guide");
if (d.status !== "completed") {
 const n = Number(pm.collectionVariables.get("poll_count") || 0) + 1;
 pm.collectionVariables.set("poll_count", String(n)); requireThat(n <= 60, "Bounded workflow polling"); pm.execution.setNextRequest(pm.info.requestName);
} else { pm.collectionVariables.set("journey_usage", d.billing_usage_id); pm.collectionVariables.set("journey_final_manifest", d.input_manifest_id); }
'''),request('Insights usage','GET','/v1/billing/usage/{{journey_usage}}', '''
requireThat(d.product === "insights" && d.quantity === "1" && d.workflow_run_id === pm.collectionVariables.get("journey_run"), "One-unit Insights usage linked to the run");
requireThat(d.input_manifest_id === pm.collectionVariables.get("journey_final_manifest"), "Usage references the final manifest");
pm.collectionVariables.set("journey_snapshot", d.risk_snapshot_id);
'''),request('Insights evidence','GET','/v1/risk-snapshots/{{journey_snapshot}}', '''
requireThat(d.workflow_run_id === pm.collectionVariables.get("journey_run"), "Snapshot belongs to the run");
requireThat(d.billing_usage_id === pm.collectionVariables.get("journey_usage"), "Snapshot and usage agree");
requireThat(d.evidence_manifest_id === pm.collectionVariables.get("journey_final_manifest"), "Evidence manifest agrees");
pm.execution.setNextRequest(null);
''')]
        else:
            items += [request('Signal activation','GET','/v1/monitors/{{journey_monitor}}','''
requireThat(d.status === "active", "Monitoring must be funded and active");
pm.collectionVariables.set("journey_period", d.monitoring_period_id);
'''),request('Signal period','GET','/v1/monitoring-periods/{{journey_period}}','''
pm.collectionVariables.set("journey_usage", d.billing_usage_id);
'''),request('Signal usage','GET','/v1/billing/usage/{{journey_usage}}','''
requireThat(d.product === "signal" && d.quantity === "1", "One Signal account-month unit");
requireThat(d.monitoring_period_id === pm.collectionVariables.get("journey_period"), "Usage belongs to the shared period");
'''),request('Signal reassessment','GET','/v1/risk-snapshots?subject_id={{journey_subject}}&limit=200','''
const changed = d.find(x => x.previous_snapshot_id === pm.collectionVariables.get("journey_baseline"));
if (!changed) {
 const n = Number(pm.collectionVariables.get("poll_count") || 0) + 1;
 pm.collectionVariables.set("poll_count", String(n)); requireThat(n <= 60, "Bounded reassessment polling"); pm.execution.setNextRequest(pm.info.requestName);
} else { requireThat(changed.billing_usage_id === pm.collectionVariables.get("journey_usage"), "Reassessment uses the existing Signal charge"); }
'''),request('Signal alerts','GET','/v1/alerts?subject_id={{journey_subject}}&limit=200','''
requireThat(d.length > 0, "Synthetic change produced an intervention signal");
pm.execution.setNextRequest(null);
''')]
        folders.append({'name':prefix+' end to end','description':'Run this folder only in a freshly provisioned sandbox fixture. Set runner delay to 2000 ms. Preserve action keys after interruption. Use the Python runner for exhaustive paginated charge reconciliation.','item':items})
    collection={'info':{'name':'AMLOK sandbox product journeys','schema':'https://schema.getpostman.com/json/collection/v2.1.0/collection.json','description':'Chained Insights and Signal sandbox tests. Run one folder with 2000 ms delay. Retain keys and resource IDs after failures; never run against production.'},
        'auth':{'type':'bearer','bearer':[{'key':'token','value':'{{api_key}}','type':'string'}]},'variable':[{'key':'base_url','value':''}], 'item':folders,
        'event':[{'listen':'prerequest','script':{'type':'text/javascript','exec':['const origin = pm.variables.get("base_url") || "";', r'if (!/^https:\/\/[^/@?#]+\/?$/.test(origin)) { pm.execution.setNextRequest(null); pm.execution.skipRequest(); throw new Error("Configure a valid HTTPS origin"); }','if (!pm.info.requestName.endsWith(" configuration") && pm.collectionVariables.get("sandbox_verified") !== "yes") { pm.execution.setNextRequest(null); pm.execution.skipRequest(); throw new Error("Run sandbox configuration first"); }']}}]}
    (ROOT/'downloads/amlok-journeys.postman_collection.json').write_text(json.dumps(collection,indent=2)+'\n')

if __name__=='__main__':generate()
