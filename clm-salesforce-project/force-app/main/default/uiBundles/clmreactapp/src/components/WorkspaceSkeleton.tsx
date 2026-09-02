/**
 * The workspace while its token is being minted and its folder listed.
 *
 * A skeleton rather than a sentence, because the two say different things. "Connecting to
 * the governed Box workspace" describes the machinery to someone who did not ask about it,
 * and on a slow mint it is the only thing on screen for several seconds. A skeleton says
 * the same thing structurally -- something is coming, here is its shape -- and because it
 * is the shape of the real table, the layout does not jump when the content lands.
 *
 * Rows are fixed at six: enough to fill the panel, few enough not to imply a count. The
 * bars vary in width so it reads as content rather than a loading bar.
 */
const ROW_WIDTHS = ["72%", "58%", "80%", "64%", "76%", "52%"];

export function WorkspaceSkeleton() {
  return (
    <div className="skeleton" data-testid="box-loading" aria-busy="true" aria-live="polite">
      <span className="visually-hidden">Loading the contract documents</span>

      <div className="skeleton-head" aria-hidden="true">
        <span className="skeleton-bar skeleton-bar-title" />
        <span className="skeleton-bar skeleton-bar-button" />
      </div>

      <div className="skeleton-table" aria-hidden="true">
        {ROW_WIDTHS.map((width, index) => (
          <div className="skeleton-row" key={index}>
            <span className="skeleton-icon" />
            <span className="skeleton-bar" style={{ width }} />
            <span className="skeleton-bar skeleton-bar-meta" />
            <span className="skeleton-bar skeleton-bar-pill" />
          </div>
        ))}
      </div>
    </div>
  );
}
