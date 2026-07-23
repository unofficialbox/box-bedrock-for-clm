#!/usr/bin/env python3
"""Build a guarded authenticated-browser executor for the unsupported Box Apps private API lab."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = ROOT / "config/box/private-api-lab-app-definition.json"
DEFAULT_CONFIG = ROOT / "config/runtime/demo-environment.json"
DEFAULT_OUTPUT = ROOT / "config/runtime/generated/box/private-api-lab-app-provisioner.js"
LAB_TITLE_PREFIX = "CLM Surface API Lab - "
FORBIDDEN_TITLES = {"Contract Lifecycle Management", "Approved Contract Clause Library"}
ACKNOWLEDGEMENT = "I understand this uses an unsupported Box private API"
MAX_PAGES_IN_LAB = 3
MAX_SECTIONS_IN_PAGE = 4


class ExperimentalAppsProvisionerError(RuntimeError):
    """Raised when the Apps lab executor cannot be built safely."""


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ExperimentalAppsProvisionerError(f"Missing required file: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ExperimentalAppsProvisionerError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise ExperimentalAppsProvisionerError(f"Expected a JSON object in {path}")
    return value


def validate_hostname(hostname: str) -> str:
    normalized = hostname.strip().lower()
    if not re.fullmatch(r"[a-z0-9.-]+\.box\.com", normalized):
        raise ExperimentalAppsProvisionerError(
            "hostname must be a bare Box hostname ending in .box.com"
        )
    return normalized


def _stable_id(*parts: str) -> str:
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()
    return digest[:12]


def normalize_pages(spec: dict[str, Any]) -> list[dict[str, Any]]:
    declared = spec.get("pages")
    if declared is None:
        return []

    if not isinstance(declared, list):
        raise ExperimentalAppsProvisionerError("pages must be an array")
    if not declared:
        raise ExperimentalAppsProvisionerError("pages must be a non-empty array when supplied")
    if len(declared) > MAX_PAGES_IN_LAB:
        raise ExperimentalAppsProvisionerError(f"pages is limited to {MAX_PAGES_IN_LAB}")

    normalized_pages: list[dict[str, Any]] = []
    seen_page_names: set[str] = set()
    for page_index, page in enumerate(declared):
        if not isinstance(page, dict):
            raise ExperimentalAppsProvisionerError(f"pages[{page_index}] must be an object")
        page_name = page.get("name")
        if not isinstance(page_name, str) or not page_name.strip():
            raise ExperimentalAppsProvisionerError(
                f"pages[{page_index}].name must be a non-empty string"
            )
        if page_name in seen_page_names:
            raise ExperimentalAppsProvisionerError(
                f"duplicate page name in pages[{page_index}]: {page_name}"
            )
        seen_page_names.add(page_name)

        sections = page.get("sections", [])
        if not isinstance(sections, list):
            raise ExperimentalAppsProvisionerError(f"pages[{page_index}].sections must be an array")
        if len(sections) > MAX_SECTIONS_IN_PAGE:
            raise ExperimentalAppsProvisionerError(
                f"pages[{page_index}].sections is limited to {MAX_SECTIONS_IN_PAGE}"
            )

        normalized_sections: list[dict[str, Any]] = []
        for section_index, section in enumerate(sections):
            if not isinstance(section, dict):
                raise ExperimentalAppsProvisionerError(
                    f"pages[{page_index}].sections[{section_index}] must be an object"
                )
            if "items" in section:
                raise ExperimentalAppsProvisionerError(
                    "page sections can not include items in this controlled lab"
                )
            title = section.get("title")
            if not isinstance(title, str) or not title.strip():
                raise ExperimentalAppsProvisionerError(
                    f"pages[{page_index}].sections[{section_index}].title must be a non-empty string"
                )
            position = section.get("position", section_index)
            size = section.get("size", 1)
            layout = section.get("layout", {})
            if not isinstance(position, int) or position < 0:
                raise ExperimentalAppsProvisionerError(
                    f"pages[{page_index}].sections[{section_index}].position must be a non-negative integer"
                )
            if not isinstance(size, int) or size <= 0:
                raise ExperimentalAppsProvisionerError(
                    f"pages[{page_index}].sections[{section_index}].size must be a positive integer"
                )
            if not isinstance(layout, dict):
                raise ExperimentalAppsProvisionerError(
                    f"pages[{page_index}].sections[{section_index}].layout must be an object"
                )
            normalized_sections.append(
                {
                    "id": f"section-{_stable_id(spec['name'], page_name, str(section_index), title)}",
                    "title": title,
                    "position": position,
                    "size": size,
                    "layout": layout,
                    "items": [],
                }
            )

        normalized_pages.append({"name": page_name, "sections": normalized_sections})

    return normalized_pages


def validate_spec(spec: dict[str, Any]) -> None:
    problems: list[str] = []

    name = spec.get("name")
    if spec.get("schemaVersion") != 1:
        problems.append("schemaVersion must be 1")
    if not isinstance(name, str) or not name.startswith(LAB_TITLE_PREFIX):
        problems.append(f"name must begin with {LAB_TITLE_PREFIX!r}")
    elif name in FORBIDDEN_TITLES:
        problems.append(f"name is forbidden for private API experiments: {name}")

    for key in ("description", "initialPageName"):
        if not isinstance(spec.get(key), str) or not spec[key].strip():
            problems.append(f"{key} must be a non-empty string")

    if "pages" in spec:
        try:
            normalize_pages(spec)
        except ExperimentalAppsProvisionerError as error:
            problems.append(str(error))

    expected = {
        "mode": "experimental-private-rest",
        "existingAppPolicy": "reconcile-exact-title",
        "delete": False,
        "publish": False,
        "share": False,
    }
    provisioning = spec.get("provisioning")
    if not isinstance(provisioning, dict):
        problems.append("provisioning must be an object")
    else:
        for key, value in expected.items():
            if provisioning.get(key) != value:
                problems.append(f"provisioning.{key} must be {value!r}")

    if problems:
        raise ExperimentalAppsProvisionerError(
            "Invalid private API Apps lab definition:\n- " + "\n- ".join(problems)
        )


def config_hostname(config: dict[str, Any]) -> str:
    box = config.get("box")
    if not isinstance(box, dict):
        raise ExperimentalAppsProvisionerError("config.box must be an object")
    return validate_hostname(str(box.get("hostname") or ""))


def executor_script(spec: dict[str, Any], hostname: str) -> str:
    validate_spec(spec)
    hostname = validate_hostname(hostname)
    desired_json = json.dumps(
        {
            "name": spec["name"],
            "description": spec["description"],
            "initialPageName": spec["initialPageName"],
            "pages": normalize_pages(spec),
        },
        separators=(",", ":"),
    )

    template = r"""/* Unsupported Box Apps private API lab. No delete, publish, or share calls. */
