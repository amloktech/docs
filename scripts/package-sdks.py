#!/usr/bin/env python3
"""Package a validated build-sdks.py output directory into deterministic ZIPs."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
build = Path(sys.argv[1]).resolve()
source_ref = sys.argv[2] if len(sys.argv) > 2 else "main"
destination = ROOT / "downloads/sdks"
destination.mkdir(parents=True, exist_ok=True)
languages = ("typescript", "python", "java", "csharp", "go", "php", "ruby")
excluded = {"node_modules", "target", "bin", "obj", "__pycache__", ".git", ".openapi-generator", ".pytest_cache", "build"}
manifest = {"sdk_version": "1.4.2", "api_version": "1.4.2", "generator_version": "7.17.0", "packages": []}
for language in languages:
    directory = build / language
    metadata = json.loads((directory / "BUILD.json").read_text())
    assert metadata["api_version"] == "1.4.2"
    assert metadata["contract_sha256"] == hashlib.sha256((ROOT / "openapi/amlok-v1.json").read_bytes()).hexdigest()
    name = f"amlok-{language}-1.4.2"
    target = destination / (name + ".zip")
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for file in sorted(directory.rglob("*")):
            relative = file.relative_to(directory)
            if not file.is_file() or excluded.intersection(relative.parts):
                continue
            if any(part.endswith(".egg-info") for part in relative.parts):
                continue
            if file.name in ("contract_fixtures_test.go", ".DS_Store") or file.suffix in (".pyc", ".log"):
                continue
            info = zipfile.ZipInfo(str(Path(name) / relative), date_time=(2026, 11, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, file.read_bytes())
    manifest["packages"].append({
        "language": language, "repository_path": "downloads/sdks/" + target.name,
        "download_url": f"https://raw.githubusercontent.com/amloktech/docs/{source_ref}/downloads/sdks/{target.name}",
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "bytes": target.stat().st_size,
        "operations": metadata["operations"], "contract_sha256": metadata["contract_sha256"],
    })
    print(language, target.stat().st_size, "bytes")
(destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
