/**
 * Same-origin endpoint that lists CLM contract records for the workspace dashboard.
 *
 * This exists so the Experience Cloud guest user is never granted access to
 * CLM_Contract__c itself. `CLM_Box_Preview_Guest` deliberately carries no business
 * object permissions -- a site visitor can mint a folder-scoped Box token and reach no
 * Salesforce data directly. That property is kept here: the guest is granted this one
 * Apex class, and the class returns a fixed, read-only projection of a handful of
 * fields. There is no filter, sort, or field parameter, so the response cannot be
 * widened from the browser.
 *
 * `without sharing` is required rather than incidental: guest users see no
 * CLM_Contract__c records under normal sharing, so a with-sharing query returns an
 * empty list on the one surface this serves. The exposure is therefore the projection
 * below, and nothing else -- adding a field here publishes it to anyone who can open
 * the site, so add deliberately.
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
        global String riskLevel;
        global Decimal dealValue;
        global Integer termMonths;
    }

    @HttpGet
    global static void listContracts() {
        RestResponse response = RestContext.response;
        response.addHeader('Content-Type', 'application/json');

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

    private without sharing class ContractReader {
        private List<ContractSummary> read() {
            List<ContractSummary> summaries = new List<ContractSummary>();
            for (CLM_Contract__c record : [
                SELECT Id, Name, Contract_ID__c, Counterparty__c, Contract_Type__c,
                       Status__c, Risk_Level__c, Deal_Value__c, Term_Months__c
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
                summary.riskLevel = record.Risk_Level__c;
                summary.dealValue = record.Deal_Value__c;
                summary.termMonths = record.Term_Months__c == null
                    ? null
                    : Integer.valueOf(record.Term_Months__c);
                summaries.add(summary);
            }
            return summaries;
        }
    }
}
