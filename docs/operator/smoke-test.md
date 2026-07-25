# Integrated Smoke Test

Use a clearly labeled non-production request. Record new IDs in a run log, not in repository documentation.

## Box Automate Agentic Orchestration gate

1. Upload `northstar-msa-redline-v3.pdf` into `01 - Intake` and apply the `clmContract` metadata with contract ID `CLM-2026-0017`, the queue's Northstar values (`contractType`, `counterparty`), and `requesterEmail`; confirm applying the metadata starts the intake workflow.
2. Confirm the extracted contract type is `MSA Package`, risk is reviewable as `Critical`, material deviations cite the redline, and no agent claims approval.
3. Correct unsupported values, then approve the human validation task.
4. Confirm Salesforce creates exactly one `CLM_Contract__c` record.
5. Apply the same `CLM-2026-0017` metadata to a second intake upload and confirm the same Salesforce record is updated rather than duplicated.
6. Confirm redline findings route one task per domain to real experts or the documented triage owner.
7. Confirm the App charts and views reflect the seeded metadata.
8. Confirm signature remains blocked while a required review is incomplete.
9. Stop before Doc Gen output creation or Box Sign send unless the owner separately approves that action.

## Additional Cross-Platform Agentic Orchestration gate

1. Launch the Salesforce React workspace with the new record, contract ID, and Box folder ID.
2. Confirm only the authorized Box folder loads through downscoped access.
3. Ask Agentforce for a cited package summary.
4. Confirm AgentCore/Strands traces specialist selection, tool calls, and the signature-block guardrail.
5. Confirm Databricks contributes analytical context but does not overwrite authoritative contract state.
6. Do not claim managed AWS or Databricks deployment if only the local deterministic trace is running.

## Reset

1. Disable workflows enabled only for testing.
2. Record test files, Salesforce records, tasks, workflow runs, and generated outputs.
3. Restore the intended open-task state for the next rehearsal.
4. Remove temporary collaborators only after checking that no other demo uses them.
5. Delete data only with the system owner's approval.

## Run log

```text
Date/time:
Operator:
Scenario:
Box hostname:
Salesforce org alias:
Metadata trigger / workflow run:
Salesforce record:
Created or reused task IDs:
Corrections made during validation:
Confirmation-gated actions performed:
Reset completed:
Open issues:
```
