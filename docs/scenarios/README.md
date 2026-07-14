# CLM Demo Scenarios

Use one track per presentation. The Northstar contract package and governance rules are shared, but the runtime story and screenshots are intentionally separate.

Building this in a new environment? Complete [Operator Start Here](../operator/00-start-here.md) before using either presenter guide.

| Track | Short name | Orchestration model | Presenter surface | Readiness |
|---|---|---|---|---|
| [Box Automate–Led Agentic Orchestration](box-automate-agentic-orchestration/README.md) | Box Automate–Led | A designed Box Automate sequence directs Extract, Box AI, and Agentforce work through explicit conditions and human gates | Box Form, Apps, Automate, Hub, tasks, Doc Gen, Sign | Build and validate per environment; activation and OAuth smoke remain gated |
| [Cross-Platform Agentic Orchestration](cross-platform-agentic-orchestration/README.md) | Cross-Platform | An AgentCore/Strands supervisor dynamically delegates to Box, Salesforce Agentforce, and Databricks specialists | Salesforce Multi-Framework React workspace plus connected platforms | Local orchestration mock and React demo; managed AWS/Databricks deployment remains future work |

## Naming rule

- Use **Box Automate–Led Agentic Orchestration** when the path is predetermined and agents enrich individual steps.
- Use **Cross-Platform Agentic Orchestration** when a supervisor selects tools or specialist agents dynamically across platforms.
- Describe the first as **workflow-directed** and the second as **supervisor-directed**. Do not describe managed integrations as live until they pass technical validation.

Each scenario link opens one canonical, ordered guide containing orientation, architecture, flow, presenter script, screenshots, component readiness, and setup checks. Shared configuration, screenshots, generated galleries, and detailed runbooks remain single-source and are referenced from those guides.
