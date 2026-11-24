"""Catch omitted definitions, invented keys and mismatched generated dictionaries."""
import csv
import hashlib
import json
import re
from pathlib import Path
from financial_meaning_guides import build_dictionary, bank_meaning, ROOT

meaning, metrics, bank, cross, taxonomy = build_dictionary()
assert meaning == json.loads((ROOT / 'downloads/financial-definitions.json').read_text())
assert len(meaning['dimensions']) == 24
assert len(meaning['metrics']) == 184
assert len(meaning['categories']) == 327
assert len(meaning['groups']) == 45
assert len(meaning['cross_system_attributes']) == 150
assert len(bank['definitions']) == 12805
assert len(meaning['analyses']) == 14
assert len(meaning['axes']) == 10

rows = list(csv.DictReader((ROOT / 'downloads/financial-attribute-dictionary.csv').open()))
keys = {d['key'] for d in bank['definitions'] + cross['definitions']}
assert len(rows) == len(keys) == 12955
assert {r['key'] for r in rows} == keys, 'Omitted or invented attribute key'
by_key = {r['key']: r for r in rows}
for d in bank['definitions']:
    row = by_key[d['key']]
    assert row['meaning'] == bank_meaning(d, bank, meaning['categories'], meaning['groups'])
    assert row['unit'] == bank['statistics'][d['statistic']]['unit']
    for key in ['context', 'direction', 'selector', 'period', 'statistic']:
        assert row[key] == d[key], (d['key'], key)
for d in cross['definitions']:
    row = by_key[d['key']]
    assert row['meaning'] == meaning['cross_system_attributes'][d['key']]
    assert row['unit'] == d['unit'] and row['period'] == d['period_basis']

# The on-page catalog must be as complete and precise as the downloadable one.
catalog = json.loads((ROOT / 'downloads/definition-table.json').read_text())
assert catalog['schema_version'] == 1
readable = {(r['type'], r['key']): r for r in catalog['rows']}
assert len(readable) == len(catalog['rows']), 'Duplicate table row'
for row in readable.values():
    row['explanation'] = ' '.join(catalog['text'][i] for i in row['meaning'])
    assert row['name'] and row['category'] and row['explanation']
assert {key for kind, key in readable if kind == 'Attribute'} == keys
for key in keys:
    assert readable['Attribute', key]['explanation'] == by_key[key]['meaning'], key
    assert readable['Attribute', key]['unit'] == by_key[key]['unit'], key
for kind, collection in [('Dimension', 'dimensions'), ('Metric', 'metrics'), ('Category', 'categories'), ('Group', 'groups')]:
    assert {key for row_type, key in readable if row_type == kind} == set(meaning[collection])
    for key, description in meaning[collection].items():
        assert readable[kind, key]['explanation'] == description
for axis, details in meaning['axes'].items():
    assert readable['Classification axis', axis]['explanation'] == details['meaning']
    for value, description in details['values'].items():
        assert readable['Classification value', axis + '.' + value]['explanation'] == description
for key, description in meaning['supporting_schedule'].items():
    assert readable['Supporting field', 'supporting_schedule.' + key]['explanation'] == description
for key, description in meaning['analyses'].items():
    assert readable['Analysis section', 'analyses.' + key]['explanation'] == description
for kind, count in catalog['counts'].items():
    assert count == sum(row['type'] == kind for row in readable.values())
catalog_page = (ROOT / 'data-model/definition-catalog.mdx').read_text()
catalog_hash = hashlib.sha256((ROOT / 'downloads/definition-table.json').read_bytes()).hexdigest()[:16]
assert 'version="' + catalog_hash + '"' in catalog_page
assert 'data-model/definition-catalog' in (ROOT / 'docs.json').read_text()

spec = json.loads((ROOT / 'openapi/amlok.json').read_text())
schemas = spec['components']['schemas']
assert set(schemas['Dimension']['properties']['key']['enum']) == set(meaning['dimensions'])
assert set(schemas['Metric']['properties']['key']['enum']) == set(meaning['metrics'])
assert set(schemas['RiskPackage']['properties']['analyses']['properties']) == set(meaning['analyses'])
assert set(schemas['FinancialSupportingSchedule']['properties']) == set(meaning['supporting_schedule'])
assert len(meaning['supporting_schedule']) == 76
for key, description in meaning['supporting_schedule'].items():
    assert '`supporting_schedule.' + key + '`' in (ROOT / 'data-model/field-dictionary.mdx').read_text()
    assert description in (ROOT / 'data-model/field-dictionary.mdx').read_text()

metric_page = (ROOT / 'api-reference/underwriting-dimensions.mdx').read_text()
assert set(re.findall(r'^### (\w+)$', metric_page, re.M)) == set(meaning['metrics'])
for d in metrics['dimensions']:
    assert meaning['dimensions'][d['key']] in metric_page
for m in metrics['metrics']:
    assert meaning['metrics'][m['key']] in metric_page
    assert '**' + m['label'] + '** · `' + m['unit'] + '`' in metric_page
for k, v in meaning['categories'].items():
    page = (ROOT / 'data-model/transaction-category-dictionary.mdx').read_text()
    assert '`' + k + '`' in page and v in page

vf = json.loads((ROOT / 'downloads/verification-field-catalog.json').read_text())['fields']
assert len(vf) == 860
for f in vf.values():
    assert f['description'] and 'Preserve the source meaning' not in f['description']
    assert f['description'] in (ROOT / 'api-reference/verification-fields.mdx').read_text()
sf = json.loads((ROOT / 'downloads/data-model-field-catalog.json').read_text())['fields']
assert len(sf) == 981
for f in sf.values():
    assert f['description']
    assert not re.match(r'Read-only .* from the normalized record\.$', f['description']), f['path']

pages = ['api-reference/underwriting-dimensions.mdx', 'data-model/transaction-category-dictionary.mdx',
         'data-model/cross-system-attribute-dictionary.mdx', 'data-model/assessment-definitions.mdx']
nav = json.dumps(json.loads((ROOT / 'docs.json').read_text())['navigation'])
for name in pages:
    text = (ROOT / name).read_text()
    assert name[:-4] in nav, 'Page absent from navigation: ' + name
    assert text.startswith('---\n') and 'description:' in text
    assert '—' not in text and '–' not in text
    for target in re.findall(r'\]\((/[^)#]+)', text):
        assert (ROOT / target[1:]).is_file() or (ROOT / (target[1:] + '.mdx')).is_file(), (name, target)

# Semantic distinctions most likely to be lost in repetitive dictionary work.
assert 'not a credit limit or offer' in meaning['metrics']['debt_service_headroom']
assert 'not prove zero accrual revenue' in meaning['metrics']['zero_revenue_month_count']
assert 'not a relative growth rate' in meaning['metrics']['spending_to_receipts_change_90d']
assert 'not the amount of scheduled installments' in meaning['cross_system_attributes']['cross_system.debt.maturing_30d.observed_principal']
assert 'not expected loss' in meaning['cross_system_attributes']['cross_system.payments.open_dispute_exposure']
assert 'must not double count' in meaning['categories']['financing.debt_service.card']
print('Definition coverage passed: 24 dimensions, 184 metrics, 12,955 attributes, 327 categories, 45 groups, 10 axes, 14 analysis sections, 981 source fields and 860 verification fields.')
