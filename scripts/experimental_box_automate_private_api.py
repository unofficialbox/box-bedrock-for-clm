#!/usr/bin/env python3
"""Build a guarded authenticated-browser executor for an empty Box Automate private-API lab draft."""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = ROOT / "config/box/private-api-lab-automate-definition.json"
DEFAULT_CONFIG = ROOT / "config/runtime/demo-environment.json"
DEFAULT_BOOTSTRAP = ROOT / "config/runtime/bootstrap-state.json"
DEFAULT_OUTPUT = ROOT / "config/runtime/generated/box/private-api-lab-automate-provisioner.js"
DEFAULT_INSPECTOR_OUTPUT = ROOT / "config/runtime/generated/box/private-api-automate-graph-inspector.js"
LAB_TITLE_PREFIX = "CLM Surface API Lab - "
FORBIDDEN_TITLES = {
    "CLM - Contract Intake Enrichment",
    "CLM - Redline Domain Review Routing",
    "CLM - Approval Packet Readiness",
    "CLM - Executed Agreement Obligations",
}
ACKNOWLEDGEMENT = "I understand this uses an unsupported Box private API"

LIST_QUERY = """query ListPrivateLabWorkflows($request: ItemV2QueryRequest!) {
  itemV2s(request: $request) {
    edges {
      node {
        id
        name
        type
        data {
          ... on WorkflowData {
            description
            status
            trigger { id triggerType }
            outcomes { id }
            gateways { id }
            edges { id }
          }
        }
      }
    }
  }
}"""

CREATE_QUERY = """mutation CreateItemV2($input: CreateItemV2Input!) {
  createItemV2(input: $input) {
    value {
      id
      name
      type
      data {
        ... on WorkflowData {
          description
          status
        }
      }
    }
  }
}"""

UPDATE_QUERY = """mutation UpdateItemV2(
  $workflow: UpdateWorkflowInput!
  $itemV2: UpdateItemV2Input!
  $itemIdentity: UpdateItemIdentityInput!
  $includeItemIdentity: Boolean!
) {
  updateWorkflow(input: $workflow) { id description }
  updateItemV2(input: $itemV2) { id name }
  updateItemIdentity(input: $itemIdentity) @include(if: $includeItemIdentity) { name }
}"""

LIST_VARIABLES = {
    "request": {
        "limit": 100,
        "orderBy": [
            {
                "direction": "DESC",
                "field": "OTHER",
                "otherField": "box:published_workflow:updatedAt",
            }
        ],
        "query": {
            "predicate": "box:item:type = :appItemType AND box:published_workflow:status IS NOT NULL",
            "params": {"appItemType": "workflow"},
        },
    }
}


