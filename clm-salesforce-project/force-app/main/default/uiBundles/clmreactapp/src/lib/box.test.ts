import { afterEach, describe, expect, test, vi } from "vitest";
import { fetchDownscopedBoxToken, getAgentContextPrompt, getClmPageContext, listBoxFolderItems } from "./box";

describe("CLM page context", () => {
  test("uses a tenant-neutral Northstar workspace fixture by default", () => {
    expect(getClmPageContext("")).toEqual({
      contractId: "CLM-2026-0017",
      folderId: "demo-workspace",
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

describe("Box folder listing", () => {
  const originalFetch = globalThis.fetch;
  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  test("returns only files and passes the downscoped token as a bearer credential", async () => {
    let seenAuth = "";
    globalThis.fetch = (async (_url: string, init?: RequestInit) => {
      seenAuth = String((init?.headers as Record<string, string>)?.Authorization || "");
      return {
        ok: true,
        json: async () => ({
          entries: [
            { id: "1", name: "msa-redline.pdf", type: "file" },
            { id: "2", name: "Subfolder", type: "folder" },
          ],
        }),
      };
    }) as unknown as typeof fetch;

    const items = await listBoxFolderItems("42", "scoped-token");
    expect(items).toEqual([{ id: "1", name: "msa-redline.pdf", type: "file" }]);
    expect(seenAuth).toBe("Bearer scoped-token");
  });

  test("returns null when Box rejects the request so the caller can fall back", async () => {
    globalThis.fetch = (async () => ({ ok: false, json: async () => ({}) })) as unknown as typeof fetch;
    expect(await listBoxFolderItems("42", "bad-token")).toBeNull();
  });

  test("returns null when the request throws", async () => {
    globalThis.fetch = (async () => {
      throw new Error("network blocked");
    }) as unknown as typeof fetch;
    expect(await listBoxFolderItems("42", "scoped-token")).toBeNull();
  });

  test("returns an empty array for a folder that is genuinely empty", async () => {
    // A freshly provisioned contract folder has no files yet and is still live content.
    // Conflating this with a failure renders fixtures over a working workspace.
    globalThis.fetch = (async () => ({ ok: true, json: async () => ({ entries: [] }) })) as unknown as typeof fetch;
    expect(await listBoxFolderItems("42", "scoped-token")).toEqual([]);
  });
});

describe("Downscoped token request", () => {
  const originalFetch = globalThis.fetch;
  afterEach(() => {
    globalThis.fetch = originalFetch;
    delete window.__CLM_RUNTIME_CONFIG__;
  });

  test("asks by record id so the org's Box mapping picks the folder", async () => {
    let seenUrl = "";
    globalThis.fetch = (async (url: string) => {
      seenUrl = url;
      return { ok: true, json: async () => ({ accessToken: "example-scoped-token", folderId: "123456789" }) };
    }) as unknown as typeof fetch;

    const granted = await fetchDownscopedBoxToken({
      folderId: "demo-workspace",
      salesforceRecordId: "a0JNS000009dn8X2AQ",
    });

    expect(seenUrl).toContain("recordId=a0JNS000009dn8X2AQ");
    // The unusable default must not be sent alongside it.
    expect(seenUrl).not.toContain("folderId=");
    // The endpoint's answer wins: the caller never knew this folder.
    expect(granted).toEqual({ accessToken: "example-scoped-token", folderId: "123456789" });
  });

  test("falls back to folderId when there is no record context", async () => {
    let seenUrl = "";
    globalThis.fetch = (async (url: string) => {
      seenUrl = url;
      return { ok: true, json: async () => ({ accessToken: "example-scoped-token", folderId: "123" }) };
    }) as unknown as typeof fetch;

    await fetchDownscopedBoxToken({ folderId: "123" });
    expect(seenUrl).toContain("folderId=123");
    expect(seenUrl).not.toContain("recordId=");
  });

  test("returns no folder when the endpoint refuses, so the caller shows fixtures", async () => {
    globalThis.fetch = (async () => ({
      ok: false,
      status: 404,
      text: async () => '{"error":"no_box_folder_mapping"}',
      json: async () => ({}),
    })) as unknown as typeof fetch;

    expect(await fetchDownscopedBoxToken({ folderId: "123", salesforceRecordId: "a0J" }))
      .toEqual({ accessToken: "", folderId: "" });
  });

  test("uses the injected token from the local harness without calling Salesforce", async () => {
    window.__CLM_RUNTIME_CONFIG__ = { boxAccessToken: "example-harness-token" };
    globalThis.fetch = (async () => {
      throw new Error("must not call the endpoint");
    }) as unknown as typeof fetch;

    expect(await fetchDownscopedBoxToken({ folderId: "123456789" }))
      .toEqual({ accessToken: "example-harness-token", folderId: "123456789" });
  });

  test("provisions the record's folder when it has none, then retries", async () => {
    // Provisioning writes the association and Apex forbids a callout after DML, so the
    // package cannot create the folder and mint in one request. Two calls is the design,
    // not a retry loop -- the second attempt is made once and only after provisioning.
    const calls: string[] = [];
    let provisioned = false;
    globalThis.fetch = (async (url: string, init?: RequestInit) => {
      const target = String(url);
      calls.push(`${init?.method || "GET"} ${target}`);
      if (target.includes("box-folder")) {
        provisioned = true;
        return { ok: true, json: async () => ({ folderId: "555" }) };
      }
      if (!provisioned) {
        return {
          ok: false,
          status: 404,
          text: async () => '{"error":"no_box_folder_mapping"}',
          json: async () => ({}),
        };
      }
      return { ok: true, json: async () => ({ accessToken: "example-scoped-token", folderId: "555" }) };
    }) as unknown as typeof fetch;

    const granted = await fetchDownscopedBoxToken({
      folderId: "demo-workspace",
      salesforceRecordId: "a01xx0000009abcAAA",
    });

    expect(granted).toEqual({ accessToken: "example-scoped-token", folderId: "555" });
    expect(calls.filter((c) => c.includes("box-folder"))).toHaveLength(1);
    expect(calls.filter((c) => c.includes("box-token"))).toHaveLength(2);
    expect(calls[1]).toContain("POST");
  });

  test("does not provision when the failure is not a missing folder", async () => {
    const calls: string[] = [];
    globalThis.fetch = (async (url: string) => {
      calls.push(String(url));
      return { ok: false, status: 403, text: async () => '{"error":"folder_not_allowed"}', json: async () => ({}) };
    }) as unknown as typeof fetch;

    expect(await fetchDownscopedBoxToken({ folderId: "123", salesforceRecordId: "a01xx0000009abcAAA" }))
      .toEqual({ accessToken: "", folderId: "" });
    expect(calls.some((c) => c.includes("box-folder"))).toBe(false);
  });
});

describe("listBoxFolderItems", () => {
  function listing(entries: unknown[]) {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({ ok: true, json: async () => ({ entries }) })),
    );
  }

  test("withholds a redline from the counterparty", async () => {
    // The downscoped token bounds which contract is reachable, not which documents within
    // it, so this filter is the only thing keeping Acme's markup off a counterparty's
    // screen.
    listing([
      { id: "1", name: "msa-executed.pdf", type: "file",
        metadata: { enterprise: { clmDocument: { versionStatus: "Executed" } } } },
      { id: "2", name: "msa-redline-v4.pdf", type: "file",
        metadata: { enterprise: { clmDocument: { versionStatus: "Redline" } } } },
    ]);

    const items = await listBoxFolderItems("123", "token");

    expect(items?.map((i) => i.name)).toEqual(["msa-executed.pdf"]);
  });

  test("matches on version status, not on the file name", async () => {
    // A redline called anything is still a redline; a document merely named "redline" is
    // not one. Filtering on the name would get both backwards.
    listing([
      { id: "1", name: "v5-final.pdf", type: "file",
        metadata: { enterprise: { clmDocument: { versionStatus: "Redline" } } } },
      { id: "2", name: "redline-policy-summary.pdf", type: "file",
        metadata: { enterprise: { clmDocument: { versionStatus: "Approved" } } } },
    ]);

    const items = await listBoxFolderItems("123", "token");

    expect(items?.map((i) => i.name)).toEqual(["redline-policy-summary.pdf"]);
  });

  test("shows a file that carries no clmDocument instance", async () => {
    // An untagged upload is a tagging gap to fix, not a document to hide -- vanishing
    // silently is worse than appearing.
    listing([{ id: "1", name: "just-uploaded.pdf", type: "file" }]);

    const items = await listBoxFolderItems("123", "token");

    expect(items?.map((i) => i.name)).toEqual(["just-uploaded.pdf"]);
  });
});