window.__clmPrivateAppsLabPromise = (async () => {
  "use strict";
  const expectedHostname = __HOSTNAME__;
  const requiredPrefix = "__PREFIX__";
  const desired = __DESIRED__;
  const base = "/app-api/crooze/call-meteor-method/v1/";

  if (location.hostname !== expectedHostname) {
    throw new Error(`Target guard failed: expected ${expectedHostname}, received ${location.hostname}`);
  }
  if (!desired.name.startsWith(requiredPrefix)) {
    throw new Error("Title guard failed: private API labs require the CLM Surface API Lab prefix");
  }

  const canonical = (value) =>
    Array.isArray(value)
      ? value.map(canonical)
      : value && typeof value === "object"
      ? Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonical(value[key])]))
      : value;
  const sortable = (value) => JSON.stringify(canonical(value));

  const normalizeSectionForCompare = (section) => ({
    id: section?.id,
    title: section?.title || "",
    position: section?.position || 0,
    size: section?.size || 1,
    layout: section?.layout || {},
    items: [],
  });

  const normalizePageForCompare = (page) => ({
    id: page?.id || page?._id || "",
    name: page?.name || "",
    sections: Array.isArray(page?.sections)
      ? page.sections.map(normalizeSectionForCompare)
      : [],
    items: Array.isArray(page?.items) ? [] : [],
  });

  const comparePages = (pagesA, pagesB) =>
    sortable((pagesA || []).map(normalizePageForCompare)) ===
    sortable((pagesB || []).map(normalizePageForCompare));

  const reconcilePages = (app) => {
    if (!Array.isArray(desired.pages) || desired.pages.length === 0) return (app.pages || []).map((page) => page);
    const byName = new Map((app.pages || []).map((page) => [String(page?.name || ""), page]));
    return desired.pages.map((desiredPage) => {
      const existing = byName.get(String(desiredPage.name || "")) || {};
      if (!existing.name && desiredPage.name !== desired.initialPageName) {
        throw new Error(`Existing page not found: ${desiredPage.name}`);
      }
      return {
        _id: existing._id,
        name: desiredPage.name,
        sections: Array.isArray(desiredPage.sections)
          ? desiredPage.sections.map((section) => ({
              id: section.id,
              title: section.title,
              position: section.position,
              size: section.size,
              layout: section.layout || {},
              items: [],
            }))
          : (existing.sections || []),
        items: existing.items || [],
      };
    });
  };

  const call = async (method, args) => {
    const response = await fetch(base + method, {
      method: "POST",
      credentials: "include",
      headers: {"content-type":"application/json"},
      body: JSON.stringify(args),
    });
    const body = await response.json();
    if (!response.ok) {
      throw new Error(`${method} failed: ${body?.message || `HTTP ${response.status}`}`);
    }
    return body;
  };

  const findMatches = async () => {
    const listed = await call("app.list", []);
    return (listed.apps || []).filter((app) => app?.name === desired.name);
  };

  let matches = await findMatches();
  if (matches.length > 1) {
    throw new Error(`Duplicate guard failed: found ${matches.length} exact-title Apps`);
  }

  let outcome = "unchanged";
  if (matches.length === 0) {
    await call("app.create", [{name: desired.name, initialPageName: desired.initialPageName}]);
    outcome = "created";
    matches = await findMatches();
    if (matches.length !== 1) {
      throw new Error(`Create verification failed: found ${matches.length} exact-title Apps`);
    }
  }

  const app = await call("app.get", [matches[0]._id]);
  const desiredPages = reconcilePages(app);
  const currentPages = app.pages || [];
  const pageStructureMatches = comparePages(desiredPages, currentPages);

  if (app.description !== desired.description || !pageStructureMatches) {
    let locked = false;
    try {
      await call("app.lock", [app._id]);
      locked = true;
      const payload = {
        _id: app._id,
        name: app.name,
        description: desired.description,
        pages: desiredPages.map((page) => ({
          _id: page._id,
          name: page.name,
          sections: page.sections,
          items: page.items,
        })),
        fromVersion: app.versionNumber,
      };
      await call("app.update.all", [payload]);
      outcome = outcome === "created" ? "created-and-updated" : "updated";
    } finally {
      if (locked) {
        try { await call("app.cancelEdit", [app._id]); } catch {}
      }
    }
  }

  const verified = await call("app.get", [matches[0]._id]);
  if (verified.description !== desired.description) {
    throw new Error("Description verification failed");
  }

  const result = {
    outcome,
    title: verified.name,
    versionNumber: verified.versionNumber,
    pageCount: (verified.pages || []).length,
    sectionCount: (verified.pages || []).reduce((count, page) => count + (page.sections || []).length, 0),
    blockCount: (verified.pages || []).reduce((count, page) => count + (page.items || []).length, 0),
  };
  console.info("CLM_APPS_PRIVATE_API_LAB", JSON.stringify(result));
  return result;
})();
"""

    script = (
        template.replace("__HOSTNAME__", json.dumps(hostname))
        .replace("__PREFIX__", LAB_TITLE_PREFIX)
        .replace("__DESIRED__", desired_json)
    )
    return " ".join(line.strip() for line in script.splitlines() if line.strip()) + "\n"


def write_executor(
    spec_path: Path,
    config_path: Path,
    output_path: Path,
    acknowledgement: str,
) -> None:
    if acknowledgement != ACKNOWLEDGEMENT:
        raise ExperimentalAppsProvisionerError(
            f"Refusing to build executor without --acknowledge {ACKNOWLEDGEMENT!r}"
        )
    script = executor_script(load_json(spec_path), config_hostname(load_json(config_path)))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(script, encoding="utf-8")
    display_path = output_path.relative_to(ROOT) if output_path.is_relative_to(ROOT) else output_path
    print(f"Prepared guarded private API Apps lab executor: {display_path}")
    print("It requires an authenticated Box web-app tab on the configured hostname.")
    print(
        "It can create, update, or leave unchanged only the exact lab title; "
        "it never deletes, publishes, or shares."
    )


def dry_run(spec_path: Path, config_path: Path) -> None:
    spec = load_json(spec_path)
    validate_spec(spec)
    hostname = config_hostname(load_json(config_path))
    print(f"DRY RUN  target: {hostname}")
    print(f"DRY RUN  exact lab title: {spec['name']}")
    page_count = len(normalize_pages(spec))
    print(f"DRY RUN  pages configured: {page_count}")
    print("DRY RUN  create/update/unchanged only; never delete, publish, or share")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    modes = result.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--write-executor", action="store_true")
    result.add_argument("--acknowledge", default="")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.dry_run:
            dry_run(args.spec, args.config)
        else:
            write_executor(args.spec, args.config, args.output, args.acknowledge)
    except ExperimentalAppsProvisionerError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
