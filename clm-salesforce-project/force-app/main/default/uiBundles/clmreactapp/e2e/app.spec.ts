import { expect, test } from "@playwright/test";

test("contract workspace exposes Salesforce record, Box content, and human approval state", async ({ page }) => {
  await page.goto("/?recordId=a01xx0000001234&contractId=CLM-2026-0017&folderId=123");
  await expect(page).toHaveTitle(/Acme Contracts/);
  await expect(page.getByRole("heading", { name: "Northstar Health MSA" })).toBeVisible();
  await expect(page.getByText(/Salesforce a01xx0000001234/)).toBeVisible();
  await expect(page.getByTestId("box-fallback")).toBeVisible();
  await expect(page.getByTestId("agentforce-placeholder")).toBeVisible();

  await page.getByRole("button", { name: /Redline reviews/ }).click();
  await expect(page.getByTestId("approvals-view")).toBeVisible();
  await expect(page.getByText("Jordan Lee")).toBeVisible();
  await expect(page.getByText("Counterparty removed the aggregate liability cap.")).toBeVisible();
  await expect(page.getByText("Signature blocked")).toBeVisible();
  await expect(page.getByRole("button", { name: /approve/i })).toHaveCount(0);
});
