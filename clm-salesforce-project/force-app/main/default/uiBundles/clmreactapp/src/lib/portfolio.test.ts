import { describe, expect, test } from "vitest";
import type { ClmContractSummary } from "./contracts";
import { byStatus, formatCompactValue, portfolioTotals, valueByCounterparty } from "./portfolio";

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
