import { useMemo, useState } from "react";
import { ClipboardCheck, FileSignature, GitCompareArrows, LayoutDashboard, Sparkles, UserRoundCheck } from "lucide-react";
import { AgentforcePanel } from "./components/AgentforcePanel";
import { BoxWorkspace } from "./components/BoxWorkspace";
import { EXPERT_ROUTES, NORTHSTAR_CONTRACT, REDLINE_FINDINGS } from "./data";
import { getAgentContextPrompt, getClmPageContext } from "./lib/box";
import { groupRedlineFindings, type RedlineReviewGroup } from "./lib/redlines";

type View = "workspace" | "approvals";

const REDLINE_REVIEW_GROUPS = groupRedlineFindings(REDLINE_FINDINGS, EXPERT_ROUTES);

export function Workspace() {
  const context = useMemo(() => getClmPageContext(), []);
  const [view, setView] = useState<View>("workspace");
  const [copied, setCopied] = useState(false);

  async function copyAgentContext() {
    await navigator.clipboard.writeText(getAgentContextPrompt());
    setCopied(true);
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark">A</span><span><strong>Acme Contracts</strong><small>Box-powered CLM</small></span></div>
        <nav aria-label="Primary">
          <button className={view === "workspace" ? "nav-active" : ""} onClick={() => setView("workspace")}><LayoutDashboard size={16} /> Workspace</button>
          <button className={view === "approvals" ? "nav-active" : ""} onClick={() => setView("approvals")}><ClipboardCheck size={16} /> Redline reviews <span className="count">{REDLINE_REVIEW_GROUPS.length}</span></button>
        </nav>
        <button className="agent-context-button" onClick={copyAgentContext}><Sparkles size={16} /> {copied ? "Context copied" : "Copy agent context"}</button>
      </header>

      <div className="contract-banner">
        <div><span className="eyebrow">{context.contractId}{context.salesforceRecordId ? ` · Salesforce ${context.salesforceRecordId}` : ""}</span><h1>{NORTHSTAR_CONTRACT.name}</h1><p>{NORTHSTAR_CONTRACT.counterparty} · {NORTHSTAR_CONTRACT.contractType}</p></div>
        <div className="banner-metrics">
          <Metric label="Value" value={NORTHSTAR_CONTRACT.value} />
          <Metric label="Term" value={NORTHSTAR_CONTRACT.term} />
          <Metric label="Risk" value={NORTHSTAR_CONTRACT.risk} danger />
          <Metric label="Status" value={NORTHSTAR_CONTRACT.status} warning />
        </div>
      </div>

      <div className="content-grid">
        <main>
          {view === "workspace" ? <BoxWorkspace folderId={context.folderId} /> : <Approvals />}
        </main>
        <AgentforcePanel />
      </div>
    </div>
  );
}

function Metric({ label, value, danger, warning }: { label: string; value: string; danger?: boolean; warning?: boolean }) {
  return <div className="metric"><span>{label}</span><strong className={danger ? "danger" : warning ? "warning" : ""}>{value}</strong></div>;
}

function Approvals() {
  return (
    <section className="approvals-card" data-testid="approvals-view">
      <div className="section-heading"><div><span className="eyebrow"><GitCompareArrows size={15} /> Redline finding router</span><h2>Domain expert review</h2><p>Differences are cited, risk-scored, and consolidated into one human-owned Box task per domain.</p></div><span className="blocked-pill"><FileSignature size={14} /> Signature blocked</span></div>
      <div className="review-summary" aria-label="Redline review summary">
        <div><strong>{REDLINE_FINDINGS.length}</strong><span>cited findings</span></div>
        <div><strong>{REDLINE_REVIEW_GROUPS.length}</strong><span>expert domains</span></div>
        <div><strong>100%</strong><span>human owned</span></div>
      </div>
      <div className="approval-list">
        {REDLINE_REVIEW_GROUPS.map((group) => <RedlineReview key={group.domain} group={group} />)}
      </div>
    </section>
  );
}

function RedlineReview({ group }: { group: RedlineReviewGroup }) {
  const confidence = Math.round(group.minimumConfidence * 100);

  return (
    <article className="review-group">
      <div className="review-group-head">
        <div className="approval-role"><UserRoundCheck size={18} /></div>
        <div className="expert-copy">
          <span>{group.domain}</span>
          <strong>{group.expert.expertName}</strong>
          <small>{group.expert.expertTitle} · Box task {group.expert.boxTaskId}</small>
        </div>
        <div className="review-badges">
          <span className={`risk risk-${group.highestRisk.toLowerCase()}`}>{group.highestRisk}</span>
          <span className="pending-pill">Pending</span>
        </div>
      </div>
      <div className="finding-list">
        {group.findings.map((finding) => (
          <div className="finding-row" key={finding.id}>
            <div className="finding-meta"><span>{finding.id}</span><span>{finding.changeType}</span><span>{finding.section}</span></div>
            <strong>{finding.summary}</strong>
            <div className="redline-copy"><del>{finding.proposedText}</del><ins>{finding.approvedPosition}</ins></div>
            <small>{finding.sourceCitation} · {finding.fallbackClauseId}</small>
          </div>
        ))}
      </div>
      <div className="routing-note"><span>Lowest classification confidence: {confidence}%</span><span>Live task assignee: {group.expert.boxAssigneeLogin}</span></div>
    </article>
  );
}
