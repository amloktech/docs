"""Small reference functions for testing explicit research invariants only."""
from datetime import datetime
from decimal import Decimal

def as_of(records,workspace,cutoff):
    cutoff=datetime.fromisoformat(cutoff)
    if cutoff.tzinfo is None: raise ValueError('timezone required')
    versions={};seen={}
    for r in records:
        if r['workspace']!=workspace: continue
        event=datetime.fromisoformat(r['event_time']); known=datetime.fromisoformat(r['known_at'])
        if event.tzinfo is None or known.tzinfo is None: raise ValueError('timezone required')
        if event>cutoff or known>cutoff: continue
        key=(r['source'],r['id'])
        version_key=(*key,r['version'])
        if version_key in seen and r!=seen[version_key]:
            raise ValueError('conflicting duplicate')
        seen[version_key]=r
        if key not in versions or r['version']>versions[key]['version']:
            versions[key]=r
    return list(versions.values())

def cash_proxy(receipts,operating_outflows,scheduled_debt):
    if any(v is None for v in [receipts,operating_outflows,scheduled_debt]): return None
    r,c,d=map(lambda v:Decimal(str(v)),[receipts,operating_outflows,scheduled_debt])
    if min(r,c,d)<0: raise ValueError('nonnegative quantities required')
    return (r-c)/d if d else None

def settlement(gross,refunds,fees,reserve):
    return Decimal(gross)-Decimal(refunds)-Decimal(fees)-Decimal(reserve)
