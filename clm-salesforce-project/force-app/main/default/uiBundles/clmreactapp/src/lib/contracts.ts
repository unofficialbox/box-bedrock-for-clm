/**
 * CLM contract records for the dashboard.
 *
 * Read through a dedicated Apex endpoint rather than a Salesforce object API. The
 * Experience Cloud guest user holds no permissions on CLM_Contract__c; it is granted the
 * ClmContractListService class, and that class returns a fixed projection. So the shape
 * below is the whole of what the browser can see, by design.
 */

import { apexRestUrl } from "./apexRest";
import { describeError, failed, firstLine, type Loaded } from "./loaded";

export interface ClmContractSummary {
  recordId: string;
  contractId?: string;
  name?: string;
  counterparty?: string;
  /** The signing subsidiary, where a counterparty contracts through several entities. */
  counterpartyEntity?: string;
  contractType?: string;
  status?: string;
  riskLevel?: string;
  dealValue?: number;
  termMonths?: number;
  /** ISO date the term ends. Absent while a contract is still being negotiated. */
  endDate?: string;
  /** The Box workspace folder associated with this contract record. */
  boxFolderId?: string;
}

/**
 * The contract records this user may see.
 *
 * An empty array is a real answer -- an org that has not been seeded yet genuinely has no
 * contracts -- and is distinct from a failure, which carries the reason it failed. There
 * is no third case where the page invents rows: a list that cannot be read says so.
 */
export async function fetchClmContracts(): Promise<Loaded<ClmContractSummary[]>> {
  try {
    const response = await fetch(apexRestUrl("/services/apexrest/clm/contracts"), {
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      const detail = firstLine(await response.text().catch(() => ""));
      return failed(
        `Salesforce returned ${response.status} for the contract list.${detail ? ` ${detail}` : ""}`,
      );
    }
    const result: unknown = await response.json();
    if (!Array.isArray(result)) {
      return failed("The contract endpoint answered with something that is not a list of records.");
    }
    return { ok: true, value: (result as ClmContractSummary[]).filter((row) => row && row.recordId) };
  } catch (error) {
    return failed(`The contract endpoint could not be reached. ${describeError(error)}`);
  }
}

/** Deal values arrive as raw numbers; the banner and list want one readable form. */
export function formatDealValue(value?: number): string {
  if (value == null) return "—";
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${Math.round(value / 1_000)}K`;
  return `$${value}`;
}
