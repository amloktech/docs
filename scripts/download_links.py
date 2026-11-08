"""Keep public download links on hosts that serve their file types."""
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
RAW_BASE = 'https://raw.githubusercontent.com/amloktech/docs/main'
LINK = re.compile(r'''(?P<prefix>\]\(|\bhref\s*=\s*["'])(?P<url>[^\s)"']+)''')
EXCLUDED = {'.git', 'node_modules', 'artifacts', 'data', 'drafts', 'implementation', 'scripts'}


def public_pages(root=ROOT):
    return sorted(path for path in root.rglob('*.mdx')
                  if not EXCLUDED.intersection(path.relative_to(root).parts))


def download_path(url):
    """Recognize docs downloads without touching product API capability URLs."""
    if url.startswith(RAW_BASE + '/downloads/'):
        return urlsplit(url[len(RAW_BASE):]).path
    parts = urlsplit(url)
    if (not parts.netloc or parts.netloc == 'docs.amlok.io') and parts.path.startswith('/downloads/'):
        return parts.path
    return None


def normalize_download_links(root=ROOT):
    # JSON is served by Mintlify. Other linked downloads use the public source
    # repository: several extensions are unsupported or require Enterprise.
    external = set()

    def replace(match):
        url = match['url']
        path = download_path(url)
        if not path or Path(path).suffix == '.json':
            return match[0]
        if not (root / path.lstrip('/')).is_file():
            raise FileNotFoundError(f'Download target does not exist: {path}')
        external.add(path)
        if url.startswith(RAW_BASE + '/'):
            return match[0]
        parts = urlsplit(url)
        suffix = ('?' + parts.query if parts.query else '') + ('#' + parts.fragment if parts.fragment else '')
        return match['prefix'] + RAW_BASE + path + suffix

    for page in public_pages(root):
        before = page.read_text()
        after = LINK.sub(replace, before)
        if after != before:
            page.write_text(after)

    return external


if __name__ == '__main__':
    print(f'Normalized {len(normalize_download_links())} public download targets.')
