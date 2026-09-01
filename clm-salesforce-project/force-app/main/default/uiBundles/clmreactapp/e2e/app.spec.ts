import { expect, test } from "@playwright/test";

test("contract workspace opens on Box content, and speaks for no contract it cannot name", async ({ page }) => {
  await page.goto("/?recordId=a01xx0000001234&contractId=CLM-2026-0017&folderId=123");
  await expect(page).toHaveTitle(/Acme Contracts/);
  await expect(page.getByTestId("box-fallback")).toBeVisible();
  await expect(page.getByTestId("agentforce-placeholder")).toBeVisible();
  // Deep-linked by record, so the app has ids but not the contract's fields. It used to
  // fill the banner from a fixture, which stated another contract's name, value and term
  // as if they were this one's -- and put the Salesforce record id in front of a
  // counterparty.
  await expect(page.locator(".contract-banner")).toHaveCount(0);
  await expect(page.getByText(/Salesforce a01xx0000001234/)).toHaveCount(0);
});

test("shows a counterparty nothing of Acme's own review process", async ({ page }) => {
  // The site serves the counterparty; the internal persona works through the MCP server.
  // The redline queue named Acme's reviewers and told the customer which of their own asks
  // was blocking signature, and "Copy agent context" papered over a limitation they should
  // never meet. Both are gone, and this is what stops either coming back by accident.
  await page.goto("/?recordId=a01xx0000001234&contractId=CLM-2026-0017&folderId=123");
  await expect(page.getByRole("button", { name: /Your contracts/ })).toBeVisible();
  await expect(page.getByRole("button", { name: /Redline reviews/ })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /Copy agent context/ })).toHaveCount(0);
  await expect(page.getByTestId("approvals-view")).toHaveCount(0);
  await expect(page.getByText("Jordan Lee")).toHaveCount(0);
});
