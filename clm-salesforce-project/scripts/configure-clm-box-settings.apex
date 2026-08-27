/*
 * Create or update the CLM Box Config org-default record (MT-039).
 * Run with the wrapper, which injects the values so no live ID lands in the working tree:
 *   BOX_ENTERPRISE_ID=<id> BOX_ALLOWED_FOLDER_IDS=<id,id> \
 *     clm-salesforce-project/scripts/configure-clm-box-settings.sh <org-alias>
 *
 * ClmBoxTokenService reads CLM_Box_Config__c.getOrgDefaults() on every request and
 * returns box_not_configured (503) while Enterprise_Id__c is blank, so this is the
 * gate that makes the downscoped-token endpoint reachable at all. It sets only the
 * non-secret half of the configuration -- the Box client id and secret belong on the
 * CLM_Box external credential (MT-038) and are never touched here.
 *
 * Idempotent by the org-default record: reruns update the same row rather than adding
 * one, and report whether anything actually changed.
 *
 * The two tokens below are substituted by the wrapper. Running this file directly
 * without substitution aborts instead of writing placeholder text into the org.
 */
String enterpriseId    = '__BOX_ENTERPRISE_ID__';
String allowedFolderIds = '__BOX_ALLOWED_FOLDER_IDS__';

// ---------- Guard: refuse unsubstituted input ----------
if (enterpriseId.startsWith('__BOX_')) {
    throw new System.IllegalArgumentException(
        'BOX CONFIG: enterprise id was not substituted. Run configure-clm-box-settings.sh instead of this file.');
}
if (allowedFolderIds.startsWith('__BOX_')) {
    throw new System.IllegalArgumentException(
        'BOX CONFIG: folder allowlist was not substituted. Run configure-clm-box-settings.sh instead of this file.');
}

// ---------- Validate against what the endpoint and the fields will accept ----------
enterpriseId = enterpriseId.trim();
if (String.isBlank(enterpriseId)) {
    throw new System.IllegalArgumentException('BOX CONFIG: enterprise id is required; a blank value leaves the endpoint returning box_not_configured.');
}
if (!enterpriseId.isNumeric()) {
    throw new System.IllegalArgumentException('BOX CONFIG: enterprise id must be numeric.');
}
if (enterpriseId.length() > 64) {
    throw new System.IllegalArgumentException('BOX CONFIG: enterprise id exceeds the 64-character field length.');
}

// Normalize the allowlist so stored values match the numeric folder ids the endpoint
// compares against. ClmBoxTokenService trims each entry, but a non-numeric entry would
// be dead weight: such a folderId is rejected by isNumeric() before the list is consulted.
List<String> normalizedFolderIds = new List<String>();
for (String candidate : allowedFolderIds.split(',')) {
    String folderId = candidate.trim();
    if (String.isBlank(folderId)) {
        continue;
    }
    if (!folderId.isNumeric()) {
        throw new System.IllegalArgumentException(
            'BOX CONFIG: allowlist entry "' + folderId + '" is not numeric; the endpoint rejects non-numeric folder ids with invalid_folder_id.');
    }
    normalizedFolderIds.add(folderId);
}
String normalizedAllowlist = String.join(normalizedFolderIds, ',');
if (normalizedAllowlist.length() > 255) {
    throw new System.IllegalArgumentException('BOX CONFIG: folder allowlist exceeds the 255-character field length.');
}

// ---------- Upsert the org default ----------
CLM_Box_Config__c config = CLM_Box_Config__c.getOrgDefaults();
if (config == null) {
    config = new CLM_Box_Config__c();
}
Boolean creating = config.Id == null;
if (creating) {
    config.SetupOwnerId = UserInfo.getOrganizationId();
}

String priorEnterpriseId = config.Enterprise_Id__c;
String priorAllowlist = config.Allowed_Folder_Ids__c;
Boolean changed = creating
    || enterpriseId != priorEnterpriseId
    || normalizedAllowlist != (priorAllowlist == null ? '' : priorAllowlist);

config.Enterprise_Id__c = enterpriseId;
config.Allowed_Folder_Ids__c = normalizedAllowlist;
upsert config;

// ---------- Report without echoing the values ----------
String action = creating ? 'created' : (changed ? 'updated' : 'unchanged');
String enterpriseHint = '...' + enterpriseId.right(4);
System.debug(LoggingLevel.INFO, 'BOX CONFIG: org-default record ' + action
    + ' (enterprise id ' + enterpriseHint + ', ' + normalizedFolderIds.size() + ' allowed folder id(s))');

if (normalizedFolderIds.isEmpty()) {
    System.debug(LoggingLevel.WARN, 'BOX CONFIG: the allowlist is empty, which ClmBoxTokenService treats as "allow any folder". '
        + 'Populate Allowed Folder Ids to scope the endpoint to the demo workspace.');
}
System.debug(LoggingLevel.INFO, 'BOX CONFIG: next, verify the endpoint: '
    + 'sf api request rest "/services/apexrest/clm/box-token?folderId=<box-folder-id>" --target-org <alias>');
