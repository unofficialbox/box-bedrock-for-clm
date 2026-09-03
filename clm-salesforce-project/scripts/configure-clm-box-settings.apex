/*
 * Create or update the CLM Box Config org-default record (MT-039).
 * Run with the wrapper, which injects the values so no live ID lands in the working tree:
 *   BOX_USER_ID=<id> BOX_ALLOWED_FOLDER_IDS=<id,id> \
 *     clm-salesforce-project/scripts/configure-clm-box-settings.sh <org-alias>
 *
 * ClmBoxTokenService reads CLM_Box_Config__c.getOrgDefaults() on every request and
 * returns box_not_configured (503) until a CCG subject is set, so this is the gate that
 * makes the downscoped-token endpoint reachable at all. It sets only the non-secret half
 * of the configuration -- the Box client id and secret belong on the CLM_Box external
 * credential (MT-038) and are never touched here.
 *
 * Subject choice. BOX_USER_ID grants as that Box user, so the token inherits access the
 * user already has and no folder collaboration is needed; this is the demo default.
 * BOX_ENTERPRISE_ID instead grants a Service Account token, whose root starts empty, so
 * the service identity must be collaborated onto the folder. Set one. If both are set the
 * user wins, matching ClmBoxTokenService.
 *
 * Idempotent by the org-default record: reruns update the same row rather than adding
 * one, and report whether anything actually changed.
 *
 * The tokens below are substituted by the wrapper. Running this file directly without
 * substitution aborts instead of writing placeholder text into the org.
 */
String boxUserId        = '__BOX_USER_ID__';
String enterpriseId     = '__BOX_ENTERPRISE_ID__';
String allowedFolderIds = '__BOX_ALLOWED_FOLDER_IDS__';
String contractsRoot    = '__BOX_CONTRACTS_ROOT_FOLDER_ID__';
String clauseLibraryHub = '__BOX_CLAUSE_LIBRARY_HUB_ID__';
String counterTemplate  = '__BOX_COUNTER_POSITION_TEMPLATE_ID__';
String demoSigner       = '__CLM_DEMO_SIGNER_EMAIL__';

// ---------- Guard: refuse unsubstituted input ----------
for (String raw : new List<String>{ boxUserId, enterpriseId, allowedFolderIds,
        contractsRoot, clauseLibraryHub, counterTemplate, demoSigner }) {
    if (raw.startsWith('__BOX_') || raw.startsWith('__CLM_')) {
        throw new System.IllegalArgumentException(
            'BOX CONFIG: values were not substituted. Run configure-clm-box-settings.sh instead of this file.');
    }
}

// ---------- Validate against what the endpoint and the fields will accept ----------
boxUserId = boxUserId.trim();
enterpriseId = enterpriseId.trim();

if (String.isBlank(boxUserId) && String.isBlank(enterpriseId)) {
    throw new System.IllegalArgumentException(
        'BOX CONFIG: set a Box user id or an enterprise id; without one the endpoint returns box_not_configured.');
}
if (String.isNotBlank(boxUserId) && !boxUserId.isNumeric()) {
    throw new System.IllegalArgumentException('BOX CONFIG: Box user id must be numeric.');
}
if (String.isNotBlank(enterpriseId) && !enterpriseId.isNumeric()) {
    throw new System.IllegalArgumentException('BOX CONFIG: enterprise id must be numeric.');
}
if (boxUserId.length() > 64 || enterpriseId.length() > 64) {
    throw new System.IllegalArgumentException('BOX CONFIG: subject id exceeds the 64-character field length.');
}

// The four settings below are what the governed actions read before they will run at
// all. Each is optional here so a partial environment can still be configured, and each
// one left blank turns into a refusal at the action rather than a wrong answer.
contractsRoot = contractsRoot.trim();
clauseLibraryHub = clauseLibraryHub.trim();
counterTemplate = counterTemplate.trim();
demoSigner = demoSigner.trim();

