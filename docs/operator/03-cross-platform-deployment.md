# Cross-Platform Agentic Orchestration Deployment Boundary

The repository currently supports two honest operating modes.

## Local demonstration mode

This mode is reproducible today:

```bash
python3 scripts/run_agentcore_mock.py
python3 -m json.tool output/agentcore/northstar-agentcore-trace.json >/dev/null
```

Deploy the Salesforce UI Bundle with `demo_operator.py salesforce-deploy`, open the React workspace, and disclose that AgentCore/Strands and Databricks are represented by deterministic local fixtures.

Run:

```bash
python3 scripts/demo_operator.py validate --scenario box-automate-agentic-orchestration
```

Do not claim managed AgentCore or Databricks execution.

## Managed integration mode

Managed mode is not a one-command deployment in this repository. Before presenting it as live, an AWS/Databricks/Agentforce administrator must provide and verify:

- Agentforce agent and application IDs plus registered actions.
- A deployed AgentCore runtime ARN and AWS region.
- Strands specialist implementations for the tool contracts under `config/agentcore/`.
- Protected AWS credentials/roles with least privilege.
- A Databricks workspace URL, SQL warehouse ID, authentication, and read-only governed dataset.
- Network/CORS configuration for the deployed Salesforce surface.
- Trace evidence showing Box, Salesforce Agentforce, and Databricks specialist calls.
- Cost, timeout, retry, teardown, and data-egress controls.

Record the non-secret values in `config/runtime/demo-environment.json`, resolve the specs, then run:

```bash
python3 scripts/demo_operator.py validate --scenario cross-platform-agentic-orchestration
```

Passing that command proves required bindings and core Box/Salesforce resources exist; it does not replace cloud-provider deployment tests. Keep the scenario labeled **local/specification-backed** until those tests are recorded.
