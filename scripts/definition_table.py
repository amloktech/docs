"""Build the readable catalog from the same definitions used by downloads."""
import hashlib
import json
from collections import Counter


FAMILIES = {
    'ar': 'Accounts receivable', 'ap': 'Accounts payable', 'commerce': 'Commerce',
    'settlements': 'Settlements', 'payments': 'Payments and disputes',
    'inventory': 'Inventory', 'debt': 'Debt and installments',
    'subscriptions': 'Subscriptions', 'accounting': 'Accounting',
    'reconciliation': 'Reconciliation',
}


def write_definition_table(root, meaning, metrics, bank, cross, taxonomy):
    texts, text_ids, rows = [], {}, []

    def add(kind, key, name, category, explanation, unit='', context='', period=''):
        parts = explanation if isinstance(explanation, list) else [explanation]
        ids = []
        for text in parts:
            if not text:
                continue
            if text not in text_ids:
                text_ids[text] = len(texts)
                texts.append(text)
            ids.append(text_ids[text])
        rows.append({'type': kind, 'key': key, 'name': name, 'category': category,
                     'meaning': ids, 'unit': unit, 'context': context, 'period': period})

    dimensions = {d['key']: d['label'] for d in metrics['dimensions']}
    groups = {g['id']: g for g in taxonomy['groups']}
    categories = {c['id']: c for c in taxonomy['categories']}
    periods = {p['id']: p['label'] for p in bank['periods']}
    for d in metrics['dimensions']:
        add('Dimension', d['key'], d['label'], 'Underwriting dimensions', meaning['dimensions'][d['key']])
    for m in metrics['metrics']:
        add('Metric', m['key'], m['label'], dimensions[m['dimension_key']], meaning['metrics'][m['key']], m['unit'], ', '.join(m['borrower_types']))
    for d in cross['definitions']:
        family = FAMILIES[d['key'].split('.')[1]]
        label = d['key'].split('.', 2)[2].replace('_', ' ').replace('.', ' - ')
        add('Attribute', d['key'], label[0].upper() + label[1:], family, meaning['cross_system_attributes'][d['key']], d['unit'], 'Observed cross-system records', d['period_basis'].replace('_', ' '))
    for d in bank['definitions']:
        selector = bank['selectors'][d['selector']]
        kind, sid = selector['kind'], selector['id']
        selected = {'posted': 'all posted activity', 'external': 'explicitly external activity', 'unclassified': 'unclassified or conflicting activity'}.get(kind, selector['label'].lower())
        context = 'depository-account cash' if d['context'] == 'bank_cashflow' else 'issuer-card account activity'
        stat = bank['statistics'][d['statistic']]
        parts = [stat['label'] + ' for ' + d['direction'] + ' ' + context + ', selecting', selected + ',', 'over ' + periods[d['period']].lower() + '.']
        category = 'Transaction activity'
        if kind == 'category':
            parts.append(meaning['categories'][sid])
            category = groups[categories[sid]['parent_id']]['label']
        elif kind == 'group':
            parts.append(meaning['groups'][sid])
            category = groups[sid]['label']
        parts.append(meaning['statistics'][d['statistic']])
        if d['context'] == 'card_activity':
            parts.append('Card direction is account activity, not a second bank cash flow.')
        add('Attribute', d['key'], selector['label'] + ' / ' + stat['label'].lower(), category, parts, stat['unit'], ('Bank cash flow' if d['context'] == 'bank_cashflow' else 'Issuer-card activity') + ' / ' + d['direction'], periods[d['period']])
    for c in taxonomy['categories']:
        add('Category', c['id'], c['label'], groups[c['parent_id']]['label'], meaning['categories'][c['id']])
    for g in taxonomy['groups']:
        parent = groups.get(g.get('parent_id'), {}).get('label', 'Transaction groups')
        add('Group', g['id'], g['label'], parent, meaning['groups'][g['id']])
    for key, value in meaning['axes'].items():
        add('Classification axis', key, value['label'], 'Transaction classification', value['meaning'])
        for enum, description in value['values'].items():
            add('Classification value', key + '.' + enum, enum.replace('_', ' ').capitalize(), value['label'], description)
    for key, description in meaning['analyses'].items():
        add('Analysis section', 'analyses.' + key, key.replace('_', ' ').capitalize(), 'Supporting analyses', description)
    for key, description in meaning['supporting_schedule'].items():
        add('Supporting field', 'supporting_schedule.' + key, key.replace('_', ' ').capitalize(), 'Financial supporting schedule', description)

    # Reuse common explanation fragments so all keys can load together without
    # repeating the same category/statistic definition thousands of times.
    data = {'schema_version': 1, 'api_version': meaning['api_version'],
            'counts': dict(Counter(r['type'] for r in rows)),
            'text': texts, 'rows': rows}
    content = json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n'
    (root / 'downloads/definition-table.json').write_text(content)
    version = hashlib.sha256(content.encode()).hexdigest()[:16]
    (root / 'data-model/definition-catalog.mdx').write_text('''---
title: "Definition catalog"
description: "Read and search the meaning of every dimension, metric, financial attribute and transaction category in the AMLOK API."
keywords: [dimensions, metrics, attributes, categories, financial definitions, data dictionary]
icon: "table-list"
mode: "wide"
---

import { DefinitionTable } from "/snippets/definition-table.jsx";

Find a definition by name, API key or financial concept. Filter by **type** and **dimension or category** to see what each item represents, its unit and its applicable context. Every explanation is readable here; downloads are optional.

<DefinitionTable version="''' + version + '''" />

## Read the catalog

| Type | What it represents |
| --- | --- |
| Dimension | A family of related underwriting concepts, such as liquidity or repayment capacity. |
| Metric | One scalar underwriting measure within a dimension, with its stated unit. |
| Attribute | A detailed observation for a particular activity, source population or period. |
| Category | The supported economic purpose of a transaction. |
| Group | A collection of related transaction categories. Group totals overlap their leaf categories. |
| Classification axis or value | An independent perspective such as cash effect, account context or payment rail, and its allowed values. |
| Analysis section | Structured supporting observations within the risk package. |
| Supporting field | A financial-statement input used alongside the source evidence. |

Definitions describe the catalog, not the number of independent facts available for each borrower. Availability depends on evidence and coverage. Missing values are not zero. Money uses the returned currency; ratios use fractions or multiples, not percentage-formatted numbers.

For record schemas and other response fields, read the [source-field dictionary](/data-model/field-dictionary), [verification fields](/api-reference/verification-fields), [source-derived attributes](/data-model/derived-attributes) and [assessment glossary](/data-model/assessment-definitions). See [Financial attributes](/data-model/financial-attributes) for retrieval and coverage rules, or [Underwriting dimensions](/api-reference/underwriting-dimensions) for the metric reference.

## Optional downloads

- [Attribute dictionary (CSV)](https://raw.githubusercontent.com/amloktech/docs/main/downloads/financial-attribute-dictionary.csv): every detailed attribute key and its complete explanation.
- [Definition meanings (JSON)](/downloads/financial-definitions.json): dimension, metric, category, group, classification and supporting-field meanings.
- [Metric catalog (JSON)](/downloads/underwriting-metric-catalog.json) and [transaction taxonomy (JSON)](/downloads/transaction-taxonomy.json): technical definitions and allowed classifications.
''')

    # Put the reading view before retrieval instructions/downloads on existing pages.
    for name in ['data-model/financial-attributes.mdx', 'api-reference/underwriting-dimensions.mdx', 'data-model/transaction-category-dictionary.mdx', 'data-model/cross-system-attribute-dictionary.mdx', 'data-model/start-here.mdx']:
        path = root / name
        content = path.read_text()
        marker = '{/* READABLE DEFINITION CATALOG */}'
        block = marker + '\nBrowse the [searchable definition catalog](/data-model/definition-catalog) to read dimensions, metrics, attributes and categories in one table. Filter by type or business area; no download is required.\n\n'
        if marker not in content:
            end = content.index('\n---', 4) + 4
            content = content[:end] + '\n\n' + block + content[end:].lstrip()
        path.write_text(content)
