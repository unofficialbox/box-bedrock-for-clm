/**
 * CLM contract records for the dashboard.
 *
 * Read through a dedicated Apex endpoint rather than a Salesforce object API. The
 * Experience Cloud guest user holds no permissions on CLM_Contract__c; it is granted the
 * ClmContractListService class, and that class returns a fixed projection. So the shape
 * below is the whole of what the browser can see, by design.
 */

import { apexRestUrl } from "./apexRest";

export interface ClmContractSummary {
  recordId: string;
  contractId?: string;
  name?: string;
  counterparty?: string;
  contractType?: string;
  status?: string;
  riskLevel?: string;
  dealValue?: number;
  termMonths?: number;
  /** The Box workspace folder associated with this contract record. */
  boxFolderId?: string;
}

/**
 * Null when the endpoint could not be reached, so the dashboard can fall back to its
 * synthetic fixture and still demo with no org behind it. An empty array means the org
 * genuinely has no contracts, which is a valid state and not a failure -- an org that has
 * not been seeded yet should say so rather than show a fixture and claim Salesforce is
 * unreachable.
 */
export async function fetchClmContracts(): Promise<ClmContractSummary[] | null> {
  try {
    const response = await fetch(apexRestUrl("/services/apexrest/clm/contracts"), {
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      console.warn(
        `[CLM] Contract list returned ${response.status}; falling back to fixtures.`,
        await response.text().catch(() => "")
      );
      return null;
    }
    const result = (await response.json()) as ClmContractSummary[];
    return Array.isArray(result) ? result.filter((row) => row && row.recordId) : null;
  } catch (error) {
    console.warn("[CLM] Contract list unreachable; falling back to fixtures.", error);
    return null;
  }
}

/** Deal values arrive as raw numbers; the banner and list want one readable form. */
export function formatDealValue(value?: number): string {
  if (value == null) return "—";
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${Math.round(value / 1_000)}K`;
  return `$${value}`;
}
