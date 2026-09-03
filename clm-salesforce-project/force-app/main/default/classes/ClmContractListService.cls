/**
 * Same-origin endpoint that lists CLM contract records for the workspace dashboard.
 *
 * This exists so the Experience Cloud guest user reaches CLM_Contract__c only through a
 * fixed projection. `CLM_Contract_External` grants read on the object, but the records are
 * Private, so a visitor sees nothing at all without the sharing rule of MT-045 -- and where
 * that rule exists, this is the shape of what they get. The guest is granted this one
 * Apex class, and the class returns a fixed, read-only projection of a handful of
 * fields. There is no filter, sort, or field parameter, so the response cannot be
 * widened from the browser.
 *
 * `without sharing` is required rather than incidental: guest users see no
 * CLM_Contract__c records under normal sharing, so a with-sharing query returns an
 * empty list on the one surface this serves. The exposure is therefore the projection
 * below, and nothing else -- adding a field here publishes it to anyone who can open
 * the site, so add deliberately.
 *
 * Two rules the projection has to obey, both learned the hard way. It must match what the
 * GraphQL path returns, or the same dashboard says different things depending on which
 * surface answered -- Risk_Level__c was selected here long after GraphQL dropped it, so
 * Acme's own assessment of a deal reached the counterparty's browser through this door.
 * And every field must be readable by the permission sets that serve the site: Salesforce
 * enforces field-level security inside SOQL for guest users and reports an unreadable
 * field as `No such column`, which fails the whole request rather than blanking a column.
 * `scripts/validate_clm.py` checks the second rule offline.
 */
@RestResource(urlMapping='/clm/contracts/*')
global with sharing class ClmContractListService {

    /** Bounded so a large org cannot turn the dashboard into an unpaged export. */
    @TestVisible
    private static final Integer MAX_RECORDS = 50;

    global class ContractSummary {
        global String recordId;
        global String contractId;
        global String name;
        global String counterparty;
        global String contractType;
        global String status;
        global Decimal dealValue;
        global Integer termMonths;
        /** ISO date, or null while the contract is still being negotiated. */
        global String endDate;
        /** The signing subsidiary, where the counterparty contracts through several. */
        global String counterpartyEntity;
        /** The Box workspace folder this contract is associated with. */
        global String boxFolderId;
    }

    @HttpGet
    global static void listContracts() {
        RestResponse response = RestContext.response;
        response.addHeader('Content-Type', 'application/json');

        // A guest is not a counterparty with no contracts; it is nobody. Sharing would
        // return an empty list either way, and the page would then state "no contract
        // records yet" to somebody whose session has simply expired -- a claim about the
        // org made from a fact about the visitor. Refusing here keeps "empty" meaning
        // empty. Granting a guest sharing rule is MT-045, a deliberate exposure.
        if (UserInfo.getUserType() == 'Guest') {
            response.statusCode = 401;
            response.responseBody = Blob.valueOf(
                JSON.serialize(new Map<String, String>{
                    'error' => 'not_authenticated',
                    'detail' => 'Sign in to see the contracts your organisation is party to.'
                })
            );
            return;
        }

        try {
            response.statusCode = 200;
            response.responseBody = Blob.valueOf(JSON.serialize(new ContractReader().read()));
        } catch (Exception e) {
            response.statusCode = 500;
            response.responseBody = Blob.valueOf(
                JSON.serialize(new Map<String, String>{
                    'error' => 'contract_list_failed',
                    'detail' => e.getTypeName()
                })
            );
        }
    }

    /**
     * `with sharing`, deliberately, and it used to be the opposite.
     *
     * This endpoint now serves one audience: a counterparty in the Experience Cloud site.
     * The internal persona reads the pipeline through the MCP server instead. So the right
     * answer to "which contracts may this caller see" is the platform's -- the
     * CLM_Counterparty_Access sharing set maps a contract's Counterparty_Account__c to the
     * signed-in user's Contact.Account, and sharing then filters the query for free.
     *
     * While this ran `without sharing` it returned every contract in the org to whoever
     * asked. On an authenticated counterparty site that means one customer reading the
     * names, values and risk levels of every other customer's deals.
     */
    private with sharing class ContractReader {
        private List<ContractSummary> read() {
            List<ContractSummary> summaries = new List<ContractSummary>();
            for (CLM_Contract__c record : [
                SELECT Id, Name, Contract_ID__c, Counterparty__c, Counterparty_Entity__c, Contract_Type__c,
                       Status__c, Deal_Value__c, Term_Months__c,
                       End_Date__c, Box_Workspace_Folder_ID__c
                FROM CLM_Contract__c
                ORDER BY LastModifiedDate DESC
                LIMIT :MAX_RECORDS
            ]) {
                ContractSummary summary = new ContractSummary();
                summary.recordId = record.Id;
                summary.contractId = record.Contract_ID__c;
                summary.name = record.Name;
                summary.counterparty = record.Counterparty__c;
                summary.contractType = record.Contract_Type__c;
                summary.status = record.Status__c;
                summary.dealValue = record.Deal_Value__c;
                summary.termMonths = record.Term_Months__c == null
                    ? null
                    : Integer.valueOf(record.Term_Months__c);
                summary.counterpartyEntity = record.Counterparty_Entity__c;
                summary.endDate = record.End_Date__c == null
                    ? null
                    : String.valueOf(record.End_Date__c);
                summary.boxFolderId = record.Box_Workspace_Folder_ID__c;
                summaries.add(summary);
            }
            return summaries;
        }
    }
}
