"""Bounded AMLOK paging and resumable export helpers (Python standard library).

Supply an authenticated API callback for JSON operations. Never send its bearer key
in fetch_part: signed export URLs are separate capabilities. No network calls run
on import. Keep the private checkpoint directory access-restricted.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import re
import urllib.request
from urllib.parse import urlparse


def consume_pages(fetch_page, commit_page, cursor=None):
    """commit_page(items, page) must atomically save effects and the next cursor.

    fetch_page(cursor) must retain original resource/filter/section parameters.
    Errors (including 410/413) propagate; no implicit snapshot restart occurs.
    """
    seen = set()
    snapshot = None
    while True:
        response = fetch_page(cursor)
        page = response['page']
        if snapshot is None:
            snapshot = page['snapshot_id']
        if page['snapshot_id'] != snapshot:
            raise ValueError('Snapshot changed within a cursor chain')
        data = response['data']
        items = data['items'] if isinstance(data, dict) else data
        next_cursor = page['next_cursor']
        if page['has_more'] and (not items or not next_cursor or next_cursor == cursor or next_cursor in seen):
            raise ValueError('Cursor chain did not make progress')
        if not page['has_more'] and next_cursor is not None:
            raise ValueError('Terminal page unexpectedly has a next cursor')
        commit_page(items, page)
        if not page['has_more']:
            return
        seen.add(next_cursor)
        cursor = next_cursor


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_part(link, offset):
    """Read bounded chunks from a signed capability; redirects are forbidden."""
    parsed = urlparse(link['url'])
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ValueError('Expected an HTTPS download capability without credentials or fragment')
    headers = {'Accept-Encoding': 'identity', 'If-Match': link['etag']}
    if offset:
        headers['Range'] = 'bytes=%d-' % offset
    request = urllib.request.Request(link['url'], headers=headers)
    with urllib.request.build_opener(NoRedirect).open(request, timeout=30) as response:
        if response.headers.get('ETag') != link['etag']:
            raise ValueError('Part ETag changed')
        if offset:
            expected = 'bytes %d-%d/%d' % (offset, link['byte_length']-1, link['byte_length'])
            if response.status != 206 or response.headers.get('Content-Range') != expected:
                raise ValueError('Unsafe range response; restart this part instead of appending')
        elif response.status != 200:
            raise ValueError('Expected a complete part response')
        encoding = response.headers.get('Content-Encoding', 'identity')
        if encoding != 'identity':
            raise ValueError('Compressed transfer cannot preserve byte offsets')
        while True:
            chunk = response.read(65536)
            if not chunk:
                break
            yield chunk


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(65536), b''):
            digest.update(chunk)
    return digest.hexdigest()


def download_export(artifact, issue_link, destination, checkpoint_dir, read_part=fetch_part):
    """issue_link(part_number) returns authorized ExportDownloadLink data.

    On network interruption, invoke again with the same artifact/checkpoint directory.
    Links are never stored. Complete part hashes and the final hash are verified.
    Successful completion keeps checkpoint parts until the caller removes them.
    """
    size, total, count = (artifact[k] for k in ['part_size_bytes','total_bytes','part_count'])
    if not all(type(v) is int and v > 0 for v in [size,total,count]) or count != (total+size-1)//size:
        raise ValueError('Invalid artifact layout')
    directory = Path(checkpoint_dir)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    state_path = directory/'artifact.json'
    identity = {k:artifact[k] for k in ['id','sha256','total_bytes','part_count','part_size_bytes']}
    if state_path.exists() and json.loads(state_path.read_text()) != identity:
        raise ValueError('Checkpoint belongs to a different artifact')
    if not state_path.exists():
        temp = directory/'artifact.json.tmp'
        temp.write_text(json.dumps(identity)); os.chmod(temp, 0o600); os.replace(temp,state_path)
    for number in range(1,count+1):
        link = issue_link(number)
        expected_size = min(size,total-(number-1)*size)
        if (link['artifact_id'] != artifact['id'] or link['part_number'] != number or
                link['byte_offset'] != (number-1)*size or link['byte_length'] != expected_size or
                not re.fullmatch('[a-f0-9]{64}',link['sha256'])):
            raise ValueError('Part metadata does not match the artifact')
        part = directory/('%08d.part' % number)
        offset = part.stat().st_size if part.exists() else 0
        if offset > expected_size:
            raise ValueError('Local part exceeds expected length')
        if offset < expected_size:
            with part.open('ab') as stream:
                os.chmod(part,0o600)
                for chunk in read_part(link,offset):
                    if not isinstance(chunk,bytes) or offset+len(chunk) > expected_size:
                        raise ValueError('Part exceeds its declared size')
                    stream.write(chunk); offset+=len(chunk)
                stream.flush(); os.fsync(stream.fileno())
        if offset != expected_size:
            raise IOError('Interrupted part: retry with the same checkpoint directory')
        if file_hash(part) != link['sha256']:
            part.unlink()  # Only this helper's corrupt temporary part, never the destination.
            raise ValueError('Part checksum mismatch; retry this part from byte zero')
    destination = Path(destination)
    temporary = destination.with_name(destination.name+'.amlok-partial')
    digest = hashlib.sha256()
    with temporary.open('wb') as stream:
        os.chmod(temporary,0o600)
        for number in range(1,count+1):
            with (directory/('%08d.part' % number)).open('rb') as part:
                for chunk in iter(lambda: part.read(65536),b''):
                    stream.write(chunk);digest.update(chunk)
        stream.flush();os.fsync(stream.fileno())
    if digest.hexdigest()!=artifact['sha256']:
        temporary.unlink()
        raise ValueError('Complete artifact checksum mismatch')
    os.replace(temporary,destination)
    return destination
