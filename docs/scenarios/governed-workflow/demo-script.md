# Governed Workflow Demo Script

**Duration:** 12–15 minutes

**Audience:** Legal Operations, Sales Operations, security, and business sponsors

## Story

1. **Open the Box App.** Show portfolio status, risk, document type, package status, and the three operational actions.
2. **Start a contract.** Open the sole `Start a New Contract` Form and explain that the submission lands in governed Box content.
3. **Show deterministic enrichment.** In Automate, follow Form submission → Extract → Box/Agentforce review → human approval. Emphasize that the route is designed, inspectable, and repeatable.
4. **Show the control point.** The approval task is the boundary between draft AI evidence and the HTTPS Connector. Rejected work returns for correction.
5. **Create the structured record.** On approval, the connector performs the Salesforce standard REST external-ID upsert and lookup. Do not imply that an agent directly authorizes the write.
6. **Review redlines and clauses.** Show the metadata-backed Clause Library page and the lived-in approved-clause Hub. Explain deterministic expert routing by domain.
7. **Generate and execute.** Show Doc Gen templates, approval evidence, and the executed-agreement destination. Signature remains human-authorized.
8. **Close on governance.** Box remains the content system of record; every mutation has a known workflow stage, owner, and audit trail.

## Required callouts

- Agents summarize, extract, compare, and recommend; people approve legal positions and signature.
- The workflow path is deterministic even when individual steps use agents.
- The live Automate workflow must remain described as inactive until OAuth testing and activation are complete.
