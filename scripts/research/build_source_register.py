"""Maintain semantic source inventory separately from acquisition-byte manifests."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'downloads/research/public-records'
# Status describes work actually done, not a promise of full-corpus access.
SOURCES=[
('edc','EDC individual transactions','CA','financing','record_sample_inspected','signed support disclosure','https://www.edc.ca/en/about-us/corporate/disclosure/reporting-transactions/individual-transaction-information.html','Signing date; country; counterparty; purpose; sector; product; CAD amount band; Canadian company','30 visible rows, 11 columns; full archive not enumerated. Guarantees, equity and financing remain separate. Signed support is not proof of disbursement.',['edc-transactions.html','edc-reporting.html']),
('iq','Investissement Québec interventions','CA-QC','financing','record_document_inspected','financing intervention','https://www.investquebec.com/fr/tout-sur-nous/diffusion-de-linformation/archives','Company; financing amount; assistance type','18-page 2023-24 PDF. Parser identifies 1,014 typed rows, not adjudicated unique loans. Amounts require visual recovery; repeated companies and co-borrowers need linkage.',['iq-interventions.pdf','iq-archives.html']),
('kinross','Kinross term loan','CA','financing','record_document_inspected','issuer financing announcement','https://www.kinross.com/news-and-investors/news-releases/press-release-details/2022/Kinross-announces-US1.0-billion-term-loan/default.aspx','Borrower; USD principal; maturity; term; use of proceeds; arrangers','One disclosed loan event. Refinancing is not new operating revenue; no repayment-performance ledger supplied.',['kinross-term-loan.html']),
('lundin','Lundin Mining credit amendment','CA','financing','record_document_inspected','facility amendment','https://www.lundinmining.com/news/lundin-mining-increases-existing-credit-facility-to-us45-billion','Facility capacity; conditional stages; maturity; reference rate; margin; lenders','One amendment. Separate initial availability, conditional capacity and actual drawn cash.',['lundin-facility.html']),
('bce','BCE annual financial report','CA','financing','record_document_inspected','dated facility position','https://www.bce.ca/cs-assets/2025-bce-annual-financial-report.pdf-blt5d552f866d8a58a3','Committed capacity; drawn amounts; letters of credit; commercial paper; net available; units; date','180-page report acquired. Liquidity table on PDF page 78 visually checked; positions are not new originations.',['bce-annual-report.pdf']),
('sedar','SEDAR+ public filings','CA','financing','documentation_verified','issuer filing','https://systems.securities-administrators.ca/onlinehelp/faqs/searching-sedar/','Issuer; filing type; publication date; available financial/contractual text','Search documentation reviewed; no bulk issuer corpus acquired. Public issuers do not represent private SMEs or consumers.',[]),
('cib','Canada Infrastructure Bank','CA','financing','documentation_verified','investment/project stage','https://cib-bic.ca/en/work-with-us/investment-process/','Project; investment stage; financial-close terminology; disclosed amount','Process reviewed; no complete project ledger acquired. Commitment, financial close and disbursement differ.',[]),
('bc-ppr','BC Personal Property Registry','CA-BC','registry','documentation_verified','registered security event','https://developer.api.bcregistry.gov.bc.ca/en-CA/products/ppr/overview/','Registrations; parties; search criteria; amendments; renewals; discharges','Documented API requires account/key and applicable fees. Documentation acquired; no paid live search executed. Not an anonymous free bulk export.',['bc-ppr.html']),
('on-ppsa','Ontario PPSA','CA-ON','registry','documentation_verified','registered security event','https://www.personalproperty.gov.on.ca/ppsrweb/en/help/makingEnquiry.htm','Name; registration; vehicle searches; registration family/history','Search help reviewed; no individual search result acquired. Security registration does not prove funded principal or repayment.',[]),
('acol','ACOL PPRS','CA','registry','documentation_verified','registered security event','https://www.acol.ca/en/pprs/responsibilities/searcher.html','Jurisdiction; registration; parties; search-report information','Documentation reviewed. Participating jurisdictions, fees and entitlements must be handled separately; no record acquisition.',[]),
('rdprm','Québec RDPRM','CA-QC','registry','documentation_verified','registered movable/personal right','https://www.rdprm.gouv.qc.ca/','Registered right; parties; dates; amendments according to returned report','Consultation documentation reviewed; no bulk export or individual report acquired.',[]),
('basr','Bank Act Security Registry','CA','registry','documentation_verified','notice of intention/security event','https://www.basr.ca/','Notice; bank/debtor; renewal; expiry; release','Principles PDF acquired. A release may also mean no security was given; do not infer successful loan repayment. No individual searches.',['basr-principles.pdf']),
('corporations','Corporations Canada','CA','registry','documentation_verified','federal legal entity','https://ised-isde.canada.ca/site/corporations-canada/en/data-services','Corporate identifier; name; status; permitted registry attributes','Data services/API verified; federal scope is not all Canadian corporations. No national identity corpus acquired.',[]),
('req','Québec enterprise register','CA-QC','registry','catalogue_verified','registered enterprise','https://www.donneesquebec.ca/recherche/dataset/registre-des-entreprises','NEQ; published entity identity and register attributes','Catalogue reviewed; underlying bulk files not acquired in this release.',[]),
('csbfp','CSBFP loans and claims','CA','outcomes_context','aggregate_inspected','annual program aggregate','https://open.canada.ca/data/dataset/3f718801-099d-4037-bb0a-1d41ba8aca8b','Fiscal year; loan count/value; claims; provincial breakdown','27 annual observations represent 214,158 loans, with zero individual loan rows. English/French tables repeat the same population. Claims are not matched cohort defaults.',['csbfp-summary.csv','csbfp-provinces.csv']),
('osb-records','OSB insolvency-record search','CA','outcomes_context','documentation_verified','individual insolvency proceeding','https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/bankruptcy-and-insolvency-records-search/instructions','Debtor match; proceeding type; dates; available case details','Search instructions verified. Authenticated/fee-based searches not executed; identity and event adjudication required.',[]),
('osb-statistics','OSB statistics','CA','outcomes_context','documentation_verified','aggregate insolvency statistic','https://ised-isde.canada.ca/site/office-superintendent-bankruptcy/en/statistics-and-research','Period; jurisdiction; aggregate insolvency counts','Context reference only; aggregate totals do not label individual borrowers.',[]),
('canlii','CanLII','CA','outcomes_context','terms_reviewed_restricted_direct_access','court/tribunal document','https://www.canlii.org/info/terms.html','Case; jurisdiction; publication; parties; judicial event','Indexed primary terms reviewed; direct retrieval restricted. No automated bulk corpus. Use authorized routes/original publishers and distinguish allegations from decisions.',[]),
('statcan','Statistics Canada WDS','CA','outcomes_context','documentation_verified','statistical observation','https://www.statcan.gc.ca/en/developers/wds/user-guide','Series; region; industry; period; value; units','Documented source route; preserve release vintage and licence. Revised present-day values can leak future information.',[]),
('boc','Bank of Canada Valet','CA','outcomes_context','prior_context_analysis','FX observation','https://www.bankofcanada.ca/valet/docs','Date; series; currency quote; value','Prior FXUSDCAD calculation inspected 249 observations in 2025. Context only; not borrower outcomes. Separate prior manifest.',[]),
('sba','SBA 7(a)/504 FOIA','US','benchmarks','record_prefix_inspected','loan-program row','https://data.sba.gov/dataset/7a-504-foia','Approval; first disbursement; amount; rate; term; industry; status; selected outcomes','548 complete rows from one US release byte prefix, plus dictionary. Not random or Canadian. LocationID is lender ID, not loan ID. EXEMPT is not known successful repayment.',['sba-prefix.csv','sba-dictionary.xlsx']),
('finqa','FinQA','US-document-benchmark','benchmarks','benchmark_executed','financial-report question','https://github.com/czyssrs/FinQA','Question; report text/table; gold evidence IDs; answer; program','6,251 train / 883 dev / 1,147 test questions. Test retrieval executed. Gold used only for scoring; no borrower outcomes. Repository licence and report rights are distinct.',['finqa-train.json','finqa-dev.json','finqa-test.json','finqa-license.txt','finqa-readme.md']),
('tatqa','TAT-QA','international-document-benchmark','benchmarks','benchmark_development_inspected','financial-report question','https://github.com/NExTplusplus/TAT-QA','Question; text; tables; answer type; evidence','278 development contexts, 1,668 questions. Not used as a locked final test. No performance reported.',['tatqa-dev.json']),
('financebench','FinanceBench','US-document-benchmark','benchmarks','sample_inspected_not_scored','financial-report question','https://www.patronus.ai/research/financebench','Question; answer; document/evidence metadata','150 released questions inspected. Publisher describes noncommercial open-sample conditions; no commercial scoring/training performed.',['financebench.jsonl','financebench-readme.md']),
('cuad','CUAD','contract-benchmark','benchmarks','documentation_verified','contract clause','https://www.atticusprojectai.org/cuad','Contract text; clause labels; spans; category','Description/licence reviewed; corpus not acquired or scored. Candidate clause task, not private bank transactions.',[]),
('berka','PKDD 1999 original source','CZ','benchmarks','unavailable','banking research dataset','https://sorry.vse.cz/~berka/challenge/pkdd1999/','Not verified from original host in this audit','Original host unavailable. No mirror corpus acquired and no training entitlement assumed.',['berka-original.html']),
]

def main():
    entries=[]
    for sid,name,jurisdiction,group,status,unit,url,fields,scope,files in SOURCES:
        entries.append(dict(source_id=sid,name=name,jurisdiction=jurisdiction,group=group,status=status,record_unit=unit,primary_url=url,available_or_documented_fields=fields.split('; '),verified_scope=scope,acquisition_files=files))
    payload={'version':'0.2','review_date':'2026-11-01','counting_rule':'Do not sum aggregates, documents, registry events, questions or parser rows as unique closed deals.','sources':entries}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'source-register.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    sections=[('financing','Financing disclosures and corporate reporting'),('registry','Registered rights and entity identity'),('outcomes_context','Outcomes, macro context and program totals'),('benchmarks','Supplementary international and document datasets')]
    page='''---
mode: "wide"
title: "Canadian public-source inventory"
description: "A source-by-source inventory of financing records, registry evidence, fields, access conditions and verified acquisition scope."
sidebarTitle: "Public-source inventory"
---

The inventory starts with original records and documented schemas. It distinguishes record inspection, aggregate inspection, schema verification and access-gated acquisition. A source can be useful without exposing a complete borrower ledger or independently verified lending outcome.

Download the [source register](/downloads/research/public-records/source-register.json), [acquisition manifest](/downloads/research/public-records/acquisition-manifest.json) and [computed source analysis](/downloads/research/public-records/source-analysis.json). The manifest preserves exact retrieved bytes through SHA-256 hashes; the register explains what those bytes mean. These are the sources reviewed for this release, not an exhaustive inventory of all Canadian public records.

'''
    for group,title in sections:
        page+=f'## {title}\n\n| Source | Fields and research use | Verified scope |\n| --- | --- | --- |\n'
        for s in entries:
            if s['group']==group:
                page+=f"| [{s['name']}]({s['primary_url']}) | {'; '.join(s['available_or_documented_fields'])}. | {s['verified_scope']} |\n"
        page+='\n'
    page+='''## What a source can prove

A financing announcement may establish parties, facility terms and a signed event. A facility-position table establishes balances at its reporting date. A registration establishes a registered right or notice. None automatically supplies a private bank ledger, every drawdown, complete repayment history or a successful outcome.

Repeated company names can represent separate interventions; co-borrower rows can describe one intervention. A facility amendment must remain linked to the original facility. Preserve published amount bands and conditions rather than replacing them with exact cash amounts. See the [verified examples](/research/public-record-findings) and [deal-corpus rules](/research/deal-corpus).

## Rights and historical availability

Repository licences and source-document rights are distinct. Public visibility does not automatically authorize every commercial training or redistribution purpose. The downloadable package contains derived counts, method code and prediction IDs rather than republishing all reports or borrower rows. Resolve source-specific rights before expanding acquisition or training.

Keep signing time, publication time, acquisition time and observation cutoff separately. For a historical test, current accessibility cannot prove that a record was available at the earlier decision date. Revised statistics, late disclosures and later court findings must not leak into past predictions.

## Acquisition priorities

First expand disclosed financing records with explicit dates, parties and product types. Adjudicate document extraction and facility linkage across announcements, filings and amendments. Acquire registry evidence through permitted access. Link outcomes only when the source establishes both the event and sufficiently reliable entity identity.

Public-document tasks and private-transaction tasks require different evidence. The inspected sources establish document fields and public financing relationships. They do not expose the connected Shopify, Stripe, accounting and bank histories needed to evaluate complete borrower cash flow. Those tasks use independently authorized evidence under the [data-foundation rules](/research/data-foundations).
'''
    (ROOT/'research/canadian-data.mdx').write_text(page)
    print(f'Wrote {len(entries)} source entries and inventory page')

if __name__=='__main__':main()
