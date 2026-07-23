#!/usr/bin/env python3
"""Build a guarded browser-automation executor for the unsupported Box Forms private API lab."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = ROOT / "config/box/private-api-lab-form-definition.json"
DEFAULT_CONFIG = ROOT / "config/runtime/demo-environment.json"
DEFAULT_FORM_RUNTIME = ROOT / "config/runtime/generated/box/form-definition.json"
DEFAULT_OUTPUT = ROOT / "config/runtime/generated/box/private-api-lab-provisioner.js"
LAB_TITLE_PREFIX = "CLM Forms API Lab - "
FORBIDDEN_TITLES = {"New Contract Request", "Start new contract"}
ACKNOWLEDGEMENT = "I understand this uses an unsupported Box private API"
SUPPORTED_FIELD_TYPES = {
    "shortText",
    "longText",
    "email",
    "number",
    "dropdown",
    "date",
    "fileUpload",
}


class ExperimentalProvisionerError(RuntimeError):
    """Raised when the private API lab executor cannot be built safely."""


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ExperimentalProvisionerError(f"Missing required file: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ExperimentalProvisionerError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise ExperimentalProvisionerError(f"Expected a JSON object in {path}")
    return value


def validate_hostname(hostname: str) -> str:
    normalized = hostname.strip().lower()
    if not re.fullmatch(r"[a-z0-9.-]+\.box\.com", normalized):
        raise ExperimentalProvisionerError("hostname must be a bare Box hostname ending in .box.com")
    return normalized


def validate_spec(spec: dict[str, Any]) -> None:
    problems: list[str] = []
    title = spec.get("name")
    if spec.get("schemaVersion") != 1:
        problems.append("schemaVersion must be 1")
    if not isinstance(title, str) or not title.startswith(LAB_TITLE_PREFIX):
        problems.append(f"name must begin with {LAB_TITLE_PREFIX!r}")
    elif title in FORBIDDEN_TITLES:
        problems.append(f"name is forbidden for private API experiments: {title}")

    provisioning = spec.get("provisioning")
    expected = {
        "mode": "experimental-private-rest",
        "existingFormPolicy": "reconcile-exact-title",
        "delete": False,
        "publishLink": False,
        "share": False,
        "submitTestResponse": False,
    }
    if not isinstance(provisioning, dict):
        problems.append("provisioning must be an object")
    else:
        for key, value in expected.items():
            if provisioning.get(key) != value:
                problems.append(f"provisioning.{key} must be {value!r}")

    fields = spec.get("fields")
    if not isinstance(fields, list) or not fields:
        problems.append("fields must be a non-empty array")
        fields = []
    if len(fields) > 10:
        problems.append("the lab executor is limited to ten fields")
    keys: set[str] = set()
    labels: set[str] = set()
    for index, field in enumerate(fields):
        prefix = f"fields[{index}]"
        if not isinstance(field, dict):
            problems.append(f"{prefix} must be an object")
            continue
        key = field.get("key")
        label = field.get("label")
        if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", key):
            problems.append(f"{prefix}.key must be a portable alphanumeric key")
        elif key in keys:
            problems.append(f"duplicate field key: {key}")
        else:
            keys.add(key)
        if not isinstance(label, str) or not label.strip():
            problems.append(f"{prefix}.label must be a non-empty string")
        elif label in labels:
            problems.append(f"duplicate field label: {label}")
        else:
            labels.add(label)
        field_type = field.get("type")
        if field_type not in SUPPORTED_FIELD_TYPES:
            problems.append(
                f"{prefix}.type must be one of {', '.join(sorted(SUPPORTED_FIELD_TYPES))}"
            )
        if field_type == "dropdown":
            options = field.get("options")
            if (
                not isinstance(options, list)
                or len(options) < 2
                or any(not isinstance(option, str) or not option.strip() for option in options)
                or len(set(options)) != len(options)
            ):
                problems.append(f"{prefix}.options must contain at least two unique non-empty strings")
        elif "options" in field:
            problems.append(f"{prefix}.options is only valid for dropdown fields")
        if not isinstance(field.get("required"), bool):
            problems.append(f"{prefix}.required must be boolean")

    if problems:
        raise ExperimentalProvisionerError("Invalid private API lab definition:\n- " + "\n- ".join(problems))


def field_id(key: str) -> str:
    digest = hashlib.sha256(key.encode("utf-8")).digest()[:16]
    token = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return f"element-{token}"


def field_component(field: dict[str, Any], element_id: str, upload_folder_id: str | None) -> dict[str, Any]:
    common = {
        "required": field["required"],
        "label": field["label"],
        "id": element_id,
    }
    field_type = field["type"]
    if field_type == "shortText":
        return {"type": "textField", "textType": "text", **common}
    if field_type == "longText":
        return {"type": "textField", "textType": "text", "multiline": True, **common}
    if field_type == "email":
        return {"type": "textField", "textType": "email", "visible": True, **common}
    if field_type == "number":
        return {"type": "numberField", **common}
    if field_type == "dropdown":
        return {"type": "selectField", "maximumSelections": 0, "options": field["options"], **common}
    if field_type == "date":
        return {
            "type": "dateTimeField",
            "dateTimeMode": "date",
            "dateLabel": "",
            "timeLabel": "",
            **common,
        }
    if field_type == "fileUpload":
        if not upload_folder_id:
            raise ExperimentalProvisionerError(
                "fileUpload fields require config.box.parentFolderId at executor generation time"
            )
        return {
            "type": "uploadField",
            "folderId": upload_folder_id,
            "showFileDescription": False,
            **common,
        }
    raise ExperimentalProvisionerError(f"Unsupported field type: {field_type}")


def form_content(spec: dict[str, Any], upload_folder_id: str | None = None) -> dict[str, Any]:
    validate_spec(spec)
    items: list[str] = []
    layout: list[dict[str, Any]] = []
    components: dict[str, Any] = {
        "group-0": {
            "id": "group-0",
            "type": "group",
            "label": spec["name"],
            "description": str(spec.get("description") or ""),
            "items": items,
        }
    }
    y = 0
    observed_heights = {"date": 151, "fileUpload": 391, "longText": 188}
    for field in spec["fields"]:
        element_id = field_id(field["key"])
        height = observed_heights.get(field["type"], 148)
        items.append(element_id)
        layout.append(
            {
                "w": 2,
                "h": height,
                "x": 0,
                "y": y,
                "i": element_id,
                "moved": False,
                "static": False,
            }
        )
        y += height
        components[element_id] = field_component(field, element_id, upload_folder_id)
    return {
        "root": "group-0",
        "layouts": {"group-0": {"layout": layout}},
        "components": components,
        "theme": None,
        "type": "form",
    }


def executor_script(spec: dict[str, Any], hostname: str, upload_folder_id: str | None = None) -> str:
    validate_spec(spec)
    hostname = validate_hostname(hostname)
    title_json = json.dumps(spec["name"])
    hostname_json = json.dumps(hostname)
    content_json = json.dumps(form_content(spec, upload_folder_id), separators=(",", ":"))
    prefix_json = json.dumps(LAB_TITLE_PREFIX)
    script = f"""/* Unsupported Box Forms private API lab. No delete, publish, share, or submit calls. */
