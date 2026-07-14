from __future__ import annotations

import csv
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
PDF_OUT = ROOT / "output" / "pdf"
JSON_OUT = ROOT / "output" / "json"
CSV_OUT = ROOT / "output" / "csv"
for directory in (PDF_OUT, JSON_OUT, CSV_OUT):
    directory.mkdir(parents=True, exist_ok=True)


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#172554"),
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="DocSubTitle",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
    )
)
styles.add(
    ParagraphStyle(
        name="SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#075985"),
        spaceBefore=11,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="Body",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
    )
)
styles.add(
    ParagraphStyle(
        name="Small",
        parent=styles["BodyText"],
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor("#64748b"),
    )
)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(0.65 * inch, 0.43 * inch, "Synthetic CLM demo artifact - not legal advice")
    canvas.drawRightString(7.85 * inch, 0.43 * inch, f"Page {doc.page}")
    canvas.restoreState()


def make_doc(path: Path):
    doc = BaseDocTemplate(
        str(path),
        pagesize=LETTER,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.65 * inch,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="template", frames=[frame], onPage=footer)])
    return doc


def p(text: str, style: str = "Body"):
    return Paragraph(text, styles[style])


def section(title: str):
    return p(title, "SectionTitle")


def table(rows, widths=None, header=True):
    processed = []
    for row in rows:
        processed.append([cell if hasattr(cell, "wrap") else p(str(cell), "Body") for cell in row])
    tbl = Table(processed, colWidths=widths, hAlign="LEFT", repeatRows=1 if header else 0)
    style = [
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        style.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0f2fe")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ]
        )
    tbl.setStyle(TableStyle(style))
    return tbl


def doc_header(title: str, subtitle: str):
    return [p(title, "DocTitle"), p(subtitle, "DocSubTitle"), Spacer(1, 0.12 * inch)]


def build_msa():
    path = PDF_OUT / "northstar-msa-redline-v3.pdf"
    story = doc_header(
        "Master Services Agreement - Redline v3",
        "Acme Robotics, Inc. and Northstar Health System | CLM-2026-Northstar",
    )
    story += [
        section("1. Parties and Scope"),
        p("This Master Services Agreement governs Acme Robotics implementation, support, and analytics services for Northstar Health System facilities in the United States."),
        section("2. Term and Renewal"),
        p("Initial term is thirty-six months from the effective date. The agreement renews automatically for successive one-year periods unless either party provides notice before expiration. <b>Issue: notice window is not defined.</b>"),
        section("3. Payment"),
        p("Fees are invoiced annually in advance unless otherwise stated in the Order Form."),
        section("4. Confidentiality"),
        p("Each party will protect confidential information using reasonable care and at least the same care it uses for its own confidential information."),
        section("5. Data Processing"),
        p("Services may include access to patient scheduling metadata and operational health data. The parties will execute a Data Processing Addendum before production use."),
        section("6. Indemnity"),
        p("Each party indemnifies the other for third-party claims arising from gross negligence, willful misconduct, or violation of law."),
        section("7. Limitation of Liability"),
        p("<b>Customer redline:</b> The aggregate liability cap is deleted. Acme remains liable for all direct, indirect, incidental, consequential, special, punitive, and exemplary damages without limitation."),
        section("8. Termination"),
        p("Northstar may terminate for convenience on thirty days written notice. <b>Issue: no early termination fee or committed revenue protection.</b>"),
        section("9. Execution"),
        p("Execution is subject to completion of legal, privacy, security, and finance approvals."),
        PageBreak(),
        section("AI Review Seeds"),
        table(
            [
                ["Finding", "Source", "Expected Severity", "Routing"],
                ["Unlimited liability", "Section 7", "Critical", "Legal VP"],
                ["Undefined renewal notice", "Section 2", "Medium", "Legal Ops"],
                ["Termination for convenience without fee", "Section 8", "High", "Finance + Legal"],
                ["Health data reference", "Section 5", "High", "Privacy + Security"],
            ],
            widths=[1.7 * inch, 1.1 * inch, 1.4 * inch, 2.0 * inch],
        ),
    ]
    make_doc(path).build(story)


