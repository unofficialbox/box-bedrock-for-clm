# CLM Demo Scenarios

Use one track per presentation. The Northstar contract package and governance rules are shared, but the runtime story and screenshots are intentionally separate.

| Track | Short name | Orchestration model | Presenter surface | Readiness |
|---|---|---|---|---|
| [Governed Workflow](governed-workflow/README.md) | Governed Workflow | Deterministic Box Automate stages with Extract, Box/Agentforce assistance, explicit conditions, and human approval gates | Box Form, Apps, Automate, Hub, tasks, Doc Gen, Sign | Live Box surfaces; Automate activation/OAuth smoke remains gated |
| [Agentic Orchestration](agentic-orchestration/README.md) | Agentic Orchestration | AgentCore/Strands supervisor delegates to Box, Salesforce, Agentforce, and Databricks specialists under human guardrails | Salesforce Multi-Framework React workspace plus all connected platforms | Local orchestration mock and React demo; managed AWS/Databricks deployment remains future work |

## Naming rule

- Use **Governed Workflow** when the path is predetermined and agents enrich individual steps.
- Use **Agentic Orchestration** when a supervisor selects tools or specialist agents dynamically across platforms.
- Do not call the first track “fully agentic,” and do not describe the second as live until its managed integrations pass the technical validation.

Shared setup, controls, sample data, and live identifiers remain in the repository-level docs. Each scenario directory owns its presenter script, component manifest, screenshot manifest, and readiness statement.
