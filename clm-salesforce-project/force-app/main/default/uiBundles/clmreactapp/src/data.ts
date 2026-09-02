export type RedlineDomain = "Commercial Legal" | "Finance" | "Privacy";
export type RedlineRisk = "Critical" | "High" | "Medium" | "Low";

export interface RedlineFinding {
  id: string;
  section: string;
  summary: string;
  changeType: "Added" | "Deleted" | "Replaced";
  domain: RedlineDomain;
  risk: RedlineRisk;
  confidence: number;
  proposedText: string;
  approvedPosition: string;
  fallbackClauseId: string;
  sourceFileId: string;
  sourceCitation: string;
}

export interface ExpertRoute {
  domain: RedlineDomain;
  expertName: string;
  expertTitle: string;
  boxTaskId: string;
  boxAssigneeLogin: string;
  assignmentMode: "Live demo triage" | "Named expert";
}

export const EXPERT_ROUTES: readonly ExpertRoute[] = [
  {
    domain: "Commercial Legal",
    expertName: "Jordan Lee",
    expertTitle: "Commercial Counsel",
    boxTaskId: "pending-commercial-legal-task",
    boxAssigneeLogin: "configured Commercial Legal reviewer",
    assignmentMode: "Named expert",
  },
  {
    domain: "Finance",
    expertName: "Priya Shah",
    expertTitle: "Finance Director",
    boxTaskId: "pending-finance-task",
    boxAssigneeLogin: "configured Finance reviewer",
    assignmentMode: "Named expert",
  },
  {
    domain: "Privacy",
    expertName: "Elena Torres",
    expertTitle: "Privacy Counsel",
    boxTaskId: "pending-privacy-task",
    boxAssigneeLogin: "configured Privacy reviewer",
    assignmentMode: "Named expert",
  },
] as const;

export const REDLINE_FINDINGS: readonly RedlineFinding[] = [
  {
    id: "RLF-001",
    section: "8.2 · Limitation of liability",
    summary: "Counterparty removed the aggregate liability cap.",
    changeType: "Deleted",
    domain: "Commercial Legal",
    risk: "Critical",
    confidence: 0.98,
    proposedText: "Supplier liability is unlimited for all claims.",
    approvedPosition: "Aggregate liability is capped at fees paid in the prior 12 months.",
    fallbackClauseId: "LOL-FALLBACK-001",
    sourceFileId: "demo-file-msa",
    sourceCitation: "MSA redline, section 8.2",
  },
  {
    id: "RLF-002",
    section: "12.1 · Renewal",
    summary: "Auto-renewal notice changed from 60 days to 15 days.",
    changeType: "Replaced",
    domain: "Commercial Legal",
    risk: "High",
    confidence: 0.96,
    proposedText: "Either party may prevent renewal with 15 days notice.",
    approvedPosition: "Renewal requires at least 60 days written notice.",
    fallbackClauseId: "TERM-FALLBACK-002",
    sourceFileId: "demo-file-msa",
    sourceCitation: "MSA redline, section 12.1",
  },
  {
    id: "RLF-003",
    section: "4.3 · Payment terms",
    summary: "Payment timing changed from Net 45 to Net 90.",
    changeType: "Replaced",
    domain: "Finance",
    risk: "High",
    confidence: 0.99,
    proposedText: "Invoices are payable within 90 days.",
    approvedPosition: "Invoices are payable within 45 days.",
    fallbackClauseId: "PAY-FALLBACK-001",
    sourceFileId: "demo-file-order",
    sourceCitation: "Order form, payment terms",
  },
  {
    id: "RLF-004",
    section: "3.4 · Regulated data",
    summary: "The DPA permits PHI processing without the required security exhibit.",
    changeType: "Added",
    domain: "Privacy",
    risk: "Critical",
    confidence: 0.94,
    proposedText: "Customer may submit PHI under the standard security controls.",
    approvedPosition: "PHI requires the approved security exhibit and documented safeguards.",
    fallbackClauseId: "DPA-FALLBACK-001",
    sourceFileId: "demo-file-dpa",
    sourceCitation: "DPA, section 3.4",
  },
] as const;
