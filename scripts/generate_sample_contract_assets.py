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
    write_json()
    write_csv()
    print(f"Wrote PDFs to {PDF_OUT}")
    print(f"Wrote JSON to {JSON_OUT}")
    print(f"Wrote CSV to {CSV_OUT}")


if __name__ == "__main__":
    main()
