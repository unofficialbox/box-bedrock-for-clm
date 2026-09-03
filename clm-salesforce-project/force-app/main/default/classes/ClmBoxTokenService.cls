/**
 * Same-origin endpoint that hands the CLM React workspace a short-lived Box token
 * scoped to a single folder. The browser never sees a credential, and neither does
 * this class.
 *
 * Two Box calls, both through the CLM_Box named credential:
 *   1. Client Credentials Grant  -> a parent token for the configured subject.
 *   2. Token exchange (downscope) -> a token limited to `scope` on one folder.
 * Only the downscoped token is returned.
 *
 * The CCG subject is configuration, not code. A Box user id on CLM_Box_Config__c
 * yields box_subject_type=user, and the parent token inherits that user's existing
 * access -- nothing needs collaborating. An enterprise id instead yields a Service
 * Account token, whose root starts empty, so the service identity must be added as a
 * collaborator on the folder. User is the demo default; enterprise remains for
 * deployments that want a non-human identity.
 *
 * Credentials live in the CLM_Box external credential as Custom authentication
 * parameters named ClientId and ClientSecret. Salesforce stores them encrypted and
 * substitutes them into the request body at callout time via merge fields, so Apex
 * holds only placeholders and no secret can reach source control. This requires
 * "Allow Merge Fields in HTTP Body" on the named credential.
 *
 * Custom rather than Basic for two reasons: the values are a client id and a secret
 * rather than a username and password, and ConnectApi.CredentialInput accepts only
 * AwsSv4 or Custom -- so a Basic principal cannot be populated programmatically and
 * would have to be typed into Setup by hand.
 *
 * The Box for Salesforce managed package cannot back this: box.Toolkit exposes no
 * token accessor, and the Authorization header it sets is not readable after
 * sendRequest, so there is no parent token to exchange.
 */
@RestResource(urlMapping='/clm/box-token/*')
global with sharing class ClmBoxTokenService {

    private static final String TOKEN_EXCHANGE_GRANT = 'urn:ietf:params:oauth:grant-type:token-exchange';
    private static final String ACCESS_TOKEN_TYPE = 'urn:ietf:params:oauth:token-type:access_token';

    /**
     * Scopes minted for the browser.
     *
     * These mirror what the workspace is allowed to offer. A control in the UI only
     * shows an affordance; this decides whether Box honours it, so the two have to be
     * kept in step -- an enabled control with a missing scope fails at the point of use
     * rather than being hidden.
     *
     * The token is still bound to a single folder by the downscope resource, so this
     * widens what may be done inside that folder and nothing beyond it.
     *
     * Space separated, per OAuth 2.0. A comma separated list is rejected by Box as a
     * single unsupported scope name -- each value is valid on its own, so the failure
     * only appears once more than one scope is requested.
     */
    private static final String DOWNSCOPE_SCOPE =
        'base_explorer item_preview item_read item_upload item_download item_delete item_rename item_share';

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

        String recordId = request.params.get('recordId');

        // A record is the only way in. The browser names a Salesforce record and the org's
        // own Box mapping decides the folder, so no Box id travels in a URL and a caller
        // cannot ask for a folder the record is not associated with.
        //
        // This used to also accept a caller-supplied folderId, bounded by an allowlist on
        // the custom setting. That was duplicative -- the managed package already scopes a
        // folder to its record -- and it did not scale: an exact-match list in a Text(255)
        // holds around seventeen ids and says nothing about their children, so it could
        // never cover per-contract folders. Left empty, as it was, the branch it guarded
        // let any caller who could reach this endpoint name any folder the service account
        // could see, and the guest user can reach this endpoint.
        if (String.isBlank(recordId)) {
            fail(response, 400, 'missing_record_id', 'Pass recordId.');
            return;
        }

        Id parsedRecordId;
        try {
            parsedRecordId = Id.valueOf(recordId);
        } catch (Exception e) {
            fail(response, 400, 'invalid_record_id', 'recordId is not a Salesforce id.');
            return;
        }
        // Inner classes cannot hold static members in Apex, hence the instance.
        String folderId = new FolderMapping().forRecord(parsedRecordId);
        if (String.isBlank(folderId)) {
            fail(response, 404, 'no_box_folder_mapping',
                'No Box folder is associated with that record. Associate one with the Box for Salesforce package first.');
            return;
        }
        if (!folderId.isNumeric()) {
            // Box folder ids are numeric; reject anything else before it reaches Box.
            fail(response, 400, 'invalid_folder_id', 'folderId must be numeric.');
            return;
        }

        CLM_Box_Config__c config = CLM_Box_Config__c.getOrgDefaults();
        if (config == null || (String.isBlank(config.Box_User_Id__c) && String.isBlank(config.Enterprise_Id__c))) {
            fail(response, 500, 'box_not_configured',
                'Set Box User Id (or Enterprise Id) on the CLM Box Config custom setting, and the Box client id and secret on the CLM Box external credential.');
            return;
        }
        try {
            // Shared with the agent actions, which need the same grant against the same app.
            String parentToken = ClmBoxAuth.parentToken();
            if (String.isBlank(parentToken)) {
                fail(response, 500, 'box_auth_failed', 'Box did not return a parent access token.');
                return;
            }
            TokenResponse payload = downscope(parentToken, folderId);
            if (payload == null) {
                fail(response, 500, 'box_downscope_failed', 'Box did not return a downscoped access token.');
                return;
            }
            response.statusCode = 200;
            response.responseBody = Blob.valueOf(JSON.serialize(payload));
        } catch (Exception e) {
            // Never surface the raw Box body or the parent token in an error path.
            fail(response, 500, 'box_request_failed', e.getTypeName());
        }
    }

    /**
     * Read a record's Box workspace folder from the Box for Salesforce package.
     *
     * Read only, deliberately. `createFolderForRecordId` provisions a folder by writing
     * the association, and Apex forbids a callout once a transaction has done DML --
     * "You have uncommitted work pending" -- so provisioning here would break the token
     * callout that follows. Provisioning lives in ClmBoxFolderService, which the client
     * calls first when this returns nothing.
     *
     * `getFolderIdByRecordId` makes no Box API call, so this stays a single indexed read.
     *
     * Null on failure, which the caller reports as no_box_folder_mapping. box.Toolkit is
     * a managed-package class, so a caller without access to it throws rather than
     * returning nothing.
     *
     * `without sharing` because this endpoint also serves the Experience Cloud guest
     * user, which sees no association records under normal sharing. It returns a folder
     * id and grants the caller no record access.
     */
    private without sharing class FolderMapping {
        private String forRecord(Id recordId) {
            try {
                return new box.Toolkit().getFolderIdByRecordId(recordId);
            } catch (Exception e) {
                System.debug(LoggingLevel.WARN, 'CLM Box: folder lookup failed: ' + e.getMessage());
                return null;
            }
        }
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
        return ClmBoxAuth.post(body);
    }

    /**
     * Apex REST rejects some status codes outright -- a 502 comes back to the caller as
     * INTERNAL_SERVER_ERROR "Invalid status code for HTTP response: 502" and the body is
     * discarded, which hides the error entirely. Upstream failures therefore use 500 and
     * carry the specific cause in the `error` field.
     */
    private static void fail(RestResponse response, Integer status, String error, String detail) {
        response.statusCode = status;
        response.responseBody = Blob.valueOf(JSON.serialize(new ServiceError(error, detail)));
    }
}
