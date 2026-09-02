import type { ClmContractSummary } from "../lib/contracts";
import { Donut, foldToPalette } from "./Donut";
import {
  byStatus,
  formatCompactValue,
  portfolioTotals,
  renewalHorizon,
  valueBreakdown,
  type Renewal,
  type Slice,
} from "../lib/portfolio";

/**
 * The portfolio at a glance, above the contract list.
 *
 * Three figures, and no tiles above them. The tiles restated the charts beside them: the
 * contract count is the donut's own centre label, "in flight" is everything the donut does
 * not colour Executed, and the renewal count is the number of rows in the renewal chart.
 * Only the portfolio's total value was a fact no figure stated, so it is that figure's
 * headline now.
 *
 * Colours are the validated three-slot categorical set (blue, orange, aqua), assigned by
 * position and never cycled. Three is also the cap under the all-pairs rule, which is why
 * statuses beyond the third fold into "Other" rather than growing a fourth hue.
 */

/**
 * Value by counterparty. One series, so one hue and no legend -- the title names it.
 * Bars are labelled at the end rather than against an axis, which keeps the figure
 * readable at the width a sidebar-less card actually gets.
 */
function ValueBars({ title, headline, slices }: { title: string; headline: string; slices: Slice[] }) {
  const largest = slices.reduce((max, s) => Math.max(max, s.value), 0);

  return (
    <figure className="chart-figure">
      <figcaption className="chart-title">{title}</figcaption>
      <p className="figure-headline">{headline}</p>
      <ul className="bars">
        {slices.map((slice) => (
          <li key={slice.label} className="bar-row">
            <span className="bar-head">
              <span className="bar-label">{slice.label}</span>
              <span className="bar-value">{formatCompactValue(slice.value)}</span>
            </span>
            <span className="bar-track">
              <span
                className="bar-fill"
                style={{ width: largest === 0 ? "0%" : `${Math.max((slice.value / largest) * 100, 1.5)}%` }}
              >
                <title>{`${slice.label}: ${formatCompactValue(slice.value)}`}</title>
              </span>
            </span>
          </li>
        ))}
      </ul>
    </figure>
  );
}

/**
 * The renewal horizon: terms ending inside the window, soonest first.
 *
 * A bar per contract, scaled by how much of the window is left, so a term that has already
 * lapsed reads as full-width rather than disappearing at zero. Lapsed terms carry the
 * critical status colour with the word "Lapsed" beside them -- status is never colour
 * alone, and this is the one place in the app where a status reading is what the chart is
 * actually for.
 */
function RenewalHorizon({ renewals, windowDays }: { renewals: Renewal[]; windowDays: number }) {
  return (
    <figure className="chart-figure">
      <figcaption className="chart-title">Renewals in the next {windowDays} days</figcaption>
      {renewals.length === 0 ? (
        <p className="chart-empty">No executed contract reaches the end of its term in this window.</p>
      ) : (
        <ul className="bars">
          {renewals.map((renewal) => {
            const lapsed = renewal.daysRemaining < 0;
            const used = lapsed ? 1 : 1 - renewal.daysRemaining / windowDays;
            return (
              <li key={renewal.label} className="bar-row">
                <span className="bar-head">
                  <span className="bar-label">{renewal.label}</span>
                  <span className={`bar-value${lapsed ? " bar-value-critical" : ""}`}>
                    {lapsed ? "Lapsed" : `${renewal.daysRemaining}d`}
                  </span>
                </span>
                <span className="bar-track">
                  <span
                    className={`bar-fill${lapsed ? " bar-fill-critical" : ""}`}
                    style={{ width: `${Math.max(used * 100, 4)}%` }}
                  >
                    <title>{`${renewal.label}: ends ${renewal.endDate}`}</title>
                  </span>
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </figure>
  );
}

const RENEWAL_WINDOW_DAYS = 90;

export function PortfolioCharts({ contracts }: { contracts: ClmContractSummary[] }) {
  if (contracts.length === 0) return null;

  const totals = portfolioTotals(contracts);
  const statuses = foldToPalette(byStatus(contracts));
  const breakdown = valueBreakdown(contracts);
  const renewals = renewalHorizon(contracts, RENEWAL_WINDOW_DAYS);
  const values = breakdown.slices.slice(0, 6);

  return (
    <section className="portfolio viz" data-testid="portfolio-charts">
      <div className="chart-row">
        <Donut slices={statuses} centreLabel="contracts" title="Contracts by status" />
        <ValueBars
          title={breakdown.title}
          headline={`${formatCompactValue(totals.value)} total`}
          slices={values}
        />
        <RenewalHorizon renewals={renewals} windowDays={RENEWAL_WINDOW_DAYS} />
      </div>
    </section>
  );
}
