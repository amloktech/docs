#!/usr/bin/env python3
"""Validate SDK coverage and Python serialization/transport with synthetic data.

Usage: PYTHONPATH=<python dependencies> python scripts/test-sdks.py <build-dir>
The build directory contains the seven language source directories. No backend
requests are made. Build each compiled-language package separately.
"""
import ast
import importlib
import json
import re
import sys
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
build = Path(sys.argv[1]).resolve()
spec = json.loads((ROOT / "openapi/amlok-v1.json").read_text())
ops = {o["operationId"]: o for path in spec["paths"].values()
       for method, o in path.items() if method in ("get", "post", "put", "patch", "delete")}
for language in ("typescript", "python", "java", "csharp", "go", "php", "ruby"):
    index = json.loads((build / language / "operation-index.json").read_text())
    assert {o["operation_id"] for o in index} == set(ops), language
    assert len(index) == len(ops), language
print(f"All seven SDK operation indexes match {len(ops)} public operations")

sys.path.insert(0, str(build / "python"))
import amlok
import urllib3

api_client = amlok.ApiClient()
count = 0
for api_file in (build / "python/amlok/api").glob("*_api.py"):
    tree = ast.parse(api_file.read_text())
    for cls in [node for node in tree.body if isinstance(node, ast.ClassDef)]:
        for fn in cls.body:
            if not isinstance(fn, ast.FunctionDef) or not fn.name.endswith("_with_http_info"):
                continue
            operation = fn.name.removesuffix("_with_http_info").replace("_", "").upper()
            if operation not in ops:
                continue
            maps = [node for node in ast.walk(fn) if isinstance(node, ast.AnnAssign)
                    and isinstance(node.target, ast.Name) and node.target.id == "_response_types_map"]
            assert len(maps) == 1, operation
            response_types = ast.literal_eval(maps[0].value)
            for status, response in ops[operation]["responses"].items():
                if not status.startswith("2"):
                    continue
                for example in response.get("content", {}).get("application/json", {}).get("examples", {}).values():
                    typ = response_types[status]
                    api_client._ApiClient__deserialize(example["value"], typ)
                    count += 1
print(f"Python deserialized {count} documented success-response examples")

config = amlok.Configuration(host="https://fixture.invalid")
config.access_token = "synthetic-test-key"
client = amlok.ApiClient(config)
sample = spec["paths"]["/v1/configuration"]["get"]["responses"]["200"]["content"]["application/json"]["examples"]["synthetic"]["value"]
pool = Mock()
pool.request.return_value = urllib3.HTTPResponse(body=json.dumps(sample).encode(), status=200,
                                               headers={"Content-Type": "application/json"})
client.rest_client.pool_manager = pool
result = amlok.PlatformApi(client).i_r007(_request_timeout=30)
assert result.data.workspace_id == "wsp_example"
args, kwargs = pool.request.call_args
assert "https://fixture.invalid/v1/configuration" in args
assert kwargs["headers"]["Authorization"] == "Bearer synthetic-test-key"
assert kwargs["redirect"] is False and kwargs["retries"] is False
assert pool.request.call_count == 1

pool.reset_mock()
pool.request.return_value = urllib3.HTTPResponse(body=b'{"error":{"code":"unauthenticated","message":"fixture"}}', status=401,
                                               headers={"Content-Type": "application/json", "X-Request-ID": "req_fixture"})
try:
    amlok.PlatformApi(client).i_r007(_request_timeout=30)
    raise AssertionError("401 was accepted")
except amlok.ApiException as error:
    assert error.status == 401
    assert error.headers["X-Request-ID"] == "req_fixture"
assert pool.request.call_count == 1
assert amlok.Money(amount="1234.50", currency="CAD").amount == "1234.50"
print("Python auth, path, error headers, no redirects/retries and decimal-string checks passed")
