import { describe, expect, test } from "vitest";
import type { ClmContractSummary } from "./contracts";
import { byStatus, formatCompactValue, portfolioTotals, valueByCounterparty, valueBreakdown, renewalHorizon } from "./portfolio";

const c = (over: Partial<ClmContractSummary>): ClmContractSummary => ({ recordId: "r", ...over });

describe("byStatus", () => {
  test("counts by status, largest first", () => {
    expect(
      byStatus([c({ status: "Executed" }), c({ status: "Legal Review" }), c({ status: "Executed" })]),
    ).toEqual([
      { label: "Executed", value: 2 },
      { label: "Legal Review", value: 1 },
    ]);
  });

  test("breaks ties by label so a hue never moves between renders", () => {
    // Categorical colour is assigned by position, so equal counts must not reorder --
    // that is colour following rank instead of the entity it names.
    const once = byStatus([c({ status: "Zulu" }), c({ status: "Alpha" })]);
    const again = byStatus([c({ status: "Alpha" }), c({ status: "Zulu" })]);
    expect(once).toEqual(again);
    expect(once[0].label).toBe("Alpha");
  });

  test("names a missing status rather than dropping the contract", () => {
    expect(byStatus([c({})])).toEqual([{ label: "Unknown", value: 1 }]);
  });
});

describe("valueByCounterparty", () => {
  test("sums value per counterparty, largest first", () => {
    expect(
      valueByCounterparty([
        c({ counterparty: "Calder", dealValue: 1_000_000 }),
        c({ counterparty: "Northstar", dealValue: 2_400_000 }),
        c({ counterparty: "Calder", dealValue: 500_000 }),
      ]),
    ).toEqual([
      { label: "Northstar", value: 2_400_000 },
      { label: "Calder", value: 1_500_000 },
    ]);
  });

  test("keeps a counterparty whose contracts carry no value", () => {
    // Absent from the chart would read as "no relationship", which is a different claim
    // from "no value recorded".
    expect(valueByCounterparty([c({ counterparty: "Acme" })])).toEqual([{ label: "Acme", value: 0 }]);
  });
});

describe("portfolioTotals", () => {
  test("counts everything not executed as in flight", () => {
    const totals = portfolioTotals([
      c({ status: "Executed", dealValue: 100 }),
      c({ status: "Legal Review", dealValue: 200 }),
      c({ status: "Intake" }),
    ]);
    expect(totals).toEqual({ contracts: 3, value: 300, inFlight: 2 });
  });
});

describe("formatCompactValue", () => {
  test("scales to K and M and never renders NaN", () => {
    expect(formatCompactValue(2_400_000)).toBe("$2.4M");
    expect(formatCompactValue(250_000)).toBe("$250K");
    expect(formatCompactValue(0)).toBe("$0");
    expect(formatCompactValue(Number.NaN)).toBe("$0");
  });
});

describe("valueBreakdown", () => {
  test("falls back to per-contract when there is only one counterparty", () => {
    // A counterparty deals with exactly one organisation, so "by counterparty" is a single
    // bar with nothing to compare against. Their own contracts are the useful comparison.
    const result = valueBreakdown([
      c({ counterparty: "Northstar", contractId: "A", dealValue: 100 }),
      c({ counterparty: "Northstar", contractId: "B", dealValue: 200 }),
    ]);
    expect(result.title).toBe("Value by contract");
    expect(result.slices.map((s) => s.label)).toEqual(["B", "A"]);
  });

  test("keeps the portfolio view when counterparties actually differ", () => {
    const result = valueBreakdown([
      c({ counterparty: "Northstar", dealValue: 100 }),
      c({ counterparty: "Calder", dealValue: 200 }),
    ]);
    expect(result.title).toBe("Value by counterparty");
    expect(result.slices.map((s) => s.label)).toEqual(["Calder", "Northstar"]);
  });
});

describe("renewalHorizon", () => {
  const today = new Date("2026-09-01T00:00:00Z");

  test("includes terms already lapsed, soonest first", () => {
    // A contract that ended last month is more exposed than one ending next month.
    // Filtering it out would drop the worst case from the chart that exists to show it.
    const horizon = renewalHorizon(
      [
        c({ contractId: "ENDS-LATER", endDate: "2026-11-14" }),
        c({ contractId: "LAPSED", endDate: "2026-05-08" }),
        c({ contractId: "ENDS-SOON", endDate: "2026-09-30" }),
      ],
      90,
      today,
    );
    expect(horizon.map((r) => r.label)).toEqual(["LAPSED", "ENDS-SOON", "ENDS-LATER"]);
    expect(horizon[0].daysRemaining).toBeLessThan(0);
  });

  test("excludes terms beyond the window", () => {
    expect(renewalHorizon([c({ contractId: "FAR", endDate: "2027-07-31" })], 90, today)).toEqual([]);
  });

  test("ignores contracts with no end date rather than inventing one", () => {
    // A contract still in negotiation has no agreed term; a renewal date on it would
    // assert something nobody has signed.
    expect(renewalHorizon([c({ contractId: "IN-REVIEW", status: "Legal Review" })], 90, today)).toEqual([]);
  });

  test("counts the last day of the term as zero days remaining, not minus one", () => {
    expect(renewalHorizon([c({ contractId: "TODAY", endDate: "2026-09-01" })], 90, today)[0].daysRemaining).toBe(0);
  });
});