def build_dpa():
    path = PDF_OUT / "northstar-dpa.pdf"
    story = doc_header("Data Processing Addendum", "Synthetic DPA for AI maturity demo")
    story += [
        section("Processing Scope"),
        p("Acme may process customer contact information, implementation data, support tickets, scheduling metadata, and limited operational health data to provide the services."),
        section("Protected Data"),
        p("<b>Issue:</b> The DPA references possible PHI processing, but the package does not include a fully approved BAA or customer-specific security exhibit."),
        section("Subprocessors"),
        p("Acme will maintain a list of subprocessors and provide notice of material changes."),
        section("Security Measures"),
        p("Acme will maintain administrative, physical, and technical safeguards described in the security exhibit."),
        section("Deletion"),
        p("Upon termination, Acme will delete or return customer data within thirty days unless retention is required by law."),
    ]
    make_doc(path).build(story)


def build_sow():
    path = PDF_OUT / "northstar-sow-implementation.pdf"
    story = doc_header("Statement of Work - Implementation Services", "Northstar Health deployment")
    story += [
        section("Scope"),
        p("Acme will configure robotics workflow analytics for five Northstar facilities and provide administrator training."),
        section("Milestones"),
        table(
            [
                ["Milestone", "Due Date", "Owner"],
                ["Kickoff complete", "2026-08-15", "Acme Delivery"],
                ["Facility 1 pilot", "2026-09-30", "Acme Delivery"],
                ["Production rollout", "2026-11-30", "Joint"],
            ],
            widths=[2.5 * inch, 1.3 * inch, 2.2 * inch],
        ),
        section("Service Levels"),
        p("<b>Issue:</b> Customer redline requests uncapped SLA credits for any month below 99.9 percent uptime."),
        section("Reporting"),
        p("Acme will provide monthly service reporting and quarterly business reviews."),
    ]
    make_doc(path).build(story)


def build_order_form():
    path = PDF_OUT / "northstar-order-form.pdf"
    story = doc_header("Order Form", "Acme Robotics subscription and services")
    story += [
        table(
            [
                ["Field", "Value"],
                ["Contract ID", "CLM-2026-Northstar"],
                ["ARR", "$2,400,000"],
                ["Term", "36 months"],
                ["Products", "Workflow Analytics, Robotics Ops Console, Premium Support"],
                ["Payment Terms", "Net 90"],
                ["Target Signature Date", "2026-07-31"],
            ],
            widths=[2.0 * inch, 4.2 * inch],
        ),
        section("Demo Issue"),
        p("Salesforce quote record states Net 45 payment terms, while this order form states Net 90. Finance approval is required before signature."),
    ]
    make_doc(path).build(story)


def build_security_exhibit():
    path = PDF_OUT / "northstar-security-exhibit.pdf"
    story = doc_header("Security Exhibit", "Security controls and evidence commitments")
    story += [
        section("Controls"),
        p("Acme maintains SOC 2 Type II reporting, annual penetration testing, encryption in transit and at rest, least-privilege access, and incident response procedures."),
        section("Evidence"),
        p("Acme will provide current SOC 2 Type II report and penetration test executive summary annually under NDA."),
        section("Incident Notice"),
        p("Security incidents affecting customer data will be reported without undue delay and no later than seventy-two hours after confirmation."),
    ]
    make_doc(path).build(story)


def build_insurance():
    path = PDF_OUT / "northstar-insurance-certificate.pdf"
    story = doc_header("Insurance Certificate", "Synthetic evidence for CLM obligation tracking")
    story += [
        table(
            [
                ["Coverage", "Limit", "Expiration"],
                ["Commercial General Liability", "$2,000,000", "2027-06-30"],
                ["Cyber Liability", "$5,000,000", "2027-06-30"],
                ["Technology Errors and Omissions", "$5,000,000", "2027-06-30"],
            ],
            widths=[2.4 * inch, 1.7 * inch, 1.7 * inch],
        ),
        section("Demo Obligation"),
        p("Create reminder ninety days before certificate expiration and assign to Legal Operations."),
    ]
    make_doc(path).build(story)


