from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "agentcore"
OUT.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def read_clause_outcomes(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="") as f:
        rows = csv.DictReader(f)
        return {row["clauseArea"]: row for row in rows}


def box_context(*, use_runtime: bool = True) -> dict:
    """Use this operator's bootstrap state when present, otherwise local fixtures."""

    state_path = ROOT / "config" / "runtime" / "bootstrap-state.json"
    if use_runtime and state_path.exists():
        box = read_json(state_path).get("box", {})
        return {
            "workspaceId": box.get("folders", {}).get("workspace", "runtime-workspace"),
            "files": box.get("files", {}),
            "source": "operator-bootstrap-state",
        }

    names = [
        "northstar-msa-redline-v3.pdf",
        "northstar-dpa.pdf",
        "northstar-sow-implementation.pdf",
        "northstar-order-form.pdf",
        "northstar-security-exhibit.pdf",
        "northstar-insurance-certificate.pdf",
    ]
    files = {
        name: f"local-fixture:{name}"
        for name in names
        if (ROOT / "output" / "pdf" / name).exists()
    }
    return {"workspaceId": "local-fixture", "files": files, "source": "generated-local-assets"}


def event(agent: str, action: str, status: str, details: dict) -> dict:
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "agent": agent,
        "action": action,
        "status": status,
        "details": details,
    }


