# Salesforce CLM Record Contract

This document completes manual tasks MT-030 and MT-031 at the repository-design level. Deployment and administrator validation remain separate tasks.

## Decision

Use a dedicated custom object:

```text
CLM_Contract__c
```

Do not overload Salesforce `Contract`, Opportunity, or an org-specific managed CLM object. The demo needs a portable structured record without introducing an Account, Opportunity, quote, or managed-package dependency.

## Ownership and sharing

| Decision | Value |
|---|---|
| Record owner | Standard `OwnerId`; authenticated integration user owns new records unless an approved assignment rule changes ownership |
| Business owner | Optional `Business_Owner__c` lookup to an active Salesforce User |
| Unresolved business owner | Preserve the validated Form value in `Business_Owner_Name__c`; do not create or guess a User |
| Internal sharing | Private |
| External sharing | Private |
| Access grant | Permission set plus the intended Lightning/Experience sharing configuration |

## Record identity and idempotency

- `Contract_ID__c` is required, unique, and an external ID.
- The Box HTTPS Connector uses Salesforce's standard external-ID REST resource to upsert by `Contract_ID__c`.
- A retry with the same `contractId` returns the existing `recordId`.
- The human-readable `Name` is `<counterparty> <contractType>`.
- Redline task routing uses a separate idempotency key: `contractId:redlineFileId:domain`.

## System-of-record boundary

Salesforce stores validated structured context and Box references. Contract files, clauses, versions, review evidence, generated documents, signatures, and content audit history remain in Box.

## Field groups

| Group | Fields |
|---|---|
| Identity | `Contract_ID__c`, `Name`, `Record_Source__c` |
| Intake | `Requester_Name__c`, `Requester_Email__c`, `Counterparty__c`, `Contract_Type__c`, `Deal_Value__c`, `Term_Months__c`, `Region__c`, `Data_Category__c`, `Target_Signature_Date__c`, `Special_Terms_Risk_Notes__c` |
| Ownership | `OwnerId`, `Business_Owner__c`, `Business_Owner_Name__c` |
| Lifecycle | `Status__c`, `Risk_Level__c`, `Latest_Routing_Status__c`, `Open_Review_Task_Count__c`, `Last_Box_Sync__c` |
| Box references | `Box_Workspace_Folder_ID__c`, `Box_Workspace_URL__c`, `Box_Intake_File_ID__c`, `Box_Redline_File_ID__c`, `Intake_Workflow_Run_ID__c` |

Machine-readable mapping: `config/salesforce/clm-contract-record.json`.

Deployable metadata: `clm-react-app/force-app/main/default/objects/CLM_Contract__c/`.

## Intake integration

```text
PATCH /services/data/{apiVersion}/sobjects/CLM_Contract__c/Contract_ID__c/{urlEncodedContractId}
```

No custom Apex REST service is required for intake. The approved Box Automate branch maps validated values directly to Salesforce field API names and sends the request through an OAuth 2.0 HTTPS connection.

An insert can return a record ID, while a successful update can return `204 No Content`. Therefore, the next workflow step retrieves the record through the same external-ID resource:

```text
GET /services/data/{apiVersion}/sobjects/CLM_Contract__c/Contract_ID__c/{urlEncodedContractId}?fields=Id,Contract_ID__c,Box_Workspace_Folder_ID__c
```

Response mapping:

```json
{
  "recordId": "Id",
  "contractId": "Contract_ID__c",
  "boxFolderId": "Box_Workspace_Folder_ID__c"
}
```

The Box Automate integration must:

1. Authenticate through an administrator-managed Salesforce OAuth 2.0 connection.
2. Use a dedicated integration user with access only to the required object and fields.
3. Validate the Box folder and file IDs.
4. Resolve `Business_Owner__c` only from an existing active User; otherwise leave it null and preserve the supplied name.
5. Upsert by `Contract_ID__c`.
6. Look up and return the same record on retry.
7. Never accept contract bytes, access tokens, connector secrets, or unreviewed AI output.

SOQL is not required for this path. If the Box Automate builder cannot retrieve by external ID, a second standard REST query operation may select `Id`, `Contract_ID__c`, and `Box_Workspace_Folder_ID__c` by the generated contract ID.

## Form and Extract mapping

The authoritative mapping is the `fieldMappings` array in `config/salesforce/clm-contract-record.json`. Key rules:

- Form values are written only after the Box human-validation gate.
- `riskLevel` is written only when a human validated the Extract/AI result.
- `boxFolderId` must be the allowlisted workspace associated with the intake.
- `boxFolderUrl` must use `kadams.ent.box.com` for this live demo.
- The uploaded package stays in Box; Salesforce receives only its Box file ID.

## Deployment acceptance criteria

- Custom object and fields deploy successfully.
- Permission set grants only the intended operator access.
- Private sharing is confirmed in the target org.
- Standard REST upsert creates one record and the follow-up lookup returns the required context.
- A duplicate request returns the same record.
- Invalid fields, unauthorized folders, and unresolved users fail closed.
- React launches with the returned record, contract, and Box folder IDs.
