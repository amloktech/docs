#!/usr/bin/env python3
"""Build versioned SDK source archives without changing the public API contract.

Requires Java and the OpenAPI Generator 7.17.0 JAR. Build tools and downloaded
dependencies belong outside the docs repository. See --help for paths.
"""
import argparse
import copy
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = "7.17.0"
VERSION = "1.4.2"
TARGETS = {
    "typescript": ("typescript-fetch", {
        "npmName": "@amlok/api-client", "npmVersion": VERSION,
        "supportsES6": True, "withInterfaces": True, "withoutRuntimeChecks": True,
    }),
    "python": ("python", {"packageName": "amlok", "packageVersion": VERSION, "library": "urllib3"}),
    "java": ("java", {
        "groupId": "io.amlok", "artifactId": "amlok-api-client", "artifactVersion": VERSION,
        "apiPackage": "io.amlok.api", "modelPackage": "io.amlok.model", "invokerPackage": "io.amlok",
        "library": "native", "serializationLibrary": "jackson", "dateLibrary": "java8",
    }),
    "csharp": ("csharp", {"packageName": "Amlok", "packageVersion": VERSION,
                             "targetFramework": "net8.0", "library": "httpclient", "nullableReferenceTypes": True}),
    "go": ("go", {"packageName": "amlok", "packageVersion": VERSION, "enumClassPrefix": True}),
    "php": ("php", {"invokerPackage": "Amlok", "packageName": "Amlok",
                       "composerPackageName": "amlok/api-client", "artifactVersion": VERSION}),
    "ruby": ("ruby", {"gemName": "amlok-api-client", "moduleName": "Amlok", "gemVersion": VERSION,
                         "gemAuthor": "AMLOK", "gemAuthorEmail": "support@amlok.tech", "library": "faraday"}),
}


def generator_input(source):
    """Adapt schema syntax for generator compatibility, never the wire contract.

    JSON Schema conditionals remain authoritative in the published 3.1 spec;
    generated language types are not a substitute for full schema validation.
    Webhooks describe incoming deliveries and must not become outbound methods.
    """
    def adapt(value):
        if isinstance(value, list):
            return [adapt(x) for x in value]
        if not isinstance(value, dict):
            return value
        d = {k: adapt(v) for k, v in value.items() if k not in ("$schema", "if", "then", "else")}
        if "const" in d:
            d["enum"] = [d.pop("const")]
        if isinstance(d.get("type"), list):
            types = d["type"]
            actual = [t for t in types if t != "null"]
            assert len(actual) == 1, "Review new union before generating SDKs"
            d["type"] = actual[0]
            d["nullable"] = "null" in types
        if isinstance(d.get("anyOf"), list) and len(d["anyOf"]) == 2:
            nonnull = [t for t in d["anyOf"] if t.get("type") != "null"]
            if len(nonnull) == 1:
                del d["anyOf"]
                d.update(nonnull[0])
                d["nullable"] = True
        if "$ref" in d and len(d) > 1:
            ref = d.pop("$ref")
            d["allOf"] = [{"$ref": ref}]
        return d

    result = adapt(copy.deepcopy(source))
    result["openapi"] = "3.0.3"
    result.pop("webhooks", None)
    # The constrained requested amount inherits Money's string type. Preserve
    # that type when the generator combines the narrower positive-amount pattern.
    requested = result["components"]["schemas"]["EP146Request"]["properties"]["requested_amount"]
    for branch in requested.get("allOf", []):
        amount = branch.get("properties", {}).get("amount")
        if amount is not None:
            amount["type"] = "string"
    context = result["components"]["schemas"]["ProcessingContext"]
    mapping = {}
    for i, name in enumerate(("InsightsProcessingContext", "SignalProcessingContext")):
        result["components"]["schemas"][name] = context["oneOf"][i]
        context["oneOf"][i] = {"$ref": "#/components/schemas/" + name}
        mapping[("insights", "signal")[i]] = "#/components/schemas/" + name
    context["discriminator"]["mapping"] = mapping
    return result


def replace(path, old, new):
    text = path.read_text()
    assert old in text, f"Generator template changed: {path}"
    path.write_text(text.replace(old, new))