if (String.isNotBlank(contractsRoot) && !contractsRoot.isNumeric()) {
    throw new System.IllegalArgumentException(
        'BOX CONFIG: the contracts root must be a numeric Box folder id; it is the ancestor_folder_id that bounds the portfolio search.');
}
if (String.isNotBlank(demoSigner) && !demoSigner.contains('@')) {
    throw new System.IllegalArgumentException('BOX CONFIG: the demo signer must be an email address.');
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

// A value not supplied leaves the stored one alone. The alternative -- writing every
// field every run -- means one forgotten export silently erases working configuration,
// and the failure only shows up as a refusal on stage. To clear one of these, clear the
// field in Setup.
String keptRoot     = String.isBlank(contractsRoot)    ? config.Contracts_Root_Folder_Id__c     : contractsRoot;
String keptHub      = String.isBlank(clauseLibraryHub) ? config.Clause_Library_Hub_Id__c        : clauseLibraryHub;
String keptTemplate = String.isBlank(counterTemplate)  ? config.Counter_Position_Template_ID__c : counterTemplate;
String keptSigner   = String.isBlank(demoSigner)       ? config.Demo_Signer_Email__c            : demoSigner;

Boolean changed = creating
    || boxUserId != (config.Box_User_Id__c == null ? '' : config.Box_User_Id__c)
    || enterpriseId != (config.Enterprise_Id__c == null ? '' : config.Enterprise_Id__c)
    || normalizedAllowlist != (config.Allowed_Folder_Ids__c == null ? '' : config.Allowed_Folder_Ids__c)
    || keptRoot != config.Contracts_Root_Folder_Id__c
    || keptHub != config.Clause_Library_Hub_Id__c
    || keptTemplate != config.Counter_Position_Template_ID__c
    || keptSigner != config.Demo_Signer_Email__c;

config.Box_User_Id__c = boxUserId;
config.Enterprise_Id__c = enterpriseId;
config.Allowed_Folder_Ids__c = normalizedAllowlist;
config.Contracts_Root_Folder_Id__c = keptRoot;
config.Clause_Library_Hub_Id__c = keptHub;
config.Counter_Position_Template_ID__c = keptTemplate;
config.Demo_Signer_Email__c = keptSigner;
upsert config;

// ---------- Report without echoing the values ----------
String subjectType = String.isNotBlank(boxUserId) ? 'user' : 'enterprise';
String subjectId = String.isNotBlank(boxUserId) ? boxUserId : enterpriseId;
String action = creating ? 'created' : (changed ? 'updated' : 'unchanged');
System.debug(LoggingLevel.INFO, 'BOX CONFIG: org-default record ' + action
    + ' (subject ' + subjectType + ' ...' + subjectId.right(4)
    + ', ' + normalizedFolderIds.size() + ' allowed folder id(s))');

if (String.isNotBlank(boxUserId) && String.isNotBlank(enterpriseId)) {
    System.debug(LoggingLevel.WARN, 'BOX CONFIG: both a user id and an enterprise id are set. '
        + 'ClmBoxTokenService grants as the user; the enterprise id is unused.');
}
if (normalizedFolderIds.isEmpty()) {
    System.debug(LoggingLevel.WARN, 'BOX CONFIG: the allowlist is empty, which ClmBoxTokenService treats as "allow any folder". '
        + 'Populate Allowed Folder Ids to scope the endpoint to the demo workspace.');
}
Map<String, String> blank = new Map<String, String>();
if (String.isBlank(keptRoot)) {
    blank.put('Contracts_Root_Folder_Id__c', 'the portfolio risk search will refuse as unbounded');
}
if (String.isBlank(keptHub)) {
    blank.put('Clause_Library_Hub_Id__c', 'clause-library questions have nothing governed to read against');
}
if (String.isBlank(keptTemplate)) {
    blank.put('Counter_Position_Template_ID__c', 'the counter-position memo cannot be generated');
}
if (String.isBlank(keptSigner)) {
    blank.put('Demo_Signer_Email__c', 'the signature action will refuse rather than invent a signer');
}
for (String field : blank.keySet()) {
    System.debug(LoggingLevel.WARN, 'BOX CONFIG: ' + field + ' is blank -- ' + blank.get(field) + '.');
}

System.debug(LoggingLevel.INFO, 'BOX CONFIG: next, verify the endpoint: '
    + 'sf api request rest "/services/apexrest/clm/box-token?folderId=<box-folder-id>" --target-org <alias>');
