import type { BoxFolderItem } from "../lib/box";
import { byDocumentStatus, byDocumentType, documentTotals, formatDate } from "../lib/documents";
import { Donut, foldToPalette } from "./Donut";

/**
 * The contract package at a glance, above its documents.
 *
 * Counts and a breakdown, both derived from the listing already on screen -- so the
 * numbers here can never disagree with the table below them.
 *
 * Two donuts beside the tiles rather than rows of their own. Type answers "what is in this
 * package"; status answers "how much of it has landed" -- the second is the one a reader
 * checks before a call, and reading it off the table meant counting pills.
 *
 * Both draw their fills from --series-N, which only the `.viz` scope defines. An earlier
 * version rendered as bars outside that scope and every track came out empty.
 */
export function WorkspaceMetrics({ files }: { files: BoxFolderItem[] | null }) {
  if (files === null || files.length === 0) return null;

  const totals = documentTotals(files);
  const types = foldToPalette(byDocumentType(files));
  const statuses = foldToPalette(byDocumentStatus(files));

  return (
    <section className="workspace-metrics viz" data-testid="workspace-metrics">
      <div className="stat-row stat-row-2x2">
        <div className="stat-tile">
          <span className="stat-label">Documents</span>
          <strong className="stat-value">{totals.documents}</strong>
        </div>
        <div className="stat-tile">
          <span className="stat-label">Approved</span>
          <strong className="stat-value">{totals.approved}</strong>
        </div>
        <div className="stat-tile">
          <span className="stat-label">Open</span>
          <strong className="stat-value">{totals.open}</strong>
          <span className="stat-note">draft or in review</span>
        </div>
        <div className="stat-tile">
          <span className="stat-label">Last change</span>
          <strong className="stat-value stat-value-date">{formatDate(totals.lastChangedAt)}</strong>
        </div>
      </div>
      <Donut slices={types} centreLabel="documents" title="Documents by type" />
      <Donut slices={statuses} centreLabel="documents" title="Documents by status" />
    </section>
  );
}
