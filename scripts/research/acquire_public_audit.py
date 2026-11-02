"""Bounded public-source acquisition. Never runs downloaded code or paid searches."""
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/research-review/public-records'
OUT.mkdir(parents=True, exist_ok=True)
SOURCES = {
    'csbfp-summary.csv': 'https://open.canada.ca/data/dataset/3f718801-099d-4037-bb0a-1d41ba8aca8b/resource/f88700b5-ff45-4b00-a89d-a68b2c134b29/download/summary_of_financial_activities.csv',
    'csbfp-provinces.csv': 'https://open.canada.ca/data/dataset/3f718801-099d-4037-bb0a-1d41ba8aca8b/resource/1c0ad1b2-4b34-40a5-95e2-2cc196fb9d3f/download/loans_and_claims_by_province_and_territory.csv',
    'sba-dictionary.xlsx': 'https://data.sba.gov/sites/default/files/uploaded_resources/7a_504_foia_data_dictionary.xlsx',
    'sba-prefix.csv': 'https://data.sba.gov/sites/default/files/uploaded_resources/FOIA_7a_FY2010_FY2019_asof_260930.csv',
    'kinross-term-loan.html': 'https://www.kinross.com/news-and-investors/news-releases/press-release-details/2022/Kinross-announces-US1.0-billion-term-loan/default.aspx',
    'lundin-facility.html': 'https://www.lundinmining.com/news/lundin-mining-increases-existing-credit-facility-to-us45-billion',
    'bce-annual-report.pdf': 'https://www.bce.ca/cs-assets/2025-bce-annual-financial-report.pdf-blt5d552f866d8a58a3',
    'bc-ppr.html': 'https://developer.api.bcregistry.gov.bc.ca/en-CA/products/ppr/overview/',
    'basr-principles.pdf': 'https://www.basr.ca/Content/pdf/Core%20Principles/English/Core%20Registry%20Principles%20EN.pdf',
    'finqa-train.json': 'https://raw.githubusercontent.com/czyssrs/FinQA/main/dataset/train.json',
    'finqa-dev.json': 'https://raw.githubusercontent.com/czyssrs/FinQA/main/dataset/dev.json',
    'finqa-test.json': 'https://raw.githubusercontent.com/czyssrs/FinQA/main/dataset/test.json',
    'finqa-license.txt': 'https://raw.githubusercontent.com/czyssrs/FinQA/main/LICENSE',
    'finqa-readme.md': 'https://raw.githubusercontent.com/czyssrs/FinQA/main/README.md',
    'tatqa-dev.json': 'https://raw.githubusercontent.com/NExTplusplus/TAT-QA/master/dataset_raw/tatqa_dataset_dev.json',
    'financebench.jsonl': 'https://raw.githubusercontent.com/patronus-ai/financebench/main/data/financebench_open_source.jsonl',
    'financebench-readme.md': 'https://raw.githubusercontent.com/patronus-ai/financebench/main/README.md',
    'edc-transactions.html': 'https://www.edc.ca/en/about-us/corporate/disclosure/reporting-transactions/individual-transaction-information.html',
    'iq-interventions.pdf': 'https://www.investquebec.com/sites/default/files/2026-02/investissement-quebec-interventions-financieres-2024.pdf',
    'edc-reporting.html': 'https://www.edc.ca/en/about-us/corporate/disclosure/reporting-transactions.html',
    'iq-archives.html': 'https://www.investquebec.com/fr/tout-sur-nous/diffusion-de-linformation/archives',
    'berka-original.html': 'https://sorry.vse.cz/~berka/challenge/pkdd1999/',
}

def main():
    manifest = json.loads((OUT / 'acquisition-manifest.json').read_text()) if (OUT / 'acquisition-manifest.json').exists() else []
    for name, url in SOURCES.items():
        if any(x['file'] == name and x.get('status') == 200 and (x.get('scope') == 'complete_file' or name == 'sba-prefix.csv') for x in manifest):
            continue
        manifest = [x for x in manifest if x['file'] != name]
        row = {'file': name, 'url': url, 'accessed_at': datetime.now(timezone.utc).isoformat()}
        try:
            req = Request(url, headers={'User-Agent': 'AMLOK public-source research audit/0.2'})
            with urlopen(req, timeout=45) as response:
                cap = 256_000 if name == 'sba-prefix.csv' else 120_000_000
                data = response.read(cap + 1)
                truncated = len(data) > cap
                if truncated:
                    data = data[:cap]
                    if name.endswith('.csv'):
                        data = data[:data.rfind(b'\n') + 1]
                row.update(status=response.status, final_url=response.url,
                           content_type=response.headers.get('Content-Type'),
                           last_modified=response.headers.get('Last-Modified'),
                           scope='byte_prefix_not_random_sample' if truncated else 'complete_file',
                           bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
                (OUT / name).write_bytes(data)
                if name.endswith('.csv'):
                    rows = list(csv.reader(io.StringIO(data.decode('utf-8-sig', errors='replace'))))
                    row['physical_csv_records'] = len(rows)
                    row['first_record'] = rows[0] if rows else []
        except Exception as exc:
            row.update(status='unavailable', error=str(exc))
        manifest.append(row)
        (OUT / 'acquisition-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        print(json.dumps({k:row.get(k) for k in ('file','status','bytes','scope','physical_csv_records')}) ,flush=True)

if __name__ == '__main__':
    main()
