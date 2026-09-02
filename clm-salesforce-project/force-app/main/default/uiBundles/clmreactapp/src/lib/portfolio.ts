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
