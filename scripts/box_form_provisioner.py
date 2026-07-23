#!/usr/bin/env python3
"""Legacy entry point for preparing the CLM Box Form Browser Use plan."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = ROOT / "config/box/form-definition.json"
DEFAULT_CONFIG = ROOT / "config/runtime/demo-environment.json"
DEFAULT_STATE = ROOT / "config/runtime/bootstrap-state.json"
DEFAULT_OUTPUT = ROOT / "config/runtime/generated/box/form-browser-plan.json"
TOKEN = re.compile(r"^\$\{([A-Za-z0-9_.]+)\}$")
FIELD_TYPES = {
    "shortText": "Short Text",
    "longText": "Long Text",
    "email": "Email",
    "number": "Number",
    "dropdown": "Dropdown",
    "date": "Date",
    "fileUpload": "File Upload",
}


class ProvisionerError(RuntimeError):
    """Raised when a safe browser plan cannot be prepared."""


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ProvisionerError(f"Missing required file: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ProvisionerError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise ProvisionerError(f"Expected a JSON object in {path}")
    return value


def validate_spec(spec: dict[str, Any]) -> None:
    problems: list[str] = []
    if spec.get("schemaVersion") != 1:
        problems.append("schemaVersion must be 1")
    if not isinstance(spec.get("name"), str) or not spec["name"].strip():
        problems.append("name must be a non-empty string")
    if not TOKEN.match(str(spec.get("destinationFolderId", ""))):
        problems.append("destinationFolderId must be one complete runtime binding")
    if spec.get("confirmationBehavior") != "box-default":
        problems.append("confirmationBehavior must be 'box-default'")

    provisioning = spec.get("provisioning")
    if not isinstance(provisioning, dict):
        problems.append("provisioning must be an object")
    else:
        expected = {
            "mode": "authenticated-browser-ui",
            "existingFormPolicy": "reconcile-exact-title",
            "saveForm": True,
            "publishLink": False,
            "share": False,
        }
        for key, value in expected.items():
            if provisioning.get(key) != value:
                problems.append(f"provisioning.{key} must be {value!r}")

    fields = spec.get("fields")
    if not isinstance(fields, list) or not fields:
        problems.append("fields must be a non-empty array")
        fields = []
    keys: set[str] = set()
    labels: set[str] = set()
    for index, field in enumerate(fields):
        prefix = f"fields[{index}]"
        if not isinstance(field, dict):
            problems.append(f"{prefix} must be an object")
            continue
        key = field.get("key")
        label = field.get("label")
        field_type = field.get("type")
        if not isinstance(key, str) or not key:
            problems.append(f"{prefix}.key must be a non-empty string")
        elif key in keys:
            problems.append(f"duplicate field key: {key}")
        else:
            keys.add(key)
        if not isinstance(label, str) or not label:
            problems.append(f"{prefix}.label must be a non-empty string")
        elif label in labels:
            problems.append(f"duplicate field label: {label}")
        else:
            labels.add(label)
        if field_type not in FIELD_TYPES:
            problems.append(f"{prefix}.type must be one of {', '.join(FIELD_TYPES)}")
        if not isinstance(field.get("required"), bool):
            problems.append(f"{prefix}.required must be boolean")
        options = field.get("options")
        if field_type == "dropdown":
            if not isinstance(options, list) or len(options) < 2 or not all(isinstance(item, str) and item for item in options):
                problems.append(f"{prefix}.options must contain at least two non-empty strings")
            elif len(options) != len(set(options)):
                problems.append(f"{prefix}.options must be unique")
        elif options is not None:
            problems.append(f"{prefix}.options is valid only for dropdown fields")

    if problems:
        raise ProvisionerError("Invalid Form definition:\n- " + "\n- ".join(problems))


def runtime_bindings(config: dict[str, Any], state: dict[str, Any]) -> dict[str, str]:
    box_config = config.get("box", {})
    box_state = state.get("box", {})
    folders = box_state.get("folders", {})
    return {
        "box.hostname": str(box_config.get("hostname") or ""),
        "box.enterpriseId": str(box_config.get("enterpriseId") or ""),
        "box.operatorLogin": str(box_config.get("operatorLogin") or ""),
        "box.folders.intake": str(folders.get("01 - Intake") or ""),
    }


def resolve_binding(value: str, bindings: dict[str, str]) -> str:
    match = TOKEN.match(value)
    if not match:
        raise ProvisionerError(f"Expected one runtime binding, received: {value}")
    key = match.group(1)
    replacement = bindings.get(key, "")
    if not replacement:
        raise ProvisionerError(f"Unresolved runtime binding: {key}")
    return replacement


def validate_hostname(hostname: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9.-]+\.box\.com", hostname):
        raise ProvisionerError("box.hostname must be a bare Box hostname ending in .box.com")
    return hostname.lower()


def browser_plan(spec: dict[str, Any], config: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    validate_spec(spec)
    bindings = runtime_bindings(config, state)
    hostname = validate_hostname(bindings["box.hostname"])
    enterprise_id = bindings["box.enterpriseId"]
    operator_login = bindings["box.operatorLogin"]
    if not enterprise_id or not operator_login:
        raise ProvisionerError("box.enterpriseId and box.operatorLogin are required target guards")
    destination_id = resolve_binding(spec["destinationFolderId"], bindings)
    fields = [
        {
            "position": index,
            "key": field["key"],
            "label": field["label"],
            "builderType": FIELD_TYPES[field["type"]],
            "required": field["required"],
            **({"options": field["options"]} if "options" in field else {}),
        }
        for index, field in enumerate(spec["fields"], 1)
    ]
    return {
        "schemaVersion": 1,
        "operation": "reconcile-saved-form",
        "transport": "authenticated-box-browser-ui",
        "target": {
            "hostname": hostname,
            "formsUrl": f"https://{hostname}/automate/forms",
            "enterpriseId": enterprise_id,
            "operatorLogin": operator_login,
        },
        "form": {
            "name": spec["name"],
            "destinationFolderId": destination_id,
            "confirmationBehavior": spec["confirmationBehavior"],
            "fields": fields,
        },
        "reconciliation": {
            "match": "exact-title",
            "onZeroMatches": "create-one-saved-form",
            "onOneMatch": "open-and-reconcile",
            "onMultipleMatches": "stop-and-report-duplicates",
        },
        "verification": [
            "exact title",
            "exact field count and order",
            "field types and required states",
            "dropdown option order",
            "destination folder",
            "Box default submission confirmation",
            "saved Form present in the Forms list",
        ],
        "decisionGate": {
            "stopBefore": ["publish", "share", "copy public link", "submit test response"],
            "requiredNextApproval": "Explicit owner approval before copying, enabling, or distributing the Form link",
        },
        "credentialHandling": {
            "exportBrowserCredentials": False,
            "callPrivateRestDirectly": False,
            "persistHeadersCookiesOrTokens": False,
        },
    }


def portable_dry_run(spec: dict[str, Any]) -> None:
    validate_spec(spec)
    print(f"DRY RUN  valid portable Form definition: {spec['name']}")
    print(f"DRY RUN  {len(spec['fields'])} ordered fields; destination remains runtime-bound")
    print("DRY RUN  Browser Use can reconcile one saved Form and must stop before link distribution")


def prepare(spec_path: Path, config_path: Path, state_path: Path, output_path: Path) -> None:
    plan = browser_plan(load_json(spec_path), load_json(config_path), load_json(state_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    try:
        display_path = output_path.relative_to(ROOT)
    except ValueError:
        display_path = output_path
    print(f"Prepared gitignored Browser Use plan: {display_path}")
    print("NO BOX CHANGES WERE MADE.")
    print("Box Forms has no supported public authoring API; an authenticated browser agent must apply this plan.")
    print("The browser agent must stop before copying, enabling, or distributing the Form link.")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--state", type=Path, default=DEFAULT_STATE)
    result.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    result.add_argument("--dry-run", action="store_true", help="Validate the portable definition without reading or writing runtime values")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.dry_run:
            portable_dry_run(load_json(args.spec))
        else:
            prepare(args.spec, args.config, args.state, args.output)
    except ProvisionerError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