class ExperimentalAutomateProvisionerError(RuntimeError):
    """Raised when the Automate lab executor cannot be built safely."""


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ExperimentalAutomateProvisionerError(f"Missing required file: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ExperimentalAutomateProvisionerError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise ExperimentalAutomateProvisionerError(f"Expected a JSON object in {path}")
    return value


def validate_hostname(hostname: str) -> str:
    normalized = hostname.strip().lower()
    if not re.fullmatch(r"[a-z0-9.-]+\.box\.com", normalized):
        raise ExperimentalAutomateProvisionerError(
            "hostname must be a bare Box hostname ending in .box.com"
        )
    return normalized


def validate_spec(spec: dict[str, Any]) -> None:
    problems: list[str] = []
    name = spec.get("name")
    if spec.get("schemaVersion") != 1:
        problems.append("schemaVersion must be 1")
    if not isinstance(name, str) or not name.startswith(LAB_TITLE_PREFIX):
        problems.append(f"name must begin with {LAB_TITLE_PREFIX!r}")
    elif name in FORBIDDEN_TITLES:
        problems.append(f"name is forbidden for private API experiments: {name}")
    if not isinstance(spec.get("description"), str) or not spec["description"].strip():
        problems.append("description must be a non-empty string")
    graph = spec.get("graph")
    manual_start = isinstance(graph, dict) and isinstance(graph.get("trigger"), dict)
    expected_policy = (
        "reconcile-exact-title-manual-start-only"
        if manual_start
        else "reconcile-exact-title-empty-draft-only"
    )
    expected = {
        "mode": "experimental-private-graphql",
        "existingWorkflowPolicy": expected_policy,
        "delete": False,
        "publish": False,
        "activate": False,
        "share": False,
        "run": False,
    }
    provisioning = spec.get("provisioning")
    if not isinstance(provisioning, dict):
        problems.append("provisioning must be an object")
    else:
        for key, value in expected.items():
            if provisioning.get(key) != value:
                problems.append(f"provisioning.{key} must be {value!r}")
    if graph is not None:
        if not isinstance(graph, dict):
            problems.append("graph must be an object")
        else:
            trigger = graph.get("trigger")
            if not isinstance(trigger, dict):
                problems.append("graph.trigger must be an object")
            else:
                if trigger.get("type") != "manualStart":
                    problems.append("graph.trigger.type must be 'manualStart'")
                if not isinstance(trigger.get("scopeFolder"), str) or not trigger["scopeFolder"].strip():
                    problems.append("graph.trigger.scopeFolder must be a non-empty runtime folder alias")
                if trigger.get("includeSubfolders") is not False:
                    problems.append("graph.trigger.includeSubfolders must be false")
                if not isinstance(trigger.get("description", ""), str):
                    problems.append("graph.trigger.description must be a string")
    if problems:
        raise ExperimentalAutomateProvisionerError(
            "Invalid private API Automate lab definition:\n- " + "\n- ".join(problems)
        )


def config_hostname(config: dict[str, Any]) -> str:
    box = config.get("box")
    if not isinstance(box, dict):
        raise ExperimentalAutomateProvisionerError("config.box must be an object")
    return validate_hostname(str(box.get("hostname") or ""))


def runtime_folder_id(bootstrap: dict[str, Any], alias: str) -> str:
    box = bootstrap.get("box")
    folders = box.get("folders") if isinstance(box, dict) else None
    folder_id = folders.get(alias) if isinstance(folders, dict) else None
    if not isinstance(folder_id, str) or not folder_id.isdigit():
        raise ExperimentalAutomateProvisionerError(
            f"bootstrap.box.folders.{alias} must be a numeric Box folder ID"
        )
    return folder_id


def deterministic_graph(spec: dict[str, Any], bootstrap: dict[str, Any] | None) -> dict[str, Any] | None:
    graph = spec.get("graph")
    if graph is None:
        return None
    if bootstrap is None:
        raise ExperimentalAutomateProvisionerError(
            "Manual Start graph generation requires the gitignored bootstrap state"
        )
    trigger_spec = graph["trigger"]
    alias = trigger_spec["scopeFolder"]
    name = spec["name"]
    trigger_id = f"trigger_{uuid.uuid5(uuid.NAMESPACE_URL, f'clm-automate:{name}:manual-start')}"
    edge_id = f"edge_{uuid.uuid5(uuid.NAMESPACE_URL, f'clm-automate:{name}:manual-start-edge')}"
    return {
        "trigger": {
            "id": trigger_id,
            "triggerType": "MANUAL",
            "triggerSubtype": "START",
            "description": trigger_spec.get("description", ""),
            "parameters": {
                "parentFolderId": runtime_folder_id(bootstrap, alias),
                "includeSubfolders": "false",
            },
            "condition": None,
        },
        "outcomes": [],
        "gateways": [],
        "edges": [
            {
                "id": edge_id,
                "source": trigger_id,
                "target": None,
                "edgeType": "BASIC",
                "condition": None,
                "label": None,
            }
        ],
    }


def executor_script(
    spec: dict[str, Any],
    hostname: str,
    bootstrap: dict[str, Any] | None = None,
) -> str:
    validate_spec(spec)
    hostname = validate_hostname(hostname)
    graph = deterministic_graph(spec, bootstrap)
    desired = json.dumps(
        {
            "name": spec["name"],
            "description": spec["description"],
            "mode": "manualStart" if graph else "empty",
            "graph": graph,
        },
        separators=(",", ":"),
    )
    script = f'''/* Unsupported Box Automate private API lab. Inactive draft only. */
window.__clmPrivateAutomateLabPromise = (async () => {{
  "use strict";
  const expectedHostname = {json.dumps(hostname)};
  const requiredPrefix = {json.dumps(LAB_TITLE_PREFIX)};
  const desired = {desired};
  if (location.hostname !== expectedHostname) throw new Error(`Target guard failed: expected ${{expectedHostname}}, received ${{location.hostname}}`);
  if (!location.pathname.startsWith("/automate")) throw new Error("Surface guard failed: open Box Automate first");
  if (!desired.name.startsWith(requiredPrefix)) throw new Error("Title guard failed: private API labs require the CLM Surface API Lab prefix");
  const client = window.__APOLLO_CLIENT__;
  const chunks = window.webpackChunkbox_workflow_client;
  if (!client || !chunks) throw new Error("Authenticated Automate page client is unavailable");
  let webpackRequire;
  chunks.push([[Date.now()], {{}}, (require) => {{ webpackRequire = require; }}]);
  const gql = webpackRequire?.(38824)?.U;
  if (typeof gql !== "function") throw new Error("Automate GraphQL document parser is unavailable");
  const listDocument = gql({json.dumps(LIST_QUERY)});
  const createDocument = gql({json.dumps(CREATE_QUERY)});
  const updateDocument = gql({json.dumps(UPDATE_QUERY)});
  const listVariables = {json.dumps(LIST_VARIABLES, separators=(",", ":"))};
  const list = async () => {{
    const response = await client.query({{query: listDocument, variables: listVariables, fetchPolicy: "network-only"}});
    return response.data?.itemV2s?.edges || [];
  }};
  const exactMatches = async () => (await list()).filter((edge) => edge.node?.name === desired.name);
  let matches = await exactMatches();
  if (matches.length > 1) throw new Error(`Duplicate guard failed: found ${{matches.length}} exact-title workflows`);
  let outcome = "unchanged";
  if (matches.length === 0) {{
    await client.mutate({{
      mutation: createDocument,
      variables: {{input: {{name: desired.name, type: "workflow", data: {{workflow: {{description: desired.description, trigger: null, outcomes: [], gateways: [], edges: []}}}}}}}},
    }});
    outcome = "created";
    matches = await exactMatches();
    if (matches.length !== 1) throw new Error(`Create verification failed: found ${{matches.length}} exact-title workflows`);
  }}
  let node = matches[0].node;
  const data = node.data || {{}};
  const hasGraph = Boolean(data.trigger) || (data.outcomes || []).length > 0 || (data.gateways || []).length > 0 || (data.edges || []).length > 0;
  if (desired.mode === "empty" && hasGraph) throw new Error("Graph guard failed: this executor only reconciles an empty lab draft");
  if (desired.mode === "manualStart" && hasGraph) {{
    if (!data.trigger || data.trigger.triggerType !== "MANUAL") throw new Error("Graph guard failed: expected only a Manual Start trigger");
    if ((data.outcomes || []).length !== 0 || (data.gateways || []).length !== 0 || (data.edges || []).length !== 1) throw new Error("Graph guard failed: expected one trigger, one edge, and no outcomes or gateways");
  }}
  if (data.status !== "INACTIVE") throw new Error(`Status guard failed: expected INACTIVE, received ${{data.status}}`);
  const desiredTriggerId = desired.graph?.trigger?.id || null;
  const desiredEdgeId = desired.graph?.edges?.[0]?.id || null;
  const graphMatches = desired.mode === "empty"
    ? !hasGraph
    : data.trigger?.id === desiredTriggerId && data.trigger?.triggerType === "MANUAL" && (data.edges || []).length === 1 && data.edges[0]?.id === desiredEdgeId;
  if (data.description !== desired.description || !graphMatches) {{
    const workflow = {{
      id: node.id,
      name: node.name,
      description: desired.description,
      trigger: desired.graph?.trigger || null,
      outcomes: desired.graph?.outcomes || [],
      gateways: desired.graph?.gateways || [],
      edges: desired.graph?.edges || [],
    }};
    await client.mutate({{
      mutation: updateDocument,
      variables: {{
        workflow,
        itemV2: {{id: node.id, name: node.name, type: "workflow"}},
        itemIdentity: {{id: node.id, name: node.name, type: "workflow"}},
        includeItemIdentity: true,
      }},
    }});
    outcome = outcome === "created" ? "created-and-updated" : "updated";
  }}
  matches = await exactMatches();
  node = matches[0]?.node;
  if (!node || node.data?.description !== desired.description) throw new Error("Description verification failed");
  const verifiedGraph = desired.mode === "empty"
    ? !node.data?.trigger && (node.data?.edges || []).length === 0
    : node.data?.trigger?.id === desiredTriggerId && node.data?.trigger?.triggerType === "MANUAL" && (node.data?.edges || []).length === 1 && node.data.edges[0]?.id === desiredEdgeId;
  if (!verifiedGraph) throw new Error("Graph verification failed");
  const result = {{
    outcome,
    title: node.name,
    status: node.data.status,
    triggerCount: node.data.trigger ? 1 : 0,
    outcomeCount: (node.data.outcomes || []).length,
    gatewayCount: (node.data.gateways || []).length,
    edgeCount: (node.data.edges || []).length,
    published: false,
    activated: false,
    shared: false,
    run: false,
    deleted: false,
  }};
  console.info("CLM_AUTOMATE_PRIVATE_API_LAB", JSON.stringify(result));
  return result;
}})();
'''
    return " ".join(line.strip() for line in script.splitlines() if line.strip()) + "\n"


def inspector_script(hostname: str, expected_title: str | None = None) -> str:
    """Build a read-only reader for an existing unpublished Automate draft.

    The write executor above only ever reconciles a lab draft, because the GraphQL
    mutation shape for outcome types beyond an empty or Manual Start graph has not
    been observed. Reading an existing workflow is a separate, verified capability:
    the editor exposes the server-provided definition in client application state
    once the page has loaded, so the graph can be captured without any mutation.

    This script issues no GraphQL operation at all. It reads already-loaded state,
    redacts identifiers, and prints a structural summary.
    """
    hostname = validate_hostname(hostname)
    title = json.dumps(expected_title) if expected_title else "null"
    script = f'''/* Unsupported Box Automate private API reader. Read-only; issues no GraphQL operation and performs no mutation. */
window.__clmPrivateAutomateInspectionPromise = (async () => {{
  "use strict";
  const expectedHostname = {json.dumps(hostname)};
  const expectedTitle = {title};
  if (location.hostname !== expectedHostname) throw new Error(`Target guard failed: expected ${{expectedHostname}}, received ${{location.hostname}}`);
  if (!location.pathname.startsWith("/automate")) throw new Error("Surface guard failed: open Box Automate first");
  const container = document.getElementById("app");
  const fiberKey = container && Object.keys(container).find((key) => key.startsWith("__reactContainer"));
  if (!fiberKey) throw new Error("Automate editor state is unavailable; let the workflow finish loading first");
  const isGraph = (value) => {{
    if (!value || typeof value !== "object") return false;
    const keys = Object.keys(value);
    return keys.includes("outcomes") && keys.includes("trigger") && keys.includes("edges") && keys.includes("configuration");
  }};
  const seen = new Set();
  const found = [];
  const scan = (value, depth) => {{
    if (depth > 4 || !value || typeof value !== "object" || seen.has(value)) return;
    seen.add(value);
    if (isGraph(value)) {{ found.push(value); return; }}
    for (const key of Object.keys(value).slice(0, 40)) {{ try {{ scan(value[key], depth + 1); }} catch (error) {{ void error; }} }}
  }};
  const queue = [container[fiberKey]];
  let visited = 0;
  while (queue.length && visited < 30000) {{
    const fiber = queue.shift();
    if (!fiber) continue;
    visited += 1;
    try {{ scan(fiber.memoizedState, 0); }} catch (error) {{ void error; }}
    try {{ scan(fiber.memoizedProps, 0); }} catch (error) {{ void error; }}
    if (fiber.child) queue.push(fiber.child);
    if (fiber.sibling) queue.push(fiber.sibling);
  }}
  const size = (value) => (value && typeof value === "object" ? Object.keys(value).length : 0);
  found.sort((left, right) => size(right.outcomes) - size(left.outcomes));
  const workflow = found[0];
  if (!workflow) throw new Error("No loaded workflow graph was found in the editor state");
  const configuration = workflow.configuration || {{}};
  if (expectedTitle !== null && configuration.name !== expectedTitle) throw new Error(`Title guard failed: expected ${{expectedTitle}}, received ${{configuration.name}}`);
  const everPublished = Boolean(configuration.firstPublishedAt || configuration.lastPublishedAt);
  if (everPublished) throw new Error("Publication guard failed: this reader only inspects a workflow that has never been published");
  const guid = /[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}/gi;
  const digits = /\\b\\d{{6,}}\\b/g;
  const mail = /[^\\s"',]+@[^\\s"',]+\\.[a-z]{{2,}}/gi;
  const redact = (value) => {{
    if (typeof value === "string") return value.replace(guid, "<guid>").replace(mail, "<email>").replace(digits, "<id>");
    if (Array.isArray(value)) return value.map(redact);
    if (value && typeof value === "object") {{
      const out = {{}};
      for (const [key, child] of Object.entries(value)) out[redact(key)] = redact(child);
      return out;
    }}
    return value;
  }};
  const result = {{
    name: configuration.name,
    description: redact(configuration.description || ""),
    status: everPublished ? "PUBLISHED" : "DRAFT",
    statusSource: "derived from publication timestamps; the loaded editor state exposes no status enum",
    everPublished,
    trigger: redact(workflow.trigger || null),
    outcomes: Object.values(workflow.outcomes || {{}}).map(redact),
    gateways: Object.values(workflow.gateways || {{}}).map(redact),
    edges: (workflow.edges || []).map(redact),
    graphqlOperationsIssued: 0,
    mutated: false,
    saved: false,
    published: false,
    activated: false,
    shared: false,
    run: false,
    deleted: false,
  }};
  console.info("CLM_AUTOMATE_PRIVATE_API_INSPECTION", JSON.stringify(result));
  return result;
}})();
'''
    return " ".join(line.strip() for line in script.splitlines() if line.strip()) + "\n"


def write_inspector(
    config_path: Path,
    output_path: Path,
    acknowledgement: str,
    expected_title: str | None,
) -> None:
    if acknowledgement != ACKNOWLEDGEMENT:
        raise ExperimentalAutomateProvisionerError(
            f"Refusing to build inspector without --acknowledge {ACKNOWLEDGEMENT!r}"
        )
    script = inspector_script(config_hostname(load_json(config_path)), expected_title)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(script, encoding="utf-8")
    display_path = output_path.relative_to(ROOT) if output_path.is_relative_to(ROOT) else output_path
    print(f"Prepared read-only private API Automate graph inspector: {display_path}")
    print("It requires an authenticated Box Automate editor page on the configured hostname.")
    print("It issues no GraphQL operation, mutates nothing, and refuses a workflow that has ever been published.")
    print("Review and sanitize its output before committing any capture.")


def write_executor(
    spec_path: Path,
    config_path: Path,
    bootstrap_path: Path,
    output_path: Path,
    acknowledgement: str,
) -> None:
    if acknowledgement != ACKNOWLEDGEMENT:
        raise ExperimentalAutomateProvisionerError(
            f"Refusing to build executor without --acknowledge {ACKNOWLEDGEMENT!r}"
        )
    spec = load_json(spec_path)
    bootstrap = load_json(bootstrap_path) if spec.get("graph") is not None else None
    script = executor_script(spec, config_hostname(load_json(config_path)), bootstrap)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(script, encoding="utf-8")
    display_path = output_path.relative_to(ROOT) if output_path.is_relative_to(ROOT) else output_path
    print(f"Prepared guarded private API Automate lab executor: {display_path}")
    print("It requires an authenticated Box Automate page on the configured hostname.")
    print("It manages one inactive lab draft and never deletes, publishes, activates, shares, or runs it.")


def dry_run(spec_path: Path, config_path: Path, bootstrap_path: Path) -> None:
    spec = load_json(spec_path)
    validate_spec(spec)
    hostname = config_hostname(load_json(config_path))
    graph = deterministic_graph(spec, load_json(bootstrap_path) if spec.get("graph") is not None else None)
    print(f"DRY RUN  target: {hostname}")
    print(f"DRY RUN  exact lab title: {spec['name']}")
    print(f"DRY RUN  graph: {'Manual Start only' if graph else 'empty'}")
    print("DRY RUN  inactive draft only; never delete, publish, activate, share, or run")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    result.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    result.add_argument("--bootstrap", type=Path, default=DEFAULT_BOOTSTRAP)
    result.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    result.add_argument("--inspector-output", type=Path, default=DEFAULT_INSPECTOR_OUTPUT)
    result.add_argument(
        "--expect-title",
        default="",
        help="Refuse to inspect unless the loaded workflow carries this exact title.",
    )
    modes = result.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--write-executor", action="store_true")
    modes.add_argument(
        "--write-inspector",
        action="store_true",
        help="Build a read-only reader for an existing unpublished draft. Issues no GraphQL operation.",
    )
    result.add_argument("--acknowledge", default="")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.dry_run:
            dry_run(args.spec, args.config, args.bootstrap)
        elif args.write_inspector:
            write_inspector(
                args.config,
                args.inspector_output,
                args.acknowledge,
                args.expect_title or None,
            )
        else:
            write_executor(args.spec, args.config, args.bootstrap, args.output, args.acknowledge)
    except ExperimentalAutomateProvisionerError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
