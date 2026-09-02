import type { BoxFolderItem } from "../lib/box";
import { byDocumentType, documentTotals, formatDate } from "../lib/documents";
import { Donut, foldToPalette } from "./Donut";

/**
 * The contract package at a glance, above its documents.
 *
 * Counts and a breakdown, both derived from the listing already on screen -- so the
 * numbers here can never disagree with the table below them.
 *
 * The type breakdown is a donut beside the tiles rather than a row of its own. It was bars,
 * and the bars were invisible: they drew their fill from --series-1, which only the
 * portfolio scope defined, so every track rendered empty. Both views now sit inside `.viz`,
 * which owns those variables, and share one donut component.
 */
export function WorkspaceMetrics({ files }: { files: BoxFolderItem[] | null }) {
  if (files === null || files.length === 0) return null;

  const totals = documentTotals(files);
  const types = foldToPalette(byDocumentType(files));

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
    </section>
  );
}
