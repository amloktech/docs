#!/usr/bin/env python3
"""Run provisioned AMLOK sandbox journeys. Standard library only; never logs keys."""
import argparse
import json
import os
from pathlib import Path
import time
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from uuid import uuid4


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class APIError(RuntimeError):
    def __init__(self, status, code):
        self.status, self.code = status, code
        super().__init__(f'HTTP {status}: {code}. State is preserved; reconcile before starting another action.')


class Client:
    def __init__(self, origin, key):
        u = urlsplit(origin)
        if u.scheme != 'https' or not u.netloc or u.username or u.password or u.query or u.fragment or u.path not in ['', '/']:
            raise ValueError('AMLOK_API_BASE_URL must be an HTTPS origin without credentials, path or query.')
        self.origin, self.key = origin.rstrip('/'), key
        self.opener = build_opener(NoRedirects())

    def request(self, method, path, body=None, key=None):
        headers = {'Authorization': 'Bearer '+self.key, 'Accept': 'application/json'}
        if key: headers['Idempotency-Key'] = key
        raw = None
        if body is not None:
            raw = json.dumps(body).encode(); headers['Content-Type'] = 'application/json'
        req = Request(self.origin+path, data=raw, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=30) as response:
                return json.load(response)
        except HTTPError as e:
            try: code = json.load(e).get('error', {}).get('code', 'http_error')
            except (ValueError, AttributeError): code = 'http_error'
            raise APIError(e.code, code) from None


