"""Render verified provider refresh guidance for Active catalog entries only."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / 'data/integration-status.json').read_text())['integrations']
profiles = json.loads((ROOT / 'data/integration-refresh.json').read_text())['integrations']
active = {item['id']: item for item in catalog if item['status'] == 'Active'}
by_id = {item['id']: item for item in profiles}
if len(by_id) != len(profiles) or set(active) != set(by_id):
    raise ValueError('Refresh profiles must match Active integration IDs exactly, without duplicates.')
start = '{/* BEGIN PROVIDER REFRESH */}'
end = '{/* END PROVIDER REFRESH */}'
pattern = re.compile(re.escape(start) + r'.*?' + re.escape(end) + r'\n*', re.S)
for item in catalog:
    path = ROOT / (item['href'].lstrip('/') + '.mdx')
    content = path.read_text()
    if item['id'] not in active:
        if start in content:
            content = pattern.sub('', content)
            content = re.sub(r'^\| Refresh \|.*$', '| Refresh | Provider-dependent; no guaranteed real-time cadence. |', content, flags=re.M)
            path.write_text(content)
        continue
    profile = by_id[item['id']]
    if not profile['sources'] or any(not source['url'].startswith('https://') for source in profile['sources']):
        raise ValueError('Official HTTPS sources are required: ' + item['id'])
    sources = ', '.join(f"[{source['title']}]({source['url']})" for source in profile['sources'])
    block = f"""{start}
## Data refresh

**Provider update cadence:** {profile['cadence']}

{profile['method']}

{profile['conditions']}

**AMLOK synchronization:** The enabled refresh mode and schedule are agreed for your connection. Provider timing describes upstream capability; allow for retrieval and processing before changes appear in AMLOK. See [data refresh and freshness](/integrations/data-refresh).

Provider references: {sources}.
{end}

"""
    if start in content:
        content = pattern.sub(lambda _: block, content)
    else:
        content = content.replace('## Data reference\n', block + '## Data reference\n', 1)
    content = re.sub(r'^\| Refresh \|.*$', '| Refresh | ' + profile['cadence'] + ' [Details](#data-refresh). |', content, flags=re.M)
    path.write_text(content)

page = '''---
title: "Data refresh"
description: "Provider update capabilities and data freshness for Active AMLOK integrations."
---

Data freshness depends on when a source publishes a change, how its API exposes it, and when the configured AMLOK synchronization retrieves and processes it. This guide covers **Active integrations**, including those marked **Beta** in the [integration status catalog](/integrations/status).

<Note>
The timings below describe **provider capabilities**. Your AMLOK refresh mode and schedule are agreed for the connection, product, and workflow. A provider's typical interval or webhook timing is not an AMLOK delivery SLA.
</Note>

## How updates reach AMLOK

| Update method | What it means |
| --- | --- |
| Event notifications | A supported source change triggers a webhook. The event may prompt a resource read; delivery and processing can take time. |
| Scheduled source refresh | The provider refreshes its own copy of institution data on a schedule. AMLOK can retrieve the latest successful result. |
| Scheduled API reads | A configured synchronization checks the API periodically. Reading an API more often does not necessarily refresh its upstream data. |
| On-demand or workflow-based | An authorized request, desktop connector, or decision workflow initiates an exchange. Permissions, user interaction, and provider restrictions still apply. |

## Provider refresh capabilities

Open an integration for its scope, requirements, and detailed refresh notes. Official provider references are linked in each row.

'''
categories = ['Payments and POS', 'Ecommerce', 'Accounting', 'Inventory and ERP', 'Bank Integrations', 'Lender Systems']
for category in categories:
    page += '### ' + category + '\n\n| Integration | Provider update cadence | Official reference |\n| --- | --- | --- |\n'
    for item in catalog:
        if item['id'] in active and item['category'] == category:
            p = by_id[item['id']]
            page += f"| [{item['name']}]({item['href']}#data-refresh) | {p['cadence']} | [Provider documentation]({p['sources'][0]['url']}) |\n"
    page += '\n'
page += '''## Agree the synchronization schedule

During onboarding, identify the resources needed for Insights and Signal, the available source update method, the synchronization schedule, and any allowed on-demand refreshes. Include provider entitlements, API quotas, customer consent, and any desktop or institution configuration.

For event-based connections, include periodic reconciliation where the provider supports it. For scheduled bank connections, align retrieval with completed source refreshes. Additional upstream refreshes may require a provider entitlement or fee and may be restricted to specific business cases.

## Interpret freshness correctly

- Check the last **successful** source refresh and synchronization, rather than the time a request was submitted.
- Treat pending transactions, later postings, reversals, refunds, and corrections as changes that can arrive after the original record.
- Reconnection, expired consent, MFA, outages, and throttling can delay updates. A successful read of cached data does not prove that the source refreshed.
- Different resources from the same provider can have different update paths. An invoice webhook does not establish the freshness of a bank balance or financial report.

Use the provider-specific notes when choosing a freshness requirement for an underwriting or monitoring workflow.
'''
(ROOT / 'integrations/data-refresh.mdx').write_text(page)
config_path = ROOT / 'docs.json'
config = json.loads(config_path.read_text())
group = next(g for t in config['navigation']['tabs'] if t['tab'] == 'Documentation' for g in t['groups'] if g['group'] == 'Integrations')
group['pages'] = [p for p in group['pages'] if p != 'integrations/data-refresh']
group['pages'].insert(group['pages'].index('integrations/status') + 1, 'integrations/data-refresh')
config_path.write_text(json.dumps(config, indent=2) + '\n')
print(f'Rendered refresh guidance for {len(active)} Active integrations and the shared guide.')
