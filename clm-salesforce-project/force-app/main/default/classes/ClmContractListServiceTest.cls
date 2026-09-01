@IsTest
private class ClmContractListServiceTest {

    private static void call() {
        RestRequest request = new RestRequest();
        request.requestURI = '/services/apexrest/clm/contracts';
        request.httpMethod = 'GET';
        RestContext.request = request;
        RestContext.response = new RestResponse();
        ClmContractListService.listContracts();
    }

    private static List<Object> body() {
        return (List<Object>) JSON.deserializeUntyped(RestContext.response.responseBody.toString());
    }

    @IsTest
    static void returnsContractsForTheDashboard() {
        insert new CLM_Contract__c(
            Name = 'Northstar Health System MSA Package',
            Contract_ID__c = 'CLM-2026-0017',
            Counterparty__c = 'Northstar Health System',
            Status__c = 'Legal Review'
        );

        Test.startTest();
        call();
        Test.stopTest();

        System.assertEquals(200, RestContext.response.statusCode);
        List<Object> rows = body();
        System.assertEquals(1, rows.size(), 'The dashboard must see the contract');
        Map<String, Object> row = (Map<String, Object>) rows[0];
        System.assertEquals('CLM-2026-0017', row.get('contractId'));
        System.assertEquals('Northstar Health System', row.get('counterparty'));
        System.assertEquals('Legal Review', row.get('status'));
        System.assert(row.containsKey('recordId'), 'The record id is what the workspace resolves a Box folder from');
    }

    @IsTest
    static void returnsAnEmptyListWhenThereAreNoContracts() {
        Test.startTest();
        call();
        Test.stopTest();

        System.assertEquals(200, RestContext.response.statusCode, 'An empty org is not an error');
        System.assertEquals(0, body().size());
    }

    @IsTest
    static void publishesOnlyTheProjectedFields() {
        // The response is what a site visitor can read, so its shape is a security
        // boundary rather than a convenience. Widening it must be a deliberate edit.
        insert new CLM_Contract__c(
            Name = 'Projection check',
            Contract_ID__c = 'CLM-TEST-1',
            Requester_Email__c = 'private@example.com',
            Special_Terms_Risk_Notes__c = 'confidential note'
        );

        Test.startTest();
        call();
        Test.stopTest();

        Map<String, Object> row = (Map<String, Object>) body()[0];
        System.assertEquals(
            new Set<String>{
                'recordId', 'contractId', 'name', 'counterparty',
                'contractType', 'status', 'riskLevel', 'dealValue', 'termMonths',
                // The dashboard deep-links a contract straight to its Box folder, so the
                // id travels with the row. It names a folder and grants nothing: reaching
                // that folder still requires a token the endpoint mints per record.
                'boxFolderId'
            },
            row.keySet(),
            'The projection changed; confirm every field here is safe to publish'
        );
        System.assertEquals(RestContext.response.responseBody.toString().contains('confidential note'), false,
            'Risk notes must not reach the browser');
        System.assertEquals(RestContext.response.responseBody.toString().contains('private@example.com'), false,
            'Requester email must not reach the browser');
    }

    @IsTest
    static void boundsTheNumberOfRecordsReturned() {
        List<CLM_Contract__c> many = new List<CLM_Contract__c>();
        for (Integer i = 0; i < ClmContractListService.MAX_RECORDS + 5; i++) {
            many.add(new CLM_Contract__c(Name = 'Contract ' + i, Contract_ID__c = 'CLM-' + i));
        }
        insert many;

        Test.startTest();
        call();
        Test.stopTest();

        System.assertEquals(ClmContractListService.MAX_RECORDS, body().size(),
            'The list must stay bounded so the dashboard cannot become an export');
    }
}
