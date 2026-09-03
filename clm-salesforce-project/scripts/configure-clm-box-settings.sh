#!/usr/bin/env bash
set -euo pipefail

# Set the non-secret Box settings on the CLM Box Config org default (MT-039).
# The Box client id and secret are NOT set here -- they belong on the CLM_Box
# external credential in Setup (MT-038) and never pass through this repository.
#
# Values come from config/deploy/environment.local.bcl, or from the environment, which
# wins so a one-off run can override the file without editing it. See
# docs/operator/deployment.md.
#
#   clm-salesforce-project/scripts/configure-clm-box-settings.sh <org-alias>
#
# or, for a single run:
#
#   BOX_USER_ID=<id> clm-salesforce-project/scripts/configure-clm-box-settings.sh <org-alias>
#
# Set BOX_USER_ID to grant as a Box user (the demo default: the token inherits
# that user's access, so no folder collaboration is needed), or BOX_ENTERPRISE_ID
# to grant a Service Account token (which must be collaborated onto the folder).
# If both are set the user wins, matching ClmBoxTokenService.
#
# Values are substituted into a temporary copy of the .apex file, so no live
# identifier is ever written into the working tree.
#
# Find the user id with:       box users:get --fields=id,login
# Find the enterprise id with: box users:get --fields=enterprise
# Find folder ids with:        box folders:items 0 --fields=id,name,type

ORG_ALIAS="${1:-agentforce}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE="${SCRIPT_DIR}/configure-clm-box-settings.apex"

if ! command -v sf >/dev/null 2>&1; then
  echo "sf CLI is not installed." >&2
  exit 1
fi

# Fill anything the shell did not supply from the BCL. The helper prints only
# assignments, so an eval here cannot run anything the file smuggles in.
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
if [[ -f "${REPO_ROOT}/scripts/clm_env.py" ]]; then
  RESOLVED_ENV="$(python3 "${REPO_ROOT}/scripts/clm_env.py" --export 2>/dev/null || true)"
  while IFS= read -r ASSIGNMENT; do
    [[ -z "${ASSIGNMENT}" ]] && continue
    NAME="${ASSIGNMENT%%=*}"
    [[ -n "${!NAME:-}" ]] && continue        # the environment already answered
    eval "export ${ASSIGNMENT}"
  done <<< "${RESOLVED_ENV}"
fi

BOX_USER_ID="${BOX_USER_ID:-}"
BOX_ENTERPRISE_ID="${BOX_ENTERPRISE_ID:-}"
BOX_CONTRACTS_ROOT_FOLDER_ID="${BOX_CONTRACTS_ROOT_FOLDER_ID:-}"
BOX_CLAUSE_LIBRARY_HUB_ID="${BOX_CLAUSE_LIBRARY_HUB_ID:-}"
BOX_COUNTER_POSITION_TEMPLATE_ID="${BOX_COUNTER_POSITION_TEMPLATE_ID:-}"
CLM_DEMO_SIGNER_EMAIL="${CLM_DEMO_SIGNER_EMAIL:-}"

if [[ -z "${BOX_USER_ID}" && -z "${BOX_ENTERPRISE_ID}" ]]; then
  echo "Set BOX_USER_ID (preferred) or BOX_ENTERPRISE_ID, in config/deploy/environment.local.bcl or the environment." >&2
  echo "  BOX_USER_ID:       box users:get --fields=id,login" >&2
  echo "  BOX_ENTERPRISE_ID: box users:get --fields=enterprise" >&2
  exit 1
fi

# Validate here as well as in Apex: it fails in a second instead of a round trip,
# and it guarantees the substituted text cannot contain sed metacharacters.
for VAR in BOX_USER_ID BOX_ENTERPRISE_ID BOX_CONTRACTS_ROOT_FOLDER_ID; do
  VALUE="${!VAR}"
  if [[ -n "${VALUE}" ]] && ! [[ "${VALUE}" =~ ^[0-9]+$ ]]; then
    echo "${VAR} must be numeric." >&2
    exit 1
  fi
done
if [[ -n "${BOX_USER_ID}" && -n "${BOX_ENTERPRISE_ID}" ]]; then
  echo "Warning: both BOX_USER_ID and BOX_ENTERPRISE_ID are set; the user subject wins." >&2
fi

# Each of these is read by one governed action, and each one blank turns into a refusal
# at demo time rather than a wrong answer. Name the cost now, not on stage.
warn_blank() {
  [[ -n "${!1:-}" ]] || echo "Warning: ${1} is not set -- ${2}." >&2
}
warn_blank BOX_CONTRACTS_ROOT_FOLDER_ID "the portfolio risk search will refuse as unbounded"
warn_blank BOX_CLAUSE_LIBRARY_HUB_ID "clause-library questions have nothing governed to read against"
warn_blank BOX_COUNTER_POSITION_TEMPLATE_ID "the counter-position memo cannot be generated"
warn_blank CLM_DEMO_SIGNER_EMAIL "the signature action will refuse rather than invent a signer"

RESOLVED="$(mktemp -t clm-box-settings)"
trap 'rm -f "${RESOLVED}"' EXIT
chmod 600 "${RESOLVED}"

sed -e "s|__BOX_USER_ID__|${BOX_USER_ID}|g" \
    -e "s|__BOX_ENTERPRISE_ID__|${BOX_ENTERPRISE_ID}|g" \
    -e "s|__BOX_CONTRACTS_ROOT_FOLDER_ID__|${BOX_CONTRACTS_ROOT_FOLDER_ID}|g" \
    -e "s|__BOX_CLAUSE_LIBRARY_HUB_ID__|${BOX_CLAUSE_LIBRARY_HUB_ID}|g" \
    -e "s|__BOX_COUNTER_POSITION_TEMPLATE_ID__|${BOX_COUNTER_POSITION_TEMPLATE_ID}|g" \
    -e "s|__CLM_DEMO_SIGNER_EMAIL__|${CLM_DEMO_SIGNER_EMAIL}|g" \
    "${TEMPLATE}" > "${RESOLVED}"

echo "Setting CLM Box Config org defaults against org: ${ORG_ALIAS}"
sf apex run --target-org "${ORG_ALIAS}" --file "${RESOLVED}"
