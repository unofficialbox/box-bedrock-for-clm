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


def build_realistic_msa():
    path = PDF_OUT / "northstar-msa-redline-v4.pdf"
    story = doc_header(
        "Master Services Agreement - Negotiated Draft v4",
        "Acme Robotics, Inc. and Northstar Health System | Effective Date: July 31, 2026 | CLM-2026-Northstar",
    )
    story += [
        p("This Master Services Agreement (the <b>Agreement</b>) is entered into as of July 31, 2026 (the <b>Effective Date</b>) by and between Acme Robotics, Inc., a Delaware corporation with offices at 500 Market Street, San Francisco, California 94105 (<b>Acme</b>), and Northstar Health System, a Minnesota nonprofit corporation with offices at 1000 Health Plaza, Minneapolis, Minnesota 55401 (<b>Customer</b>). Acme and Customer may each be a <b>Party</b> and together the <b>Parties</b>."),
        section("RECITALS"),
        p("A. Acme provides hosted robotics operations, workflow analytics, implementation, support, and related professional services. B. Customer operates healthcare facilities and wishes to use the Services for operational workflows. C. The Parties intend that each Order Form and Statement of Work executed under this Agreement will be governed by these terms."),
        section("1. DEFINITIONS"),
        p("1.1 <b>Affiliate</b> means an entity that directly or indirectly controls, is controlled by, or is under common control with a Party. <b>Authorized User</b> means an employee, contractor, or agent whom Customer permits to use the Services. <b>Customer Data</b> means data submitted to or collected by the Services on Customer's behalf. <b>Documentation</b> means Acme's then-current user documentation. <b>Order Form</b> means an ordering document signed by both Parties. <b>Professional Services</b> means implementation, configuration, training, and advisory services described in a Statement of Work. <b>Services</b> means the hosted services, support, and Professional Services identified in an Order Form."),
        p("1.2 <b>Protected Health Information</b> or <b>PHI</b> has the meaning assigned under HIPAA. <b>Security Incident</b> means confirmed unauthorized access to or acquisition, use, disclosure, alteration, or destruction of Customer Data in Acme's possession or control, excluding unsuccessful attempts that do not compromise Customer Data."),
        section("2. ORDERING; PRIORITY"),
        p("2.1 Customer may purchase Services through mutually executed Order Forms. An Affiliate may enter into its own Order Form, in which case that Order Form creates a separate agreement between Acme and that Affiliate."),
        p("2.2 In the event of conflict, the following order controls: (a) a Business Associate Agreement solely for PHI; (b) a Data Processing Addendum solely for personal data; (c) an Order Form; (d) a Statement of Work; (e) this Agreement; and (f) the Documentation. A lower-priority document overrides a higher-priority document only when it identifies the provision being overridden."),
        section("3. SERVICES AND USE RIGHTS"),
        p("3.1 Subject to Customer's payment of applicable fees and compliance with this Agreement, Acme grants Customer a limited, non-exclusive, non-transferable right during the applicable subscription term to access and use the Services for Customer's internal business operations."),
        p("3.2 Customer will not: (a) sell, resell, sublicense, or provide the Services to a third party except Authorized Users; (b) reverse engineer the Services except to the extent a restriction is prohibited by law; (c) use the Services to develop a competing product; (d) bypass usage limits or security controls; or (e) upload unlawful content or malicious code."),
        p("3.3 Acme may use subcontractors to perform the Services but remains responsible for their performance. Acme will provide at least thirty days' prior notice before appointing a new subprocessor that will process Customer personal data."),
        PageBreak(),
        section("4. CUSTOMER RESPONSIBILITIES"),
        p("4.1 Customer is responsible for Authorized Users, the accuracy and legality of Customer Data, obtaining required notices and consents, and configuring access permissions. Customer will maintain reasonable administrative safeguards for credentials and promptly notify Acme of suspected unauthorized use."),
        p("4.2 Customer will not submit PHI until the Parties execute a Business Associate Agreement and complete the security implementation checklist. Customer remains responsible for determining whether the Services are appropriate for a regulated workflow and for all clinical or operational decisions."),
        section("5. PROFESSIONAL SERVICES"),
        p("5.1 Each Statement of Work will identify scope, assumptions, dependencies, personnel, milestones, fees, and acceptance criteria. Unless otherwise stated, deliverables are accepted when Customer confirms acceptance or fails to provide a reasonably detailed rejection notice within ten business days after delivery."),
        p("5.2 Changes to scope, schedule, or assumptions require a written change order signed by authorized representatives. Acme is not responsible for delays caused by Customer's failure to provide timely access, decisions, data, or personnel."),
        section("6. FEES, INVOICING, AND TAXES"),
        p("6.1 Customer will pay the fees stated in each Order Form. Subscription fees are invoiced annually in advance and Professional Services monthly in arrears unless the applicable Order Form states otherwise. Undisputed amounts are due forty-five days from invoice date."),
        p("6.2 Customer may withhold a disputed amount if it provides written notice describing the dispute before the due date and pays all undisputed amounts. The Parties will work in good faith to resolve invoice disputes within thirty days."),
        p("6.3 Fees exclude sales, use, value-added, and similar transaction taxes. Customer is responsible for such taxes except taxes based on Acme's net income, property, or employees. Acme will reasonably cooperate with valid exemption documentation."),
        p("<font color='#b91c1c'><b>NORTHSTAR REDLINE:</b> Customer requests Net 90 payment terms and a unilateral right to offset any alleged damages, credits, or refunds against amounts invoiced by Acme.</font>"),
        section("7. SERVICE LEVELS AND SUPPORT"),
        p("7.1 Acme will provide support and service levels described in the applicable Order Form. Scheduled maintenance announced at least five business days in advance and emergency maintenance are excluded from availability calculations."),
        p("7.2 Service credits are Customer's sole monetary remedy for a service-level failure and will not exceed twenty percent of the monthly subscription fees for the affected Service."),
        p("<font color='#b91c1c'><b>NORTHSTAR REDLINE:</b> Customer proposes uncapped service credits, a full monthly refund for availability below 99.5 percent, and termination rights after any two failures in a rolling six-month period.</font>"),
        PageBreak(),
        section("8. DATA OWNERSHIP AND USE"),
        p("8.1 As between the Parties, Customer owns Customer Data. Customer grants Acme a limited right to host, copy, transmit, display, and otherwise process Customer Data only as necessary to provide, secure, support, and improve the Services and as otherwise instructed by Customer."),
        p("8.2 Acme may generate and use aggregated or de-identified information that cannot reasonably identify Customer, an Authorized User, or an individual. Acme will not sell Customer Data or use Customer Data to train a generally available artificial intelligence model without Customer's prior written consent."),
        p("8.3 Upon expiration or termination, Customer may export Customer Data for thirty days. Acme will delete remaining Customer Data within sixty days after the export period, except for backup copies deleted through normal retention cycles or data retained as required by law."),
        section("9. PRIVACY AND REGULATED DATA"),
        p("9.1 The Data Processing Addendum is incorporated when Acme processes personal data on Customer's behalf. If Customer authorizes PHI processing, the Parties will execute a Business Associate Agreement before PHI enters the production Services."),
        p("9.2 Acme will process Customer Data only in documented accordance with this Agreement and Customer's lawful instructions. Acme will reasonably assist Customer with data subject requests, regulatory inquiries, and data protection impact assessments relating to the Services."),
        section("10. INFORMATION SECURITY"),
        p("10.1 Acme will maintain a written information security program with administrative, technical, and physical safeguards appropriate to the nature of Customer Data, including encryption in transit and at rest, least-privilege access, logging, vulnerability management, annual penetration testing, workforce training, and incident response."),
        p("10.2 Acme will notify Customer without undue delay, and in no event later than seventy-two hours after confirming a Security Incident. Notice will include known details concerning the nature, scope, affected data, mitigation, and corrective action, subject to ongoing investigation and law-enforcement restrictions."),
        p("10.3 Once annually, Acme will provide its then-current SOC 2 Type II report and penetration-test executive summary under reasonable confidentiality restrictions. Additional audits require reasonable advance notice, must avoid disruption, and are at Customer's expense unless they reveal a material breach."),
        p("<font color='#b91c1c'><b>NORTHSTAR REDLINE:</b> Customer requests notice within twelve hours after any suspected event, direct participation in Acme's forensic investigation, and unlimited on-site audits by Customer and its regulators.</font>"),
        section("11. CONFIDENTIALITY"),
        p("11.1 Confidential Information means nonpublic information disclosed by a Party that is marked confidential or should reasonably be understood as confidential. It excludes information the recipient can demonstrate was lawfully known without restriction, independently developed, rightfully received from a third party, or publicly available without breach."),
        p("11.2 The recipient will use Confidential Information only to perform or exercise rights under this Agreement and protect it using at least reasonable care. Disclosure is permitted to personnel and advisers with a need to know who are bound by confidentiality obligations at least as protective as these terms."),
        PageBreak(),
        section("12. INTELLECTUAL PROPERTY"),
        p("12.1 Acme and its licensors own the Services, Documentation, technology, methods, templates, improvements, and all related intellectual property rights. No rights are granted except as expressly stated."),
        p("12.2 Customer owns Customer Data and Customer-specific materials supplied to Acme. Upon full payment, Customer receives a perpetual, non-exclusive license to use deliverables created specifically for Customer under a Statement of Work, excluding Acme technology, tools, know-how, and reusable components."),
        p("12.3 If Customer provides suggestions or feedback, Acme may use them without restriction or obligation, provided Acme does not identify Customer as the source without permission."),
        section("13. WARRANTIES"),
        p("13.1 Each Party warrants that it has authority to enter into this Agreement. Acme warrants that the Services will materially conform to the Documentation and Professional Services will be performed in a professional and workmanlike manner. Customer's exclusive remedy is correction or reperformance; if Acme cannot cure a material breach, Customer may terminate the affected Service and receive a refund of prepaid unused fees."),
        p("13.2 Except for the express warranties in this Agreement, the Services are provided as is and Acme disclaims implied warranties of merchantability, fitness for a particular purpose, title, and noninfringement to the maximum extent permitted by law. Acme does not warrant uninterrupted or error-free operation or that artificial intelligence output will be complete or suitable for a legal, clinical, or financial decision."),
        section("14. MUTUAL INDEMNIFICATION"),
        p("14.1 Acme will defend Customer against a third-party claim that Customer's authorized use of the Services infringes a United States patent, copyright, or trademark and will pay damages finally awarded or agreed in settlement. Acme may modify or replace the affected Service or terminate it and refund prepaid unused fees if continued use is commercially unreasonable."),
        p("14.2 Customer will defend Acme against third-party claims arising from Customer Data, Customer's unlawful use of the Services, or Customer's breach of Section 3.2, and will pay damages finally awarded or agreed in settlement."),
        p("14.3 Indemnification requires prompt notice, control of the defense by the indemnifying Party, and reasonable cooperation. A settlement may not admit fault by or impose nonmonetary obligations on the indemnified Party without its consent."),
        section("15. LIMITATION OF LIABILITY"),
        p("15.1 Except for Excluded Claims, each Party's aggregate liability arising out of or relating to this Agreement will not exceed fees paid or payable under the affected Order Form during the twelve months preceding the event giving rise to liability."),
        p("15.2 Neither Party will be liable for lost profits, revenues, goodwill, or data, or for indirect, special, incidental, consequential, exemplary, or punitive damages, even if advised of their possibility."),
        p("15.3 Excluded Claims means a Party's fraud, willful misconduct, breach of confidentiality, infringement or misappropriation of the other Party's intellectual property, indemnification obligations, or Customer's payment obligations. Liability for a breach of data security or privacy obligations is capped at two times the amount in Section 15.1."),
        p("<font color='#b91c1c'><b>NORTHSTAR REDLINE:</b> Customer deletes Sections 15.1 through 15.3 and proposes unlimited liability for all direct and indirect damages, including lost revenue, reputational harm, regulatory penalties, and replacement-service costs.</font>"),
        PageBreak(),
        section("16. INSURANCE"),
        p("During the term, Acme will maintain commercial general liability coverage of at least $2,000,000 per occurrence, technology errors and omissions coverage of at least $5,000,000, cyber liability coverage of at least $5,000,000, workers' compensation as required by law, and automobile liability where applicable. Certificates of insurance will be provided upon request."),
        section("17. TERM AND TERMINATION"),
        p("17.1 This Agreement begins on the Effective Date and continues until all Order Forms expire or are terminated. Each Order Form has the subscription term stated in that Order Form and renews for successive one-year periods unless either Party provides at least ninety days' written notice before the current term ends."),
        p("17.2 Either Party may terminate this Agreement or an affected Order Form for material breach if the breach remains uncured thirty days after written notice, or ten days for nonpayment. Either Party may terminate immediately if the other becomes insolvent, ceases business, or becomes subject to a bankruptcy proceeding not dismissed within sixty days."),
        p("17.3 Upon termination, Customer will stop using the terminated Services and pay accrued amounts. If Customer terminates for Acme's uncured material breach, Acme will refund prepaid fees for the unused terminated period. Sections intended by their nature to survive will survive."),
        p("<font color='#b91c1c'><b>NORTHSTAR REDLINE:</b> Customer adds termination for convenience on thirty days' notice with a pro rata refund of all prepaid fees and no early termination charge.</font>"),
        section("18. COMPLIANCE WITH LAW"),
        p("Each Party will comply with laws applicable to its performance. Customer will not use the Services in violation of healthcare, privacy, employment, export-control, or sanctions laws. Neither Party will offer or accept an improper payment in connection with this Agreement."),
        section("19. BUSINESS CONTINUITY"),
        p("Acme will maintain and annually test business continuity and disaster recovery plans designed to restore material Services following a disruption. Upon request, Acme will provide a summary of current recovery objectives and the most recent test results, subject to confidentiality restrictions."),
        section("20. PUBLICITY"),
        p("Neither Party may issue a press release or use the other Party's name, trademarks, or logos in public marketing without prior written consent. Acme may identify Customer in a factual customer list only after receiving written brand approval."),
        section("21. RECORDS AND AUDIT"),
        p("Acme will retain records reasonably necessary to substantiate invoices and compliance with material contractual controls for at least three years. Customer may audit such records once annually through an independent auditor under confidentiality obligations, with thirty days' notice and during normal business hours."),
        PageBreak(),
        section("22. DISPUTE RESOLUTION; GOVERNING LAW"),
        p("Before filing litigation, senior representatives will meet in good faith to resolve a dispute. This Agreement is governed by Delaware law without regard to conflict-of-law rules. State and federal courts located in Wilmington, Delaware have exclusive jurisdiction, and each Party consents to venue there."),
        p("<font color='#b91c1c'><b>NORTHSTAR REDLINE:</b> Customer replaces Delaware law and venue with Minnesota law and exclusive venue in Hennepin County, Minnesota.</font>"),
        section("23. NOTICES"),
        p("Legal notices must be in writing and delivered by nationally recognized overnight courier or certified mail to the addresses above, with a copy by email to legal@acmerobotics.example for Acme and contracts@northstar.example for Customer. Notices are effective upon confirmed delivery."),
        section("24. ASSIGNMENT"),
        p("Neither Party may assign this Agreement without the other's prior written consent, except to an Affiliate or in connection with a merger, reorganization, or sale of substantially all relevant assets, provided the assignee is not a direct competitor and assumes all obligations. An impermissible assignment is void."),
        section("25. FORCE MAJEURE"),
        p("Neither Party is liable for delay caused by events beyond its reasonable control, excluding payment obligations. The affected Party will provide prompt notice, use reasonable efforts to mitigate, and resume performance as soon as practicable."),
        section("26. GENERAL"),
        p("This Agreement and incorporated documents constitute the entire agreement and supersede prior discussions concerning their subject matter. Amendments and waivers must be in writing and signed by authorized representatives. If a provision is unenforceable, it will be modified to the minimum extent necessary and the remaining provisions remain effective. The Parties are independent contractors. Electronic signatures and counterparts are effective."),
        section("SIGNATURES"),
        table(
            [
                ["ACME ROBOTICS, INC.", "NORTHSTAR HEALTH SYSTEM"],
                ["By: ______________________________", "By: ______________________________"],
                ["Name: Elena Martinez", "Name: Marcus Bennett"],
                ["Title: Chief Revenue Officer", "Title: Chief Procurement Officer"],
                ["Date: _____________________________", "Date: _____________________________"],
            ],
            widths=[3.45 * inch, 3.45 * inch],
        ),
        PageBreak(),
        section("EXHIBIT A - INITIAL ORDER SUMMARY"),
        table(
            [
                ["Commercial Term", "Agreed Draft Value"],
                ["Services", "Workflow Analytics, Robotics Ops Console, Premium Support"],
                ["Subscription term", "36 months"],
                ["Annual recurring fees", "$2,400,000"],
                ["Implementation fees", "$325,000 fixed fee"],
                ["Payment terms", "Acme: Net 45; Northstar redline: Net 90"],
                ["Production facilities", "Five United States facilities"],
                ["Target production date", "November 30, 2026"],
            ],
            widths=[2.1 * inch, 4.8 * inch],
        ),
        section("EXHIBIT B - NEGOTIATION ISSUE REGISTER"),
        table(
            [
                ["Clause", "Customer Position", "Risk", "Required Review"],
                ["6. Fees", "Net 90 plus unilateral offset", "High", "Finance and Legal"],
                ["7. Service Levels", "Uncapped credits and broad termination", "High", "Service Owner and Finance"],
                ["10. Security", "12-hour notice and unlimited audits", "High", "Security and Privacy"],
                ["15. Liability", "Unlimited direct and indirect damages", "Critical", "Legal VP and Finance"],
                ["17. Termination", "Convenience termination with full refund", "High", "Finance and Legal"],
                ["22. Governing Law", "Minnesota law and venue", "Medium", "Legal"],
            ],
            widths=[0.9 * inch, 2.8 * inch, 0.8 * inch, 2.4 * inch],
        ),
        Spacer(1, 0.2 * inch),
        p("This synthetic agreement is designed for contract-lifecycle demonstrations. Names, addresses, terms, and legal provisions are fictional and must not be used as legal advice or as a production agreement.", "Small"),
    ]
    make_doc(path).build(story)


