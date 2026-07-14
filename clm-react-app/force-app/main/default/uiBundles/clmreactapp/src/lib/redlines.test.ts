import { describe, expect, test } from "vitest";
import { EXPERT_ROUTES, REDLINE_FINDINGS } from "../data";
import { groupRedlineFindings } from "./redlines";

describe("groupRedlineFindings", () => {
  test("consolidates findings into one review queue item per expert domain", () => {
    const groups = groupRedlineFindings(REDLINE_FINDINGS, EXPERT_ROUTES);

    expect(groups).toHaveLength(3);
    expect(groups.find((group) => group.domain === "Commercial Legal")).toMatchObject({
      highestRisk: "Critical",
      minimumConfidence: 0.96,
      expert: { boxTaskId: "42899891150" },
    });
    expect(groups.find((group) => group.domain === "Commercial Legal")?.findings).toHaveLength(2);
  });

  test("fails closed when a domain has no configured expert", () => {
    expect(() => groupRedlineFindings(REDLINE_FINDINGS, EXPERT_ROUTES.slice(1))).toThrow(
      "No expert route configured for Commercial Legal",
    );
  });
});
