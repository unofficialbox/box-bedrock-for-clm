# Product and Permission Checklist

Have administrators complete this before external writes. Product names and availability may vary by subscription; an accessible screen and a small test are the authoritative checks.

| Capability | Required for | Owner | Verification |
|---|---|---|---|
| Box folders/files | Both scenarios | Box admin | Operator can open the approved parent folder and upload/delete a disposable test file |
| Enterprise metadata templates | Both | Box metadata admin | Operator can open metadata-template administration and create templates |
| Box Forms | Box Automate–Led Agentic Orchestration | Forms builder | Forms surface opens and allows an unpublished draft |
| Box Apps | Box Automate–Led Agentic Orchestration | Apps builder | Apps builder opens and supports metadata views/charts |
| Box Automate | Box Automate–Led Agentic Orchestration | Workflow admin | Automate builder exposes Form trigger, Extract Agent, Box Agent, approval, conditional split, and HTTPS Request |
| Box AI/Extract | Both | Box AI admin | Selected agents can access only the intended demo content |
| Box Hubs | Both | Hub owner | Operator can create an unpublished Hub draft |
| Box Doc Gen | Both | Doc Gen admin | A generated Word file can be marked as a template |
| Box Sign | Both | Sign admin | Sign surface opens; do not send a request during entitlement testing |
| Box CLI application | Setup automation | Box platform admin | `box users:get me --json` returns the configured enterprise and operator |
| Salesforce metadata deployment | Both | Salesforce admin | `sf org display` matches the configured org and the operator can validate a deployment |
| Salesforce API-only integration user | Box Automate–Led Agentic Orchestration | Salesforce admin | Minimum-access integration profile/license is available |
| Salesforce External Client App | Box Automate–Led Agentic Orchestration | Salesforce admin | External Client App Manager allows client credentials and Run As configuration |
| Salesforce Agentforce | Agentic/agent-assisted features | Agentforce admin | Agent builder and required action registration surfaces open |
| Salesforce UI Bundle | Cross-Platform Agentic Orchestration | Salesforce admin | UI Bundle metadata can deploy and be placed on the intended page |
| AWS AgentCore/Strands | Managed Agentic mode only | AWS admin | Runtime, roles, network path, trace, and cost controls pass deployment tests |
| Databricks | Managed Agentic mode only | Databricks admin | Read-only warehouse/query path returns the synthetic analytics dataset |

Record unavailable capabilities before choosing a scenario. Missing managed AgentCore or Databricks access requires **local demonstration mode**, not an improvised live claim.
