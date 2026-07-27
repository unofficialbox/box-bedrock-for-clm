#!/usr/bin/env bash
set -euo pipefail

# Upload each CLM_Contract__c record's contract document into its Box folder.
# Run AFTER seed-clm-sample-data.sh, and after deploying the Clm_Sample_Msa_* static resources.

ORG_ALIAS="${1:-agentforce}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v sf >/dev/null 2>&1; then
  echo "sf CLI is not installed." >&2
  exit 1
fi

echo "Uploading CLM contract files into Box record folders against org: ${ORG_ALIAS}"
sf apex run --target-org "${ORG_ALIAS}" --file "${SCRIPT_DIR}/seed-clm-contract-files.apex"
