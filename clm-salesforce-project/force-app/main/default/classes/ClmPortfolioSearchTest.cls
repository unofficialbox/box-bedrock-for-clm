/**
 * The point of this action is that a caller never supplies a folder id, so the tests that
 * matter are about the boundary: it comes from configuration, it is actually sent, and a
 * missing one refuses rather than searching the whole enterprise.
 */
@IsTest
private class ClmPortfolioSearchTest {

    /**
     * Two callouts happen here, not one: ClmBoxAuth grants a parent token first, then the
     * metadata query runs. Test.setMock intercepts both, so a mock that answers everything
     * with the query payload hands the token grant a body with no access_token -- and the
     * action then refuses before it ever searches, which is a mock bug wearing the costume
     * of a code bug. Dispatch on the endpoint.
     */
    private class QueryMock implements HttpCalloutMock {
        private final Integer status;
        private final String payload;
        private String seenBody;

        private QueryMock(Integer status, String payload) {
            this.status = status;
            this.payload = payload;
        }

        public HttpResponse respond(HttpRequest request) {
            HttpResponse response = new HttpResponse();
            if (request.getEndpoint().contains('oauth2/token')) {
                response.setStatusCode(200);
                response.setBody('{"access_token":"example-parent-token","expires_in":3600}');
                return response;
            }
            this.seenBody = request.getBody();
            response.setStatusCode(this.status);
            response.setBody(this.payload);
            return response;
        }
    }

    private static final String TWO_HITS =
        '{"entries":[{"id":"111","name":"calder-msa-customer-paper-v2.pdf"},'
        + '{"id":"222","name":"northstar-msa-redline-v4.pdf"}]}';

    private static void configure(String root, String enterprise) {
        insert new CLM_Box_Config__c(
            SetupOwnerId = UserInfo.getOrganizationId(),
            Contracts_Root_Folder_Id__c = root,
            Enterprise_Id__c = enterprise,
            Box_User_Id__c = 'demo user'
        );
    }

    private static ClmPortfolioSearch.Result run(String risk) {
        ClmPortfolioSearch.Request req = new ClmPortfolioSearch.Request();
        req.inputRiskLevel = risk;
        return ClmPortfolioSearch.find(new List<ClmPortfolioSearch.Request>{ req })[0];
    }

    @IsTest
    static void boundsTheSearchToTheConfiguredRoot() {
        // The whole reason this action exists: the caller says "Critical", not a folder id.
        configure('42', '5105484');
        QueryMock mock = new QueryMock(200, TWO_HITS);
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        ClmPortfolioSearch.Result result = run('Critical');
        Test.stopTest();

        System.assert(mock.seenBody != null, 'No query callout happened. Summary was: ' + result.outputSummary);
        System.assert(mock.seenBody.contains('"ancestor_folder_id":"42"'), 'The boundary is sent, and it came from configuration.');
        System.assert(mock.seenBody.contains('enterprise_5105484.clmDocument'), 'The template is the org\'s, not the caller\'s.');
        System.assert(mock.seenBody.contains('"risk":"Critical"'), 'The one thing the caller supplies is the risk level.');
        System.assertEquals(2, result.outputCount, 'Both matches counted.');
    }

    @IsTest
    static void returnsLinksRatherThanIds() {
        // An id is meaningless to the person the answer is read to.
        configure('42', '5105484');
        Test.setMock(HttpCalloutMock.class, new QueryMock(200, TWO_HITS));

        Test.startTest();
        ClmPortfolioSearch.Result result = run('Critical');
        Test.stopTest();

        System.assert(result.outputSummary.contains('https://app.box.com/file/111'), 'Each document is a link.');
        System.assert(!result.outputSummary.contains('(id '), 'No bare ids in what a person reads.');
    }

    @IsTest
    static void refusesRatherThanSearchingTheWholeEnterpriseUnconfigured() {
        // Unbounded, this query returns documents from other environments carrying the same
        // file names. Refusing is the safe failure; searching everything is not.
        Test.setMock(HttpCalloutMock.class, new QueryMock(200, TWO_HITS));

        Test.startTest();
        ClmPortfolioSearch.Result result = run('Critical');
        Test.stopTest();

        System.assertEquals(0, result.outputCount, 'Nothing was searched.');
        System.assert(result.outputSummary.contains('not configured'), 'And it says why.');
    }

    @IsTest
    static void asksForARiskLevelWhenGivenNone() {
        configure('42', '5105484');

        Test.startTest();
        ClmPortfolioSearch.Result result = run(null);
        Test.stopTest();

        System.assert(result.outputSummary.contains('Critical'), 'It names the levels rather than failing silently.');
    }

    @IsTest
    static void saysSoWhenNothingIsFlagged() {
        configure('42', '5105484');
        Test.setMock(HttpCalloutMock.class, new QueryMock(200, '{"entries":[]}'));

        Test.startTest();
        ClmPortfolioSearch.Result result = run('Low');
        Test.stopTest();

        System.assertEquals(0, result.outputCount);
        System.assert(result.outputSummary.contains('No governed contract document'), 'An empty result is an answer, not an error.');
    }

    @IsTest
    static void reportsARefusalFromBox() {
        configure('42', '5105484');
        Test.setMock(HttpCalloutMock.class, new QueryMock(403, '{"code":"forbidden"}'));

        Test.startTest();
        ClmPortfolioSearch.Result result = run('Critical');
        Test.stopTest();

        System.assert(result.outputSummary.contains('403'), 'The status reaches the caller.');
    }
}
