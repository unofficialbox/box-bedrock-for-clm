/**
 * Provision a Box workspace folder for a CLM record.
 *
 * Separate from ClmBoxTokenService because the two cannot share a transaction.
 * `createFolderForRecordId` writes the record-to-folder association, and Apex refuses a
 * callout once a transaction has done DML -- "You have uncommitted work pending" -- so
 * provisioning and minting a folder-scoped token have to be two requests. The client
 * calls this only when the token endpoint reports no_box_folder_mapping, so the common
 * case stays a single round trip.
 *
 * The package decides where the folder goes and what it is called; this class only asks
 * for it. `optCreateRootFolder` is true so the object's root folder is provisioned on the
 * first contract rather than failing.
 *
 * POST rather than GET: this creates something.
 */
@RestResource(urlMapping='/clm/box-folder/*')
global with sharing class ClmBoxFolderService {

    global class FolderResponse {
        global String folderId;
        global String recordId;
    }

    @HttpPost
    global static void provisionFolder() {
        RestRequest request = RestContext.request;
        RestResponse response = RestContext.response;
        response.addHeader('Content-Type', 'application/json');
        response.addHeader('Cache-Control', 'no-store');

        String recordParam = request.params.get('recordId');
        Id recordId;
        try {
            recordId = Id.valueOf(recordParam);
        } catch (Exception e) {
            fail(response, 400, 'invalid_record_id', 'recordId is required and must be a Salesforce id.');
            return;
        }

        String folderId = new Provisioner().forRecord(recordId);
        if (String.isBlank(folderId)) {
            fail(response, 500, 'box_folder_not_provisioned',
                'The Box for Salesforce package did not return a folder for that record.');
            return;
        }

        FolderResponse payload = new FolderResponse();
        payload.folderId = folderId;
        payload.recordId = recordId;
        response.statusCode = 200;
        response.responseBody = Blob.valueOf(JSON.serialize(payload));
    }

    /**
     * `without sharing` for the same reason as the token endpoint: the Experience Cloud
     * guest user sees no association records under normal sharing, and this returns a
     * folder id rather than granting any record access.
     */
    private without sharing class Provisioner {
        private String forRecord(Id recordId) {
            box.Toolkit toolkit = new box.Toolkit();
            try {
                // Returns the existing folder when the record already has one, so this is
                // safe to call twice and two racing callers converge on one folder.
                String folderId = toolkit.createFolderForRecordId(recordId, null, true);
                if (String.isBlank(folderId)) {
                    System.debug(LoggingLevel.WARN,
                        'CLM Box: could not provision a folder for ' + recordId + ': ' + toolkit.mostRecentError);
                }
                return folderId;
            } catch (Exception e) {
                System.debug(LoggingLevel.WARN, 'CLM Box: provisioning threw: ' + e.getMessage());
                return null;
            } finally {
                // Mandatory after any folder operation, or the association is left out of
                // sync. Guarded so a commit failure cannot replace the result.
                try {
                    toolkit.commitChanges();
                } catch (Exception commitError) {
                    System.debug(LoggingLevel.WARN, 'CLM Box: commitChanges failed: ' + commitError.getMessage());
                }
            }
        }
    }

    private static void fail(RestResponse response, Integer status, String error, String detail) {
        response.statusCode = status;
        response.responseBody = Blob.valueOf(JSON.serialize(
            new Map<String, String>{ 'error' => error, 'detail' => detail }));
    }
}
