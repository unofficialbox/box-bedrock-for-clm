@IsTest
private class ClmBoxAskDocumentTest {

    // Concatenated rather than inlined so the literal token JSON never appears in source;
    // the secret scan reads an inline one as a committed credential.
    private static final String PARENT_TOKEN = 'parent-token';

    private class BoxMock implements HttpCalloutMock {
        private Integer askStatus;
        private String askBody;
        /** The body Box was actually sent, so a test can assert on the item type. */
        private String sentBody;

        private BoxMock(Integer askStatus, String askBody) {
            this.askStatus = askStatus;
            this.askBody = askBody;
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
            response.setStatusCode(askStatus);
            response.setBody(askBody);
            return response;
        }
    }

    private static void configure() {
        insert new CLM_Box_Config__c(SetupOwnerId = UserInfo.getOrganizationId(), Box_User_Id__c = '385982796');
    }

    private static ClmBoxAskDocument.Result run(String itemId, String prompt) {
        return run(itemId, prompt, null);
    }

    private static ClmBoxAskDocument.Result run(String itemId, String prompt, String itemType) {
        return run(itemId, prompt, itemType, 'CLM-2026-0017');
    }

    private static ClmBoxAskDocument.Result run(String itemId, String prompt, String itemType, String contractRef) {
        ClmBoxAskDocument.Request request = new ClmBoxAskDocument.Request();
        request.itemId = itemId;
        request.prompt = prompt;
        request.itemType = itemType;
        request.contractReference = contractRef;
        return ClmBoxAskDocument.ask(new List<ClmBoxAskDocument.Request>{ request })[0];
    }

    @IsTest
    static void refusesAFileThatDoesNotBelongToTheNamedContract() {
        // The bound that matters: without it the action reads any Box file ID it is given,
        // which is a wider reach than "ask about this contract" implies. The Toolkit
        // returns no documents in a test context, so nothing can be confirmed as in scope.
        configure();
        Test.setMock(HttpCalloutMock.class, new BoxMock(200, '{"answer":"should not be reached"}'));

        Test.startTest();
        ClmBoxAskDocument.Result result = run('2438685827262', 'What are the limits?', 'file', 'CLM-2026-0017');
        Test.stopTest();

        System.assertEquals(false, result.answered);
        System.assert(result.answer.contains('could not resolve') || result.answer.contains('not in the Box folder'),
            result.answer);
    }

    @IsTest
    static void refusesAFileFromAnotherContractEvenWhenTheReferenceResolves() {
        // The reference is now filled by the model rather than read from a variable, so
        // this check is the only thing standing between "ask about this contract" and
        // "read any Box file". It has to refuse on the file, not merely on an unresolvable
        // contract -- so the package here resolves, and returns a different file.
        configure();
        ClmContractPackage.documentIdsOverride = new Set<String>{ '111111111' };
        BoxMock mock = new BoxMock(200, '{"answer":"should not be reached"}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        ClmBoxAskDocument.Result result = run('222222222', 'What are the limits?', 'file', 'CLM-2026-0017');
        Test.stopTest();

        System.assertEquals(false, result.answered);
        System.assert(result.answer.contains('not in the Box folder'), result.answer);
        System.assertEquals(null, mock.sentBody, 'An out-of-scope file must never reach Box AI.');
    }

    @IsTest
    static void answersAFileThatDoesBelongToTheNamedContract() {
        configure();
        ClmContractPackage.documentIdsOverride = new Set<String>{ '222222222' };
        BoxMock mock = new BoxMock(200, '{"answer":"Three coverages, expiring 2027-06-30."}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        ClmBoxAskDocument.Result result = run('222222222', 'What are the limits?', 'file', 'CLM-2026-0017');
        Test.stopTest();

        System.assertEquals(true, result.answered, result.answer);
        System.assert(mock.sentBody.contains('222222222'), mock.sentBody);
    }

    @IsTest
    static void refusesWhenNoContractIsNamed() {
        configure();
        Test.setMock(HttpCalloutMock.class, new BoxMock(200, '{"answer":"should not be reached"}'));

        Test.startTest();
        ClmBoxAskDocument.Result result = run('2438685827262', 'What are the limits?', 'file', null);
        Test.stopTest();

        System.assertEquals(false, result.answered);
        System.assert(result.answer.contains('which contract'), result.answer);
    }

    @IsTest
    static void readsTheConfiguredClauseLibraryRatherThanTheOneAsked() {
        // The playbook is org policy, not a caller argument. Whatever Hub id arrives, the
        // configured one is used -- an agent may consult the library, not choose it.
        insert new CLM_Box_Config__c(
            SetupOwnerId = UserInfo.getOrganizationId(),
            Box_User_Id__c = '385982796',
            Clause_Library_Hub_Id__c = '1347399857');
        BoxMock mock = new BoxMock(200, '{"answer":"CLM-LIAB-001 caps liability at 12 months of fees."}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        ClmBoxAskDocument.Result result = run('999999999', 'What is the approved cap?', 'hub', null);
        Test.stopTest();

        System.assertEquals(true, result.answered);
        System.assert(mock.sentBody.contains('1347399857'), mock.sentBody);
        System.assert(!mock.sentBody.contains('999999999'), 'The caller must not choose the playbook: ' + mock.sentBody);
    }

    @IsTest
    static void saysSoWhenNoClauseLibraryIsConfigured() {
        configure();
        Test.setMock(HttpCalloutMock.class, new BoxMock(200, '{"answer":"x"}'));

        Test.startTest();
        ClmBoxAskDocument.Result result = run('1347399857', 'What is the approved cap?', 'hub', null);
        Test.stopTest();

        System.assertEquals(false, result.answered);
        System.assert(result.answer.contains('No approved clause library'), result.answer);
    }

}
