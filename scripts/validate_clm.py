#!/usr/bin/env python3
"""Run the complete CLM repository or presenter-readiness verification matrix."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from dataclasses import dataclass
from datetime import UTC, date, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
REACT = ROOT / "clm-salesforce-project" / "force-app" / "main" / "default" / "uiBundles" / "clmreactapp"
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
EXCLUDED_PARTS = {
    ".git", "node_modules", "dist", "build", "coverage", "playwright-report",
    "test-results", "__pycache__", ".pytest_cache",
}
MAX_TEXT_BYTES = 5_000_000
RUNTIME_ID_SUFFIXES = {".md", ".json", ".py", ".ts", ".tsx", ".js", ".xml", ".sh", ".yml", ".yaml", ".toml", ".env", ".properties"}
SECRET_ASSIGNMENT = re.compile(
    r'''(?ix)["']?(client[_-]?secret|access[_-]?token|refresh[_-]?token|api[_-]?key|password)["']?\s*[:=]\s*["']([^"'\n]+)'''
)
PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
LIVE_BOX_HOST = re.compile(r"https?://[a-z0-9-]+\.ent\.box\.com", re.IGNORECASE)
LIVE_SALESFORCE_HOST = re.compile(r"https?://(?!example\.)[a-z0-9-]+(?:\.develop)?\.my\.salesforce\.com", re.IGNORECASE)
LONG_NUMERIC_ID = re.compile(r"(?<![A-Za-z0-9])\d{10,}(?![A-Za-z0-9])")


class ValidationError(RuntimeError):
    """Raised when one verification row fails."""


@dataclass
class Result:
    name: str
    status: str
    seconds: float
    detail: str = ""


def run_command(command: list[str], *, cwd: Path = ROOT) -> str:
    try:
        completed = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError) as error:
        stdout = getattr(error, "stdout", "") or ""
        stderr = getattr(error, "stderr", "") or ""
        detail = "\n".join(part.strip() for part in (stdout, stderr) if part.strip())
        raise ValidationError(detail or str(error)) from error
    return "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())


def repository_files(root: Path = ROOT) -> list[Path]:
    if (root / ".git").exists() and shutil.which("git"):
        output = run_command(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root)
        return [root / item for item in output.split("\0") if item]
    return [path for path in root.rglob("*") if path.is_file() and not EXCLUDED_PARTS.intersection(path.parts)]


def secret_findings(text: str, label: str) -> list[str]:
    findings: list[str] = []
    for match in SECRET_ASSIGNMENT.finditer(text):
        value = match.group(2).strip().lower()
        if not any(marker in value for marker in ("${", "example", "placeholder", "replace", "<", "your-", "none")):
            findings.append(f"{label}: possible committed {match.group(1)}")
    if PRIVATE_KEY.search(text):
        findings.append(f"{label}: private key material")
    return findings


def check_secrets_and_runtime_ids(root: Path = ROOT) -> str:
    findings: list[str] = []
    scanned = 0
    placeholder_marker = "replace" + "-with-"
    for path in repository_files(root):
        relative = path.relative_to(root)
        if EXCLUDED_PARTS.intersection(relative.parts) or path.stat().st_size > MAX_TEXT_BYTES:
            continue
        try:
            raw = path.read_bytes()
            if b"\x00" in raw:
                continue
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        scanned += 1
        findings.extend(secret_findings(text, str(relative)))
        if LIVE_BOX_HOST.search(text):
            findings.append(f"{relative}: tenant-specific Box hostname")
        if LIVE_SALESFORCE_HOST.search(text):
            findings.append(f"{relative}: org-specific Salesforce hostname")
        if placeholder_marker in text.lower() and ".example." not in path.name:
            findings.append(f"{relative}: unresolved replace-with placeholder outside an example file")
        if (
            relative.parts
            and relative.parts[0] not in {"output", "sample-data"}
            and path.suffix.lower() in RUNTIME_ID_SUFFIXES
        ):
            for line_number, line in enumerate(text.splitlines(), 1):
                if LONG_NUMERIC_ID.search(line):
                    findings.append(f"{relative}:{line_number}: possible live numeric identifier")
    if findings:
        raise ValidationError("Secrets or environment-bound values found:\n" + "\n".join(findings))
    return f"{scanned} tracked text files"


def check_json_and_schemas(root: Path = ROOT) -> str:
    try:
        from jsonschema.validators import Draft202012Validator
    except ImportError as error:
        raise ValidationError("Install Python validation dependencies: python3 -m pip install -r requirements-dev.txt") from error
    failures: list[str] = []
    count = 0
    schema_count = 0
    for path in sorted(root.rglob("*.json")):
        if EXCLUDED_PARTS.intersection(path.relative_to(root).parts) or path.name.startswith("tsconfig"):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            count += 1
            if isinstance(data, dict) and "$schema" in data:
                Draft202012Validator.check_schema(data)
                schema_count += 1
        except Exception as error:
            failures.append(f"{path.relative_to(root)}: {error}")
    if failures:
        raise ValidationError("Invalid JSON or JSON Schema:\n" + "\n".join(failures))
    return f"{count} JSON files, {schema_count} schemas"


def check_local_links(root: Path = ROOT) -> str:
    failures: list[str] = []
    sources = [
        path for path in repository_files(root)
        if path.suffix.lower() == ".md" and not EXCLUDED_PARTS.intersection(path.relative_to(root).parts)
    ]
    for source in sources:
        for target in MARKDOWN_LINK.findall(source.read_text(encoding="utf-8")):
            if target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            destination = (source.parent / target.split("#", 1)[0]).resolve()
            if not destination.exists():
                failures.append(f"{source.relative_to(root)} -> {target}")
    if failures:
        raise ValidationError("Broken local Markdown links:\n" + "\n".join(failures))
    return f"{len(sources)} Markdown files"


def check_diagram_drift(root: Path = ROOT) -> str:
    executable = shutil.which("mmdc")
    if not executable:
        raise ValidationError("Mermaid CLI is required; install @mermaid-js/mermaid-cli so mmdc is on PATH")
    sources = sorted((root / "docs" / "diagrams").glob("*.mmd"))
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="clm-diagrams-") as directory:
        temporary = Path(directory)
        for source in sources:
            committed = source.with_suffix(".svg")
            rendered = temporary / committed.name
            if not committed.is_file():
                failures.append(f"missing {committed.relative_to(root)}")
                continue
            run_command([executable, "-i", str(source), "-o", str(rendered), "-b", "transparent"], cwd=root)
            if rendered.read_bytes() != committed.read_bytes():
                failures.append(f"{source.relative_to(root)} -> {committed.relative_to(root)}")
    if failures:
        raise ValidationError("Mermaid/SVG drift:\n" + "\n".join(failures))
    return f"{len(sources)} source/render pairs"


def load_script(name: str, root: Path = ROOT):
    path = root / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"clm_validation_{name}", path)
    if spec is None or spec.loader is None:
        raise ValidationError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def normalized_trace(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))

    def remove_timestamps(value):
        if isinstance(value, dict):
            return {
                key: remove_timestamps(item)
                for key, item in value.items()
                if key not in {"generatedAt", "timestamp"}
            }
        if isinstance(value, list):
            return [remove_timestamps(item) for item in value]
        return value

    return remove_timestamps(data)


def docx_semantic_archive(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        members: dict[str, bytes] = {}
        for name in sorted(archive.namelist()):
            content = archive.read(name)
            if name == "docProps/core.xml":
                text = content.decode("utf-8")
                text = re.sub(
                    r"(<dcterms:(?:created|modified)[^>]*>).*?(</dcterms:(?:created|modified)>)",
                    r"\1<TIMESTAMP>\2",
                    text,
                )
                content = text.encode("utf-8")
            members[name] = content
        return members


def check_generated_fixtures(root: Path = ROOT) -> str:
    try:
        import docx  # noqa: F401
        import reportlab  # noqa: F401
    except ImportError as error:
        raise ValidationError("Install Python validation dependencies: python3 -m pip install -r requirements-dev.txt") from error

    with tempfile.TemporaryDirectory(prefix="clm-fixtures-") as directory:
        temporary = Path(directory)
        sample_runs: list[Path] = []
        for index in range(2):
            destination = temporary / f"sample-{index}"
            module = load_script(f"generate_sample_contract_assets", root)
            module.PDF_OUT = destination / "pdf"
            module.JSON_OUT = destination / "json"
            module.CSV_OUT = destination / "csv"
            for output in (module.PDF_OUT, module.JSON_OUT, module.CSV_OUT):
                output.mkdir(parents=True, exist_ok=True)
            module.main()
            sample_runs.append(destination)
        for relative in ("json/northstar-clm-records.json", "json/clause-playbook.json", "csv/historical-clause-outcomes.csv"):
            first = sample_runs[0] / relative
            second = sample_runs[1] / relative
            committed = root / "output" / relative
            if first.read_bytes() != second.read_bytes() or first.read_bytes() != committed.read_bytes():
                raise ValidationError(f"Deterministic fixture drift: output/{relative}")
        if len(list((sample_runs[0] / "pdf").glob("*.pdf"))) != 6:
            raise ValidationError("Expected six generated contract PDFs")

        trace_runs: list[Path] = []
        for index in range(2):
            module = load_script("run_agentcore_mock", root)
            module.OUT = temporary / f"trace-{index}"
            module.OUT.mkdir(parents=True, exist_ok=True)
            module.main()
            trace_runs.append(module.OUT / "northstar-agentcore-trace.json")
        committed_trace = root / "output" / "agentcore" / "northstar-agentcore-trace.json"
        if normalized_trace(trace_runs[0]) != normalized_trace(trace_runs[1]) or normalized_trace(trace_runs[0]) != normalized_trace(committed_trace):
            raise ValidationError("AgentCore trace differs beyond the generated timestamp")

        docgen_runs: list[Path] = []
        for index in range(2):
            module = load_script("generate_docgen_templates", root)
            module.OUTPUT = temporary / f"docgen-{index}"
            module.main()
            docgen_runs.append(module.OUTPUT)
        expected_docx = {
            "clm-approval-memo-template.docx",
            "clm-order-summary-template.docx",
            "clm-renewal-notice-template.docx",
        }
        if {path.name for path in docgen_runs[0].glob("*.docx")} != expected_docx:
            raise ValidationError("Doc Gen output set is incomplete")
        for name in expected_docx:
            first_archive = docx_semantic_archive(docgen_runs[0] / name)
            if first_archive != docx_semantic_archive(docgen_runs[1] / name) or first_archive != docx_semantic_archive(root / "output" / "docgen" / name):
                raise ValidationError(f"Doc Gen template drift: {name}")
    return "6 PDFs, 3 deterministic data fixtures, 1 trace, 3 Doc Gen templates"


def check_generated_presenters(root: Path = ROOT) -> str:
    with tempfile.TemporaryDirectory(prefix="clm-presenters-") as directory:
        output = Path(directory)
        module = load_script("build_scenario_guides", root)
        module.OUTPUT = output
        for scenario in module.SCENARIOS:
            module.build_scenario(scenario)
        module = load_script("build_clm_experience_gallery", root)
        module.OUTPUT = output
        module.build()
        for name, filename in (
            ("build_executive_marketecture", "05-executive-marketecture.html"),
            ("build_agentcore_primary_marketecture", "06-agentcore-agent-experience-marketecture.html"),
            ("build_customer_datasheet", "07-customer-solution-datasheet.html"),
            ("build_contract_lifecycle_readiness_marketecture", "08-contract-lifecycle-readiness-marketecture.html"),
        ):
            module = load_script(name, root)
            module.OUTPUT = output / filename
            module.build()
        expected = {f"{index:02d}" for index in range(9)}
        generated = {path.name[:2] for path in output.glob("*.html")}
        if generated != expected:
            raise ValidationError(f"Presenter output order is incomplete: {sorted(generated)}")
        drift = [
            path.name for path in sorted(output.glob("*.html"))
            if path.read_bytes() != (root / "output" / "html" / path.name).read_bytes()
        ]
        if drift:
            raise ValidationError("Generated presenter drift:\n" + "\n".join(drift))
    return "9 deterministic self-contained HTML files"


class PortableResourceParser(HTMLParser):
    """Collect network-backed HTML attributes and CSS URLs."""

    CSS_EXTERNAL_URL = re.compile(r'''url\(\s*["']?(?:https?:)?//''', re.IGNORECASE)

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.external_references: list[str] = []
        self._style_depth = 0

    @staticmethod
    def is_external(value: str) -> bool:
        normalized = value.strip().lower()
        return normalized.startswith(("http://", "https://", "//"))

    def inspect_attributes(self, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if not value:
                continue
            lowered = name.lower()
            if lowered in {"src", "href"} and self.is_external(value):
                self.external_references.append(value)
            elif lowered == "srcset":
                for candidate in value.split(","):
                    url = candidate.strip().split(maxsplit=1)[0]
                    if self.is_external(url):
                        self.external_references.append(url)
            elif lowered == "style" and self.CSS_EXTERNAL_URL.search(value):
                self.external_references.append(value)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.inspect_attributes(attrs)
        if tag.lower() == "style":
            self._style_depth += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.inspect_attributes(attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "style" and self._style_depth:
            self._style_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._style_depth and self.CSS_EXTERNAL_URL.search(data):
            self.external_references.append(data)


def check_manifests_and_screenshots(root: Path = ROOT, *, today: date | None = None) -> str:
    today = today or datetime.now(UTC).date()
    failures: list[str] = []
    scenario_paths = sorted((root / "config" / "demo").glob("*-demo-manifest.json"))
    scenario_ids = {path.name.removesuffix("-demo-manifest.json") for path in scenario_paths}
    if len(scenario_paths) != 2:
        failures.append(f"expected 2 scenario manifests, found {len(scenario_paths)}")
    for path in scenario_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("manifestVersion", "scenario", "presenterSurface", "included", "readiness", "documentation", "screenshots"):
            if key not in data:
                failures.append(f"{path.relative_to(root)}: missing {key}")
        for target in data.get("documentation", {}).values():
            if isinstance(target, str) and not (root / target).exists():
                failures.append(f"{path.relative_to(root)}: missing {target}")

    manifest_path = root / "config" / "demo" / "screenshot-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("screenshots", [])
    declared = {entry.get("path") for entry in entries}
    actual = {
        path.relative_to(root).as_posix()
        for path in (root / "output" / "screenshots").rglob("*.png")
    }
    if not entries or not actual:
        failures.append("screenshot inventory must not be empty")
    if declared != actual:
        failures.append(f"screenshot manifest mismatch; missing={sorted(actual - declared)} extra={sorted(declared - actual)}")
    covered_scenarios = {entry.get("scenario") for entry in entries}
    missing_scenarios = scenario_ids - covered_scenarios
    if missing_scenarios:
        failures.append(f"screenshot coverage missing scenarios: {sorted(missing_scenarios)}")
    freshness_days = int(manifest.get("freshnessDays", 0))
    for entry in entries:
        for key in ("path", "scenario", "sourceSurface", "capturedOn", "readiness"):
            if not entry.get(key):
                failures.append(f"screenshot entry missing {key}: {entry}")
        try:
            captured = date.fromisoformat(entry["capturedOn"])
            age = (today - captured).days
            if age < 0 or age > freshness_days:
                failures.append(f"{entry['path']}: capture age {age} days exceeds 0..{freshness_days}")
        except (KeyError, ValueError) as error:
            failures.append(f"invalid capture date: {entry.get('path')}: {error}")
        if entry.get("readiness") != "real-demo":
            failures.append(f"{entry.get('path')}: readiness must be real-demo")

    html_paths = sorted((root / "output" / "html").glob("*.html"))
    if len(html_paths) != 9:
        failures.append(f"expected 9 HTML outputs, found {len(html_paths)}")
    for path in html_paths:
        parser = PortableResourceParser()
        parser.feed(path.read_text(encoding="utf-8"))
        if parser.external_references:
            failures.append(f"{path.relative_to(root)}: external asset reference")
    if failures:
        raise ValidationError("Manifest, screenshot, or portability failures:\n" + "\n".join(failures))
    return f"2 scenarios, {len(entries)} current real screenshots, 9 portable HTML files"


def check_reset_and_idempotency_contract(root: Path = ROOT) -> str:
    operator = json.loads((root / "config" / "operator" / "operator-workflow.json").read_text(encoding="utf-8"))
    connectors = json.loads((root / "config" / "box" / "https-connectors.json").read_text(encoding="utf-8"))
    operator_text = json.dumps(operator).lower()
    connector_text = json.dumps(connectors).lower()
    manual_text = (root / "docs" / "operator" / "manual-task-register.md").read_text(encoding="utf-8").lower()
    required = {
        "operator duplicate check": "duplicate" in operator_text,
        "operator reset check": "reset" in operator_text,
        "connector idempotency key": "idempotencykey" in connector_text,
        "manual reset tasks": "reset" in manual_text,
    }
    missing = [name for name, present in required.items() if not present]
    if missing:
        raise ValidationError("Missing reset/idempotency contracts: " + ", ".join(missing))
    return "portable retry, duplicate, confirmation, and reset contracts"


def check_live_receipts(root: Path = ROOT, *, required: bool) -> str:
    path = root / "config" / "runtime" / "validation-receipts.json"
    if not path.is_file():
        if required:
            raise ValidationError("Presenter-ready validation requires config/runtime/validation-receipts.json")
        return "SKIP:repository mode; live environment receipts are not required"
    receipt_text = path.read_text(encoding="utf-8")
    receipt_secrets = secret_findings(receipt_text, str(path.relative_to(root)))
    if receipt_secrets:
        raise ValidationError("Secrets found in live receipts:\n" + "\n".join(receipt_secrets))
    data = json.loads(receipt_text)
    receipts = data.get("receipts", [])
    freshness_days = int(data.get("freshnessDays", 30))
    failures: list[str] = []
    placeholder_marker = "replace" + "-with-"
    for receipt in receipts:
        platform = receipt.get("platform", "unknown")
        for key in ("environment", "validatedAt", "actionMode", "businessKey", "status", "evidence", "cleanupOwner"):
            value = receipt.get(key)
            if not value or placeholder_marker in str(value).lower():
                failures.append(f"{platform}: missing or placeholder {key}")
        try:
            validated = datetime.fromisoformat(str(receipt["validatedAt"]).replace("Z", "+00:00"))
            age = (datetime.now(UTC) - validated.astimezone(UTC)).days
            if age < 0 or age > freshness_days:
                failures.append(f"{platform}: receipt age {age} days exceeds 0..{freshness_days}")
        except (KeyError, ValueError) as error:
            failures.append(f"{platform}: invalid validatedAt: {error}")
    if failures:
        raise ValidationError("Live receipt validation failed:\n" + "\n".join(failures))
    platforms = {
        receipt.get("platform")
        for receipt in receipts
        if receipt.get("status") == "passed" and receipt.get("actionMode") == "live"
    }
    expected = {"Box", "Salesforce", "AgentCore", "Databricks"}
    if platforms != expected:
        raise ValidationError(f"Live receipt coverage is incomplete: expected={sorted(expected)} actual={sorted(platforms)}")
    return "Box, Salesforce, AgentCore, and Databricks receipts"


def check_react_script(script: str, root: Path = ROOT) -> str:
    workspace = root / REACT.relative_to(ROOT)
    if not (workspace / "node_modules").is_dir():
        raise ValidationError(f"{workspace.relative_to(root)} is missing node_modules; run npm ci")
    package = json.loads((workspace / "package.json").read_text(encoding="utf-8"))
    if script not in package.get("scripts", {}):
        raise ValidationError(f"React workspace does not define npm run {script}")
    if script == "test":
        command = ["npm", "test", "--", "--run"]
    elif script == "build":
        command = ["npm", "run", "build", "--", "--mode", "standalone"]
    else:
        command = ["npm", "run", script]
    run_command(command, cwd=workspace)
    return workspace.relative_to(root).as_posix()


def execute(name: str, action: Callable[[], str]) -> Result:
    start = time.monotonic()
    try:
        detail = action()
        if detail.startswith("SKIP:"):
            return Result(name, "SKIP", time.monotonic() - start, detail.removeprefix("SKIP:"))
        return Result(name, "PASS", time.monotonic() - start, detail)
    except Exception as error:  # keep the full matrix visible after a failure
        return Result(name, "FAIL", time.monotonic() - start, str(error))


def validate(*, skip_react: bool, skip_playwright: bool, presenter_ready: bool, root: Path = ROOT) -> list[Result]:
    rows: list[tuple[str, Callable[[], str]]] = [
        ("secrets + runtime IDs", lambda: check_secrets_and_runtime_ids(root)),
        ("JSON + schemas", lambda: check_json_and_schemas(root)),
        ("local Markdown links", lambda: check_local_links(root)),
        ("Mermaid/SVG drift", lambda: check_diagram_drift(root)),
        ("Python tests", lambda: run_command([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=root)),
        ("generated fixtures", lambda: check_generated_fixtures(root)),
        ("generated presenters", lambda: check_generated_presenters(root)),
        ("manifests + screenshots", lambda: check_manifests_and_screenshots(root)),
        ("reset + idempotency", lambda: check_reset_and_idempotency_contract(root)),
    ]
    if not skip_react:
        rows.extend([
            ("React unit tests", lambda: check_react_script("test", root)),
            ("React lint", lambda: check_react_script("lint", root)),
            ("React build", lambda: check_react_script("build", root)),
        ])
        if not skip_playwright:
            rows.append(("Playwright", lambda: check_react_script("test:e2e", root)))
    rows.append(("live validation receipts", lambda: check_live_receipts(root, required=presenter_ready)))
    return [execute(name, action) for name, action in rows]


def print_matrix(results: list[Result]) -> None:
    width = max(len(item.name) for item in results)
    for item in results:
        first_line = item.detail.splitlines()[0] if item.detail else ""
        print(f"{item.status:<4}  {item.name:<{width}}  {item.seconds:>6.2f}s  {first_line}")
    passed = sum(item.status == "PASS" for item in results)
    failed = sum(item.status == "FAIL" for item in results)
    skipped = sum(item.status == "SKIP" for item in results)
    print(f"\nSummary: {passed} passed, {failed} failed, {skipped} skipped")
    for item in results:
        if item.status == "FAIL":
            print(f"\n[{item.name}]\n{item.detail}")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--presenter-ready", action="store_true", help="Require current live validation receipts for every platform")
    result.add_argument("--skip-react", action="store_true", help="Skip React unit, lint, build, and Playwright checks")
    result.add_argument("--skip-playwright", action="store_true", help="Run React unit, lint, and build without browser E2E")
    result.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    return result


def main() -> int:
    args = parser().parse_args()
    results = validate(
        skip_react=args.skip_react,
        skip_playwright=args.skip_playwright,
        presenter_ready=args.presenter_ready,
        root=args.root.resolve(),
    )
    print_matrix(results)
    return 1 if any(item.status == "FAIL" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
