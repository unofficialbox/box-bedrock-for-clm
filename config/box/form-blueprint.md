# Box Form Blueprint: New Contract Request

Build this Form after `python3 scripts/demo_operator.py box-foundation`. Bind its destination to the generated `CLM-2026-Northstar / 01 - Intake` folder from `config/runtime/bootstrap-state.json`.

## Fields

| Label | Type | Required | Options / rehearsal value |
|---|---|---|---|
| Requester name | Short text | Yes | `Jordan Lee` |
| Requester email | Email | Yes | `jordan.lee@acmerobotics.example` |
| Contract ID | Short text | Yes | `CLM-2026-0017`; reuse only for the idempotency retry |
| Counterparty | Short text | Yes | `Northstar Health System` |
| Contract type | Dropdown | Yes | `MSA Package`, `DPA`, `SOW`, `Order Form`, `Procurement Agreement` |
| Deal value | Number | Yes | `2400000` |
| Contract term months | Number | Yes | `36` |
| Region | Dropdown | Yes | `US`, `EU`, `APAC`, `Global` |
| Data category | Dropdown | Yes | `None`, `Personal Data`, `PHI`, `Financial Data`, `Confidential` |
| Target signature date | Date | Yes | A future rehearsal-safe date |
| Business owner | Short text | Yes | `Account Executive` |
| Upload contract package | File upload | Yes | Generated `northstar-msa-redline-v3.pdf` |
| Special terms / risk notes | Long text | No | Mention liability, PHI, and Net 90 review triggers |

Confirmation message:

> Your contract request is in review. Legal Operations will validate extracted terms before downstream record creation.

## Build and validation

1. Build and test the Form while unpublished.
2. Verify the exact title, field order, field types, required states, options, destination, and confirmation message.
3. Obtain owner approval immediately before publishing.
4. Record the published URL in gitignored `config/runtime/demo-environment.json`.
5. Submit the smoke-test values and confirm the upload lands in this environment's generated intake folder.

Do not create a second intake Form. The Box App must reference this published Form as its sole intake action.
