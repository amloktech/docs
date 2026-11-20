"""Validate the downloadable fictional metric examples against the public contract."""
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / 'downloads/sandbox-metric-coverage.json').read_text())
definitions = json.loads((ROOT / 'downloads/underwriting-metric-catalog.json').read_text())
catalog = json.loads((ROOT / 'data/sandbox-catalog.json').read_text())
schemas = json.loads((ROOT / 'openapi/amlok.json').read_text())['components']['schemas']
metrics = {metric['key']: metric for metric in definitions['metrics']}
dimensions = {dimension['key'] for dimension in definitions['dimensions']}
scenarios = {scenario['id'] for scenario in catalog['scenarios']}
fixtures = {fixture['id'] for fixture in catalog['businesses']}
statuses = {'available', 'unavailable', 'not_applicable'}
decimal = re.compile(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?')

assert set(report) == {'catalog_version', 'metric_catalog_version', 'fixture_observation_at',
                       'scope', 'expected_metric_count', 'covered_metric_count', 'uncovered',
                       'scenarios', 'metrics'}, 'Only public fixture metadata belongs in this download'
assert report['catalog_version'] in {'2026-11-19.3', catalog['version']}, 'Retained metric snapshot must identify its actual fixture version'
assert report['metric_catalog_version'] == definitions['version']
assert report['expected_metric_count'] == report['covered_metric_count'] == len(metrics)
assert report['uncovered'] == []
assert {metric['key'] for metric in report['metrics']} == set(metrics) == set(schemas['Metric']['properties']['key']['enum'])
assert len(report['metrics']) == len(metrics), 'Duplicate metric definitions'
datetime.fromisoformat(report['fixture_observation_at'].replace('Z', '+00:00'))

def context(value):
    assert value['fixture_id'] in fixtures and value['scenario_id'] in scenarios
    return value['scenario_id'], value['fixture_id'], value['case']

case_counts = {}
for case in report['scenarios']:
    assert set(case) == {'fixture_id', 'scenario_id', 'case', 'borrower_type', 'product', 'counts', 'dimensions'}
    key = context(case)
    assert key not in case_counts, 'Duplicate scenario summary'
    assert case['borrower_type'] in {'business', 'person'} and case['product'] in {'insights', 'signal'}
    assert set(case['counts']) == statuses and sum(case['counts'].values()) == len(metrics)
    assert all(isinstance(count, int) and count >= 0 for count in case['counts'].values())
    assert {dimension['key'] for dimension in case['dimensions']} == dimensions
    assert len(case['dimensions']) == len(dimensions)
    assert sum(dimension['available'] for dimension in case['dimensions']) == case['counts']['available']
    assert sum(dimension['total'] for dimension in case['dimensions']) == len(metrics)
    for dimension in case['dimensions']:
        assert set(dimension) == {'key', 'status', 'available', 'total'}
        assert dimension['status'] in statuses | {'partial'}
        assert 0 <= dimension['available'] <= dimension['total']
    case_counts[key] = 0

recommended = {('full_metric_coverage', 'maple-retail'), ('full_metric_coverage', 'cedar-software'),
               ('personal_income', 'maple-retail'), ('monitoring_metric_coverage', 'maple-retail')}
for metric in report['metrics']:
    assert set(metric) == {'key', 'label', 'dimension_key', 'examples'}
    definition = metrics[metric['key']]
    assert metric['label'] == definition['label'] and metric['dimension_key'] == definition['dimension_key']
    assert metric['examples'], 'A metric without a numeric example is not covered'
    assert any((example['scenario_id'], example['fixture_id']) in recommended for example in metric['examples'])
    seen = set()
    for example in metric['examples']:
        assert set(example) == {'fixture_id', 'scenario_id', 'case', 'value', 'unit', 'currency',
                                'supporting_input_count', 'evidence_count', 'window'}
        key = context(example)
        assert key in case_counts and key not in seen
        seen.add(key)
        case_counts[key] += 1
        assert decimal.fullmatch(example['value'])
        assert example['unit'] == definition['unit']
        assert example['currency'] is None or example['currency'] in {'CAD', 'USD'}
        assert example['supporting_input_count'] > 0 and example['evidence_count'] > 0
        assert set(example['window']) == {'start', 'end'}
        start, end = [datetime.fromisoformat(example['window'][part].replace('Z', '+00:00')) for part in ['start', 'end']]
        assert start < end

for case in report['scenarios']:
    assert case_counts[context(case)] == case['counts']['available'], 'Example totals must match scenario summaries'
for page in ['sandbox/sample-package.mdx', 'sandbox/businesses-and-scenarios.mdx', 'api-reference/sandbox-journeys.mdx']:
    text = (ROOT / page).read_text()
    assert '/downloads/sandbox-metric-coverage.json' in text
    assert 'scalar underwriting metrics' in text and '12,955 definitions' in text
assert '/downloads/sandbox-metric-coverage.json' in (ROOT / 'scripts/sandbox_guides.py').read_text()
print(json.dumps({'metrics': len(metrics), 'dimensions': len(dimensions), 'example_cases': len(case_counts),
                  'covered': report['covered_metric_count'], 'recommended_runs_cover_all': True,
                  'scope': 'fictional metric examples; no customer identifiers or source payloads'}))
