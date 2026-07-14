import type { ExpertRoute, RedlineDomain, RedlineFinding, RedlineRisk } from "../data";

export interface RedlineReviewGroup {
  domain: RedlineDomain;
  expert: ExpertRoute;
  findings: readonly RedlineFinding[];
  highestRisk: RedlineRisk;
  minimumConfidence: number;
}

const RISK_ORDER: Record<RedlineRisk, number> = {
  Low: 0,
  Medium: 1,
  High: 2,
  Critical: 3,
};

export function groupRedlineFindings(
  findings: readonly RedlineFinding[],
  routes: readonly ExpertRoute[],
): RedlineReviewGroup[] {
  const routeByDomain = new Map(routes.map((route) => [route.domain, route]));
  const findingsByDomain = new Map<RedlineDomain, RedlineFinding[]>();

  for (const finding of findings) {
    const domainFindings = findingsByDomain.get(finding.domain) ?? [];
    domainFindings.push(finding);
    findingsByDomain.set(finding.domain, domainFindings);
  }

  return Array.from(findingsByDomain, ([domain, domainFindings]) => {
    const expert = routeByDomain.get(domain);
    if (!expert) {
      throw new Error(`No expert route configured for ${domain}`);
    }

    let highestRisk = domainFindings[0].risk;
    let minimumConfidence = domainFindings[0].confidence;
    for (const finding of domainFindings.slice(1)) {
      if (RISK_ORDER[finding.risk] > RISK_ORDER[highestRisk]) highestRisk = finding.risk;
      if (finding.confidence < minimumConfidence) minimumConfidence = finding.confidence;
    }

    return { domain, expert, findings: domainFindings, highestRisk, minimumConfidence };
  });
}
