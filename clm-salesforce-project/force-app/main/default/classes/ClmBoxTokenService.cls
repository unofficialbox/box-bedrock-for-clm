/**
 * Same-origin endpoint that hands the CLM React workspace a short-lived Box token
 * scoped to a single folder. The browser never sees a client secret and never sees
 * the parent token.
 *
 * Two Box calls, in order:
 *   1. Client Credentials Grant  -> an enterprise-scoped parent token.
 *   2. Token exchange (downscope) -> a token limited to `scope` on one folder.
 * Only the downscoped token is returned.
 *
 * The Box for Salesforce managed package cannot back this: box.Toolkit exposes no
 * token accessor, and the Authorization header it sets is not readable after
 * sendRequest, so there is no parent token to exchange. Hence a dedicated Box
 * platform app, with its credentials held in the protected CLM_Box_Config__c
 * custom setting (data, never committed metadata).
 */
@RestResource(urlMapping='/clm/box-token/*')
global with sharing class ClmBoxTokenService {

    private static final String TOKEN_URL = 'https://api.box.com/oauth2/token';
    private static final String TOKEN_EXCHANGE_GRANT = 'urn:ietf:params:oauth:grant-type:token-exchange';
    private static final String ACCESS_TOKEN_TYPE = 'urn:ietf:params:oauth:token-type:access_token';

    /** Read-only preview scopes. Deliberately excludes upload, delete, and share. */
    private static final String DOWNSCOPE_SCOPE = 'base_explorer,item_preview,item_read';

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
        // A token is per-user and short-lived; never let a proxy or browser cache it.
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
        if (config == null || String.isBlank(config.Client_Id__c) || String.isBlank(config.Client_Secret__c)
            || String.isBlank(config.Enterprise_Id__c)) {
            fail(response, 503, 'box_not_configured',
                'Populate the CLM Box Config custom setting with the Box app client id, client secret, and enterprise id.');
            return;
        }
        if (!isFolderAllowed(config, folderId)) {
            fail(response, 403, 'folder_not_allowed',
                'folderId is not in the configured Allowed Folder Ids list.');
            return;
        }

        try {
            String parentToken = requestEnterpriseToken(config);
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

    /** Client Credentials Grant against the Box enterprise. Returns the parent token. */
    private static String requestEnterpriseToken(CLM_Box_Config__c config) {
        Map<String, String> form = new Map<String, String>{
            'grant_type' => 'client_credentials',
            'client_id' => config.Client_Id__c,
            'client_secret' => config.Client_Secret__c,
            'box_subject_type' => 'enterprise',
            'box_subject_id' => config.Enterprise_Id__c
        };
        HttpResponse res = post(form);
        if (res.getStatusCode() != 200) {
            return null;
        }
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        return (String) body.get('access_token');
    }

    /** Exchange the parent token for one limited to preview scopes on a single folder. */
    private static TokenResponse downscope(String parentToken, String folderId) {
        Map<String, String> form = new Map<String, String>{
            'grant_type' => TOKEN_EXCHANGE_GRANT,
            'subject_token' => parentToken,
            'subject_token_type' => ACCESS_TOKEN_TYPE,
            'scope' => DOWNSCOPE_SCOPE,
            'resource' => 'https://api.box.com/2.0/folders/' + folderId
        };
        HttpResponse res = post(form);
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

    private static HttpResponse post(Map<String, String> form) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint(TOKEN_URL);
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/x-www-form-urlencoded');
        req.setTimeout(20000);
        req.setBody(encodeForm(form));
        return new Http().send(req);
    }

    private static String encodeForm(Map<String, String> form) {
        List<String> pairs = new List<String>();
        for (String key : form.keySet()) {
            pairs.add(EncodingUtil.urlEncode(key, 'UTF-8') + '=' + EncodingUtil.urlEncode(form.get(key), 'UTF-8'));
        }
        return String.join(pairs, '&');
    }

    private static void fail(RestResponse response, Integer status, String error, String detail) {
        response.statusCode = status;
        response.responseBody = Blob.valueOf(JSON.serialize(new ServiceError(error, detail)));
    }
}
