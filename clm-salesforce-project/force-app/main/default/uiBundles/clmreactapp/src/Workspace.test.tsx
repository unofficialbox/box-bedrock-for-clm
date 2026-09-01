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

  test("shows a counterparty nothing of Acme's own review process", () => {
    // This app is the counterparty's surface now; the internal persona works through the
    // MCP server. The redline review queue named Acme's own reviewers and told the customer
    // which of their asks was blocking signature, and "Copy agent context" was a workaround
    // for a limitation they should never meet. Neither belongs in front of a counterparty.
    render(<Workspace />);
    expect(screen.queryByRole("button", { name: /Redline reviews/ })).not.toBeInTheDocument();
    expect(screen.queryByTestId("approvals-view")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Copy agent context/ })).not.toBeInTheDocument();
    expect(screen.queryByText("Jordan Lee")).not.toBeInTheDocument();
  });

  test("keeps Acme's own risk assessment off the counterparty's screen", async () => {
    // Risk_Level__c is what Acme thinks of the contract, not a fact about it -- the same
    // category as the redline queue. It is also why the list went blank for a real
    // counterparty: the field was in the GraphQL projection but withheld by the permission
    // set, and UI API rejects the whole query when one selected field is hidden, which
    // reads as "this counterparty has no contracts".
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => [
          {
            recordId: "a01xx0000009abcAAA",
            contractId: "CLM-1",
            name: "A Contract",
            boxFolderId: "1",
            riskLevel: "Critical",
          },
        ],
      })),
    );
    render(<Workspace />);
    await screen.findByTestId("contract-row");
    expect(screen.queryByText("Critical")).not.toBeInTheDocument();
    expect(screen.queryByText("Risk")).not.toBeInTheDocument();
  });

  test("names the contract list as the counterparty's own", () => {
    render(<Workspace />);
    expect(screen.getByRole("button", { name: /Your contracts/ })).toBeVisible();
  });

  test("does not narrate its own plumbing to a counterparty", async () => {
    // The heading and blurb faced a developer: "CLM contracts", read "over the GraphQL UI
    // API", resolving a folder "from the Box for Salesforce record mapping". None of that
    // means anything to the customer whose contracts these are.
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => [
          { recordId: "a01xx0000009abcAAA", contractId: "CLM-1", name: "A", boxFolderId: "1" },
        ],
      })),
    );
    render(<Workspace />);
    await screen.findByTestId("contracts-view");
    expect(screen.queryByText(/GraphQL UI API/)).not.toBeInTheDocument();
    expect(screen.queryByText(/record mapping/)).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "CLM contracts" })).not.toBeInTheDocument();
  });

  test("shows the Salesforce record returned by the intake flow", () => {
    window.history.replaceState({}, "", "/?recordId=a01xx0000001234&contractId=CLM-99&folderId=123");
    render(<Workspace />);
    expect(screen.getByText(/CLM-99 · Salesforce a01xx0000001234/)).toBeVisible();
  });

  test("asks by record so the package resolves or provisions the folder", async () => {
    // The package owns the association and provisions a folder for a record that has
    // none, so the record id is asked for even when a folder is already denormalised
    // onto the row -- that copy can fall behind the association.
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
    expect(tokenCall).toContain("recordId=a01xx0000009abcAAA");
    expect(tokenCall).not.toContain("folderId=");
  });

  test("puts the contract in the address bar so it can be linked and reloaded", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => {
        if (String(url).includes("/clm/contracts")) {
          return {
            ok: true,
            json: async () => [
              {
                recordId: "a01xx0000009abcAAA",
                contractId: "CLM-2026-0017",
                name: "Northstar MSA",
                boxFolderId: "123456789",
              },
            ],
          };
        }
        throw new Error("no box endpoint in this test");
      }),
    );

    render(<Workspace />);
    expect(window.location.search).toBe("");

    fireEvent.click(await screen.findByTestId("contract-row"));

    const params = new URLSearchParams(window.location.search);
    expect(params.get("folderId")).toBe("123456789");
    expect(params.get("recordId")).toBe("a01xx0000009abcAAA");
    expect(params.get("contractId")).toBe("CLM-2026-0017");
  });

  test("an org with no contracts says so instead of showing a fixture", async () => {
    // An empty list is a real answer. Showing the fixture here would claim Salesforce is
    // unreachable when it answered perfectly well.
    vi.stubGlobal("fetch", vi.fn(async () => ({ ok: true, json: async () => [] })));

    render(<Workspace />);
    expect(await screen.findByTestId("contracts-empty")).toBeVisible();
    expect(screen.queryByTestId("contracts-fixture-note")).not.toBeInTheDocument();
    expect(screen.queryByTestId("contract-row")).not.toBeInTheDocument();
  });
});
