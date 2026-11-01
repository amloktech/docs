"""Bounded descriptive public-data analysis. Does not train any model."""
from pathlib import Path
import hashlib, json, urllib.request

ROOT=Path(__file__).resolve().parents[2]
URL='https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?start_date=2025-01-01&end_date=2025-12-31'

def main():
    raw=urllib.request.urlopen(URL,timeout=30).read(); payload=json.loads(raw)
    rows=payload['observations']
    assert all('2025-01-01' <= r['d'] <= '2025-12-31' for r in rows)
    values=[float(r['FXUSDCAD']['v']) for r in rows if 'FXUSDCAD' in r]
    assert values and all(x>0 for x in values)
    result={'source_url':URL,'series':'FXUSDCAD','meaning':'CAD per USD','year':2025,
            'count':len(values),'minimum':min(values),'maximum':max(values),
            'arithmetic_mean':sum(values)/len(values),'sha256':hashlib.sha256(raw).hexdigest(),
            'use':'Descriptive public macro example only; no borrower linkage, forecasting or model fitting.'}
    dest=ROOT/'artifacts/research-review'; dest.mkdir(parents=True,exist_ok=True)
    (dest/'boc-fx-2025.json').write_bytes(raw)
    (ROOT/'downloads/research/public-data-summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