def build_executed_msa(year, effective_date, executed_date, arr, term_months=36):
    """A fully-executed (signed) Northstar MSA for a prior year - no redlines, signed block."""
    path = PDF_OUT / f"northstar-msa-{year}-executed.pdf"
    story = doc_header(
        f"Master Services Agreement - Executed {year}",
        f"Acme Robotics, Inc. and Northstar Health System | Effective Date: {effective_date} | CLM-{year}-Northstar",
    )
    story += [
        p(f"This Master Services Agreement (the <b>Agreement</b>) is entered into as of {effective_date} (the <b>Effective Date</b>) by and between Acme Robotics, Inc., a Delaware corporation (<b>Acme</b>), and Northstar Health System, a Minnesota nonprofit corporation (<b>Customer</b>). This Agreement was executed by the Parties and is in full force and effect."),
        section("1. SERVICES AND USE RIGHTS"),
        p("Subject to Customer's payment of applicable fees, Acme grants Customer a limited, non-exclusive, non-transferable right during the subscription term to access and use the Services for Customer's internal business operations."),
        section("2. FEES, INVOICING, AND TAXES"),
        p("Customer will pay the fees stated in each Order Form. Subscription fees are invoiced annually in advance; undisputed amounts are due forty-five days from invoice date. Fees exclude transaction taxes other than taxes on Acme's net income."),
        section("3. SERVICE LEVELS AND SUPPORT"),
        p("Acme will provide the support and service levels described in the applicable Order Form. Service credits are Customer's sole monetary remedy for a service-level failure and will not exceed twenty percent of the monthly subscription fees for the affected Service."),
        section("4. DATA OWNERSHIP AND PRIVACY"),
        p("As between the Parties, Customer owns Customer Data. Acme will process Customer Data only to provide, secure, support, and improve the Services. Where Acme processes personal data or PHI, the Data Processing Addendum and Business Associate Agreement govern that processing."),
        section("5. INFORMATION SECURITY"),
        p("Acme maintains a written information security program with administrative, technical, and physical safeguards, including encryption in transit and at rest, least-privilege access, logging, vulnerability management, and annual penetration testing. Acme will notify Customer of a confirmed Security Incident without undue delay and no later than seventy-two hours after confirmation."),
        section("6. CONFIDENTIALITY"),
        p("Each Party will use the other's Confidential Information only to perform or exercise rights under this Agreement and will protect it using at least reasonable care."),
        section("7. LIMITATION OF LIABILITY"),
        p("Except for Excluded Claims, each Party's aggregate liability will not exceed the fees paid or payable under the affected Order Form during the twelve months preceding the event giving rise to liability. Neither Party is liable for indirect, special, incidental, consequential, or punitive damages."),
        section("8. TERM AND TERMINATION"),
        p(f"This Agreement began on the Effective Date and continues for a subscription term of {term_months} months, renewing for successive one-year periods unless either Party provides at least ninety days' written notice before the current term ends. Either Party may terminate for uncured material breach."),
        section("9. GOVERNING LAW"),
        p("This Agreement is governed by Delaware law without regard to conflict-of-law rules. State and federal courts located in Wilmington, Delaware have exclusive jurisdiction."),
        PageBreak(),
        section("SIGNATURES"),
        p(f"Executed by the Parties as of {executed_date}.", "Small"),
        table(
            [
                ["ACME ROBOTICS, INC.", "NORTHSTAR HEALTH SYSTEM"],
                ["By: /s/ Elena Martinez", "By: /s/ Marcus Bennett"],
                ["Name: Elena Martinez", "Name: Marcus Bennett"],
                ["Title: Chief Revenue Officer", "Title: Chief Procurement Officer"],
                [f"Date: {executed_date}", f"Date: {executed_date}"],
            ],
            widths=[3.45 * inch, 3.45 * inch],
        ),
        section(f"EXHIBIT A - ORDER SUMMARY ({year})"),
        table(
            [
                ["Commercial Term", "Agreed Value"],
                ["Services", "Workflow Analytics, Robotics Ops Console, Premium Support"],
                ["Subscription term", f"{term_months} months"],
                ["Annual recurring fees", arr],
                ["Payment terms", "Net 45"],
                ["Governing law", "Delaware"],
            ],
            widths=[2.1 * inch, 4.8 * inch],
        ),
        Spacer(1, 0.2 * inch),
        p("This synthetic executed agreement is designed for contract-lifecycle demonstrations. Names, terms, and provisions are fictional and are not legal advice.", "Small"),
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



def build_calder_customer_paper():
    """Calder's own template, not Acme's.

    The point of this document is that the liability position is not where anyone would
    look for it. There is no section called "Limitation of Liability" and no cap stated
    anywhere. The exposure lives in two places that have to be read together: an uncapped
    indemnity at Article 19, and a sub-clause buried in General Provisions at 22.4 called
    "Responsibility for Losses".

    That is what makes the demo honest. A template diff cannot find it -- there is no Acme
    template to diff against -- and a keyword search for "limitation of liability" returns
    nothing. Only reading the document against a governed clause library does.

    Roles are inverted from Acme's paper: here Acme is the Supplier and Calder is the
    Company, which is how customer paper actually reads.
    """
    path = PDF_OUT / "calder-msa-customer-paper-v2.pdf"
    story = doc_header(
        "Master Agreement for Supplier Services",
        "Calder Financial Group plc and Acme Robotics, Inc. | Calder Legal Template MA-2024 rev.3 | CLM-2026-Calder",
    )
    story += [
        p("THIS MASTER AGREEMENT FOR SUPPLIER SERVICES (this <b>Agreement</b>) is made on 12 August 2026 BETWEEN Calder Financial Group plc, registered in England and Wales, whose registered office is at 40 Bishopsgate, London EC2N 4AJ (the <b>Company</b>), and Acme Robotics, Inc., a Delaware corporation of 500 Market Street, San Francisco, California 94105 (the <b>Supplier</b>)."),
        p("<i>Drafted on the Company's standard form. Supplier amendments are shown in the margin and remain subject to Company Legal approval. The Company does not accept supplier paper.</i>"),
        section("ARTICLE 1 - INTERPRETATION"),
        p("1.1 In this Agreement: <b>Deliverables</b> means anything the Supplier is required to provide under a Statement of Work; <b>Company Data</b> means all data provided by or on behalf of the Company or generated by the Services; <b>Losses</b> means all losses, liabilities, damages, costs, claims, demands, fines, penalties and expenses of any kind, whether direct or indirect and whether foreseeable or not; <b>Regulator</b> means any authority with supervisory jurisdiction over the Company."),
        p("1.2 A reference to a statute includes its subordinate legislation as amended. Headings are for convenience only and <b>do not affect interpretation</b>. Where a provision is expressed to be without limitation, no rule of ejusdem generis applies."),
        section("ARTICLE 2 - APPOINTMENT AND TERM"),
        p("2.1 The Company appoints the Supplier on a non-exclusive basis to provide the Services described in each Statement of Work. The Company gives no volume commitment and may procure equivalent services from any third party at any time."),
        p("2.2 This Agreement commences on the date above and continues for thirty-six months unless terminated earlier. The Company may extend for successive twelve-month periods on written notice. The Supplier has no corresponding right of extension or renewal."),
        section("ARTICLE 3 - THE SERVICES"),
        p("3.1 The Supplier shall provide the Services with the skill and care reasonably expected of a specialist supplier experienced in providing services of a similar type, scope and complexity to regulated financial institutions."),
        p("3.2 The Supplier shall comply with all Company policies notified to it from time to time, including the Company's Third Party Code of Conduct, Information Security Standard and Operational Resilience Policy, as each may be updated."),
        PageBreak(),
        section("ARTICLE 6 - CHARGES AND PAYMENT"),
        p("6.1 The Company shall pay the charges set out in the applicable Statement of Work within sixty days of receipt of a valid and undisputed invoice. Invoices must quote a valid purchase order number; invoices without one will be returned unpaid."),
        p("6.2 The Company may <b>set off</b> against any sum due to the Supplier any amount owed to the Company by the Supplier or any of its affiliates, whether under this Agreement or otherwise, and whether liquidated or not."),
        p("6.3 Charges are fixed for the first twenty-four months. Thereafter any increase requires ninety days' notice and shall not exceed the lesser of CPI and three per cent per annum."),
        section("ARTICLE 11 - REGULATORY OBLIGATIONS"),
        p("11.1 The Supplier acknowledges that the Company is a regulated firm and that the Services may constitute a material outsourcing. The Supplier shall provide the Company and each Regulator with access to its premises, personnel, systems and records on request."),
        p("11.2 The Supplier shall not sub-contract any part of the Services without the Company's prior written consent, and remains liable for the acts and omissions of any approved sub-contractor as if they were its own."),
        section("ARTICLE 14 - INFORMATION SECURITY AND DATA"),
        p("14.1 The Supplier shall implement and maintain technical and organisational measures no less protective than the Company's Information Security Standard, and shall notify the Company of any actual or suspected security incident within twenty-four hours of becoming aware of it."),
        p("14.2 All Company Data remains the property of the Company. On termination the Supplier shall return or securely destroy Company Data as directed and certify completion within thirty days."),
        PageBreak(),
        section("ARTICLE 19 - INDEMNITIES"),
        p("19.1 The Supplier shall indemnify, defend and hold harmless the Company, its affiliates and their respective officers, employees and agents against all Losses arising out of or in connection with: (a) any breach of this Agreement by the Supplier; (b) any act, omission, negligence or wilful misconduct of the Supplier or its personnel or sub-contractors; (c) any claim that the Deliverables infringe a third party's intellectual property rights; (d) any security incident affecting Company Data in the Supplier's possession or control; and (e) any regulatory investigation, fine, penalty or censure imposed on the Company to the extent attributable to the Supplier."),
        p("19.2 The indemnities in clause 19.1 are <b>primary obligations</b>, survive termination without limit of time, and are <b>not subject to any exclusion or limitation set out elsewhere in this Agreement</b>."),
        p("19.3 The Company's rights under this Article are in addition to, and not in substitution for, any other right or remedy available to it at law or in equity."),
        section("ARTICLE 20 - INSURANCE"),
        p("20.1 The Supplier shall maintain, at its own cost, professional indemnity, cyber and public liability insurance each with a limit of not less than ten million pounds per claim, and shall provide certificates of currency annually and on request."),
        section("ARTICLE 22 - GENERAL PROVISIONS"),
        p("22.1 <b>Notices.</b> Notices must be in writing and delivered by hand, recorded delivery or email to the addresses notified by each party for the purpose."),
        p("22.2 <b>Assignment.</b> The Company may assign or novate this Agreement to any affiliate or to a purchaser of the relevant business. The Supplier may not assign, novate, charge or otherwise deal with this Agreement without the Company's prior written consent."),
        p("22.3 <b>Entire agreement.</b> This Agreement constitutes the entire agreement between the parties and supersedes all prior arrangements. Nothing limits liability for fraud or fraudulent misrepresentation."),
        p("22.4 <b>Responsibility for Losses.</b> Each party is responsible for the Losses it causes. The Supplier shall be responsible for all Losses suffered or incurred by the Company arising out of or in connection with the Supplier's performance or non-performance of this Agreement, including loss of profit, loss of revenue, loss of anticipated savings, loss or corruption of data, regulatory fines and reputational harm. <b>No financial cap applies to the Supplier's responsibility under this clause.</b> The Company's responsibility to the Supplier is limited to the charges properly invoiced and unpaid at the date of the relevant claim."),
        p("22.5 <b>Governing law.</b> This Agreement and any non-contractual obligation arising out of it are governed by the laws of England and Wales, and the parties submit to the exclusive jurisdiction of the courts of England and Wales."),
        section("SUPPLIER MARGIN NOTES - FOR COMPANY LEGAL REVIEW"),
        table(
            [
                ["Clause", "Supplier position"],
                ["19.2", "Supplier requests the indemnities be made subject to the responsibility provisions, not carved out of them."],
                ["22.4", "Supplier requests an aggregate financial cap and exclusion of indirect and consequential Losses."],
                ["6.2", "Supplier requests set-off be limited to sums due under this Agreement only."],
                ["11.1", "Supplier requests regulator access be on reasonable notice and during business hours."],
            ],
            widths=[1.1 * inch, 5.4 * inch],
        ),
        p("<i>Status: with Company Legal. No Company response received as at the date of this draft.</i>"),
    ]
    make_doc(path).build(story)
    return path

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
        # Force LF: the repository normalizes text to LF via .gitattributes, so a
        # CRLF write here reads back as drift on any fresh clone.
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerows(rows)


def build_calder_executed(
    year,
    template_rev,
    signed_on,
    charges,
    cap_months,
    prior_year=None,
):
    """A prior Calder agreement, executed, on Calder's own paper.

    These two documents exist to make one point that a single contract cannot make: the
    2026 draft is not asking Acme for something new. It is asking for two positions Calder
    already conceded, in writing, twice.

    Both prior agreements carry a negotiated 22.4 -- an aggregate cap at twenty-four months
    of charges -- and a negotiated 19.2 that subjects the indemnities to that cap except for
    IP infringement and data breach. Template rev.3, the one in front of Acme now, silently
    restores the unamended house text of both clauses. So the finding is not "this is off
    policy"; it is "your own template dropped two amendments you agreed to", which is a
    different and much better conversation to hand to legal.

    The clause numbers are deliberately identical across all three documents, so the reader
    can put 22.4 beside 22.4 and see it.
    """
    path = PDF_OUT / f"calder-msa-{year}-executed.pdf"
    renewal = prior_year is not None
    story = doc_header(
        f"Master Agreement for Supplier Services - Executed {year}"
        + (" (Renewal)" if renewal else ""),
        f"Calder Financial Group plc and Acme Robotics, Inc. | "
        f"Calder Legal Template {template_rev} | CLM-{year}-Calder",
    )
    story += [
        p(
            f"THIS MASTER AGREEMENT FOR SUPPLIER SERVICES was made on {signed_on} BETWEEN "
            f"Calder Financial Group plc (the <b>Company</b>) and Acme Robotics, Inc. (the "
            f"<b>Supplier</b>). This Agreement was executed by the parties and performed to "
            f"its term."
            + (
                f" It renewed and superseded the agreement executed in {prior_year}, "
                f"carrying forward the amendments recorded in Schedule 1 of that agreement."
                if renewal
                else ""
            )
        ),
        p(
            "<i>Drafted on the Company's standard form. The amendments at Article 19 and "
            "clause 22.4 below were agreed with Company Legal during negotiation and are "
            "recorded in Schedule 1.</i>"
        ),
        section("ARTICLE 2 - APPOINTMENT AND TERM"),
        p(
            "2.2 This Agreement commenced on the date above and continued for twenty-four "
            "months. The Company was entitled to extend for successive twelve-month periods "
            "on written notice."
        ),
        section("ARTICLE 6 - CHARGES AND PAYMENT"),
        p(
            f"6.1 The Company paid the charges set out in each Statement of Work within "
            f"sixty days of receipt of a valid and undisputed invoice. Aggregate charges "
            f"for the term were {charges}."
        ),
        p(
            "6.2 The Company's right of set-off was limited, <b>as amended</b>, to sums due "
            "and payable under this Agreement only."
        ),
        section("ARTICLE 19 - INDEMNITIES"),
        p(
            "19.1 The Supplier indemnified the Company against Losses arising out of any "
            "breach of this Agreement by the Supplier, any negligence or wilful misconduct "
            "of its personnel, any claim that the Deliverables infringed a third party's "
            "intellectual property rights, and any security incident affecting Company Data "
            "in the Supplier's control."
        ),
        p(
            "19.2 <b>As amended.</b> The indemnities in clause 19.1 are <b>subject to the "
            "financial cap in clause 22.4</b>, save that the cap does not apply to "
            "sub-clauses 19.1(c) (intellectual property infringement) and 19.1(d) (security "
            "incident affecting Company Data), which remain uncapped."
        ),
        PageBreak(),
        section("ARTICLE 22 - GENERAL PROVISIONS"),
        p(
            "22.4 <b>Responsibility for Losses. As amended.</b> Each party is responsible "
            "for the Losses it causes. The Supplier's aggregate responsibility to the "
            f"Company under or in connection with this Agreement <b>shall not exceed the "
            f"charges paid or payable in the {cap_months} months preceding the event giving "
            f"rise to the claim</b>. Neither party is responsible to the other for loss of "
            "profit, loss of revenue, loss of anticipated savings or reputational harm, "
            "whether direct or indirect. This clause does not limit liability for fraud, or "
            "for the uncapped sub-clauses identified in clause 19.2."
        ),
        p(
            "22.5 <b>Governing law.</b> England and Wales, exclusive jurisdiction of the "
            "courts of England and Wales."
        ),
        section("SCHEDULE 1 - AGREED AMENDMENTS TO THE COMPANY STANDARD FORM"),
        p(
            "The following departures from the Company's standard form were agreed by "
            "Company Legal and applied to the executed text above.",
            "Small",
        ),
        table(
            [
                ["Clause", "Standard form", "As executed"],
                [
                    "19.2",
                    "Indemnities not subject to any limitation elsewhere",
                    f"Subject to the 22.4 cap, except IP and data-breach claims",
                ],
                [
                    "22.4",
                    "No financial cap on Supplier responsibility",
                    f"Aggregate cap at {cap_months} months of charges",
                ],
                [
                    "6.2",
                    "Set-off against any sum owed by Supplier or its affiliates",
                    "Set-off limited to sums due under this Agreement",
                ],
            ],
            widths=[0.8 * inch, 2.9 * inch, 2.8 * inch],
        ),
        section("SIGNATURES"),
        p(f"Executed by the parties on {signed_on}.", "Small"),
        table(
            [
                ["CALDER FINANCIAL GROUP PLC", "ACME ROBOTICS, INC."],
                ["By: /s/ Priya Raghunathan", "By: /s/ Elena Martinez"],
                ["Name: Priya Raghunathan", "Name: Elena Martinez"],
                ["Title: Group General Counsel", "Title: Chief Revenue Officer"],
                [f"Date: {signed_on}", f"Date: {signed_on}"],
            ],
            widths=[3.45 * inch, 3.45 * inch],
        ),
        Spacer(1, 0.2 * inch),
        p(
            "This synthetic executed agreement is designed for contract-lifecycle "
            "demonstrations. Names, terms, and provisions are fictional and are not legal "
            "advice.",
            "Small",
        ),
    ]
    make_doc(path).build(story)
    return path


def build_calder_sow(year, sow_ref, charges, services, po_number):
    """A Statement of Work under the Calder master agreement.

    On the Company's form, like everything else in this deal, and deliberately consistent
    with the master: sixty-day payment at 6.1, the purchase-order condition that sends an
    invoice back unpaid, and the twenty-four month price freeze at 6.3. The SOW is where a
    reader checks whether the commercial terms match the record, so those three have to be
    the same numbers the MSA uses.
    """
    path = PDF_OUT / f"calder-sow-{year}.pdf"
    story = doc_header(
        f"Statement of Work {sow_ref}",
        f"Calder Financial Group plc and Acme Robotics, Inc. | Under the Master Agreement for Supplier Services | CLM-{year}-Calder",
    )
    story += [
        p(f"This Statement of Work is entered into under, and is governed by, the Master Agreement for Supplier Services between the parties. Capitalised terms have the meaning given in that Agreement. Where this Statement of Work conflicts with the Agreement, the Agreement prevails."),
        section("1. SERVICES"),
        p(services),
        section("2. TERM"),
        p(f"This Statement of Work commences on execution and continues for twenty-four months unless terminated in accordance with the Agreement."),
        section("3. CHARGES"),
        table(
            [
                ["Item", "Basis", "Amount"],
                ["Platform subscription", "Annual, in advance", charges],
                ["Implementation services", "Fixed price, on milestone", "As set out in Schedule 1"],
                ["Support", "Included", "Nil"],
            ],
            widths=[2.3 * inch, 2.3 * inch, 2.3 * inch],
        ),
        p(f"3.1 Invoices must quote purchase order number <b>{po_number}</b>. Invoices without a valid purchase order number will be returned unpaid, in accordance with clause 6.1 of the Agreement."),
        p("3.2 The Company shall pay valid and undisputed invoices within sixty days of receipt."),
        p("3.3 Charges are fixed for the first twenty-four months. Thereafter any increase requires ninety days' notice and shall not exceed the lesser of CPI and three per cent per annum."),
        section("4. SERVICE LEVELS"),
        table(
            [
                ["Measure", "Target", "Measurement window"],
                ["Platform availability", "99.5% excluding planned maintenance", "Calendar month"],
                ["Priority 1 response", "Within 1 hour", "24x7"],
                ["Priority 2 response", "Within 4 business hours", "Business hours"],
            ],
            widths=[2.3 * inch, 2.6 * inch, 2.0 * inch],
        ),
        section("5. COMPANY DEPENDENCIES"),
        p("The Company shall provide timely access to nominated personnel, test environments and data necessary for the Supplier to perform. Delay attributable to a Company dependency does not constitute Supplier non-performance for the purposes of clause 22.4 of the Agreement."),
        section("6. GOVERNANCE"),
        p("The parties shall hold a monthly service review and a quarterly commercial review. The Supplier shall report against the service levels above at each service review."),
        Spacer(1, 0.2 * inch),
        p("This synthetic statement of work is designed for contract-lifecycle demonstrations. Names, terms, and provisions are fictional and are not legal advice.", "Small"),
    ]
    make_doc(path).build(story)
    return path


def build_calder_dpa():
    """Calder's data processing schedule for the 2026 negotiation.

    Written to sit under the customer paper rather than beside it: it points back at
    Article 14 for the security measures and at Article 11 for regulator access, so a
    reader following the liability question through the package finds the same
    twenty-four-hour notification obligation stated twice and can see it is not a drafting
    accident.
    """
    path = PDF_OUT / "calder-dpa-2026.pdf"
    story = doc_header(
        "Data Processing Schedule",
        "Calder Financial Group plc and Acme Robotics, Inc. | Schedule 4 to the Master Agreement | CLM-2026-Calder",
    )
    story += [
        p("This Schedule forms part of the Master Agreement for Supplier Services. The Company is the controller and the Supplier is the processor in respect of Company Data processed under the Agreement."),
        section("1. SUBJECT MATTER AND DURATION"),
        p("The Supplier processes Company Data for the term of the Agreement and for no longer than is necessary to provide the Services, subject to the return and destruction obligation at clause 14.2 of the Agreement."),
        section("2. NATURE AND PURPOSE"),
        table(
            [
                ["Category", "Detail"],
                ["Data subjects", "Company employees, contractors, and customers of the Company"],
                ["Personal data", "Name, business contact details, role, system identifiers, transaction records"],
                ["Special categories", "None permitted without the Company's prior written consent"],
                ["Processing", "Hosting, analysis, support, and reporting in connection with the Services"],
            ],
            widths=[1.6 * inch, 5.0 * inch],
        ),
        section("3. SECURITY MEASURES"),
        p("The Supplier shall implement technical and organisational measures no less protective than the Company's Information Security Standard, as required by clause 14.1 of the Agreement. Measures include encryption in transit and at rest, least-privilege access control, logging and monitoring, vulnerability management, and annual independent penetration testing."),
        section("4. PERSONAL DATA BREACH"),
        p("The Supplier shall notify the Company of any actual or suspected personal data breach <b>within twenty-four hours</b> of becoming aware of it, and shall provide the information the Company reasonably requires to meet its own regulatory notification deadlines. This mirrors, and does not replace, the incident notification obligation at clause 14.1."),
        section("5. SUB-PROCESSORS"),
        p("The Supplier shall not appoint a sub-processor without the Company's prior written consent, and remains fully liable for the acts and omissions of any approved sub-processor, consistent with clause 11.2 of the Agreement."),
        section("6. AUDIT AND REGULATOR ACCESS"),
        p("The Supplier shall make available the information necessary to demonstrate compliance with this Schedule and shall permit audits by the Company and by each Regulator, on the access terms set out at clause 11.1 of the Agreement."),
        section("7. INTERNATIONAL TRANSFERS"),
        p("The Supplier shall not transfer Company Data outside the United Kingdom or the European Economic Area without the Company's prior written consent and an approved transfer mechanism."),
        Spacer(1, 0.2 * inch),
        p("This synthetic data processing schedule is designed for contract-lifecycle demonstrations. Names, terms, and provisions are fictional and are not legal advice.", "Small"),
    ]
    make_doc(path).build(story)
    return path


def build_calder_security_standard():
    """The Company's Information Security Standard.

    Article 3.2 and clause 14.1 of the customer paper both bind Acme to this document
    without reproducing any of it, which is exactly how customer paper works: the
    obligation is a reference, and the reference is where the actual requirements live.
    Putting it in the folder is what lets someone answer "what did we actually sign up to"
    rather than "the MSA says we comply with their standard".
    """
    path = PDF_OUT / "calder-supplier-security-standard.pdf"
    story = doc_header(
        "Information Security Standard for Suppliers",
        "Calder Financial Group plc | Third Party Security Standard TPS-2024 rev.2 | Referenced at Articles 3.2 and 14.1",
    )
    story += [
        p("This Standard applies to every supplier processing Company Data or connecting to Company systems. Compliance is a contractual obligation under the Master Agreement for Supplier Services. Deviations require a documented exception approved by the Company's Chief Information Security Officer."),
        section("1. ACCESS CONTROL"),
        p("Multi-factor authentication for all administrative and remote access. Access reviewed quarterly and revoked within twenty-four hours of a leaver event. No shared accounts. Privileged access recorded and session-logged."),
        section("2. ENCRYPTION"),
        p("Company Data encrypted in transit using TLS 1.2 or above, and at rest using AES-256 or an equivalent approved algorithm. Key management documented and keys rotated at least annually."),
        section("3. VULNERABILITY AND PATCH MANAGEMENT"),
        table(
            [
                ["Severity", "Remediation window"],
                ["Critical", "72 hours"],
                ["High", "14 days"],
                ["Medium", "60 days"],
            ],
            widths=[2.2 * inch, 4.4 * inch],
        ),
        section("4. INCIDENT MANAGEMENT"),
        p("The supplier shall notify the Company of any actual or suspected security incident affecting Company Data <b>within twenty-four hours</b> of becoming aware of it, and shall provide a written root cause analysis within ten business days of closure."),
        section("5. RESILIENCE"),
        p("Documented business continuity and disaster recovery plans, tested at least annually, with a recovery time objective of four hours and a recovery point objective of fifteen minutes for services supporting a material outsourcing."),
        section("6. ASSURANCE"),
        p("Annual independent penetration test, with the summary report provided to the Company on request. Current ISO/IEC 27001 certification or an equivalent recognised by the Company. Annual completion of the Company's third party security questionnaire."),
        section("7. PERSONNEL"),
        p("Background screening for all personnel with access to Company Data, to the standard applicable in the relevant jurisdiction, and annual security awareness training."),
        Spacer(1, 0.2 * inch),
        p("This synthetic security standard is designed for contract-lifecycle demonstrations. Names, terms, and provisions are fictional and are not legal advice.", "Small"),
    ]
    make_doc(path).build(story)
    return path


def main():
    build_msa()
    build_realistic_msa()
    build_executed_msa(2024, "July 31, 2024", "July 24, 2024", "$2,150,000")
    build_executed_msa(2025, "July 31, 2025", "July 23, 2025", "$2,275,000")
    build_dpa()
    build_sow()
    build_order_form()
    build_security_exhibit()
    build_insurance()
    build_calder_customer_paper()
    build_calder_executed(2022, "MA-2021 rev.1", "14 March 2022", "GBP 1,400,000", 24)
    build_calder_executed(
        2024, "MA-2024 rev.2", "9 May 2024", "GBP 1,850,000", 24, prior_year=2022
    )
    build_calder_sow(2022, "SOW-CAL-001", "GBP 1,400,000", "Supplier shall provide the Robotics Operations Console and associated support to the Company's operations function.", "PO-CAL-88214")
    build_calder_sow(2024, "SOW-CAL-002", "GBP 1,850,000", "Supplier shall provide the Robotics Operations Console, Workflow Analytics, and associated support across the Company's operations and risk functions.", "PO-CAL-93307")
    build_calder_sow(2026, "SOW-CAL-003", "GBP 2,100,000", "Supplier shall provide the Robotics Operations Console, Workflow Analytics, and Regulatory Reporting Extract across the Company's operations, risk, and compliance functions.", "PO-CAL-10442")
    build_calder_dpa()
    build_calder_security_standard()
    write_json()
    write_csv()
    print(f"Wrote PDFs to {PDF_OUT}")
    print(f"Wrote JSON to {JSON_OUT}")
    print(f"Wrote CSV to {CSV_OUT}")


if __name__ == "__main__":
    main()