def harden(language, directory):
    """Deterministic fixes to transport defaults and misleading template metadata."""
    if language == "typescript":
        replace(directory / "src/runtime.ts", "...overriddenInit,", "...overriddenInit,\n            redirect: 'error',")
        p = directory / "package.json"
        data = json.loads(p.read_text())
        data.update(author="AMLOK", description="AMLOK API client", private=True)
        data.pop("repository", None)
        p.write_text(json.dumps(data, indent=2) + "\n")
    elif language == "python":
        p = directory / "amlok/rest.py"
        text, count = re.subn(r"(self\.pool_manager\.request\(\s*method,\s*url,)",
                              r"\1\n                    redirect=False, retries=False,", p.read_text())
        assert count == 6, "Review Python transport template"
        p.write_text(text)
        replace(directory / "pyproject.toml", 'Repository = "https://github.com/GIT_USER_ID/GIT_REPO_ID"', 'Documentation = "https://docs.amlok.io/overview/sdks"')
        replace(directory / "pyproject.toml", '{name = "OpenAPI Generator Community",email = "team@openapitools.org"}', '{name = "AMLOK",email = "support@amlok.tech"}')
        p = directory / "setup.py"
        p.write_text(p.read_text().replace('author="OpenAPI Generator community"', 'author="AMLOK"')
                     .replace('author_email="team@openapitools.org"', 'author_email="support@amlok.tech"'))
    elif language == "java":
        p = directory / "pom.xml"
        text = p.read_text()
        text = re.sub(r"\s*<(scm|developers|licenses)>.*?</\1>", "", text, flags=re.S)
        text = text.replace("<url>https://github.com/openapitools/openapi-generator</url>", "<url>https://docs.amlok.io/overview/sdks</url>")
        p.write_text(text)
    elif language == "csharp":
        replace(directory / "src/Amlok/Client/ApiClient.cs", "new HttpClientHandler();", "new HttpClientHandler { AllowAutoRedirect = false };")
        p = directory / "src/Amlok/Amlok.csproj"
        text = re.sub(r"\s*<(RepositoryUrl|RepositoryType|PackageReleaseNotes|Copyright)>.*?</\1>", "", p.read_text())
        text = text.replace("<Authors>OpenAPI</Authors>", "<Authors>AMLOK</Authors>")
        text = text.replace("<Company>OpenAPI</Company>", "<Company>AMLOK</Company>")
        text = text.replace("<AssemblyTitle>OpenAPI Library</AssemblyTitle>", "<AssemblyTitle>AMLOK API client</AssemblyTitle>")
        p.write_text(text.replace("<Description>A library generated from a OpenAPI doc</Description>", "<Description>AMLOK API client</Description>"))
    elif language == "go":
        p = directory / "go.mod"
        p.write_text(re.sub(r"^module .*", "module amlok.local/client", p.read_text()))
    elif language == "php":
        p = directory / "composer.json"
        data = json.loads(p.read_text())
        data.update(homepage="https://docs.amlok.io/overview/sdks", authors=[{"name": "AMLOK"}])
        data.pop("license", None)
        p.write_text(json.dumps(data, indent=2) + "\n")
        for p in (directory / "lib/Api").glob("*.php"):
            replace(p, "new Client();", "new Client(['allow_redirects' => false, 'timeout' => 30]);")
    elif language == "ruby":
        p = directory / "amlok-api-client.gemspec"
        text = re.sub(r"^  s.license.*\n", "", p.read_text(), flags=re.M)
        p.write_text(text.replace('s.homepage    = "https://openapi-generator.tech"', 's.homepage    = "https://docs.amlok.io/overview/sdks"'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jar", required=True, type=Path)
    parser.add_argument("--java", default="java")
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--language", choices=TARGETS, action="append")
    args = parser.parse_args()
    actual = subprocess.check_output([args.java, "-jar", str(args.jar), "version"], text=True).strip()
    assert actual == GENERATOR, (actual, GENERATOR)
    spec_bytes = (ROOT / "openapi/amlok-v1.json").read_bytes()
    spec = json.loads(spec_bytes)
    assert spec["info"]["version"] == VERSION
    source_hash = hashlib.sha256(spec_bytes).hexdigest()
    args.work_dir.mkdir(parents=True, exist_ok=True)
    adapted = generator_input(spec)
    ops = [{"operation_id": o["operationId"], "method": m.upper(), "path": p,
            "summary": o["summary"], "group": o["tags"][0]}
           for p, item in spec["paths"].items() for m, o in item.items()
           if m in ("get", "post", "put", "patch", "delete")]
    for language in args.language or TARGETS:
        generator, config = TARGETS[language]
        output = args.work_dir / language
        if output.exists():
            raise SystemExit(f"Output already exists; use a fresh work directory: {output}")
        config = dict(config, disallowAdditionalPropertiesIfNotPresent=False, hideGenerationTimestamp=True)
        config_file = args.work_dir / f"{language}.config.json"
        config_file.write_text(json.dumps(config, indent=2))
        input_spec = copy.deepcopy(adapted)
        if language == "php":
            # PHP's generator drops oneOf fields during deserialization. Keep
            # the complete wire shape; the canonical schema enforces which
            # parent ID is valid for each product.
            schemas = input_spec["components"]["schemas"]
            properties = dict(schemas["InsightsProcessingContext"]["properties"],
                              **schemas["SignalProcessingContext"]["properties"])
            properties["product"] = {"type": "string", "enum": ["insights", "signal"]}
            schemas["ProcessingContext"] = {
                "type": "object", "properties": properties, "required": ["product"],
                "additionalProperties": False,
                "description": "Insights requires workflow_run_id. Signal requires monitoring_period_id. See the canonical ProcessingContext schema for conditional validation.",
            }
        if language == "python":
            def patterns(v):
                if isinstance(v, dict):
                    if isinstance(v.get("pattern"), str):
                        v["pattern"] = "/" + v["pattern"].replace("/", "\\/") + "/"
                    for x in v.values(): patterns(x)
                elif isinstance(v, list):
                    for x in v: patterns(x)
            patterns(input_spec)
        input_file = args.work_dir / f"{language}.input.json"
        input_file.write_text(json.dumps(input_spec))
        command = [args.java, "-jar", str(args.jar), "generate", "-i", str(input_file),
                   "-g", generator, "-o", str(output), "-c", str(config_file),
                   "--global-property", "apiTests=false,modelTests=false,apiDocs=false,modelDocs=false"]
        if language == "typescript":
            command += ["--type-mappings", "DateTime=string,Date=string"]
        with (args.work_dir / f"{language}.log").open("w") as log:
            subprocess.run(command, stdout=log, stderr=log, check=True)
        harden(language, output)
        for name in (".github", "git_push.sh", ".travis.yml", "test", "spec", "api", "docs", "README.md"):
            p = output / name
            if p.is_dir(): shutil.rmtree(p)
            elif p.exists(): p.unlink()
        for p in output.rglob("LICENSE*"):
            # Do not introduce a licensing policy from a generator's placeholder.
            if p.is_file(): p.unlink()
        (output / "operation-index.json").write_text(json.dumps(ops, indent=2) + "\n")
        (output / "BUILD.json").write_text(json.dumps({
            "sdk_version": VERSION, "api_version": VERSION, "generator": GENERATOR,
            "language": language, "contract_sha256": source_hash, "operations": len(ops),
            "contract_url": "https://docs.amlok.io/openapi/amlok-v1.json",
        }, indent=2) + "\n")
        (output / "README.md").write_text(f"""# AMLOK {language} API client

Source distribution {VERSION}, generated with OpenAPI Generator {GENERATOR}.

Installation and examples: https://docs.amlok.io/overview/sdks
The account manager supplies the environment URL and portal access. An authorized
administrator creates a workspace-scoped API key in the portal. Keep it server-side.
Always set the institution-issued origin; api.example.com is a placeholder.

This archive contains generated API methods and models, plus an operation index.
Operation IDs match the public API contract. No package-registry release is implied.
Generated types do not implement all JSON Schema conditional validation rules.
The published OpenAPI 3.1 contract and server validation remain authoritative.
Do not change monetary strings into floating-point amounts.

Explicitly configure timeouts and redirect handling as shown in the guide. Do not
enable blanket retries. Reuse the same idempotency key for the same action and
recover accepted commands before submitting anything again. Pagination, polling,
webhook verification and workflow orchestration are application responsibilities.
The SDK does not add financial commands, servicing, or standalone paid products.

Generated source is checked locally; it does not establish a live backend result.
Run the provisioned sandbox journeys before production use.
""")
        print(f"Generated {language}: {len(ops)} operations", flush=True)


if __name__ == "__main__":
    main()
