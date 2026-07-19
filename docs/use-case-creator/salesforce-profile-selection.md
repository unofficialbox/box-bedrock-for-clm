# Salesforce Experience Selection

## Selected profile: internal workspace

This CLM demo uses an internal Salesforce workspace with a Multi-Framework React UI Bundle. It does not require an Experience Cloud customer portal.

| Concern | Decision |
|---|---|
| Primary users | Internal Legal Operations, Sales, Finance, Privacy, and Security reviewers |
| Primary record | `CLM_Contract__c` |
| UI | `clmreactapp` Multi-Framework React UI Bundle |
| Structured authority | Salesforce |
| Content authority | Box |
| Agent surface | Salesforce Agentforce with explicit Box and contract context |
| Access model | Private object sharing plus the least-privilege `CLM_Demo_Operator` permission set |
| Intake integration | Standard REST external-ID upsert and lookup |

See [Salesforce Record Contract](salesforce-record-contract.md) for schema, ownership, idempotency, and Box-reference rules. See `clm-salesforce-project/README.md` for deployment and runtime limitations.

Choose another Salesforce profile only if the intended audience or trust boundary changes. A customer-facing portal, partner portal, or public experience requires a separate authorization, sharing, and threat-model review; it must not be inferred from this internal workspace.
