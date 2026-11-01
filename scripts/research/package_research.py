"""Package only public methods, generated data, and measured research artifacts."""
from pathlib import Path
import hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[2]

def main():
    files=sorted(set(
        list((ROOT/'scripts/research').glob('*.py'))+
        [ROOT/'scripts/research/requirements.txt']+
        list((ROOT/'artifacts/research-review/experiment').glob('*.*'))+
        [ROOT/'artifacts/research-review/boc-fx-2025.json']+
        list((ROOT/'downloads/research').glob('*.json'))+
        list((ROOT/'images/research').glob('*.png'))
    ))
    entries={str(p.relative_to(ROOT)):p.read_bytes() for p in files if p.is_file()}
    manifest={path:{'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)} for path,data in entries.items()}
    entries['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    entries['README.md']=b'''# AMLOK research reproducibility package 0.1

This package contains an executed synthetic event-transformer experiment and a
descriptive public Bank of Canada FX analysis. No real borrower data or production
model is included. Do not use generated probabilities for lending decisions.

Use an isolated Python 3.12 environment and install scripts/research/requirements.txt.
Run scripts/research/test_research.py to verify the included predictions, arrays,
checkpoints, metrics, public-source snapshot, and selected evidence invariants.

To repeat training, run scripts/research/run_synthetic_study.py. This overwrites local
experiment outputs. To refresh the public FX acquisition, run scripts/research/public_data.py
(network access required). Preserve this original snapshot before regenerating.
Run scripts/research/render_results.py to regenerate plots and the result page.
The renderer creates research/synthetic-study.mdx and the chart directories as needed.

MANIFEST.json contains hashes and sizes of the included original artifacts.
Bank of Canada source: https://www.bankofcanada.ca/valet/docs
Source terms: https://www.bankofcanada.ca/terms/
Research documentation: https://docs.amlok.io/research
No foundation-model, real-cohort, or frontier-comparison claim is established.
'''
    dest=ROOT/'downloads/research/amlok-research-0.1.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for name,content in sorted(entries.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,11,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,content)
    print(json.dumps({'path':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'members':len(entries)}))

if __name__=='__main__':main()
