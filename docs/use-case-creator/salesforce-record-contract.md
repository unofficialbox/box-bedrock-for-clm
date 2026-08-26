# Salesforce Contract Record

Completes MT-030 and MT-031 at the repository-design level. Deployment and administrator validation are separate tasks.

## Decision

Use a dedicated custom object:

```text
CLM_Contract__c
```

Do not overload Salesforce `Contract` or org-specific managed CLM objects. `CLM_Contract__c` is the authoritative structured record; it links to standard Account and Opportunity records for business context.

## Ownership and sharing

| Decision | Value |
|---|---|
| Record owner | Standard `OwnerId`; authenticated integration user owns new records unless an approved assignment rule changes ownership |
| Business owner | Optional `Business_Owner__c` lookup to an active Salesforce User |
| Unresolved business owner | Preserve the validated metadata value in `Business_Owner_Name__c`; do not create or guess a User |
| Internal sharing | Private |
| External sharing | Private |
| Access grant | Permission set plus the intended Lightning/Experience sharing configuration |

## Record identity and idempotency

- `Contract_ID__c` is optional for manual demo records, but remains the external ID used by Box for duplicate-safe synchronization.
- The Box HTTPS Connector uses Salesforce's standard external-ID REST resource to upsert by `Contract_ID__c`.
- A retry with the same `contractId` returns the existing `recordId`.
- The Salesforce record form requires only three user-facing values: `Name`, `Deal_Value__c` (labeled **Amount**), and `Target_Signature_Date__c`.
- For Box intake, `Name` is generated as `CLM Intake - <contractId>`, so the trigger still asks for only Contract ID, Amount, and Target Signature Date.
- Redline task routing uses a separate idempotency key: `contractId:redlineFileId:domain`.

## System-of-record boundary

Salesforce stores validated structured context and ownership metadata. Contract files, clauses, versions, review evidence, generated documents, signatures, and content audit history remain in Box.

## Field groups

| Group | Fields |
|---|---|
| Identity | `Name`, `Contract_ID__c`, `Record_Source__c` |
| Intake | `Requester_Name__c`, `Requester_Email__c`, `Counterparty__c`, `Counterparty_Account__c`, `Opportunity__c`, `Contract_Type__c`, `Deal_Value__c`, `Term_Months__c`, `Region__c`, `Data_Category__c`, `Target_Signature_Date__c`, `Special_Terms_Risk_Notes__c` |
| Ownership | `OwnerId`, `Business_Owner__c`, `Business_Owner_Name__c` |
| Lifecycle | `Status__c`, `Risk_Level__c` |

Machine-readable mapping: `config/salesforce/clm-contract-record.bcl`.

Deployable metadata: `clm-salesforce-project/force-app/main/default/objects/CLM_Contract__c/`.

## Intake integration

> **Inbound email is the realistic first hop.** Before a contract reaches the Box intake, it usually arrives by email. The `EmailIntakeHandler` inbound email service (see [Inbound Email Intake Service](../operator/email-intake-service.md)) captures a counterparty's email onto the matching Opportunity's activity timeline and uploads the attachment **straight into that Opportunity's Box folder** via the Box for Salesforce managed package — the file is stored once, in Box, not duplicated as a Salesforce File. That handler does **not** create `CLM_Contract__c` — record creation stays in the governed path described here.

> **Proven live path vs. design target.** The workflow uses a plain **POST** create to the sobject collection (`services/data/{apiVersion}/sobjects/CLM_Contract__c`), captured in `config/box/https-connectors.bcl` as `salesforceContractCreate`. This POST was proven end to end on 2026-07-22 — but via the now-removed Box Form trigger. Intake is now sourced from the `clmContract` metadata trigger (`static.trigger.metadata.<key>`), and that metadata-triggered variant has not been re-verified live. The POST is **not idempotent**: a resubmission creates a second record. The external-ID **PATCH upsert** described below is the duplicate-safe *design target*; it is not currently the live path. Restore it — and re-verify against a live run — only if duplicate safety is required. The connector marks this in `config/box/https-connectors.bcl` (`salesforceContractCreate`, `idempotency.safe = false`).

The duplicate-safe design is an upsert by external ID:

```text
PATCH /services/data/{apiVersion}/sobjects/CLM_Contract__c/Contract_ID__c/{urlEncodedContractId}
```

No custom Apex REST service is required for intake. The approved Box Automate branch maps validated values directly to Salesforce field API names and sends the request over an OAuth 2.0 HTTPS connection.

An insert returns a record ID; a successful update returns `204 No Content`. So the next step retrieves the record through the same external-ID resource:

```text
GET /services/data/{apiVersion}/sobjects/CLM_Contract__c/Contract_ID__c/{urlEncodedContractId}?fields=Id,Contract_ID__c
```

Response mapping:

```json
{
  "recordId": "Id",
  "contractId": "Contract_ID__c"
}
```

`Counterparty_Account__c` and `Opportunity__c` are not part of the intake path: the intake metadata supplies no Account or Opportunity ID, so the connector neither writes nor reads them. They are populated by the packaged sample data or manual entry; `salesforceContractLookup` fetches only `Id` and `Contract_ID__c`.

The Box Automate integration must:

1. Authenticate through an administrator-managed Salesforce OAuth 2.0 connection.
2. Use a dedicated integration user with access only to the required object and fields.
3. Validate the Box folder and file IDs.
4. Resolve `Business_Owner__c` only from an existing active User; otherwise leave it null and preserve the supplied name.
5. Upsert by `Contract_ID__c`.
6. Look up and return the same record on retry.
7. Never accept contract bytes, access tokens, connector secrets, or unreviewed AI output.

SOQL is not required. If the Box Automate builder cannot retrieve by external ID, a second standard REST query may select `Id` and `Contract_ID__c` by the generated contract ID.

## Metadata and Extract mapping

The authoritative mapping is the `fieldMappings` array in `config/salesforce/clm-contract-record.bcl`. Key rules:

- Only Name, Amount, and Target Signature Date are mandatory on the Salesforce record layout; every other field is optional for a fast demo flow. Amount and Target Signature Date stay schema-optional so older records with blanks do not block an upgrade.
- Metadata values are written only after the Box human-validation gate.
- `riskLevel` is written only when a human validated the Extract/AI result.
- `boxFolderId` must be the allowlisted workspace associated with the intake.
- `boxFolderUrl` must use the hostname recorded for the target Box enterprise.
- The uploaded package stays in Box; Salesforce receives only its Box file ID.

## Deployment acceptance criteria

- Custom object and fields deploy successfully.
- Permission set grants only the intended operator access.
- Private sharing is confirmed in the target org.
- Standard REST upsert creates one record and the follow-up lookup returns the required context.
- A duplicate request returns the same record.
- Invalid fields, unauthorized folders, and unresolved users fail closed.
- React launches with the returned record, contract, and Box folder IDs.
