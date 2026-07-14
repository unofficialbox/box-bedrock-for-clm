import { describe, expect, test } from "vitest";
import { getAgentContextPrompt, getClmPageContext } from "./box";

describe("CLM page context", () => {
  test("uses the live Northstar workspace by default", () => {
    expect(getClmPageContext("")).toEqual({
      contractId: "CLM-2026-0017",
      folderId: "399081692991",
    });
  });

  test("passes explicit record context to Agentforce with guardrails", () => {
    const prompt = getAgentContextPrompt("?recordId=a01xx0000001234&contractId=CLM-99&folderId=123");
    expect(prompt).toContain("Current CLM contract: CLM-99.");
    expect(prompt).toContain("Governed Box workspace folder ID: 123.");
    expect(prompt).toContain("Salesforce CLM record ID: a01xx0000001234.");
    expect(prompt).toContain("Do not approve legal language");
  });
});