def write_json():
    records = {
        "contract": {
            "contractId": "CLM-2026-Northstar",
            "counterparty": "Northstar Health System",
            "contractType": "MSA Package",
            "status": "Legal Review",
            "dealValue": 2400000,
            "termMonths": 36,
            "region": "US",
            "dataCategory": "PHI",
            "owner": "Maya Chen",
            "legalReviewer": "Jordan Lee",
            "riskLevel": "High",
            "targetSignatureDate": "2026-07-31",
            "renewalDate": "2029-07-31",
            "noticeDeadline": "2029-04-30",
        },
        "salesforceOpportunity": {
            "id": "006-demo-northstar",
            "accountName": "Northstar Health System",
            "stage": "Contracting",
            "amount": 2400000,
            "paymentTerms": "Net 45",
            "closeDate": "2026-07-31",
            "products": ["Workflow Analytics", "Robotics Ops Console", "Premium Support"],
        },
        "approvalMatrix": [
            {"condition": "dealValue > 1000000", "approver": "Finance", "slaHours": 24},
            {"condition": "dataCategory = PHI", "approver": "Privacy", "slaHours": 24},
            {"condition": "dataCategory = PHI", "approver": "Security", "slaHours": 24},
            {"condition": "riskLevel in High,Critical", "approver": "Legal VP", "slaHours": 48},
            {"condition": "paymentTerms beyond Net 60", "approver": "Finance", "slaHours": 24},
        ],
    }
    (JSON_OUT / "northstar-clm-records.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")

    playbook = {
        "limitationOfLiability": {
            "standard": "Liability capped at fees paid in prior 12 months.",
            "fallback": "Cap at 24 months fees with privacy and security carveouts.",
            "escalateWhen": "Uncapped liability or consequential damages are included.",
        },
        "paymentTerms": {
            "standard": "Net 30 or Net 45.",
            "fallback": "Net 60 with finance approval.",
            "escalateWhen": "Net 90 or unilateral setoff appears.",
        },
        "dataProcessing": {
            "standard": "Approved DPA and security exhibit required before PHI processing.",
            "fallback": "Customer DPA accepted after privacy and security review.",
            "escalateWhen": "PHI is referenced without approved DPA/BAA/security exhibit.",
        },
        "slaCredits": {
            "standard": "Service credits capped at monthly fees.",
            "fallback": "Higher capped credits with service owner approval.",
            "escalateWhen": "Uncapped SLA credits or refund rights appear.",
        },
    }
    (JSON_OUT / "clause-playbook.json").write_text(json.dumps(playbook, indent=2) + "\n", encoding="utf-8")


def write_csv():
    rows = [
        ["clauseArea", "standardAcceptedPct", "fallbackAcceptedPct", "avgNegotiationDays", "renewalImpact"],
        ["Limitation of Liability", "71", "24", "5.2", "Medium"],
        ["Payment Terms", "82", "14", "2.4", "Low"],
        ["Data Processing", "63", "31", "6.8", "High"],
        ["SLA Credits", "76", "18", "3.5", "Medium"],
        ["Termination for Convenience", "68", "21", "4.1", "Medium"],
    ]
    with (CSV_OUT / "historical-clause-outcomes.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)


def main():
    build_msa()
    build_dpa()
    build_sow()
    build_order_form()
    build_security_exhibit()
    build_insurance()
    write_json()
    write_csv()
    print(f"Wrote PDFs to {PDF_OUT}")
    print(f"Wrote JSON to {JSON_OUT}")
    print(f"Wrote CSV to {CSV_OUT}")


if __name__ == "__main__":
    main()
