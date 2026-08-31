import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { Workspace } from "./Workspace";

beforeEach(() => {
  window.history.replaceState({}, "", "/");
  Object.assign(navigator, { clipboard: { writeText: vi.fn().mockResolvedValue(undefined) } });
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("local demo")));
});

describe("Workspace", () => {
  test("opens on the contract list when the page carries no record context", async () => {
    render(<Workspace />);
    // Nothing identifies a contract yet, so the dashboard is the entry point.
    expect(await screen.findByTestId("contracts-view")).toBeVisible();
    // Salesforce is unreachable here, so the list says so rather than showing empty.
    expect(screen.getByTestId("contracts-fixture-note")).toBeVisible();
  });

  test("opens the workspace for a contract chosen from the list", async () => {
    render(<Workspace />);
    fireEvent.click(await screen.findByTestId("contract-row"));
    expect(screen.getByRole("heading", { name: "Northstar Health MSA" })).toBeVisible();
    expect(await screen.findByTestId("box-fallback")).toBeVisible();
    expect(screen.getByTestId("agentforce-placeholder")).toBeVisible();
    expect(screen.getByText("northstar-msa-redline-v3.pdf")).toBeVisible();
  });

  test("goes straight to the workspace when the page is opened on a record", async () => {
    // A Lightning or Experience page bound to one contract should not ask again.
    window.history.replaceState({}, "", "/?recordId=a01xx0000001234&folderId=123");
    render(<Workspace />);
    expect(await screen.findByTestId("box-fallback")).toBeVisible();
    expect(screen.queryByTestId("contracts-view")).not.toBeInTheDocument();
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

  test("opens the folder the contract record names, without asking the endpoint to resolve one", async () => {
    // The endpoint prefers recordId when both are sent, so a record that already names a
    // folder must not also send one -- it would resolve the mapping and ignore the field.
    const urls: string[] = [];
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => {
        urls.push(String(url));
        if (String(url).includes("/clm/contracts")) {
          return {
            ok: true,
            json: async () => [
              { recordId: "a01xx0000009abcAAA", name: "Northstar MSA 2025", boxFolderId: "123456789" },
            ],
          };
        }
        throw new Error("no box endpoint in this test");
      }),
    );

    render(<Workspace />);
    fireEvent.click(await screen.findByTestId("contract-row"));

    await screen.findByTestId("box-fallback");
    const tokenCall = urls.find((url) => url.includes("box-token")) || "";
    expect(tokenCall).toContain("folderId=123456789");
    expect(tokenCall).not.toContain("recordId=");
  });
});
