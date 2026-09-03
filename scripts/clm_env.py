#!/usr/bin/env python3
"""Resolve the environment-specific settings this demo needs, from BCL or the shell.

Every value that binds the demo to one Salesforce org or one Box enterprise is declared
in config/deploy/environment.bcl. That file is committed and holds placeholders only --
a live folder id in the working tree is what the secret scan rejects. Real values go in
config/deploy/environment.local.bcl, which is gitignored.

Precedence is environment variable, then the local BCL, then nothing. The environment
wins so a one-off run can override a file without editing it.

Usage:
    python3 scripts/clm_env.py --export          # shell-eval-able assignments
    python3 scripts/clm_env.py --check           # report what is set, exit 1 if incomplete
"""
from __future__ import annotations

import argparse
import os
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bcl import BCLError, load_bcl  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "config" / "deploy" / "environment.bcl"
LOCAL = ROOT / "config" / "deploy" / "environment.local.bcl"

# A value that still reads like the placeholder it shipped as.
PLACEHOLDER = ("<", ">")


def _settings(config: dict) -> dict[str, dict]:
    """Flatten the grouped BCL into envVar -> the setting's own description."""
    found: dict[str, dict] = {}
    for group in ("boxSubject", "boxContent", "demo"):
        for name, setting in (config.get(group) or {}).items():
            if isinstance(setting, dict) and setting.get("envVar"):
                found[setting["envVar"]] = {"name": name, **setting}
    return found


def _is_placeholder(value: str) -> bool:
    return value.startswith(PLACEHOLDER[0]) and value.endswith(PLACEHOLDER[1])


def resolve() -> tuple[dict[str, str], list[dict]]:
    """Return (resolved values by env var, settings still missing)."""
    schema = _settings(load_bcl(SCHEMA))

    local: dict[str, str] = {}
    if LOCAL.is_file():
        for env_var, setting in _settings(load_bcl(LOCAL)).items():
            value = str(setting.get("value", "")).strip()
            if value and not _is_placeholder(value):
                local[env_var] = value

    resolved: dict[str, str] = {}
    missing: list[dict] = []
    for env_var, setting in schema.items():
        value = os.environ.get(env_var, "").strip() or local.get(env_var, "")
        if value:
            resolved[env_var] = value
        else:
            missing.append(setting)
    return resolved, missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", action="store_true", help="print shell assignments")
    parser.add_argument("--check", action="store_true", help="report coverage and exit 1 if incomplete")
    args = parser.parse_args()

    try:
        resolved, missing = resolve()
    except (BCLError, OSError) as error:
        print(f"clm_env: {error}", file=sys.stderr)
        return 2

    if args.export:
        for env_var, value in sorted(resolved.items()):
            print(f"{env_var}={shlex.quote(value)}")
        return 0

    # --check, and the default.
    source = LOCAL if LOCAL.is_file() else None
    print(f"Schema:   {SCHEMA.relative_to(ROOT)}")
    print(f"Values:   {source.relative_to(ROOT) if source else 'environment variables only'}")
    for env_var in sorted(resolved):
        print(f"  set     {env_var}")
    for setting in sorted(missing, key=lambda s: s["envVar"]):
        print(f"  MISSING {setting['envVar']}  -> {setting.get('field', '?')}")
        print(f"          {setting.get('withoutIt', '')}")

    # A subject is one-of, so it is satisfied by either half.
    subject = {"BOX_USER_ID", "BOX_ENTERPRISE_ID"}
    blocking = [s for s in missing if s["envVar"] not in subject]
    if not (subject & set(resolved)):
        print("  MISSING a Box subject: set BOX_USER_ID (preferred) or BOX_ENTERPRISE_ID.")
        return 1
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
