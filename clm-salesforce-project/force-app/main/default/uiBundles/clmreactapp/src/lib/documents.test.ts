import { describe, expect, test } from "vitest";
import type { BoxFolderItem } from "./box";
import { byMostRecent, documentFacts, formatDate } from "./documents";

function file(over: Partial<BoxFolderItem> & { id: string }): BoxFolderItem {
  return { name: `${over.id}.pdf`, type: "file", ...over };
}

describe("documentFacts", () => {
  test("prefers the document's own change date over the upload's", () => {
    // Everything in a seeded folder shares an upload minute. content_modified_at is when
    // the document actually changed, which is what a reader means by "last modified".
    const facts = documentFacts(
      file({ id: "a", modified_at: "2026-09-01T17:08:11Z", content_modified_at: "2026-08-21T15:10:00Z" }),
    );
    expect(facts.changedAt).toBe("2026-08-21T15:10:00Z");
  });

  test("falls back to the upload date when Box has no content date", () => {
    expect(documentFacts(file({ id: "a", modified_at: "2026-09-01T17:08:11Z" })).changedAt)
      .toBe("2026-09-01T17:08:11Z");
  });

  test("counts only approved and executed as approved", () => {
    const status = (s?: string) =>
      documentFacts(file({ id: "a", metadata: { enterprise: { clmDocument: { versionStatus: s } } } })).approved;
    expect(status("Approved")).toBe(true);
    expect(status("Executed")).toBe(true);
    expect(status("Draft")).toBe(false);
    expect(status("Redline")).toBe(false);
    expect(status(undefined)).toBe(false);
  });
});

describe("byMostRecent", () => {
  test("orders newest first and leaves the caller's array alone", () => {
    // The table renders the folder's own order; reordering it underneath would make the
    // table and the timeline disagree about which document is which.
    const input = [
      file({ id: "old", content_modified_at: "2026-06-15T10:20:00Z" }),
      file({ id: "new", content_modified_at: "2026-08-21T15:10:00Z" }),
    ];
    expect(byMostRecent(input).map((f) => f.id)).toEqual(["new", "old"]);
    expect(input.map((f) => f.id)).toEqual(["old", "new"]);
  });

  test("puts documents with no date last rather than dropping them", () => {
    const ordered = byMostRecent([
      file({ id: "undated" }),
      file({ id: "dated", content_modified_at: "2026-06-15T10:20:00Z" }),
    ]);
    expect(ordered.map((f) => f.id)).toEqual(["dated", "undated"]);
  });
});

describe("formatDate", () => {
  test("renders an em dash rather than Invalid Date", () => {
    expect(formatDate(undefined)).toBe("—");
    expect(formatDate("not-a-date")).toBe("—");
  });
});
