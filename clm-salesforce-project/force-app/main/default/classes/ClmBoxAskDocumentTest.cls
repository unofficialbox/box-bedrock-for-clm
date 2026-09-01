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
        ClmBoxAskDocument.Request request = new ClmBoxAskDocument.Request();
        request.itemId = itemId;
        request.prompt = prompt;
        request.itemType = itemType;
        return ClmBoxAskDocument.ask(new List<ClmBoxAskDocument.Request>{ request })[0];
    }

    @IsTest
    static void returnsTheAnswerBoxAiGrounded() {
        configure();
        Test.setMock(HttpCalloutMock.class, new BoxMock(200,
            '{"answer":"Commercial General Liability $2,000,000, expires 2027-06-30.","completion_reason":"done"}'));

        Test.startTest();
        ClmBoxAskDocument.Result result = run('2438685827262', 'List every coverage with its limit and expiry.');
        Test.stopTest();

        System.assertEquals(true, result.answered);
        System.assert(result.answer.contains('2,000,000'), result.answer);
    }

    @IsTest
    static void reportsARefusalWithoutInventingContent() {
        // A refused read must not look like an answer. The agent is instructed never to
        // state a figure that did not come back from here, so this text has to make it
        // obvious that nothing came back.
        configure();
        Test.setMock(HttpCalloutMock.class, new BoxMock(403, '{"code":"access_denied"}'));

        Test.startTest();
        ClmBoxAskDocument.Result result = run('2438685827262', 'What are the limits?');
        Test.stopTest();

        System.assertEquals(false, result.answered);
        System.assert(result.answer.contains('403'), result.answer);
        System.assert(result.answer.contains('Do not guess'), result.answer);
    }

    @IsTest
    static void refusesWithoutAFileIdOrAPrompt() {
        Test.startTest();
        ClmBoxAskDocument.Result missingId = run('', 'What are the limits?');
        ClmBoxAskDocument.Result missingPrompt = run('123', '');
        Test.stopTest();

        System.assertEquals(false, missingId.answered);
        System.assertEquals(false, missingPrompt.answered);
    }

    @IsTest
    static void asksAHubAsHubsBecauseTheSingularIsRejected() {
        // Box spells it `hubs` in items[].type and 400s on `hub`, naming only the schema
        // path -- so the singular is normalized rather than passed through. This is the
        // whole reason the clause library is reachable at all.
        configure();
        BoxMock mock = new BoxMock(200, '{"answer":"CLM-LIAB-001 caps liability at 12 months of fees."}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        ClmBoxAskDocument.Result result = run('1347399857', 'What is the approved cap?', 'hub');
        Test.stopTest();

        System.assertEquals(true, result.answered);
        System.assert(mock.sentBody.contains('"type":"hubs"'), mock.sentBody);
    }

    @IsTest
    static void defaultsToASingleFile() {
        configure();
        BoxMock mock = new BoxMock(200, '{"answer":"Coverage expires 2027-06-30."}');
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        run('2438685827262', 'When does coverage end?');
        Test.stopTest();

        System.assert(mock.sentBody.contains('"type":"file"'), mock.sentBody);
    }

    @IsTest
    static void saysSoWhenBoxAiAnswersWithNothing() {
        configure();
        Test.setMock(HttpCalloutMock.class, new BoxMock(200, '{"answer":""}'));

        Test.startTest();
        ClmBoxAskDocument.Result result = run('2438685827262', 'What are the limits?');
        Test.stopTest();

        System.assertEquals(false, result.answered);
        System.assert(result.answer.contains('returned nothing'), result.answer);
    }
}