class Journey:
    def __init__(self, client, state_path, journey, timeout=300, sleep=time.sleep):
        self.client, self.path, self.journey = client, Path(state_path), journey
        self.timeout, self.sleep = timeout, sleep
        self.state = json.loads(self.path.read_text()) if self.path.exists() else {'origin': client.origin, 'journey': journey, 'actions': {}}
        if self.state['origin'] != client.origin or self.state['journey'] != journey:
            raise ValueError('This state file belongs to another origin or journey.')

    def save(self):
        temp = self.path.with_name(self.path.name+'.tmp')
        fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f: json.dump(self.state, f, indent=2)
        os.replace(temp, self.path)

    def get(self, path, params=None):
        return self.client.request('GET', path+('?' + urlencode(params) if params else ''))

    def all(self, path, params=None):
        params = dict(params or {}); result = []
        for _ in range(100):
            response = self.get(path, params); result.extend(response['data'])
            page = response.get('page', {})
            if not page.get('has_more'): return result
            if not page.get('next_cursor'): raise RuntimeError('Incomplete pagination response.')
            params['cursor'] = page['next_cursor']
        raise RuntimeError('Pagination bound exceeded; no completeness assertion was made.')

    def wait(self, fetch, done, blocked=lambda x: None):
        deadline = time.monotonic()+self.timeout
        while True:
            value = fetch()
            reason = blocked(value)
            if reason: raise RuntimeError(reason+' State is preserved; do not replace this run.')
            if done(value): return value
            if time.monotonic() >= deadline: raise TimeoutError('Polling deadline reached. Resume with the same state file; server work was not cancelled.')
            self.sleep(min(5, max(1, value.get('retry_after_seconds') or 2)))

    def post(self, name, operation_id, path, body):
        action = self.state['actions'].get(name)
        if action:
            if (action['operation_id'], action['path'], action['body']) != (operation_id, path, body):
                raise RuntimeError('Saved intended request changed. Reconcile the original action first.')
            if action.get('resource_id'): return action['resource_id']
        else:
            action = {'operation_id': operation_id, 'path': path, 'body': body, 'key': str(uuid4())}
            self.state['actions'][name] = action; self.save()
        try:
            result = self.client.request('POST', path, body, action['key'])['data']
            resource_id = result['id']
        except APIError as e:
            if e.code != 'idempotency_result_expired': raise
            receipt = self.client.request('GET','/v1/request-receipts/lookup?'+urlencode({'operation_id':operation_id,'target_path':path}),key=action['key'])['data']
            if receipt['status'] == 'resource_unavailable': raise RuntimeError('Original resource expired. Contact support; do not resubmit.')
            resource_id = receipt['resource_id']
        action['resource_id'] = resource_id; self.save(); return resource_id

    def run(self):
        config = self.get('/v1/configuration')['data']
        if config['environment'] != 'sandbox': raise RuntimeError('This runner refuses production environments.')
        if self.state.get('workspace_id',config['workspace_id']) != config['workspace_id']: raise RuntimeError('The API key points to a different workspace.')
        self.state['workspace_id'] = config['workspace_id']; self.save()
        if not self.state.get('fixture'):
            fixtures = self.all('/v1/sandbox/scenarios')
            self.state['fixture'] = next(x for x in fixtures if x['id'] == self.journey+'_success'); self.save()
        f = self.state['fixture']
        # After acceptance, use the accepted IDs even if readiness or configuration later changes.
        if not self.state['actions']:
            self.wait(lambda:self.get('/v1/subjects/'+f['subject_id']+'/readiness',{'product':self.journey})['data'],
                      lambda x:x['status']=='ready', lambda x:('Readiness blocked: '+json.dumps(x['checks'])) if x['status']=='blocked' else None)
        if self.journey == 'insights': return self.insights(f)
        return self.signal(f,config)

    def insights(self,f):
        body={'subject_id':f['subject_id'],'workflow_type':'underwrite','workflow_version':f['workflow_version'],
              'application_id':f['application_id'],'input_manifest_id':f['input_manifest_id'],'input_resource_ids':[f['application_id']]}
        rid=self.post('underwrite','EP147','/v1/workflow-runs',body)
        run=self.wait(lambda:self.get('/v1/workflow-runs/'+rid)['data'],lambda x:x['status']=='completed',
            lambda x:('Workflow '+x['status']+': '+json.dumps(x.get('failure') or x.get('blocked_reason'))) if x['status'] in ['failed','cancelled','blocked_by_limit','waiting_for_data','waiting_for_credits'] else None)
        usage=self.get('/v1/billing/usage/'+run['billing_usage_id'])['data']
        snapshot=self.get('/v1/risk-snapshots/'+usage['risk_snapshot_id'])['data']
        assert usage['product']=='insights' and usage['subject_id']==f['subject_id'] and usage['workflow_run_id']==rid
        assert usage['quantity']=='1' and snapshot['workflow_run_id']==rid and snapshot['billing_usage_id']==usage['id']
        assert snapshot['evidence_manifest_id']==run['input_manifest_id']==usage['input_manifest_id']
        records=self.all('/v1/billing/usage',{'from':usage['billing_period_start'],'to':usage['billing_period_end'],'product':'insights','source_resource_id':rid})
        charges=[x for x in records if x['entry_type']=='charge' and x['workflow_run_id']==rid]
        assert len(charges)==1, 'Expected exactly one underwriting charge.'
        self.state['result']={'workflow_id':rid,'risk_snapshot_id':snapshot['id'],'usage_id':usage['id'],'amount':usage['amount']};self.save()
        return self.state['result']

    def signal(self,f,config):
        if 'monitor' in self.state['actions']:
            body=self.state['actions']['monitor']['body']
        else:
            rules=next(x for x in config['rulesets'] if x['id']==f['ruleset_version'])
            body={'subject_id':f['subject_id'],'baseline_snapshot_id':f['baseline_snapshot_id'],'resource_types':rules['resource_types'],
                  'attribute_keys':rules['attribute_keys'],'cadence':f['cadence'],'ruleset_version':f['ruleset_version']}
        mid=self.post('monitor','EP150','/v1/monitors',body)
        monitor=self.wait(lambda:self.get('/v1/monitors/'+mid)['data'],lambda x:x['status']=='active',lambda x:'Monitor '+x['status'] if x['status'] in ['blocked','cancelled','paused'] else None)
        period=self.get('/v1/monitoring-periods/'+monitor['monitoring_period_id'])['data']
        def changed():
            snaps=self.all('/v1/risk-snapshots',{'subject_id':f['subject_id']})
            alerts=self.all('/v1/alerts',{'subject_id':f['subject_id']})
            return {'snapshots':[x for x in snaps if x['previous_snapshot_id']==f['baseline_snapshot_id']], 'alerts':alerts}
        change=self.wait(changed,lambda x:bool(x['snapshots'] and x['alerts']))
        usage=self.get('/v1/billing/usage/'+period['billing_usage_id'])['data']
        assert usage['product']=='signal' and usage['quantity']=='1' and usage['subject_id']==f['subject_id']
        rows=self.all('/v1/billing/usage',{'from':period['period_start'],'to':period['period_end']})
        charges=[x for x in rows if x['subject_id']==f['subject_id'] and x['entry_type']=='charge']
        assert len(charges)==1 and charges[0]['id']==usage['id'], 'Expected one Signal charge and no Insights charge for this fixture.'
        self.state['result']={'monitor_id':mid,'monitoring_period_id':period['id'],'risk_snapshot_id':change['snapshots'][0]['id'],'usage_id':usage['id'],'amount':usage['amount']};self.save()
        return self.state['result']


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('journey',choices=['insights','signal']);p.add_argument('--state',required=True);p.add_argument('--timeout',type=int,default=300)
    args=p.parse_args()
    client=Client(os.environ['AMLOK_API_BASE_URL'],os.environ['AMLOK_API_KEY'])
    print(json.dumps(Journey(client,args.state,args.journey,args.timeout).run(),indent=2))

if __name__=='__main__':main()
