@IsTest
private class ClmBoxTokenServiceTest {

    private static final String PARENT_TOKEN = 'parent-token-value';
    private static final String CHILD_TOKEN = 'downscoped-token-value';
    private static final String FOLDER_ID = '123456789';

    /**
     * Answers both Box calls in sequence and records what was sent, so the tests can
     * assert the parent token is exchanged rather than returned.
     */
    private class BoxMock implements HttpCalloutMock {
        private Integer ccgStatus;
        private Integer exchangeStatus;
        private String exchangeBody;
        public List<String> bodies = new List<String>();

        BoxMock(Integer ccgStatus, Integer exchangeStatus, String exchangeBody) {
            this.ccgStatus = ccgStatus;
            this.exchangeStatus = exchangeStatus;
            this.exchangeBody = exchangeBody;
        }

        public HttpResponse respond(HttpRequest request) {
            bodies.add(request.getBody());
            HttpResponse res = new HttpResponse();
            res.setHeader('Content-Type', 'application/json');
            if (request.getBody().contains('grant_type=client_credentials')) {
                res.setStatusCode(ccgStatus);
                res.setBody(ccgStatus == 200
                    ? '{"access_token":"' + PARENT_TOKEN + '","expires_in":3600}'
                    : '{"error":"invalid_client"}');
                return res;
            }
            res.setStatusCode(exchangeStatus);
            res.setBody(exchangeBody);
            return res;
        }
    }

    private static BoxMock okMock() {
        return new BoxMock(200, 200, '{"access_token":"' + CHILD_TOKEN + '","expires_in":2400}');
    }

    private static void configure(String allowedFolders) {
        insert new CLM_Box_Config__c(
            SetupOwnerId = UserInfo.getOrganizationId(),
            Client_Id__c = 'client-id',
            Client_Secret__c = 'client-secret',
            Enterprise_Id__c = '99999',
            Allowed_Folder_Ids__c = allowedFolders
        );
    }

    private static void call(String folderId) {
        RestRequest request = new RestRequest();
        request.requestURI = '/services/apexrest/clm/box-token';
        request.httpMethod = 'GET';
        if (folderId != null) {
            request.addParameter('folderId', folderId);
        }
        RestContext.request = request;
        RestContext.response = new RestResponse();
        ClmBoxTokenService.getDownscopedToken();
    }

    private static Map<String, Object> body() {
        return (Map<String, Object>) JSON.deserializeUntyped(RestContext.response.responseBody.toString());
    }

    @IsTest
    static void returnsDownscopedTokenForAnAllowedFolder() {
        configure(FOLDER_ID);
        BoxMock mock = okMock();
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        call(FOLDER_ID);
        Test.stopTest();

        System.assertEquals(200, RestContext.response.statusCode, 'Expected a successful token response');
        Map<String, Object> payload = body();
        System.assertEquals(CHILD_TOKEN, payload.get('accessToken'), 'Should return the downscoped token');
        System.assertEquals(FOLDER_ID, payload.get('folderId'), 'Should echo the requested folder');
        System.assertEquals(2400, payload.get('expiresIn'), 'Should surface the Box expiry');
    }

    @IsTest
    static void neverReturnsTheParentToken() {
        configure(null);
        Test.setMock(HttpCalloutMock.class, okMock());

        Test.startTest();
        call(FOLDER_ID);
        Test.stopTest();

        String raw = RestContext.response.responseBody.toString();
        System.assert(!raw.contains(PARENT_TOKEN), 'The enterprise parent token must never reach the browser');
    }

    @IsTest
    static void exchangesTheParentTokenScopedToTheRequestedFolder() {
        configure(null);
        BoxMock mock = okMock();
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        call(FOLDER_ID);
        Test.stopTest();

        System.assertEquals(2, mock.bodies.size(), 'Expected a client-credentials call then an exchange call');
        String exchange = mock.bodies[1];
        System.assert(exchange.contains(EncodingUtil.urlEncode(PARENT_TOKEN, 'UTF-8')),
            'The exchange must present the parent token as subject_token');
        System.assert(exchange.contains(EncodingUtil.urlEncode('https://api.box.com/2.0/folders/' + FOLDER_ID, 'UTF-8')),
            'The exchange must scope the token to the requested folder');
        System.assert(!exchange.contains('client_secret'), 'The exchange must not resend the client secret');
    }

    @IsTest
    static void rejectsAFolderOutsideTheAllowlist() {
        configure('111,222');
        Test.setMock(HttpCalloutMock.class, okMock());

        Test.startTest();
        call(FOLDER_ID);
        Test.stopTest();

        System.assertEquals(403, RestContext.response.statusCode, 'Folders outside the allowlist must be refused');
        System.assertEquals('folder_not_allowed', body().get('error'));
    }

    @IsTest
    static void rejectsAMissingFolderId() {
        configure(null);
        Test.startTest();
        call(null);
        Test.stopTest();

        System.assertEquals(400, RestContext.response.statusCode);
        System.assertEquals('missing_folder_id', body().get('error'));
    }

    @IsTest
    static void rejectsANonNumericFolderId() {
        configure(null);
        Test.startTest();
        call('../../etc/passwd');
        Test.stopTest();

        System.assertEquals(400, RestContext.response.statusCode, 'Non-numeric ids must not reach Box');
        System.assertEquals('invalid_folder_id', body().get('error'));
    }

    @IsTest
    static void reportsWhenBoxCredentialsAreNotConfigured() {
        Test.startTest();
        call(FOLDER_ID);
        Test.stopTest();

        System.assertEquals(503, RestContext.response.statusCode, 'An unconfigured org should fail closed');
        System.assertEquals('box_not_configured', body().get('error'));
    }

    @IsTest
    static void reportsWhenBoxRejectsTheClientCredentials() {
        configure(null);
        Test.setMock(HttpCalloutMock.class, new BoxMock(401, 200, '{}'));

        Test.startTest();
        call(FOLDER_ID);
        Test.stopTest();

        System.assertEquals(502, RestContext.response.statusCode);
        System.assertEquals('box_auth_failed', body().get('error'));
    }

    @IsTest
    static void reportsWhenBoxRejectsTheDownscopeExchange() {
        configure(null);
        Test.setMock(HttpCalloutMock.class, new BoxMock(200, 400, '{"error":"invalid_grant"}'));

        Test.startTest();
        call(FOLDER_ID);
        Test.stopTest();

        System.assertEquals(502, RestContext.response.statusCode);
        System.assertEquals('box_downscope_failed', body().get('error'));
    }
}
