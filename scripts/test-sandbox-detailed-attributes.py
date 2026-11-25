"""Check scenario discoverability and preserve existing public read contracts."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / 'data/sandbox-catalog.json').read_text())
spec = json.loads((ROOT / 'openapi/amlok.json').read_text())
schemas = spec['components']['schemas']
assert catalog['version'] == '2026-11-25.1'
assert len(catalog['businesses']) == 6
assert len(catalog['scenarios']) == len({s['id'] for s in catalog['scenarios']}) == 39
scenario = next(s for s in catalog['scenarios'] if s['id'] == 'detailed_attribute_coverage')
assert scenario['category'] == 'Underwriting'
assert scenario['required_products'] == ['insights']
assert scenario['owner_only'] is False and scenario['requires_endpoint'] is False
assert scenario['required_scopes'] == next(s for s in catalog['scenarios'] if s['id'] == 'full_metric_coverage')['required_scopes']
assert json.loads((ROOT / 'downloads/sandbox-scenarios.json').read_text()) == catalog
catalog_response = spec['paths']['/v1/sandbox/catalog']['get']['responses']['200']['content']['application/json']
assert catalog_response['example']['data'] == catalog

schema = schemas['CreateSandboxRunRequest']
assert set(schema['properties']['scenario_id']['enum']) == {s['id'] for s in catalog['scenarios']}
for fixture in catalog['businesses']:
    command = {'scenario_id': scenario['id'], 'fixture_id': fixture['id'], 'catalog_version': catalog['version']}
    Draft202012Validator(schema).validate(command)
    assert not Draft202012Validator(schema).is_valid({**command, 'catalog_version': '2026-11-19.3'})

# Saved historical runs remain readable; only new commands pin the current catalog.
assert schemas['SandboxRun']['properties']['catalog_version']['type'] == 'string'
assert 'const' not in schemas['SandboxRun']['properties']['catalog_version']
for field in ['created_at', 'first_opened_at', 'completed_at', 'cancelled_at']:
    assert field in schemas['EmbeddingSession']['properties'], f'Hub lifecycle field lost: {field}'
assert len(spec['x-risk-package-sections']) == 52
assert spec['x-risk-package-sections']['metrics']['items']['$ref'].endswith('/RiskMetricEntry')
assert len(schemas['Metric']['properties']['key']['enum']) == 184
assert 'metrics' not in schemas['RiskPackage']['properties'], 'Paged metrics are a derived view, not duplicated storage'
metric_snapshot = json.loads((ROOT / 'downloads/sandbox-metric-coverage.json').read_text())
assert metric_snapshot['catalog_version'] == '2026-11-19.3', 'Do not relabel historical test evidence'
assert metric_snapshot['covered_metric_count'] == 184
coverage = json.loads((ROOT / 'downloads/sandbox-attribute-coverage.json').read_text())
summary = json.loads((ROOT / 'downloads/sandbox-attribute-coverage-summary.json').read_text())
assert coverage['complete'] and summary['complete']
assert coverage['fixture_catalog_version'] == summary['fixture_catalog_version'] == '2026-11-19.4', 'Preserve the measured historical coverage version'
assert coverage['fixture_observation_at'] == summary['fixture_observation_at']
assert len(coverage['attributes']) == len({a['key'] for a in coverage['attributes']}) == 12955
assert len(coverage['scenarios']) == len(summary['scenarios']) == 21
counts = summary['current']
assert (counts['nonzero'], counts['zero_only'], counts['unavailable_everywhere']) == (9339, 2719, 897)
assert counts['numeric_including_zero'] == counts['nonzero'] + counts['zero_only'] == 12058
assert counts['definitions'] == counts['numeric_including_zero'] + counts['unavailable_everywhere']
assert summary['catalogs']['cross_system']['nonzero'] == 150
for outcome in ['nonzero', 'zero_only', 'unavailable_everywhere']:
    assert sum(a['coverage'] == outcome for a in coverage['attributes']) == counts[outcome] == coverage['totals'][outcome]
for attribute in coverage['attributes']:
    assert len(attribute['observations']) == len(coverage['scenarios'])
    for value in attribute['examples'].values():
        assert 0 <= value['case'] < len(coverage['scenarios'])
for path in ['sandbox/sample-package.mdx', 'api-reference/sandbox-journeys.mdx',
             'sandbox/businesses-and-scenarios.mdx', 'console/sandbox.mdx', 'data-model/financial-attributes.mdx']:
    text = (ROOT / path).read_text()
    assert 'detailed_attribute_coverage' in text or 'Detailed financial attributes' in text
    assert '35 complete months' in text
    assert text.count('BEGIN DETAILED ATTRIBUTE SCENARIO') == 1
print(json.dumps({'scenarios': 39, 'fixtures': 6, 'catalog_version': catalog['version'],
                  'saved_metric_snapshot': metric_snapshot['catalog_version'],
                  'hub_timestamps': 4, 'risk_sections': 52, 'scalar_metrics': 184}))
