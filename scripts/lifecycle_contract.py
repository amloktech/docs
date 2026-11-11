"""Extend the single product contract with shared identity and workflow lifecycle rules."""
import json
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def apply_patch(target, changes):
    for change in changes:
        parent=target
        for key in change['path'][:-1]:parent=parent[key]
        key=change['path'][-1]
        if change.get('remove'):parent.pop(key,None)
        else:parent[key]=deepcopy(change['value'])

def extend(spec, fixtures):
    patch=json.loads((ROOT/'data/api-lifecycle-contract-patch.json').read_text())
    apply_patch(spec,patch['contract'])
    apply_patch(fixtures,patch['fixtures'])
    media=spec['paths']['/v1/risk-packages/{id}']['get']['responses']['200']['content']['application/json']
    views=media['x-response-views']
    view=deepcopy(views['dimensions'])
    view['title']='participants (view=section)'
    view['schema']['properties']['data']={'$ref':'#/components/schemas/RiskSectionParticipants'}
    view['example']['data']={'view':'section','risk_package_id':fixtures['RiskPackage']['id'],'record_version':1,
      'section':'participants','section_metadata':None,'items':deepcopy(fixtures['RiskPackage'].get('participants',[])),
      'total_items':len(fixtures['RiskPackage'].get('participants',[]))}
    views['participants']=view
    return patch['operations']
