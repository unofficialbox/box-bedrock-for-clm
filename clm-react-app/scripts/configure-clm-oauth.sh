#!/usr/bin/env bash

set -euo pipefail

TARGET_ORG="${1:-agentforce}"
EXPECTED_ORG_ID="00DgL000003D0LRUA0"
INTEGRATION_USERNAME="box.automate.clm+00dgl000003d0lrua0@boxdemo.com"
INTEGRATION_EMAIL="kadams@boxdemo.com"
INTEGRATION_PROFILE="Minimum Access - API Only Integrations"
PERMISSION_SET="CLM_Box_Automate_Integration"

require_command() {
    command -v "$1" >/dev/null 2>&1 || {
        echo "Required command not found: $1" >&2
        exit 1
    }
}

require_command sf
require_command jq

deploy_source() {
    local deploy_json
    deploy_json="$(sf project deploy start \
        --target-org "$TARGET_ORG" \
        --wait 10 \
        --json \
        "$@")"

    if ! jq -e '.status == 0 and .result.success == true' >/dev/null <<<"$deploy_json"; then
        jq '{status, result: {id: .result.id, status: .result.status, failures: .result.details.componentFailures}}' <<<"$deploy_json" >&2
        exit 1
    fi

    jq '{id: .result.id, status: .result.status}' <<<"$deploy_json"
}

ORG_JSON="$(sf org display --target-org "$TARGET_ORG" --json)"
ORG_ID="$(jq -r '.result.id // empty' <<<"$ORG_JSON")"

if [[ "$ORG_ID" != "$EXPECTED_ORG_ID" ]]; then
    echo "Refusing to configure org $ORG_ID; expected $EXPECTED_ORG_ID." >&2
    exit 1
fi

PROFILE_ID="$(
    sf data query \
        --target-org "$TARGET_ORG" \
        --query "SELECT Id FROM Profile WHERE Name='${INTEGRATION_PROFILE}' AND UserLicense.Name='Salesforce Integration' LIMIT 1" \
        --json \
    | jq -r '.result.records[0].Id // empty'
)"

if [[ -z "$PROFILE_ID" ]]; then
    echo "Required integration profile not found: $INTEGRATION_PROFILE" >&2
    exit 1
fi

USER_ID="$(
    sf data query \
        --target-org "$TARGET_ORG" \
        --query "SELECT Id FROM User WHERE Username='${INTEGRATION_USERNAME}' LIMIT 1" \
        --json \
    | jq -r '.result.records[0].Id // empty'
)"

if [[ -z "$USER_ID" ]]; then
    USER_BODY="$(jq -nc \
        --arg username "$INTEGRATION_USERNAME" \
        --arg email "$INTEGRATION_EMAIL" \
        --arg profileId "$PROFILE_ID" \
        '{
            Username: $username,
            FirstName: "Integration",
            LastName: "Box Automate CLM",
            Alias: "boxclm",
            Email: $email,
            TimeZoneSidKey: "America/New_York",
            LocaleSidKey: "en_US",
            EmailEncodingKey: "UTF-8",
            LanguageLocaleKey: "en_US",
            ProfileId: $profileId,
            IsActive: true,
            UserPermissionsSFContentUser: false,
            UserPermissionsKnowledgeUser: false,
            UserPermissionsMarketingUser: false,
            UserPermissionsOfflineUser: false,
            UserPermissionsSupportUser: false
        }')"

    USER_ID="$(
        sf api request rest '/services/data/v67.0/sobjects/User' \
            --target-org "$TARGET_ORG" \
            --method POST \
            --header 'Content-Type: application/json' \
            --body "$USER_BODY" \
        | jq -r '.id // empty'
    )"

    if [[ -z "$USER_ID" ]]; then
        echo "Salesforce did not return the new integration user ID." >&2
        exit 1
    fi
fi

ASSIGNMENT_COUNT="$(
    sf data query \
        --target-org "$TARGET_ORG" \
        --query "SELECT COUNT() FROM PermissionSetAssignment WHERE AssigneeId='${USER_ID}' AND PermissionSet.Name='${PERMISSION_SET}'" \
        --json \
    | jq -r '.result.totalSize'
)"

if [[ "$ASSIGNMENT_COUNT" == "0" ]]; then
    sf org assign permset \
        --target-org "$TARGET_ORG" \
        --name "$PERMISSION_SET" \
        --on-behalf-of "$INTEGRATION_USERNAME"
fi

deploy_source \
    --source-dir force-app/main/default/externalClientApps/Box_Automate_CLM.eca-meta.xml

deploy_source \
    --source-dir force-app/main/default/extlClntAppGlobalOauthSets/Box_Automate_CLM_glbloauth.ecaGlblOauth-meta.xml \
    --source-dir force-app/main/default/extlClntAppOauthSettings/Box_Automate_CLM_oauth.ecaOauth-meta.xml

deploy_source \
    --source-dir force-app/main/default/extlClntAppOauthPolicies/Box_Automate_CLM_oauthPlcy.ecaOauthPlcy-meta.xml

sf data query \
    --target-org "$TARGET_ORG" \
    --query "SELECT Id,Username,IsActive,Profile.Name FROM User WHERE Id='${USER_ID}'"

sf data query \
    --target-org "$TARGET_ORG" \
    --query "SELECT Id,Assignee.Username,PermissionSet.Name FROM PermissionSetAssignment WHERE AssigneeId='${USER_ID}' AND PermissionSet.Name='${PERMISSION_SET}'"

sf org list metadata \
    --target-org "$TARGET_ORG" \
    --metadata-type ExternalClientApplication \
    --json \
| jq '.result[] | select(.fullName == "Box_Automate_CLM") | {id, fullName, lastModifiedDate}'

echo "Salesforce metadata configuration is complete."
echo "Manual secret handoff remains: copy the ECA consumer secret into the Box Automate managed OAuth connection."
