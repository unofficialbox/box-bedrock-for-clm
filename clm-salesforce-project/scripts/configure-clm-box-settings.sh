#!/usr/bin/env bash
set -euo pipefail

# Set the non-secret Box settings on the CLM Box Config org default (MT-039).
# The Box client id and secret are NOT set here -- they belong on the CLM_Box
# external credential in Setup (MT-038) and never pass through this repository.
#
#   BOX_ENTERPRISE_ID=<id> BOX_ALLOWED_FOLDER_IDS=<id,id> \
#     clm-salesforce-project/scripts/configure-clm-box-settings.sh <org-alias>
#
# Values are substituted into a temporary copy of the .apex file, so no live
# identifier is ever written into the working tree.
#
# Find the enterprise id with:  box users:get --fields=enterprise
# Find folder ids with:         box folders:items 0 --fields=id,name,type

ORG_ALIAS="${1:-agentforce}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE="${SCRIPT_DIR}/configure-clm-box-settings.apex"

if ! command -v sf >/dev/null 2>&1; then
  echo "sf CLI is not installed." >&2
  exit 1
fi

: "${BOX_ENTERPRISE_ID:?set BOX_ENTERPRISE_ID (find it with: box users:get --fields=enterprise)}"
BOX_ALLOWED_FOLDER_IDS="${BOX_ALLOWED_FOLDER_IDS:-}"

# Validate here as well as in Apex: it fails in a second instead of a round trip,
# and it guarantees the substituted text cannot contain sed metacharacters.
if ! [[ "${BOX_ENTERPRISE_ID}" =~ ^[0-9]+$ ]]; then
  echo "BOX_ENTERPRISE_ID must be numeric." >&2
  exit 1
fi
if [[ -n "${BOX_ALLOWED_FOLDER_IDS}" ]] && ! [[ "${BOX_ALLOWED_FOLDER_IDS}" =~ ^[0-9]+(,[0-9]+)*$ ]]; then
  echo "BOX_ALLOWED_FOLDER_IDS must be a comma-separated list of numeric folder ids." >&2
  exit 1
fi
if [[ -z "${BOX_ALLOWED_FOLDER_IDS}" ]]; then
  echo "Warning: BOX_ALLOWED_FOLDER_IDS is empty, which allows the endpoint to mint a token for ANY folder." >&2
fi

RESOLVED="$(mktemp -t clm-box-settings)"
trap 'rm -f "${RESOLVED}"' EXIT
chmod 600 "${RESOLVED}"

sed -e "s|__BOX_ENTERPRISE_ID__|${BOX_ENTERPRISE_ID}|g" \
    -e "s|__BOX_ALLOWED_FOLDER_IDS__|${BOX_ALLOWED_FOLDER_IDS}|g" \
    "${TEMPLATE}" > "${RESOLVED}"

echo "Setting CLM Box Config org defaults against org: ${ORG_ALIAS}"
sf apex run --target-org "${ORG_ALIAS}" --file "${RESOLVED}"
