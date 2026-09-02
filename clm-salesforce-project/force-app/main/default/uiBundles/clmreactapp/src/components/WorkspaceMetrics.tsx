import type { BoxFolderItem } from "../lib/box";
import { byDocumentType, documentTotals, formatDate } from "../lib/documents";

/**
 * The contract package at a glance, above its documents.
 *
 * Counts and a breakdown, both derived from the listing already on screen -- so the
 * numbers here can never disagree with the table below them.
 *
 * The type breakdown is bars rather than a donut. A donut answers "what share of the
 * whole", which for four document types of one or two files each is a question nobody is
 * asking; bars answer "how many of each", which is the one they are.
 */
export function WorkspaceMetrics({ files }: { files: BoxFolderItem[] | null }) {
  if (files === null || files.length === 0) return null;

  const totals = documentTotals(files);
  const types = byDocumentType(files);
  const most = types.reduce((max, t) => Math.max(max, t.value), 0);

  return (
    <section className="workspace-metrics" data-testid="workspace-metrics">
      <div className="stat-row stat-row-4">
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

      <figure className="chart-figure">
        <figcaption className="chart-title">Documents by type</figcaption>
        <ul className="bars">
          {types.map((type) => (
            <li key={type.label} className="bar-row">
              <span className="bar-label" title={type.label}>{type.label}</span>
              <span className="bar-track">
                <span
                  className="bar-fill"
                  style={{ width: most === 0 ? "0%" : `${Math.max((type.value / most) * 100, 3)}%` }}
                >
                  <title>{`${type.label}: ${type.value}`}</title>
                </span>
              </span>
              <span className="bar-value">{type.value}</span>
            </li>
          ))}
        </ul>
      </figure>
    </section>
  );
}