def main(*, use_runtime: bool = True) -> None:
    records = read_json(ROOT / "output" / "json" / "northstar-clm-records.json")
    playbook = read_json(ROOT / "output" / "json" / "clause-playbook.json")
    outcomes = read_clause_outcomes(ROOT / "output" / "csv" / "historical-clause-outcomes.csv")
    box = box_context(use_runtime=use_runtime)

    contract = records["contract"]
    opportunity = records["salesforceOpportunity"]
    approval_matrix = records["approvalMatrix"]

    trace: list[dict] = []
    trace.append(
        event(
            "clm-supervisor-agent",
            "start_workflow",
            "started",
            {
                "contractId": contract["contractId"],
                "routingMode": "supervisor",
                "framework": "Strands",
                "workspaceFolderId": box["workspaceId"],
                "workspaceSource": box["source"],
            },
        )
    )

    files = box["files"]
    required_docs = [
        "northstar-msa-redline-v3.pdf",
        "northstar-dpa.pdf",
        "northstar-sow-implementation.pdf",
        "northstar-order-form.pdf",
        "northstar-security-exhibit.pdf",
        "northstar-insurance-certificate.pdf",
    ]
    missing_docs = [name for name in required_docs if name not in files]
    trace.append(
        event(
            "box-contract-package-agent",
            "validate_package",
            "complete" if not missing_docs else "needs_attention",
            {
                "folderId": box["workspaceId"],
                "requiredDocuments": required_docs,
                "missingDocuments": missing_docs,
            },
        )
    )

    payment_terms_from_order_form = "Net 90"
    payment_mismatch = payment_terms_from_order_form != opportunity["paymentTerms"]
    trace.append(
        event(
            "salesforce-commercial-agent",
            "compare_order_form_to_opportunity",
            "exception" if payment_mismatch else "matched",
            {
                "opportunityId": opportunity["id"],
                "salesforcePaymentTerms": opportunity["paymentTerms"],
                "orderFormPaymentTerms": payment_terms_from_order_form,
                "requiresFinanceApproval": payment_mismatch,
            },
        )
    )

    risk_findings = [
        {
            "clauseArea": "Limitation of Liability",
            "source": "northstar-msa-redline-v3.pdf Section 7",
            "severity": "Critical",
            "issue": "Customer deleted liability cap and added broad uncapped damages.",
            "fallback": playbook["limitationOfLiability"]["fallback"],
            "requiredApprover": "Legal VP",
        },
        {
            "clauseArea": "Data Processing",
            "source": "northstar-dpa.pdf Processing Scope; northstar-msa-redline-v3.pdf Section 5",
            "severity": "High",
            "issue": "PHI processing is referenced before privacy/security approval is complete.",
            "fallback": playbook["dataProcessing"]["fallback"],
            "requiredApprover": "Privacy + Security",
        },
        {
            "clauseArea": "SLA Credits",
            "source": "northstar-sow-implementation.pdf Service Levels",
            "severity": "High",
            "issue": "Customer redline requests uncapped SLA credits.",
            "fallback": playbook["slaCredits"]["fallback"],
            "requiredApprover": "Service Owner",
        },
        {
            "clauseArea": "Payment Terms",
            "source": "northstar-order-form.pdf; northstar-clm-records.json",
            "severity": "High",
            "issue": "Order form states Net 90 while Salesforce opportunity states Net 45.",
            "fallback": playbook["paymentTerms"]["fallback"],
            "requiredApprover": "Finance",
        },
    ]
    trace.append(
        event(
            "clause-risk-agent",
            "compare_to_playbook",
            "findings_created",
            {"findingCount": len(risk_findings), "findings": risk_findings},
        )
    )

    benchmark_rows = []
    for finding in risk_findings:
        outcome = outcomes.get(finding["clauseArea"])
        if outcome:
            benchmark_rows.append(
                {
                    "clauseArea": finding["clauseArea"],
                    "standardAcceptedPct": int(outcome["standardAcceptedPct"]),
                    "fallbackAcceptedPct": int(outcome["fallbackAcceptedPct"]),
                    "avgNegotiationDays": float(outcome["avgNegotiationDays"]),
                    "renewalImpact": outcome["renewalImpact"],
                }
            )
    trace.append(
        event(
            "databricks-analytics-agent",
            "query_clause_outcomes",
            "benchmarks_returned",
            {"benchmarks": benchmark_rows},
        )
    )

    approval_routes = []
    for rule in approval_matrix:
        condition = rule["condition"]
        triggered = (
            condition == "dealValue > 1000000"
            or condition == "dataCategory = PHI"
            or condition == "riskLevel in High,Critical"
            or (condition == "paymentTerms beyond Net 60" and payment_mismatch)
        )
        if triggered:
            approval_routes.append(
                {
                    "approver": rule["approver"],
                    "condition": condition,
                    "slaHours": rule["slaHours"],
                    "status": "required",
                }
            )
    trace.append(
        event(
            "salesforce-approval-agent",
            "route_approvals",
            "approvals_required",
            {"routes": approval_routes},
        )
    )

    signature_block = {
        "requestedAction": "prepare_signature_packet",
        "blocked": True,
        "reason": "Required Legal VP, Finance, Privacy, and Security approvals are incomplete.",
        "guardrails": [
            "no_ai_final_legal_approval",
            "block_signature_until_required_approvals_complete",
            "privacy_security_approval_required_for_phi",
            "finance_approval_required_for_payment_term_mismatch",
        ],
    }
    trace.append(event("clm-supervisor-agent", "enforce_guardrails", "blocked", signature_block))

    obligations = [
        {
            "obligationType": "Renewal Notice",
            "owner": "Customer Success Manager",
            "dueDate": contract["noticeDeadline"],
            "sourceClause": "MSA Section 2",
            "status": "Open",
        },
        {
            "obligationType": "Security Evidence",
            "owner": "Security",
            "dueDate": "Annual",
            "sourceClause": "Security Exhibit Evidence",
            "status": "Open",
        },
        {
            "obligationType": "Data Deletion",
            "owner": "Privacy",
            "dueDate": "30 days after termination",
            "sourceClause": "DPA Deletion",
            "status": "Open",
        },
        {
            "obligationType": "Insurance",
            "owner": "Legal Ops",
            "dueDate": "Before certificate expiration",
            "sourceClause": "Insurance Certificate",
            "status": "Open",
        },
    ]
    trace.append(
        event(
            "obligation-monitor-agent",
            "extract_obligations",
            "candidate_obligations_created",
            {
                "note": "Draft package only. Do not activate obligations until execution.",
                "obligations": obligations,
            },
        )
    )

    report = {
        "demo": "CLM-2026-Northstar",
        "generatedAt": datetime.now(UTC).isoformat(),
        "orchestrationLayer": "AWS Bedrock AgentCore",
        "framework": "Strands",
        "systems": {
            "unstructured": "Box",
            "structured": "Salesforce",
            "analytics": "Databricks",
        },
        "finalState": "signature_blocked_pending_human_approvals",
        "trace": trace,
    }

    out_path = OUT / "northstar-agentcore-trace.json"
    with out_path.open("w") as f:
        json.dump(report, f, indent=2)
        f.write("\n")

    print(out_path)


if __name__ == "__main__":
    main()
