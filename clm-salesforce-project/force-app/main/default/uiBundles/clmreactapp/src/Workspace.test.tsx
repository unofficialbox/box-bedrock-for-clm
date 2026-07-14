import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { Workspace } from "./Workspace";

beforeEach(() => {
  window.history.replaceState({}, "", "/");
  Object.assign(navigator, { clipboard: { writeText: vi.fn().mockResolvedValue(undefined) } });
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("local demo")));
});

describe("Workspace", () => {
  test("renders the Box-backed Northstar contract and safe Agentforce state", async () => {
    render(<Workspace />);
    expect(screen.getByRole("heading", { name: "Northstar Health MSA" })).toBeVisible();
    expect(await screen.findByTestId("box-fallback")).toBeVisible();
    expect(screen.getByTestId("agentforce-placeholder")).toBeVisible();
    expect(screen.getByText("northstar-msa-redline-v3.pdf")).toBeVisible();
  });

  test("groups cited redline findings by human expert and never presents an automated approval control", () => {
    render(<Workspace />);
    fireEvent.click(screen.getByRole("button", { name: /Redline reviews/ }));
    expect(screen.getByTestId("approvals-view")).toBeVisible();
    expect(screen.getByText("Jordan Lee")).toBeVisible();
    expect(screen.getByText("Priya Shah")).toBeVisible();
    expect(screen.getByText("Elena Torres")).toBeVisible();
    expect(screen.getByText("Counterparty removed the aggregate liability cap.")).toBeVisible();
    expect(screen.getByText(/Task assignee: configured Commercial Legal reviewer/)).toBeVisible();
    expect(screen.getByText(/Task assignee: configured Finance reviewer/)).toBeVisible();
    expect(screen.getByText(/Task assignee: configured Privacy reviewer/)).toBeVisible();
    expect(screen.getByText("Signature blocked")).toBeVisible();
    expect(screen.queryByRole("button", { name: /approve/i })).not.toBeInTheDocument();
  });

  test("shows the Salesforce record returned by the intake flow", () => {
    window.history.replaceState({}, "", "/?recordId=a01xx0000001234&contractId=CLM-99&folderId=123");
    render(<Workspace />);
    expect(screen.getByText(/CLM-99 · Salesforce a01xx0000001234/)).toBeVisible();
  });
});
