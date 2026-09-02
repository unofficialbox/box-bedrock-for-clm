import type { ClmContractSummary } from "../lib/contracts";
import {
  byStatus,
  formatCompactValue,
  portfolioTotals,
  valueBreakdown,
  type Slice,
} from "../lib/portfolio";

/**
 * The portfolio at a glance, above the contract list.
 *
 * Three tiles, a donut and a bar. The tiles carry the headlines, which is the honest form
 * for a single number -- a chart of one value is decoration. The donut answers "what state
 * is this portfolio in" and the bar answers "who is it with, and for how much", which are
 * the two questions the list itself cannot answer at a glance.
 *
 * Colours are the validated three-slot categorical set (blue, orange, aqua), assigned by
 * position and never cycled. Three is also the cap under the all-pairs rule, which is why
 * statuses beyond the third fold into "Other" rather than growing a fourth hue.
 */

const MAX_SLICES = 3;

/** Folds the tail into a single "Other" so the palette is never extended past its cap. */
function capped(slices: Slice[]): Slice[] {
  if (slices.length <= MAX_SLICES) return slices;
  const head = slices.slice(0, MAX_SLICES - 1);
  const rest = slices.slice(MAX_SLICES - 1);
  return [...head, { label: "Other", value: rest.reduce((sum, s) => sum + s.value, 0) }];
}

function StatTile({ label, value, note }: { label: string; value: string; note?: string }) {
  return (
    <div className="stat-tile">
      <span className="stat-label">{label}</span>
      <strong className="stat-value">{value}</strong>
      {note ? <span className="stat-note">{note}</span> : null}
    </div>
  );
}

/**
 * A donut, drawn as stroked arcs on one circle.
 *
 * Each arc carries a 2px surface-coloured gap so adjacent segments read as separate marks
 * rather than one band changing colour, and every segment is direct-labelled in the legend
 * with its count -- the light palette's aqua sits under 3:1 against white, and the
 * validator's contrast warning is discharged by labels, not ignored.
 */
function StatusDonut({ slices }: { slices: Slice[] }) {
  const total = slices.reduce((sum, s) => sum + s.value, 0);
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const gap = 2;

  // Each arc starts where the previous one ended, folded rather than accumulated into an
  // outer variable: mutating during render is what makes a component disagree with itself
  // across re-renders.
  const arcs = slices.reduce<
    Array<{ label: string; value: number; index: number; dash: number; offset: number; length: number }>
  >((acc, slice, index) => {
    const previous = acc[acc.length - 1];
    const offset = previous ? previous.offset + previous.length : 0;
    const length = total === 0 ? 0 : (slice.value / total) * circumference;
    return [...acc, { ...slice, index, length, offset, dash: Math.max(length - gap, 0) }];
  }, []);

  return (
    <figure className="chart-figure">
      <figcaption className="chart-title">Contracts by status</figcaption>
      <div className="donut-row">
        <svg viewBox="0 0 140 140" className="donut" role="img" aria-label={`Contracts by status, ${total} in total`}>
          <g transform="translate(70,70) rotate(-90)">
            {arcs.map((arc) => (
              <circle
                key={arc.label}
                r={radius}
                fill="none"
                stroke={`var(--series-${arc.index + 1})`}
                strokeWidth="16"
                strokeDasharray={`${arc.dash} ${circumference - arc.dash}`}
                strokeDashoffset={-arc.offset}
              >
                <title>{`${arc.label}: ${arc.value} of ${total}`}</title>
              </circle>
            ))}
          </g>
          <text x="70" y="66" className="donut-total">{total}</text>
          <text x="70" y="84" className="donut-total-label">contracts</text>
        </svg>

        {/* Legend and direct labels in one: identity is never colour alone. */}
        <ul className="legend">
          {slices.map((slice, index) => (
            <li key={slice.label}>
              <span className="legend-swatch" style={{ background: `var(--series-${index + 1})` }} />
              <span className="legend-label">{slice.label}</span>
              <span className="legend-value">{slice.value}</span>
            </li>
          ))}
        </ul>
      </div>
    </figure>
  );
}

/**
 * Value by counterparty. One series, so one hue and no legend -- the title names it.
 * Bars are labelled at the end rather than against an axis, which keeps the figure
 * readable at the width a sidebar-less card actually gets.
 */
function ValueBars({ title, slices }: { title: string; slices: Slice[] }) {
  const largest = slices.reduce((max, s) => Math.max(max, s.value), 0);

  return (
    <figure className="chart-figure">
      <figcaption className="chart-title">{title}</figcaption>
      <ul className="bars">
        {slices.map((slice) => (
          <li key={slice.label} className="bar-row">
            <span className="bar-label" title={slice.label}>{slice.label}</span>
            <span className="bar-track">
              <span
                className="bar-fill"
                style={{ width: largest === 0 ? "0%" : `${Math.max((slice.value / largest) * 100, 1.5)}%` }}
              >
                <title>{`${slice.label}: ${formatCompactValue(slice.value)}`}</title>
              </span>
            </span>
            <span className="bar-value">{formatCompactValue(slice.value)}</span>
          </li>
        ))}
      </ul>
    </figure>
  );
}

export function PortfolioCharts({ contracts }: { contracts: ClmContractSummary[] }) {
  if (contracts.length === 0) return null;

  const totals = portfolioTotals(contracts);
  const statuses = capped(byStatus(contracts));
  const breakdown = valueBreakdown(contracts);
  const values = breakdown.slices.slice(0, 6);

  return (
    <section className="portfolio" data-testid="portfolio-charts">
      <div className="stat-row">
        <StatTile label="Contracts" value={String(totals.contracts)} />
        <StatTile label="Total value" value={formatCompactValue(totals.value)} />
        <StatTile
          label="In flight"
          value={String(totals.inFlight)}
          note="not yet executed"
        />
      </div>
      <div className="chart-row">
        <StatusDonut slices={statuses} />
        <ValueBars title={breakdown.title} slices={values} />
      </div>
    </section>
  );
}
