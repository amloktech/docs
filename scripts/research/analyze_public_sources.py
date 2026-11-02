"""Inspect actual acquired public records; report denominators without recasting units."""
import csv
import hashlib
import html
import json
import re
from collections import Counter
from decimal import Decimal
from pathlib import Path

import pdfplumber
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'artifacts/research-review/public-records'
OUT=ROOT/'downloads/research/public-records'
OUT.mkdir(parents=True,exist_ok=True)

def number(value):
    return Decimal(value.strip().replace(',','').replace(' ',''))

def main():
    rows=list(csv.reader((DATA/'csbfp-summary.csv').open(encoding='cp1252')))
    years=[]
    for row in rows[5:]:
        if row[0].startswith('Total'):
            total=row
            break
        years.append({'fiscal_year':row[0].replace('\u2013','-'),'loans':int(number(row[1])),
                      'loan_value_cad_thousands':str(number(row[2])),'claims_paid':int(number(row[5]))})
    assert sum(x['loans'] for x in years)==int(number(total[1]))
    sba=list(csv.DictReader((DATA/'sba-prefix.csv').open(encoding='utf-8-sig')))
    edc=[]
    for table in re.findall(r'<table\b.*?</table>',(DATA/'edc-transactions.html').read_text(),re.S):
        raw=[[html.unescape(re.sub('<[^>]*>',' ',c)).strip() for c in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',r,re.S)] for r in re.findall(r'<tr\b.*?</tr>',table,re.S)]
        if raw and 'Signing Date' in raw[0]:
            edc=[dict(zip(raw[0],r)) for r in raw[1:]]
    iq=[]
    with pdfplumber.open(DATA/'iq-interventions.pdf') as pdf:
        for page_index,page in enumerate(pdf.pages):
            for table_index,table in enumerate(page.extract_tables()):
                for row_index,row in enumerate(table):
                    if len(row)>=3 and row[0] and row[0]!="Nom de l'entreprise" and row[-1] in ['Prêt','Garantie','Capitaux propres ou quasi-capitaux propres']:
                        iq.append({'page':page_index+1,'table_index':table_index,'row_index':row_index,'name':row[0], 'amount_text':row[-2], 'type':row[-1]})
    bce=PdfReader(DATA/'bce-annual-report.pdf')
    iq_pdf=PdfReader(DATA/'iq-interventions.pdf')
    # Hand-read from the rendered original page 2, not generated records.
    probes=[{'source_pdf_page':2,'row':1,'amount':375000},
            {'source_pdf_page':2,'row':2,'amount':75000},
            {'source_pdf_page':2,'row':3,'amount':1000000},
            {'source_pdf_page':2,'row':4,'amount':2075000},
            {'source_pdf_page':2,'row':5,'amount':1616250}]
    text=iq_pdf.pages[1].extract_text()
    clean=re.sub(r'[^0-9]','',text)
    for probe in probes:
        probe['pypdf_amount_digits_found']=str(probe['amount']) in clean
    finqa={s:json.loads((DATA/f'finqa-{s}.json').read_text()) for s in ['train','dev','test']}
    tatqa=json.loads((DATA/'tatqa-dev.json').read_text())
    fb=[json.loads(x) for x in (DATA/'financebench.jsonl').read_text().splitlines()]
    result={
      'version':'0.2','record_unit_warning':'Never add aggregate represented loans, source rows, questions and registry events into one deal total.',
      'csbfp':{'source':'csbfp-summary.csv','annual_observations':len(years),'period':[years[0]['fiscal_year'],years[-1]['fiscal_year']],
               'reported_loans_sum':sum(x['loans'] for x in years),'reported_total_loan_value_cad_thousands':str(number(total[2])),
               'row_loan_value_sum_cad_thousands':str(sum(Decimal(x['loan_value_cad_thousands']) for x in years)),
               'individual_loan_rows_in_file':0,'years':years},
      'edc':{'source':'edc-transactions.html','visible_table_rows':len(edc),'fields':list(edc[0]),
             'countries':dict(Counter(r['Country'] for r in edc)),
             'products':dict(Counter(r['Product'] for r in edc)),
             'scope':'visible current-page table only; not total archive; signed support, not necessarily disbursement'},
      'iq':{'source':'iq-interventions.pdf','pages':len(iq_pdf.pages),
            'machine_extracted_rows_with_recognized_types':len(iq),
            'types':dict(Counter(r['type'] for r in iq)),
            'rows_with_amount_text':sum(bool(r['amount_text']) for r in iq),
            'scope':'parser output count, not an independently adjudicated full census or unique closed loans',
            'page_2_visual_amount_probes':probes},
      'bce':{'source':'bce-annual-report.pdf','pages':len(bce.pages),'liquidity_pdf_page':78,'printed_page':76,
             'as_of':'2025-12-31','currency':'CAD','units':'millions',
             'committed_facilities':{'available':6393,'drawn':1409,'letters_of_credit':71,'commercial_paper':2550,'net_available':2363},
             'reconciliation_residual':6393-1409-71-2550-2363},
      'sba':{'source':'sba-prefix.csv','sample_rows':len(sba),'columns':list(sba[0]),
             'scope':'byte prefix from FY2010-FY2019 release, not random or representative',
             'us_only':True,'location_id_is':'lender identifier, not loan identifier'},
      'finqa':{'source':'original author repository','split_counts':{k:len(v) for k,v in finqa.items()},
               'test_source_filenames':len({x['filename'] for x in finqa['test']})},
      'tatqa':{'contexts_in_dev':len(tatqa),'questions_in_dev':sum(len(x['questions']) for x in tatqa)},
      'financebench':{'inspected_open_sample_questions':len(fb),'commercial_evaluation_status':'not run; noncommercial terms require resolution'},
    }
    # Publish source locators and field availability, not a reprint of company lists.
    # IDs identify source observations; they are not deduplicated facilities/deals.
    index=[]
    def add(source,locator,event_type,fields,entity_text=None):
        digest=hashlib.sha256((DATA/source).read_bytes()).hexdigest()
        identity=json.dumps([digest,locator],sort_keys=True,ensure_ascii=False)
        row={'record_id':'pub_'+hashlib.sha256(identity.encode()).hexdigest()[:24],
             'source_file':source,'source_sha256':digest,'locator':locator,
             'record_type':event_type,'field_availability':fields,
             'facility_deduplication':'not_adjudicated','independent_outcome':False}
        if entity_text:
            row['source_party_text_sha256']=hashlib.sha256(entity_text.encode()).hexdigest()
        index.append(row)
    for i,row in enumerate(edc):
        add('edc-transactions.html',{'table':'individual-transactions','data_row_1_based':i+1},
            'signed_support_disclosure',{'text_fields':[k for k,v in row.items() if v],
                                        'amount_encoding':'published_CAD_band','product':row['Product']},row['Counterparty'])
    for row in iq:
        add('iq-interventions.pdf',{'pdf_page_1_based':row['page'],'table_0_based':row['table_index'],'row_0_based':row['row_index']},
            'published_financing_intervention',{'text_fields':['company','assistance_type'],
                'amount_encoding':'requires_visual_recovery' if not row['amount_text'] else 'text',
                'assistance_type':row['type']},row['name'])
    add('kinross-term-loan.html',{'section':'financing-announcement'},'term_loan_announcement',
        {'verified_fields':['borrower','principal','currency','term','maturity','use_of_proceeds','arrangers']})
    add('lundin-facility.html',{'section':'facility-amendment-announcement'},'facility_amendment_announcement',
        {'verified_fields':['borrower','commitment','currency','conditional_capacity','maturity','reference_rate','margin']})
    add('bce-annual-report.pdf',{'pdf_page_1_based':78,'printed_page':76,'table':'committed credit facilities'},'aggregate_facility_position',
        {'verified_fields':['as_of','currency','units','available','drawn','letters_of_credit','commercial_paper','net_available']})
    (OUT/'record-index.jsonl').write_text(''.join(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n' for row in index))
    result['record_index']={'observations':len(index),'by_source':dict(Counter(row['source_file'] for row in index)),
        'unit':'source observations with stable locators, not unique closed deals',
        'sha256':hashlib.sha256((OUT/'record-index.jsonl').read_bytes()).hexdigest()}
    (OUT/'source-analysis.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    manifests=json.loads((DATA/'acquisition-manifest.json').read_text())
    for row in manifests:
        row.pop('first_record',None)
        # No private local paths or raw borrower rows enter the public manifest.
        if row.get('status')==200:
            assert hashlib.sha256((DATA/row['file']).read_bytes()).hexdigest()==row['sha256']
    (OUT/'acquisition-manifest.json').write_text(json.dumps(manifests,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['csbfp','sba']},indent=2,ensure_ascii=False))
    print('CSBFP',result['csbfp']['annual_observations'],result['csbfp']['reported_loans_sum'])

if __name__=='__main__':main()