window.__clmPrivateApiLabPromise = (async () => {{
  "use strict";
  const expectedHostname = {hostname_json};
  const title = {title_json};
  const requiredPrefix = {prefix_json};
  const desiredContent = {content_json};
  const base = "/app-api/file-request-web";

  if (location.hostname !== expectedHostname) {{
    throw new Error(`Target guard failed: expected ${{expectedHostname}}, received ${{location.hostname}}`);
  }}
  if (!title.startsWith(requiredPrefix)) {{
    throw new Error("Title guard failed: private API labs require the CLM lab prefix");
  }}

  const requestJson = async (path, options = {{}}) => {{
    const response = await fetch(`${{base}}${{path}}`, {{credentials: "include", ...options}});
    const body = response.status === 204 ? null : await response.json();
    if (!response.ok) {{
      const message = body?.message || body?.error || `HTTP ${{response.status}}`;
      throw new Error(`Box Forms private API failed: ${{message}}`);
    }}
    return {{response, body}};
  }};
  const multipart = (values) => {{
    const data = new FormData();
    for (const [key, value] of Object.entries(values)) {{
      data.append(key, typeof value === "string" ? value : JSON.stringify(value));
    }}
    return data;
  }};
  const parseContent = (value) => typeof value === "string" ? JSON.parse(value) : value;
  const sortValue = (value) => Array.isArray(value)
    ? value.map(sortValue)
    : (value && typeof value === "object")
      ? Object.fromEntries(Object.keys(value).sort().map((key) => [key, sortValue(value[key])]))
      : value;
  const canonical = (value) => JSON.stringify(sortValue(value));
  const listEntries = (body) => Array.isArray(body)
    ? body
    : (body?.data || body?.entries || body?.items || body?.fileRequests || []);

  const listed = await requestJson("/file-requests?limit=20&sortDirection=DESC&sortField=modifiedAt&type=form");
  const matches = listEntries(listed.body).filter((item) =>
    (item?.title || item?.form?.title) === title
  );
  if (matches.length > 1) {{
    throw new Error(`Duplicate guard failed: found ${{matches.length}} exact-title Forms`);
  }}

  let outcome;
  let status;
  let visibility;
  if (matches.length === 0) {{
    const created = await requestJson("/form", {{
      method: "POST",
      body: multipart({{title, content: desiredContent}}),
    }});
    outcome = "created";
    status = created.body?.status;
    visibility = created.body?.visibility;
  }} else {{
    const formId = matches[0]?.fileRequestId || matches[0]?.id || matches[0]?.formId;
    if (!formId) throw new Error("Exact-title match did not include a Form identifier");
    const detail = await requestJson(`/file-request/${{formId}}`);
    const current = parseContent(detail.body?.form?.content);
    if (canonical(current) === canonical(desiredContent)) {{
      outcome = "unchanged";
    }} else {{
      const versionId = detail.body?.form?.versionId || detail.body?.formVersion?.id || matches[0]?.formVersionId;
      if (!versionId) throw new Error("Existing Form did not include a version identifier");
      const updated = await requestJson(`/form-version/${{versionId}}`, {{
        method: "POST",
        body: multipart({{fileRequestId: formId, content: desiredContent}}),
      }});
      outcome = "updated";
      status = updated.body?.status;
    }}
    status ||= detail.body?.status || detail.body?.form?.status;
    visibility ||= detail.body?.visibility;
  }}

  const result = {{outcome, title, status, visibility, fieldCount: desiredContent.components["group-0"].items.length}};
  console.info("CLM_FORMS_PRIVATE_API_LAB", JSON.stringify(result));
  return result;
}})();
"""
    return " ".join(line.strip() for line in script.splitlines() if line.strip()) + "\n"


def config_hostname(config: dict[str, Any]) -> str:
    box = config.get("box")
    if not isinstance(box, dict):
        raise ExperimentalProvisionerError("config.box must be an object")
    return validate_hostname(str(box.get("hostname") or ""))


def runtime_upload_folder_id(form_runtime: dict[str, Any]) -> str | None:
    value = str(form_runtime.get("destinationFolderId") or "").strip()
    if value and not value.isdigit():
        raise ExperimentalProvisionerError("runtime destinationFolderId must contain only digits")
    return value or None


def write_executor(
    spec_path: Path,
    config_path: Path,
    form_runtime_path: Path,
    output_path: Path,
    acknowledgement: str,
) -> None:
    if acknowledgement != ACKNOWLEDGEMENT:
        raise ExperimentalProvisionerError(
            f"Refusing to build executor without --acknowledge {ACKNOWLEDGEMENT!r}"
        )
    config = load_json(config_path)
    spec = load_json(spec_path)
    upload_folder_id = None
    if any(field.get("type") == "fileUpload" for field in spec.get("fields", [])):
        upload_folder_id = runtime_upload_folder_id(load_json(form_runtime_path))
    script = executor_script(
        spec,
        config_hostname(config),
        upload_folder_id,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(script, encoding="utf-8")
    try:
        display_path = output_path.relative_to(ROOT)
    except ValueError:
        display_path = output_path
    print(f"Prepared guarded private API lab executor: {display_path}")
    print("The executor contains no credentials and makes no changes until browser automation runs it in an authenticated Box page.")
    print("It can create, update, or leave unchanged only the exact CLM lab title; it never deletes.")
    print("Do not paste it into DevTools; apply it through an authenticated browser automation session.")


def dry_run(spec_path: Path, config_path: Path, form_runtime_path: Path) -> None:
    spec = load_json(spec_path)
    validate_spec(spec)
    config = load_json(config_path)
    hostname = config_hostname(config)
    upload_folder_id = None
    if any(field.get("type") == "fileUpload" for field in spec["fields"]):
        upload_folder_id = runtime_upload_folder_id(load_json(form_runtime_path))
    content = form_content(spec, upload_folder_id)
    print(f"DRY RUN  target: {hostname}")
    print(f"DRY RUN  exact lab title: {spec['name']}")
    print(f"DRY RUN  {len(content['components']['group-0']['items'])} field(s); create/update/unchanged only; never delete")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--form-runtime", type=Path, default=DEFAULT_FORM_RUNTIME)
    result.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    modes = result.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--write-executor", action="store_true")
    result.add_argument("--acknowledge", default="", help="Required exact unsupported-private-API acknowledgement")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.dry_run:
            dry_run(args.spec, args.config, args.form_runtime)
        else:
            write_executor(args.spec, args.config, args.form_runtime, args.output, args.acknowledge)
    except ExperimentalProvisionerError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
