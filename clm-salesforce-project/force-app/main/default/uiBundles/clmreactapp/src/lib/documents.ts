import type { BoxFolderItem } from "./box";

/**
 * The facts about a document that both the table and the timeline need.
 *
 * Kept in one place because the two views must never disagree: a row saying a document was
 * approved while the timeline beside it says otherwise is worse than either view alone.
 */
export interface DocumentFacts {
  /** When the document itself changed, preferring Box's content date over the upload's. */
  changedAt?: string;
  /** Who Box records as having made that change. */
  changedBy?: string;
  /** Draft, Redline, Approved, Executed -- whatever the clmDocument instance carries. */
  status?: string;
  /** True only when the document has actually been approved, not merely drafted. */
  approved: boolean;
}

export function documentFacts(file: BoxFolderItem): DocumentFacts {
  const clm = file.metadata?.enterprise?.clmDocument;
  const status = clm?.versionStatus;
  return {
    changedAt: file.content_modified_at || file.modified_at,
    changedBy: file.modified_by?.name,
    status,
    approved: status === "Approved" || status === "Executed",
  };
}

/** A short, unambiguous date. Returns an em dash rather than "Invalid Date". */
export function formatDate(iso?: string): string {
  if (!iso) return "—";
  const at = new Date(iso);
  return Number.isNaN(at.getTime())
    ? "—"
    : at.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}

/**
 * Documents newest first.
 *
 * Sorts a copy: the table renders the folder's own order, and reordering it underneath
 * would make the two views disagree about which document is which.
 */
export function byMostRecent(files: BoxFolderItem[]): BoxFolderItem[] {
  return [...files].sort((a, b) => {
    const left = documentFacts(a).changedAt;
    const right = documentFacts(b).changedAt;
    if (!left && !right) return 0;
    if (!left) return 1;
    if (!right) return -1;
    return new Date(right).getTime() - new Date(left).getTime();
  });
}
