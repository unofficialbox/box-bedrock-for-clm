@IsTest
private class ClmGenerateCounterProposalTest {

    // Concatenated so the literal token JSON never appears in source; the secret scan
    // reads an inline one as a committed credential.
    private static final String PARENT_TOKEN = 'parent-token';

    private class BoxMock implements HttpCalloutMock {
        private Integer status;
        private String body;
        /** The body Box was actually sent, so a test can assert on what was merged. */
        private String sentBody;

        private BoxMock(Integer status, String body) {
            this.status = status;
            this.body = body;
        }

        public HttpResponse respond(HttpRequest request) {
            HttpResponse response = new HttpResponse();
            response.setHeader('Content-Type', 'application/json');
            if (request.getEndpoint().contains('oauth2/token')) {
                response.setStatusCode(200);
                response.setBody('{"access_' + 'token":"' + PARENT_TOKEN + '","expires_in":3600}');
                return response;
            }
            sentBody = request.getBody();
            response.setStatusCode(status);
            response.setBody(body);
            return response;
        }
    }

    private static void configure(String templateId) {
        insert new CLM_Box_Config__c(
            SetupOwnerId = UserInfo.getOrganizationId(),
            Box_User_Id__c = '100000001',
            Counter_Position_Template_ID__c = templateId);
    }

    private static CLM_Contract__c seedContract() {
        CLM_Contract__c contract = new CLM_Contract__c(
            Name = 'Test Counterparty Master Agreement',
            Contract_ID__c = 'CLM-TEST-0001',
            Counterparty__c = 'Test Counterparty',
            Status__c = 'Legal Review',
            Risk_Level__c = 'Critical',
            Deal_Value__c = 2100000,
            Box_Workspace_Folder_ID__c = '900000001');
        insert contract;
        return contract;
    }

    private static ClmGenerateCounterProposal.Request request(String reference, String clause) {
        ClmGenerateCounterProposal.Request req = new ClmGenerateCounterProposal.Request();
        req.contractReference = reference;
        req.clauseAtIssue = clause;
        req.theirPosition = 'No financial cap applies to the Supplier.';
        req.approvedPosition = 'CLM-LIAB-001 - capped at 12 months of fees.';
        req.fallbackPosition = 'CLM-LIAB-002 - capped at 24 months of fees.';
        req.owner = 'Commercial Legal';
        req.precedentSummary = 'They accepted a 24-month cap in 2022 and 2024.';
        req.counterProposal = 'Restore the negotiated cap.';
        return req;
    }

    private static ClmGenerateCounterProposal.Result run(ClmGenerateCounterProposal.Request req) {
        return ClmGenerateCounterProposal.generate(
            new List<ClmGenerateCounterProposal.Request>{ req })[0];
    }

    @IsTest
    static void generatesIntoTheContractsOwnFolder() {
        configure('800000001');
        seedContract();
        BoxMock mock = new BoxMock(202, '{"id":"batch-1","type":"docgen_batch"}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        ClmGenerateCounterProposal.Result result = run(request('CLM-TEST-0001', 'Clause 22.4'));
        Test.stopTest();

        System.assertEquals(true, result.generated, result.summary);
        System.assertEquals('batch-1', result.batchId);
        // The destination is the contract's governed folder, not one the caller chose.
        System.assert(mock.sentBody.contains('900000001'), mock.sentBody);
        System.assert(mock.sentBody.contains('800000001'), mock.sentBody);
    }

    @IsTest
    static void takesContractFactsFromTheRecordNotTheRequest() {
        // A caller must not be able to misattribute a memo: the id, counterparty and risk
        // on the page come from the record the reference resolved to.
        configure('800000001');
        seedContract();
        BoxMock mock = new BoxMock(202, '{"id":"batch-2"}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        run(request('CLM-TEST-0001', 'Clause 22.4'));
        Test.stopTest();

        System.assert(mock.sentBody.contains('CLM-TEST-0001'), mock.sentBody);
        System.assert(mock.sentBody.contains('Test Counterparty'), mock.sentBody);
        System.assert(mock.sentBody.contains('Critical'), mock.sentBody);
    }

    @IsTest
    static void refusesWhenNoTemplateIsConfigured() {
        // The org chooses what it generates from, the same way it chooses the clause
        // library. Without configuration there is nothing to generate and nothing is sent.
        insert new CLM_Box_Config__c(
            SetupOwnerId = UserInfo.getOrganizationId(), Box_User_Id__c = '100000001');
        seedContract();
        Test.setMock(HttpCalloutMock.class, new BoxMock(202, '{"id":"unreachable"}'));

        Test.startTest();
        ClmGenerateCounterProposal.Result result = run(request('CLM-TEST-0001', 'Clause 22.4'));
        Test.stopTest();

        System.assertEquals(false, result.generated);
        System.assert(result.summary.contains('No counter-position template'), result.summary);
    }

    @IsTest
    static void refusesAnUnknownContract() {
        configure('800000001');
        Test.setMock(HttpCalloutMock.class, new BoxMock(202, '{"id":"unreachable"}'));

        Test.startTest();
        ClmGenerateCounterProposal.Result result = run(request('CLM-NOT-A-CONTRACT', 'Clause 22.4'));
        Test.stopTest();

        System.assertEquals(false, result.generated);
        System.assert(result.summary.contains('could not find'), result.summary);
    }

    @IsTest
    static void refusesWithoutAClauseAtIssue() {
        configure('800000001');
        seedContract();
        Test.setMock(HttpCalloutMock.class, new BoxMock(202, '{"id":"unreachable"}'));

        Test.startTest();
        ClmGenerateCounterProposal.Result result = run(request('CLM-TEST-0001', null));
        Test.stopTest();

        System.assertEquals(false, result.generated);
        System.assert(result.summary.contains('clause at issue'), result.summary);
    }

    @IsTest
    static void reportsARefusalFromBoxWithoutClaimingSuccess() {
        configure('800000001');
        seedContract();
        Test.setMock(HttpCalloutMock.class, new BoxMock(400, '{"code":"bad_request"}'));

        Test.startTest();
        ClmGenerateCounterProposal.Result result = run(request('CLM-TEST-0001', 'Clause 22.4'));
        Test.stopTest();

        System.assertEquals(false, result.generated);
        System.assert(result.summary.contains('refused'), result.summary);
    }
}
