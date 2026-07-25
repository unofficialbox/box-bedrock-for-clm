# CLM Salesforce sample records

This folder contains portable, demo-safe sample data definitions and an executable seed script.

## Captured records

- **Accounts**
  - `Northstar Health` (Healthcare)
  - `Acme Cloudworks` (Technology)

- **Contacts**
  - Alex Mendoza (`alex.mendoza@northstar.example`)
  - Sarah Kim (`sarah.kim@acmecloudworks.example`)

- **Opportunities**
  - `Northstar Master Service Agreement 2026`
  - `Acme Cloudworks Cloud Security Expansion 2026`

- **CLM Contracts**
  - `CLM-SAMPLE-NST-001`
  - `CLM-SAMPLE-ACM-001`

## Relationships populated

- `CLM_Contract__c.Counterparty_Account__c` references `Account`.
- `CLM_Contract__c.Opportunity__c` references `Opportunity`.
- Opportunities are related to their owning Accounts.
- Contacts are related to their owning Accounts.

## Seed behavior

- **Idempotent and rerunnable**
  - Accounts by `Name`
  - Contacts by `Email`
  - Opportunities by `Name` + `AccountId`
  - Contracts by `Contract_ID__c`
- Existing records are updated with required relationship fields so links stay aligned.
- Missing records are created.

## Files

- `clm-sample-records.bcl` — descriptive sample-record spec in the repository's BCL format. Mirrors the Apex values for packaging; it is not read at seed time.
- `../scripts/seed-clm-salesforce-sample-data.apex` — Apex executable and source of truth used by org seeding.
- `../scripts/seed-clm-sample-data.sh` — one-command `sf` wrapper.

## Run

```bash
./scripts/seed-clm-sample-data.sh agentforce
```
