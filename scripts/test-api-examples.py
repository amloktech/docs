"""Exercise the downloadable signature helpers and syntax-check public samples."""
import ast
import hashlib
import hmac
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
module_spec = importlib.util.spec_from_file_location('verify_webhook', ROOT/'downloads/verify_webhook.py')
verifier = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(verifier)
NOW = 1792764000
SECRET = 'whsec_synthetic_test_only'
BODY = '{"id":"evt_test","type":"sync.completed","resource_id":"sync_test","resource_version":2,"data":{"label":"Café"}}'

def header(body=BODY, timestamp=NOW, secret=SECRET):
    digest = hmac.new(secret.encode(), (str(timestamp)+'.'+body).encode(), hashlib.sha256).hexdigest()
    return f't={timestamp},v1={digest}'

cases = []
def case(name, valid, body=BODY, signature=None, secret=SECRET, now=NOW):
    cases.append(dict(name=name,valid=valid,body=body,header=signature or header(body),secret=secret,now=now))

case('valid UTF-8 raw body', True)
case('multiple signatures with one valid digest', True, signature=header()+',v1='+'0'*64)
case('timestamp boundary', True, now=NOW+300)
case('tampered raw body', False, body=BODY+' ', signature=header())
case('wrong secret', False, secret='wrong')
case('empty secret', False, secret='')
case('expired timestamp', False, now=NOW+301)
case('future timestamp', False, now=NOW-301)
case('duplicate timestamp', False, signature=header()+f',t={NOW}')
case('malformed digest', False, signature=f't={NOW},v1=zz')
case('missing digest', False, signature=f't={NOW}')
case('malformed header', False, signature='malformed')
case('signed invalid JSON', False, body='{bad-json')
case('signed non-object envelope', False, body='[]')
case('signed missing event ID', False, body='{"type":"sync.completed","resource_id":"sync_test","resource_version":2}')
case('signed boolean version', False, body='{"id":"evt_test","type":"sync.completed","resource_id":"sync_test","resource_version":true}')

for item in cases:
    accepted = False
    try:
        event = verifier.verify_webhook(item['body'].encode(),item['header'],item['secret'],item['now'])
        accepted = event['id'] == 'evt_test'
    except (ValueError, TypeError):
        pass
    assert accepted == item['valid'], 'Python: '+item['name']

counts = {'webhookCasesPerLanguage':len(cases),'javascriptSamples':0,'shellSamples':0,'guideCodeBlocks':0}
with tempfile.TemporaryDirectory(prefix='amlok-api-tests-') as temp:
    temp = Path(temp)
    (temp/'cases.json').write_text(json.dumps(cases))
    runner = temp/'verify.mjs'
    runner.write_text('import { readFileSync } from "node:fs";\nimport assert from "node:assert/strict";\nimport { verifyWebhook } from '+json.dumps((ROOT/'downloads/verify-webhook.mjs').as_uri())+';\n'+'''
const cases = JSON.parse(readFileSync(new URL('./cases.json', import.meta.url)));
for (const c of cases) {
  let accepted = false;
  try { accepted = verifyWebhook(Buffer.from(c.body), c.header, c.secret, c.now).id === 'evt_test'; } catch {}
  assert.equal(accepted, c.valid, c.name);
}
''')
    subprocess.run(['node',str(runner)],check=True)

    def check_sample(language, code):
        if language in ['JavaScript','javascript']:
            target=temp/'sample.mjs';target.write_text(code)
            subprocess.run(['node','--check',str(target)],check=True,capture_output=True)
            counts['javascriptSamples']+=1
        elif language in ['Shell','bash']:
            subprocess.run(['bash','-n'],input=code,text=True,check=True,capture_output=True)
            counts['shellSamples']+=1
        elif language=='python': ast.parse(code)
        elif language=='json': json.loads(code)

    spec=json.loads((ROOT/'openapi/amlok-v1.json').read_text())
    for methods in spec['paths'].values():
        for operation in methods.values():
            for sample in operation['x-codeSamples']: check_sample(sample['lang'],sample['source'])
    for page in (ROOT/'api-reference').glob('*.mdx'):
        text=page.read_text()
        assert '@@EP' not in text, page
        for language,code in re.findall(r'```(\w+)\n(.*?)\n```',text,re.S):
            check_sample(language,code);counts['guideCodeBlocks']+=1

collection=json.loads((ROOT/'downloads/amlok-api.postman_collection.json').read_text())
assert sum(len(group['item']) for group in collection['item'])==sum(len(methods) for methods in spec['paths'].values())
variables={item['key']:item['value'] for item in collection['variable']}
assert variables['api_key']=='' and variables['base_url']==''
pages=list((ROOT/'api-reference').rglob('*.mdx'))
index=json.loads((ROOT/'data/api-reference-index.json').read_text())
assert len(pages)==len(index)+21
assert all('\u2014' not in page.read_text() for page in pages)
(ROOT/'artifacts/api-code-validation.json').write_text(json.dumps(counts,indent=2)+'\n')
print(json.dumps(counts))
