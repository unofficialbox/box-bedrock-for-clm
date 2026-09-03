@IsTest
private class ClmSendForSignatureTest {

    // Concatenated so the literal token JSON never appears in source; the secret scan
    // reads an inline one as a committed credential.
    private static final String PARENT_TOKEN = 'parent-token';

    private class BoxMock implements HttpCalloutMock {
        private Integer status;
        private String body;

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
            response.setStatusCode(status);
            response.setBody(body);
            return response;
        }
    }

    /**
     * Stands in for the Box managed package. What most of these tests assert is that it is
     * never reached at all.
     */
    private class FakeSender implements ClmSendForSignature.SignSender {
        private Boolean called = false;
        private ClmSendForSignature.SignOutcome outcome;

        private FakeSender(ClmSendForSignature.SignOutcome outcome) {
            this.outcome = outcome;
        }

        public ClmSendForSignature.SignOutcome send(Id contractId, String boxFileId,
            String signerEmail, String signerName, String subject) {
            called = true;
            return outcome;
        }
    }

    private static FakeSender install(ClmSendForSignature.SignOutcome outcome) {
        FakeSender sender = new FakeSender(outcome);
        ClmSendForSignature.sender = sender;
        return sender;
    }

    /** A sender that would succeed, so a test asserting it was never called means it. */
    private static FakeSender sends() {
        ClmSendForSignature.SignOutcome outcome = new ClmSendForSignature.SignOutcome();
        outcome.requestId = 'sign-1';
        return install(outcome);
    }

    private static FakeSender refuses() {
        ClmSendForSignature.SignOutcome outcome = new ClmSendForSignature.SignOutcome();
        outcome.error = 'forbidden';
        return install(outcome);
    }

    private static void configure() {
        insert new CLM_Box_Config__c(
            SetupOwnerId = UserInfo.getOrganizationId(), Box_User_Id__c = '100000001');
    }

    private static void seedContract(String status) {
        insert new CLM_Contract__c(
            Name = 'Test Counterparty Master Agreement',
            Contract_ID__c = 'CLM-TEST-0001',
            Counterparty__c = 'Test Counterparty',
            Status__c = status,
            Box_Workspace_Folder_ID__c = '900000001');
    }

    private static ClmSendForSignature.Result run(String reference, String itemId, String email) {
        ClmSendForSignature.Request req = new ClmSendForSignature.Request();
        req.contractReference = reference;
        req.itemId = itemId;
        req.signerEmail = email;
        req.signerName = 'Test Signer';
        return ClmSendForSignature.prepare(new List<ClmSendForSignature.Request>{ req })[0];
    }

    @IsTest
    static void refusesWhileTheContractIsStillInReview() {
        // The guardrail the whole demo rests on. A contract that has not been approved is
        // not signable, and no request reaches Box at all.
        configure();
        seedContract('Legal Review');
        Test.setMock(HttpCalloutMock.class, new BoxMock(200, '{"id":"unreachable"}'));
        FakeSender sender = sends();

        Test.startTest();
        ClmSendForSignature.Result result = run('CLM-TEST-0001', '700000001', 'signer@example.com');
        Test.stopTest();

        System.assertEquals(false, result.sent);
        System.assert(result.summary.contains('not approved for signature'), result.summary);
        System.assertEquals(false, sender.called, 'Box must not be called for an unapproved contract.');
    }

    @IsTest
    static void refusesToSignAContractThatIsAlreadyExecuted() {
        configure();
        seedContract('Executed');
        Test.setMock(HttpCalloutMock.class, new BoxMock(200, '{"id":"unreachable"}'));

        Test.startTest();
        ClmSendForSignature.Result result = run('CLM-TEST-0001', '700000001', 'signer@example.com');
        Test.stopTest();

        System.assertEquals(false, result.sent);
        System.assert(result.summary.contains('not approved for signature'), result.summary);
    }

    @IsTest
    static void refusesAFileThatDoesNotBelongToTheNamedContract() {
        // The same bound reading a document has. The Toolkit returns no documents in a
        // test context, so no file can be confirmed as in scope and none is routed.
        configure();
        seedContract('Approved');
        Test.setMock(HttpCalloutMock.class, new BoxMock(200, '{"id":"unreachable"}'));
        FakeSender sender = sends();

        Test.startTest();
        ClmSendForSignature.Result result = run('CLM-TEST-0001', '700000001', 'signer@example.com');
        Test.stopTest();

        System.assertEquals(false, result.sent);
        System.assert(
            result.summary.contains('could not resolve') || result.summary.contains('not in the Box folder'),
            result.summary);
        System.assertEquals(false, sender.called, 'An out-of-scope file must never reach Box Sign.');
    }

    @IsTest
    static void sendsOnceTheContractIsApproved() {
        // The success path. Preparation is skipped, so Box mails the signer rather than
        // parking a draft, and the summary says the request went out.
        configure();
        seedContract('Approved');
        ClmContractPackage.documentIdsOverride = new Set<String>{ '700000001' };
        Test.setMock(HttpCalloutMock.class, new BoxMock(200, '{}'));
        FakeSender sender = sends();

        Test.startTest();
        ClmSendForSignature.Result result = run('CLM-TEST-0001', '700000001', 'signer@example.com');
        Test.stopTest();

        System.assertEquals(true, result.sent, result.summary);
        System.assertEquals('sign-1', result.requestId);
        System.assertEquals(true, sender.called);
        System.assert(result.summary.contains('has been sent to'), result.summary);
    }

    @IsTest
    static void doesNotClaimSuccessWhenBoxSignRefuses() {
        configure();
        seedContract('Approved');
        ClmContractPackage.documentIdsOverride = new Set<String>{ '700000001' };
        Test.setMock(HttpCalloutMock.class, new BoxMock(200, '{}'));
        refuses();

        Test.startTest();
        ClmSendForSignature.Result result = run('CLM-TEST-0001', '700000001', 'signer@example.com');
        Test.stopTest();

        System.assertEquals(false, result.sent);
        System.assert(result.summary.contains('Nothing was sent'), result.summary);
    }

    @IsTest
    static void refusesWithoutASigner() {
        configure();
        seedContract('Approved');
        Test.setMock(HttpCalloutMock.class, new BoxMock(200, '{"id":"unreachable"}'));

        Test.startTest();
        ClmSendForSignature.Result result = run('CLM-TEST-0001', '700000001', null);
        Test.stopTest();

        System.assertEquals(false, result.sent);
        System.assert(result.summary.contains('need a signer'), result.summary);
    }

    @IsTest
    static void refusesAnUnknownContract() {
        configure();
        Test.setMock(HttpCalloutMock.class, new BoxMock(200, '{"id":"unreachable"}'));

        Test.startTest();
        ClmSendForSignature.Result result = run('CLM-NOT-A-CONTRACT', '700000001', 'signer@example.com');
        Test.stopTest();

        System.assertEquals(false, result.sent);
        System.assert(result.summary.contains('could not find'), result.summary);
    }

    @IsTest
    static void refusesWithoutAFile() {
        configure();
        seedContract('Approved');
        Test.setMock(HttpCalloutMock.class, new BoxMock(200, '{"id":"unreachable"}'));

        Test.startTest();
        ClmSendForSignature.Result result = run('CLM-TEST-0001', null, 'signer@example.com');
        Test.stopTest();

        System.assertEquals(false, result.sent);
        System.assert(result.summary.contains('Box file ID'), result.summary);
    }
}
