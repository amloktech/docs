"""Package derived public research artifacts without redistributing source corpora."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[2]
NAMES=['acquire_public_audit.py','analyze_public_sources.py','build_source_register.py','benchmark_public_evidence.py','test_public_research.py','render_public_results.py','package_public_research.py','requirements-public.txt','train_public_baselines.py']
files=[ROOT/'scripts/research'/n for n in NAMES]
files+=list((ROOT/'downloads/research/public-records').glob('*'))
files+=list((ROOT/'downloads/research/corpus').glob('*'))
files+=list((ROOT/'research').rglob('*.mdx'))
files+=[ROOT/'images/research/public-retrieval.png',ROOT/'images/research/public-retrieval.svg']
manifest={str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)}
readme='''AMLOK public-record research package 0.3

Read research/reproducibility.mdx for acquisition and execution commands.
This bundle includes derived artifacts, code and methods. Original public
reports and loan-row files are not redistributed. Download them only through
the documented source routes, subject to their applicable rights and terms.

The record index contains source observations, not adjudicated unique loans.
The executed results measure structured-loan classification on actual SBA
records and lexical evidence retrieval on real financial reports. Hosted frontier and AMLOK foundation-model comparisons are not run.

MANIFEST.json gives a SHA-256 digest and byte count for each packaged file.
'''
out=ROOT/'downloads/research/amlok-public-records-0.3.zip'
with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=9) as z:
    def put(name,data):
        info=ZipInfo(name,date_time=(2026,11,1,0,0,0));info.compress_type=ZIP_DEFLATED
        info.external_attr=0o644<<16;z.writestr(info,data)
    for p in sorted(files):put(str(p.relative_to(ROOT)),p.read_bytes())
    put('MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    put('README.txt',readme)
summary={'file':out.name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'files':len(files),'version':'0.3'}
(ROOT/'downloads/research/amlok-public-records-0.3.manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
