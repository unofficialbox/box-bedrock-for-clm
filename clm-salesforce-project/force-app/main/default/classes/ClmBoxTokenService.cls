/**
 * Same-origin endpoint that hands the CLM React workspace a short-lived Box token
 * scoped to a single folder. The browser never sees a credential, and neither does
 * this class.
 *
 * Two Box calls, both through the CLM_Box named credential:
 *   1. Client Credentials Grant  -> an enterprise-scoped parent token.
 *   2. Token exchange (downscope) -> a token limited to `scope` on one folder.
 * Only the downscoped token is returned.
 *
 * Credentials live in the CLM_Box external credential (Basic protocol: Username is
 * the Box client id, Password is the client secret). Salesforce stores them
 * encrypted and substitutes them into the request body at callout time via merge
 * fields, so Apex holds only placeholders and no secret can reach source control.
 * This requires "Allow Merge Fields in HTTP Body" on the named credential.
 *
 * The Box for Salesforce managed package cannot back this: box.Toolkit exposes no
 * token accessor, and the Authorization header it sets is not readable after
 * sendRequest, so there is no parent token to exchange.
 */
@RestResource(urlMapping='/clm/box-token/*')
global with sharing class ClmBoxTokenService {

    @TestVisible
    private static final String TOKEN_ENDPOINT = 'callout:CLM_Box/oauth2/token';
    private static final String TOKEN_EXCHANGE_GRANT = 'urn:ietf:params:oauth:grant-type:token-exchange';
    private static final String ACCESS_TOKEN_TYPE = 'urn:ietf:params:oauth:token-type:access_token';

    /** Read-only preview scopes. Deliberately excludes upload, delete, and share. */
    private static final String DOWNSCOPE_SCOPE = 'base_explorer,item_preview,item_read';

    /** Reuse the enterprise token across requests so each preview costs one Box call, not two. */
    private static final String CACHE_KEY = 'ClmBoxParentToken';
    private static final Integer CACHE_SAFETY_MARGIN_SECONDS = 300;

    global class TokenResponse {
        global String accessToken;
        global Integer expiresIn;
        global String folderId;
        global String scope;
    }

    global class ServiceError {
        global String error;
        global String detail;
        global ServiceError(String error, String detail) {
            this.error = error;
            this.detail = detail;
        }
    }

    @HttpGet
    global static void getDownscopedToken() {
        RestRequest request = RestContext.request;
        RestResponse response = RestContext.response;
        response.addHeader('Content-Type', 'application/json');
        // A token is short-lived and folder-scoped; never let a proxy or browser cache it.
        response.addHeader('Cache-Control', 'no-store');

        String folderId = request.params.get('folderId');
        if (String.isBlank(folderId)) {
            fail(response, 400, 'missing_folder_id', 'folderId is required.');
            return;
        }
        if (!folderId.isNumeric()) {
            // Box folder ids are numeric; reject anything else before it reaches Box.
            fail(response, 400, 'invalid_folder_id', 'folderId must be numeric.');
            return;
        }

        CLM_Box_Config__c config = CLM_Box_Config__c.getOrgDefaults();
        if (config == null || String.isBlank(config.Enterprise_Id__c)) {
            fail(response, 503, 'box_not_configured',
                'Set Enterprise Id on the CLM Box Config custom setting, and the Box client id and secret on the CLM Box external credential.');
            return;
        }
        if (!isFolderAllowed(config, folderId)) {
            fail(response, 403, 'folder_not_allowed',
                'folderId is not in the configured Allowed Folder Ids list.');
            return;
        }

        try {
            String parentToken = enterpriseToken(config);
            if (String.isBlank(parentToken)) {
                fail(response, 502, 'box_auth_failed', 'Box did not return an enterprise access token.');
                return;
            }
            TokenResponse payload = downscope(parentToken, folderId);
            if (payload == null) {
                fail(response, 502, 'box_downscope_failed', 'Box did not return a downscoped access token.');
                return;
            }
            response.statusCode = 200;
            response.responseBody = Blob.valueOf(JSON.serialize(payload));
        } catch (Exception e) {
            // Never surface the raw Box body or the parent token in an error path.
            fail(response, 502, 'box_request_failed', e.getTypeName());
        }
    }

    /**
     * An empty allowlist means "any folder". Populate Allowed_Folder_Ids__c with a
     * comma-separated list to restrict the endpoint to the demo workspace.
     */
    private static Boolean isFolderAllowed(CLM_Box_Config__c config, String folderId) {
        if (String.isBlank(config.Allowed_Folder_Ids__c)) {
            return true;
        }
        for (String allowed : config.Allowed_Folder_Ids__c.split(',')) {
            if (allowed.trim() == folderId) {
                return true;
            }
        }
        return false;
    }

    /** Cached enterprise token, falling back to a fresh grant. */
    private static String enterpriseToken(CLM_Box_Config__c config) {
        String cached = cacheGet();
        if (String.isNotBlank(cached)) {
            return cached;
        }
        HttpResponse res = post(
            'grant_type=client_credentials'
            // Merge fields are substituted by Salesforce and must not be encoded here.
            + '&client_id={!$Credential.Username}'
            + '&client_secret={!$Credential.Password}'
            + '&box_subject_type=enterprise'
            + '&box_subject_id=' + EncodingUtil.urlEncode(config.Enterprise_Id__c, 'UTF-8')
        );
        if (res.getStatusCode() != 200) {
            return null;
        }
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        String token = (String) body.get('access_token');
        Integer expiresIn = body.get('expires_in') == null ? 0 : Integer.valueOf(body.get('expires_in'));
        cachePut(token, expiresIn);
        return token;
    }

    /** Exchange the parent token for one limited to preview scopes on a single folder. */
    private static TokenResponse downscope(String parentToken, String folderId) {
        HttpResponse res = post(
            'grant_type=' + EncodingUtil.urlEncode(TOKEN_EXCHANGE_GRANT, 'UTF-8')
            + '&subject_token=' + EncodingUtil.urlEncode(parentToken, 'UTF-8')
            + '&subject_token_type=' + EncodingUtil.urlEncode(ACCESS_TOKEN_TYPE, 'UTF-8')
            + '&scope=' + EncodingUtil.urlEncode(DOWNSCOPE_SCOPE, 'UTF-8')
            + '&resource=' + EncodingUtil.urlEncode('https://api.box.com/2.0/folders/' + folderId, 'UTF-8')
        );
        if (res.getStatusCode() != 200) {
            return null;
        }
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        String token = (String) body.get('access_token');
        if (String.isBlank(token)) {
            return null;
        }
        TokenResponse payload = new TokenResponse();
        payload.accessToken = token;
        payload.expiresIn = body.get('expires_in') == null ? 0 : Integer.valueOf(body.get('expires_in'));
        payload.folderId = folderId;
        payload.scope = DOWNSCOPE_SCOPE;
        return payload;
    }

    private static HttpResponse post(String body) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint(TOKEN_ENDPOINT);
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/x-www-form-urlencoded');
        req.setTimeout(20000);
        req.setBody(body);
        return new Http().send(req);
    }

    /** Org cache is optional: without a partition these are no-ops, not failures. */
    private static String cacheGet() {
        try {
            return (String) Cache.Org.get(CACHE_KEY);
        } catch (Exception e) {
            return null;
        }
    }

    private static void cachePut(String token, Integer expiresIn) {
        if (String.isBlank(token)) {
            return;
        }
        Integer ttl = expiresIn - CACHE_SAFETY_MARGIN_SECONDS;
        if (ttl < 60) {
            return;
        }
        try {
            Cache.Org.put(CACHE_KEY, token, Math.min(ttl, 28800));
        } catch (Exception e) {
            // No partition allocated; every request simply re-grants.
        }
    }

    private static void fail(RestResponse response, Integer status, String error, String detail) {
        response.statusCode = status;
        response.responseBody = Blob.valueOf(JSON.serialize(new ServiceError(error, detail)));
    }
}
