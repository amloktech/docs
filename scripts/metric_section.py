"""Add a derived, independently paged metric view without changing stored packages."""
from copy import deepcopy


def extend(spec, fixtures):
    schemas = spec['components']['schemas']
    dimension = schemas['Dimension']
    entry = {
        'type': 'object',
        'properties': {
            'dimension_key': deepcopy(dimension['properties']['key']),
            'dimension_status': deepcopy(dimension['properties']['status']),
            'metric': {'$ref': '#/components/schemas/Metric'},
        },
        'required': ['dimension_key', 'dimension_status', 'metric'],
        'additionalProperties': False,
        'description': 'One unchanged metric from the immutable package, with its parent dimension key and status. A derived view of dimensions[].metrics, not a new stored assessment or calculation.',
    }
    entry['properties']['dimension_status']['description'] = 'Availability of the complete parent dimension, not only this metric or page.'
    entry['allOf'] = [
        {'if': {'properties': {'dimension_key': deepcopy(rule['if']['properties']['key'])}},
         'then': {'properties': {'metric': deepcopy(rule['then']['properties']['metrics']['items'])}}}
        for rule in dimension.get('allOf', [])
        if 'key' in rule.get('if', {}).get('properties', {})
        and 'metrics' in rule.get('then', {}).get('properties', {})
    ]
    schemas['RiskMetricEntry'] = entry
    section = deepcopy(schemas['RiskSectionDimensions'])
    section['properties']['section'] = {'const': 'metrics'}
    section['properties']['items']['items'] = {'$ref': '#/components/schemas/RiskMetricEntry'}
    section['description'] = 'Metrics flattened in original dimension order and then original metric order. All fields, evidence, unavailable values and missing reasons are preserved.'
    schemas['RiskSectionMetrics'] = section
    spec['x-risk-package-sections']['metrics'] = {
        'items': {'$ref': '#/components/schemas/RiskMetricEntry'}, 'metadata_schema': None,
    }
    union = schemas['RiskPackageSection']
    reference = {'$ref': '#/components/schemas/RiskSectionMetrics'}
    if reference not in union['oneOf']:
        union['oneOf'].append(reference)
    union['discriminator']['mapping']['metrics'] = reference['$ref']

    operation = spec['paths']['/v1/risk-packages/{id}']['get']
    parameter = next(p for p in operation['parameters'] if p['name'] == 'section')
    if 'metrics' not in parameter['schema']['enum']:
        parameter['schema']['enum'].append('metrics')
    operation['description'] += ' Use section=metrics to page individual metrics with their parent dimension key/status when a whole dimension is too large; begin with limit=1 and follow page.next_cursor. This derived view preserves every metric field and does not add a metrics field to stored RiskPackage objects or full exports.'

    summary_sections = schemas['RiskPackageSummary']['properties']['sections']
    names = summary_sections['items']['properties']['section']['enum']
    if 'metrics' not in names:
        names.append('metrics')
    summary_sections['minItems'] = summary_sections['maxItems'] = len(names)
    package = fixtures['RiskPackage']
    entries = [dict(dimension_key=d['key'], dimension_status=d['status'], metric=deepcopy(m))
               for d in package['dimensions'] for m in d['metrics']]
    views = operation['responses']['200']['content']['application/json']['x-response-views']
    view = deepcopy(views['dimensions'])
    view['title'] = 'metrics (view=section)'
    view['schema']['properties']['data'] = reference
    view['example']['data'].update(section='metrics', section_metadata=None,
                                  items=entries[:1], total_items=len(entries))
    view['example']['page'].update(next_cursor='cursor_metrics_synthetic' if len(entries) > 1 else None,
                                  has_more=len(entries) > 1)
    views['metrics'] = view
    counts = views['summary']['example']['data']['sections']
    counts[:] = [row for row in counts if row['section'] != 'metrics']
    counts.append(dict(section='metrics', item_count=len(entries)))
    spec['x-contract-revision'] = '2026-11-19.metric-sections.1'
