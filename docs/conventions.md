# Conventions

Shared vocabulary and safety rules for everyone working in this repository. The root
[README](../README.md) covers what the project is and how to get running; this file holds
the governance conventions those workflows depend on.

## Readiness vocabulary

Use these exact terms in documentation, configuration, and presenter claims:

| State | Meaning |
|---|---|
| **Portable specification** | Secret-free architecture, contracts, manifests, prompts, and setup instructions exist. |
| **Local deterministic fixture** | Repeatable local data, traces, documents, UI tests, or presenter output demonstrate the contract without claiming a live integration. |
| **Deployed integration** | The capability has passed current tests in the named target environment with secret-free evidence. |
| **Presenter-ready live** | The complete scenario has current receipts, screenshots, reset evidence, and a rehearsed human-operated path. |

Never promote a capability based only on configuration files or local fixtures.

## Safety contract

- Keep credentials and target-environment identifiers in ignored runtime files.
- Use external IDs for duplicate-safe Salesforce and Box operations.
- Separate dry-run planning from explicit apply operations.
- Confirm the exact enterprise, org, folder, and record before external writes.
- Require human approval for legal positions, document generation, signature, publishing, sharing, and destructive reset actions.
- Preserve citations for material contract findings.
- Record partial failures and reconcile before retrying.
- Reset only resources owned by the current demo run and retain evidence.
