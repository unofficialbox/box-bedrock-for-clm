import { afterEach, describe, expect, test } from "vitest";
import { fetchBoxEmbedLink, fetchDownscopedBoxToken, getAgentContextPrompt, getClmPageContext, listBoxFolderItems } from "./box";

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

  test("returns an empty list when Box rejects the request so the caller can fall back", async () => {
    globalThis.fetch = (async () => ({ ok: false, json: async () => ({}) })) as unknown as typeof fetch;
    expect(await listBoxFolderItems("42", "bad-token")).toEqual([]);
  });

  test("returns an empty list when the request throws", async () => {
    globalThis.fetch = (async () => {
      throw new Error("network blocked");
    }) as unknown as typeof fetch;
    expect(await listBoxFolderItems("42", "scoped-token")).toEqual([]);
  });
});

describe("Box embed link", () => {
  const originalFetch = globalThis.fetch;
  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  test("requests the expiring embed link with the downscoped token", async () => {
    let seenUrl = "";
    let seenAuth = "";
    globalThis.fetch = (async (url: string, init?: RequestInit) => {
      seenUrl = url;
      seenAuth = String((init?.headers as Record<string, string>)?.Authorization || "");
      return { ok: true, json: async () => ({ expiring_embed_link: { url: "https://acme.app.box.com/preview/expiring_embed/abc" } }) };
    }) as unknown as typeof fetch;

    expect(await fetchBoxEmbedLink("99", "scoped-token")).toBe(
      "https://acme.app.box.com/preview/expiring_embed/abc",
    );
    // The field has to be requested explicitly; Box omits it from the default response.
    expect(seenUrl).toContain("fields=expiring_embed_link");
    expect(seenUrl).toContain("/2.0/files/99");
    expect(seenAuth).toBe("Bearer scoped-token");
  });

  test("returns empty when the token lacks item_preview, which Box reports as a 200 with no link", async () => {
    globalThis.fetch = (async () => ({ ok: true, json: async () => ({ type: "file", id: "99" }) })) as unknown as typeof fetch;
    expect(await fetchBoxEmbedLink("99", "scoped-token")).toBe("");
  });

  test("returns empty when Box rejects the request", async () => {
    globalThis.fetch = (async () => ({ ok: false, text: async () => "forbidden", json: async () => ({}) })) as unknown as typeof fetch;
    expect(await fetchBoxEmbedLink("99", "bad-token")).toBe("");
  });

  test("returns empty when the request throws", async () => {
    globalThis.fetch = (async () => {
      throw new Error("network blocked");
    }) as unknown as typeof fetch;
    expect(await fetchBoxEmbedLink("99", "scoped-token")).toBe("");
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
});
