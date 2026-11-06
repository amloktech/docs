"""Validate a supplied runtime acceptance report; never fabricate benchmark results."""
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent

def problems(report,contract):
 issues=[]
 if report.get('evidence_status')!='executed':issues.append('Runtime evidence has not been executed')
 if report.get('contract_revision')!=contract['contract_revision']:issues.append('Contract revision does not match the acceptance contract')
 for key in contract['required_environment_fields']:
  if not report.get(key):issues.append('Missing environment field: '+key)
 cases=report.get('cases',{})
 for name in contract['required_cases']:
  case=cases.get(name,{})
  if case.get('result')!='passed':issues.append('Missing or failed case: '+name)
  if not case.get('evidence_refs'):issues.append('Missing evidence references: '+name)
 metrics=report.get('metrics',{})
 for name in contract['metrics_required']:
  value=metrics.get(name)
  if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:issues.append('Invalid measurement: '+name)
 for name in ['admitted_requests','completed_jobs','elapsed_seconds']:
  if not isinstance(metrics.get(name),(int,float)) or metrics[name]<=0:issues.append('No executed workload: '+name)
 for name in contract['zero_tolerance_metrics']:
  if metrics.get(name)!=0:issues.append('Zero-tolerance failure: '+name)
 for name in ['agreed_workload','agreed_targets','target_comparison','reviewer']:
  if not report.get(name):issues.append('Missing acceptance basis: '+name)
 return issues

if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python scripts/validate-enterprise-evidence.py report.json')
 contract=json.loads((ROOT/'implementation/enterprise-acceptance.json').read_text())
 report=json.loads(Path(sys.argv[1]).read_text());issues=problems(report,contract)
 print(json.dumps({'ready_for_runtime_review':not issues,'issues':issues},indent=2));raise SystemExit(bool(issues))
