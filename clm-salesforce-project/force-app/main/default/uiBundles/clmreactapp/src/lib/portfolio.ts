import type { ClmContractSummary } from "./contracts";

/**
 * The shapes the portfolio views draw.
 *
 * Derivation lives here rather than in the components so the tiles, the donut and the bar
 * chart cannot disagree: a headline reading "8 contracts" above a donut summing to 7 is
 * the kind of error a reader notices and a developer does not.
 */

export interface Slice {
  label: string;
  value: number;
}

/**
 * Contracts by status, largest first, with a stable order for equal counts.
 *
 * Categorical hues are assigned by position, so the order has to be deterministic -- a
 * status that changes colour between renders because two counts tied is exactly the
 * "colour follows rank, not entity" mistake.
 */
export function byStatus(contracts: ClmContractSummary[]): Slice[] {
  const counts = new Map<string, number>();
  for (const contract of contracts) {
    const label = contract.status?.trim() || "Unknown";
    counts.set(label, (counts.get(label) || 0) + 1);
  }
  return [...counts.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value || a.label.localeCompare(b.label));
}

/**
 * Total contract value per counterparty, largest first.
 *
 * Contracts with no value still count toward their counterparty at zero rather than
 * vanishing: a counterparty absent from the chart reads as "no relationship", which is a
 * different claim from "no value recorded".
 */
export function valueByCounterparty(contracts: ClmContractSummary[]): Slice[] {
  const totals = new Map<string, number>();
  for (const contract of contracts) {
    const label = contract.counterparty?.trim() || "Unknown";
    totals.set(label, (totals.get(label) || 0) + (contract.dealValue || 0));
  }
  return [...totals.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value || a.label.localeCompare(b.label));
}

export interface PortfolioTotals {
  contracts: number;
  value: number;
  /** Anything not yet executed -- the work still in front of somebody. */
  inFlight: number;
}

export function portfolioTotals(contracts: ClmContractSummary[]): PortfolioTotals {
  return {
    contracts: contracts.length,
    value: contracts.reduce((sum, c) => sum + (c.dealValue || 0), 0),
    inFlight: contracts.filter((c) => (c.status || "").toLowerCase() !== "executed").length,
  };
}

/** Compact currency, because these sit in tiles and axis labels, not in a ledger. */
export function formatCompactValue(value: number): string {
  if (!Number.isFinite(value) || value === 0) return "$0";
  if (Math.abs(value) >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (Math.abs(value) >= 1_000) return `$${Math.round(value / 1_000)}K`;
  return `$${Math.round(value)}`;
}

/** Total value per contract, largest first. Labelled by reference, which is what the row says. */
export function valueByContract(contracts: ClmContractSummary[]): Slice[] {
  return contracts
    .map((contract) => ({
      label: contract.contractId || contract.name || contract.recordId,
      value: contract.dealValue || 0,
    }))
    .sort((a, b) => b.value - a.value || a.label.localeCompare(b.label));
}

/**
 * The breakdown worth drawing, and what to call it.
 *
 * A counterparty sees contracts with exactly one organisation, so "value by counterparty"
 * is a single bar -- a chart that has nothing to compare. Falling back to per-contract
 * gives the same reader the comparison they can actually use, and an internal reader with
 * several counterparties still gets the portfolio view. The chart shows whichever
 * dimension actually varies.
 */
export function valueBreakdown(contracts: ClmContractSummary[]): { title: string; slices: Slice[] } {
  const byParty = valueByCounterparty(contracts);
  return byParty.length > 1
    ? { title: "Value by counterparty", slices: byParty }
    : { title: "Value by contract", slices: valueByContract(contracts) };
}

export interface Renewal {
  label: string;
  endDate: string;
  /** Negative once the term has already ended. */
  daysRemaining: number;
}

/** Whole days between two dates, ignoring the time of day so "today" is zero, not -1. */
function daysBetween(from: Date, to: Date): number {
  const day = 24 * 60 * 60 * 1000;
  const a = Date.UTC(from.getUTCFullYear(), from.getUTCMonth(), from.getUTCDate());
  const b = Date.UTC(to.getUTCFullYear(), to.getUTCMonth(), to.getUTCDate());
  return Math.round((b - a) / day);
}

/**
 * Contracts whose term ends within `withinDays`, soonest first.
 *
 * Only contracts that carry an end date can appear, which means only executed ones: a
 * contract still being negotiated has no agreed term, and inventing an expiry for it would
 * put a renewal date on a deal nobody has signed.
 *
 * Terms that have already lapsed are included rather than filtered out. A contract that
 * ended last month is more urgent than one ending next month, and dropping it would leave
 * the most exposed part of the portfolio off the chart that exists to show exposure.
 */
export function renewalHorizon(
  contracts: ClmContractSummary[],
  withinDays = 90,
  today = new Date(),
): Renewal[] {
  return contracts
    .flatMap((contract) => {
      if (!contract.endDate) return [];
      const end = new Date(contract.endDate);
      if (Number.isNaN(end.getTime())) return [];
      const daysRemaining = daysBetween(today, end);
      if (daysRemaining > withinDays) return [];
      return [{
        label: contract.contractId || contract.name || contract.recordId,
        endDate: contract.endDate,
        daysRemaining,
      }];
    })
    .sort((a, b) => a.daysRemaining - b.daysRemaining);
}
