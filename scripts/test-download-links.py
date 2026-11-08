"""Catch hosted-asset regressions after the canonical guide generator runs."""
from pathlib import Path
from tempfile import TemporaryDirectory

from download_links import LINK, RAW_BASE, ROOT, download_path, normalize_download_links, public_pages


def audit(root):
    external, json_targets = set(), set()
    for page in public_pages(root):
        for match in LINK.finditer(page.read_text()):
            url = match['url']
            path = download_path(url)
            if not path:
                continue
            assert (root / path.lstrip('/')).is_file(), (page, path, 'missing download')
            if Path(path).suffix == '.json':
                assert not url.startswith(RAW_BASE), (page, url, 'JSON should remain on the docs host')
                json_targets.add(path)
            else:
                assert url.startswith(RAW_BASE + '/downloads/'), (page, url, 'unsupported same-host download')
                external.add(path)
    return external, json_targets


# Exercise a newly generated page, including future file types, HTML links,
# query/anchor preservation, JSON exceptions and unrelated API capabilities.
with TemporaryDirectory() as directory:
    root = Path(directory)
    (root / 'downloads').mkdir()
    for name in ['client.mjs', 'report.csv', 'next-client.py', 'inputs.json']:
        (root / 'downloads' / name).write_text('fixture')
    page = root / 'generated.mdx'
    page.write_text('''[Client](/downloads/client.mjs)
<a href="https://docs.amlok.io/downloads/report.csv?download=1#rows">Report</a>
[Future helper](/downloads/next-client.py)
[Inputs](/downloads/inputs.json)
[Capability](https://api.amlok.io/downloads/synthetic-download-token)
''')
    normalize_download_links(root)
    external, json_targets = audit(root)
    assert len(external) == 3 and len(json_targets) == 1
    assert RAW_BASE + '/downloads/report.csv?download=1#rows' in page.read_text()
    assert 'https://api.amlok.io/downloads/synthetic-download-token' in page.read_text()
    before = page.read_bytes()
    normalize_download_links(root)
    assert page.read_bytes() == before, 'normalization is not stable'
    page.write_text(page.read_text().replace(RAW_BASE + '/downloads/client.mjs', '/downloads/client.mjs'))
    try:
        audit(root)
    except AssertionError as error:
        assert 'unsupported same-host download' in str(error)
    else:
        raise AssertionError('The audit accepted a regressed generated download link')

external, json_targets = audit(ROOT)
assert external, 'No source-hosted downloads were audited'
assert json_targets, 'No same-host JSON downloads were audited'
print(f'Download links passed: {len(external)} public source downloads, {len(json_targets)} same-host JSON targets; normalization is stable and rejects regressions.')
