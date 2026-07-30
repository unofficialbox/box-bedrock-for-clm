#!/usr/bin/env python3
"""Generate Box DocGen-ready CLM Word templates with deterministic styling."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "docgen"
BLUE = "2E74B5"
DARK = "1F4D78"
GRAY = "5F6368"
LIGHT = "F2F4F7"

SERIF = "Times New Roman"
STRIKE = "9A3412"
INSERT = "1D4ED8"

# northstar-msa-2026-redline.docx is a contract, not a merge template and not an
# extraction worksheet. Every value the Salesforce intake connector binds is stated
# in ordinary contract language - the parties clause, the fee clause, the term
# clause, the notices clause, and the Exhibit A order form - exactly as a real MSA
# would state it. Nothing is presented as a labelled extraction field, so Box
# Extract has to normalise real contract prose ("Two Hundred Fifty Thousand Dollars
# ($250,000.00)" -> 250000.00, "thirty-six (36) months" -> 36, "United States" ->
# US) rather than copy a pre-cleaned value.
#
# Two fields are deliberately NOT on the face of this document:
#   riskLevel             - an assessment, not a contract term. Produced by the Box
#                           Agent and confirmed by a human at the approval task
#                           (config/box/automate-workflows.bcl riskLevelGate).
#   specialTermsRiskNotes - a derived review summary, not a contract term.
# Values otherwise mirror the CLM-SAMPLE-NST-001 seed record in
# clm-salesforce-project/scripts/seed-clm-salesforce-sample-data.apex.


def set_font(run, size=11, bold=False, color="000000", italic=False):
    run.font.name = "Calibri"
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Calibri")
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Calibri")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_geometry(table, widths_dxa):
    table.autofit = False
    total = sum(widths_dxa)
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    tbl_w.set(qn("w:w"), str(total))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), "120")
    tbl_ind.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths_dxa:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            tc_w.set(qn("w:w"), str(widths_dxa[idx]))
            tc_w.set(qn("w:type"), "dxa")
            set_cell_margins(cell)


def configure(doc, running_label, footer_label="Acme Robotics | CLM-2026-Northstar"):
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.right_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.1
    for style_name, size, before, after, color in (
        ("Heading 1", 16, 16, 8, BLUE),
        ("Heading 2", 13, 12, 6, BLUE),
        ("Heading 3", 12, 8, 4, DARK),
    ):
        style = doc.styles[style_name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    header.paragraph_format.space_after = Pt(0)
    set_font(header.add_run(running_label), 9, True, GRAY)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_font(footer.add_run(footer_label), 8, False, GRAY)


def add_title(doc, kicker, title, subtitle):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    set_font(p.add_run(kicker.upper()), 9, True, BLUE)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    set_font(p.add_run(title), 23, True, "000000")
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(16)
    set_font(p.add_run(subtitle), 12, False, GRAY)


def add_key_values(doc, rows):
    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"
    for label, value in rows:
        cells = table.add_row().cells
        cells[0].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        cells[1].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        shade(cells[0], LIGHT)
        shade(cells[1], "FFFFFF")
        set_font(cells[0].paragraphs[0].add_run(label), 10, True, DARK)
        set_font(cells[1].paragraphs[0].add_run(value), 10.5)
    set_table_geometry(table, [2700, 6660])
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def serif_run(paragraph, text, size=10.5, bold=False, italic=False, color="000000", strike=False, underline=False):
    """Add a Times New Roman run, optionally struck through or underlined for redline markup."""
    run = paragraph.add_run(text)
    run.font.name = SERIF
    rpr = run._element.get_or_add_rPr()
    rpr.rFonts.set(qn("w:ascii"), SERIF)
    rpr.rFonts.set(qn("w:hAnsi"), SERIF)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.underline = underline
    run.font.color.rgb = RGBColor.from_string(color)
    if strike:
        node = OxmlElement("w:strike")
        node.set(qn("w:val"), "true")
        rpr.append(node)
    return run


def clause_paragraph(doc, segments, indent=0.0, space_after=8, justify=True):
    """Render one clause body from (text, kind) segments.

    kind is "" for settled text, "strike" for counterparty deletions, and "insert"
    for counterparty insertions, so the markup reads like a tracked-changes redline
    rather than a coloured summary line.
    """
    paragraph = doc.add_paragraph()
    fmt = paragraph.paragraph_format
    fmt.space_after = Pt(space_after)
    fmt.line_spacing = 1.15
    if indent:
        fmt.left_indent = Inches(indent)
    if justify:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for text, kind in segments:
        if kind == "strike":
            serif_run(paragraph, text, color=STRIKE, strike=True)
        elif kind == "insert":
            serif_run(paragraph, text, color=INSERT, underline=True)
        else:
            serif_run(paragraph, text)
    return paragraph


def clause_heading(doc, number, title):
    paragraph = doc.add_paragraph()
    fmt = paragraph.paragraph_format
    fmt.space_before = Pt(12)
    fmt.space_after = Pt(4)
    fmt.keep_with_next = True
    serif_run(paragraph, f"{number}. ", size=11, bold=True)
    serif_run(paragraph, title.upper(), size=11, bold=True)
    return paragraph


def comment_paragraph(doc, text):
    """A margin-style negotiation comment, as counsel would leave in a draft."""
    paragraph = doc.add_paragraph()
    fmt = paragraph.paragraph_format
    fmt.left_indent = Inches(0.35)
    fmt.space_before = Pt(2)
    fmt.space_after = Pt(10)
    serif_run(paragraph, "[Comment - Northstar counsel]: ", size=9, bold=True, italic=True, color=STRIKE)
    serif_run(paragraph, text, size=9, italic=True, color=GRAY)
    return paragraph


def add_section_text(doc, heading, value):
    doc.add_heading(heading, level=2)
    p = doc.add_paragraph()
    set_font(p.add_run(value), 11)


def approval_memo():
    doc = Document()
    configure(doc, "CLM Approval Memo")
    add_title(doc, "Decision required", "Contract Approval Memo", "Northstar Health System agreement package")
    add_key_values(doc, [
        ("Contract ID", "{{contract.id}}"),
        ("Counterparty", "{{contract.counterparty}}"),
        ("Contract type", "{{contract.type}}"),
        ("Deal value", "{{contract.currency}}{{contract.dealValue}}"),
        ("Region / data", "{{contract.region}} / {{contract.dataCategory}}"),
        ("Target signature", "{{contract.targetSignatureDate}}"),
        ("Business owner", "{{contract.businessOwner}}"),
    ])
    add_section_text(doc, "Executive summary", "{{approval.executiveSummary}}")
    add_key_values(doc, [
        ("Legal review", "{{reviews.legalStatus}} - {{reviews.legalSummary}}"),
        ("Finance review", "{{reviews.financeStatus}} - {{reviews.financeSummary}}"),
        ("Privacy / security", "{{reviews.privacySecurityStatus}} - {{reviews.privacySecuritySummary}}"),
        ("Overall risk", "{{approval.riskLevel}}"),
    ])
    add_section_text(doc, "Recommendation", "{{approval.recommendation}}")
    add_key_values(doc, [
        ("Approver", "{{approval.approver}}"),
        ("Decision", "{{approval.decision}}"),
        ("Decision date", "{{approval.decisionDate}}"),
    ])
    return doc


def order_summary():
    doc = Document()
    configure(doc, "Commercial Order Summary")
    add_title(doc, "Commercial record", "Order Form Summary", "Structured deal terms for review and approval")
    add_key_values(doc, [
        ("Contract ID", "{{contract.id}}"),
        ("Customer", "{{contract.counterparty}}"),
        ("Annual value", "{{commercial.currency}}{{commercial.annualValue}}"),
        ("Total value", "{{commercial.currency}}{{commercial.totalValue}}"),
        ("Term", "{{commercial.termMonths}} months"),
        ("Effective date", "{{commercial.effectiveDate}}"),
        ("Payment terms", "{{commercial.paymentTerms}}"),
        ("Renewal", "{{commercial.renewalType}}"),
        ("Renewal notice", "{{commercial.renewalNoticeDays}} days"),
        ("Governing law", "{{commercial.governingLaw}}"),
    ])
    add_section_text(doc, "Commercial exception", "{{commercial.exceptionSummary}}")
    add_section_text(doc, "Approval note", "{{commercial.approvalNote}}")
    return doc


def renewal_notice():
    doc = Document()
    configure(doc, "Contract Renewal Notice")
    add_title(doc, "Contract notice", "Renewal Notice", "Formal notice generated from tracked obligations")
    add_key_values(doc, [
        ("Notice date", "{{notice.date}}"),
        ("Recipient", "{{recipient.name}}, {{recipient.title}}"),
        ("Recipient company", "{{recipient.company}}"),
        ("Recipient email", "{{recipient.email}}"),
        ("Contract ID", "{{contract.id}}"),
        ("Agreement", "{{contract.name}}"),
        ("Current term ends", "{{renewal.currentTermEndDate}}"),
        ("Notice deadline", "{{renewal.noticeDeadline}}"),
    ])
    add_section_text(doc, "Notice", "{{renewal.noticeText}}")
    add_section_text(doc, "Requested action", "{{renewal.requestedAction}}")
    add_key_values(doc, [
        ("Sender", "{{sender.name}}, {{sender.title}}"),
        ("Sender company", "{{sender.company}}"),
        ("Sender email", "{{sender.email}}"),
    ])
    return doc


def msa_redline():
    """Current-year MSA still in redline: a real Word contract, not a merge template.

    Reads as an executable agreement would - recitals, defined terms, numbered
    clauses in legal prose, tracked-changes markup, counsel comments, a signature
    block, and an Exhibit A order form. Every value the Salesforce intake connector
    binds is stated the way a contract states it, never as a labelled extraction
    field, so Box Extract must normalise real prose rather than copy clean values.
    See the MSA note at the top of this module for what is deliberately absent.
    """
    doc = Document()
    configure(doc, "Master Services Agreement - DRAFT (Redline)", "Acme Robotics, Inc. | Confidential | Page ")

    heading = doc.add_paragraph()
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    heading.paragraph_format.space_after = Pt(2)
    serif_run(heading, "MASTER SERVICES AGREEMENT", size=14, bold=True)

    reference = doc.add_paragraph()
    reference.alignment = WD_ALIGN_PARAGRAPH.CENTER
    reference.paragraph_format.space_after = Pt(14)
    serif_run(reference, "Agreement Reference No. CLM-SAMPLE-NST-001", size=10, bold=True)
    serif_run(reference, "\nDRAFT FOR DISCUSSION ONLY - SUBJECT TO CONTRACT - NOT EXECUTED", size=9, bold=True, color=STRIKE)

    clause_paragraph(doc, [(
        "This Master Services Agreement (this “Agreement”) is entered into as of the Effective Date "
        "set forth in Exhibit A (the “Effective Date”) by and between Acme Robotics, Inc., a Delaware "
        "corporation with its principal place of business at 1 Innovation Way, Wilmington, Delaware, "
        "United States (“Acme” or “Supplier”), and Northstar Health, a Minnesota nonprofit "
        "health system with its principal place of business at 500 Riverside Avenue, Minneapolis, "
        "Minnesota, United States (“Northstar” or “Customer”). Acme and Northstar are each a "
        "“Party” and together the “Parties.”",
        "",
    )], space_after=10)

    clause_paragraph(doc, [(
        "WHEREAS Customer wishes to procure certain robotics automation and support services for "
        "deployment across its United States facilities, and Supplier wishes to provide those "
        "services, the Parties agree as follows:",
        "",
    )], space_after=6)

    clause_heading(doc, 1, "Definitions and Order of Precedence")
    clause_paragraph(doc, [(
        "1.1  “Order Form” means an ordering document executed by both Parties that references "
        "this Agreement and sets out the Services, fees, and term. The initial Order Form is "
        "attached as Exhibit A and is incorporated by reference. In the event of a conflict between "
        "this Agreement and an Order Form, the Order Form controls solely as to commercial terms.",
        "",
    )], indent=0.25)
    clause_paragraph(doc, [(
        "1.2  “Services” means the robotics automation, integration, and support services "
        "described in the applicable Order Form. “Security Incident” means any confirmed "
        "unauthorised acquisition, access, use, or disclosure of Customer Data.",
        "",
    )], indent=0.25)

    clause_heading(doc, 2, "Fees, Invoicing, and Taxes")
    clause_paragraph(
        doc,
        [
            (
                "2.1  Customer shall pay the fees set forth in each Order Form. The total fees payable "
                "under the initial Order Form are Two Hundred Fifty Thousand Dollars ($250,000.00), "
                "exclusive of applicable taxes. Subscription fees are invoiced annually in advance, and "
                "Customer shall pay each undisputed invoice within ",
                "",
            ),
            ("forty-five (45)", "strike"),
            (" ", ""),
            ("ninety (90)", "insert"),
            (
                " days after the invoice date. Fees are stated and payable in United States dollars.",
                "",
            ),
        ],
        indent=0.25,
    )
    clause_paragraph(
        doc,
        [
            (
                "2.2  Except as expressly set out in Section 2.3, all amounts are non-cancellable and "
                "non-refundable, and Customer shall have no right of set-off against any amount invoiced.",
                "",
            ),
            (
                " Notwithstanding the foregoing, Customer may withhold and set off against any invoiced "
                "amount any sums Customer alleges in good faith to be owed to it by Supplier.",
                "insert",
            ),
        ],
        indent=0.25,
    )
    comment_paragraph(
        doc,
        "Net 45 moved to Net 90 to align with Northstar accounts-payable policy. Unilateral "
        "set-off right added at 2.2; we expect Supplier to resist this.",
    )

    clause_heading(doc, 3, "Service Levels and Support")
    clause_paragraph(
        doc,
        [
            (
                "3.1  Supplier shall use commercially reasonable efforts to make the Services available "
                "no less than ninety-nine and five tenths percent (99.5%) of the time in any calendar "
                "month, excluding scheduled maintenance. Service credits are Customer's sole and "
                "exclusive monetary remedy for any failure to meet this commitment and shall not exceed ",
                "",
            ),
            ("twenty percent (20%) of", "strike"),
            (" ", ""),
            ("one hundred percent (100%) of", "insert"),
            (
                " the monthly subscription fees for the affected Service.",
                "",
            ),
        ],
        indent=0.25,
    )
    clause_paragraph(
        doc,
        [
            (
                "3.2  Customer may terminate the affected Order Form for cause if Supplier fails to meet "
                "the availability commitment in ",
                "",
            ),
            ("three (3) consecutive calendar months", "strike"),
            (" ", ""),
            ("any two (2) months in a rolling six (6) month period", "insert"),
            (".", ""),
        ],
        indent=0.25,
    )

    clause_heading(doc, 4, "Data Protection and Information Security")
    clause_paragraph(
        doc,
        [
            (
                "4.1  Supplier shall maintain an information security programme consistent with ISO/IEC "
                "27001. Supplier shall notify Customer of a ",
                "",
            ),
            ("confirmed", "strike"),
            (" ", ""),
            ("suspected or confirmed", "insert"),
            (" Security Incident without undue delay and in any event no later than ", ""),
            ("seventy-two (72) hours", "strike"),
            (" ", ""),
            ("twelve (12) hours", "insert"),
            (
                " after becoming aware of it. Customer may audit Supplier's compliance with this "
                "Section once annually upon thirty (30) days' prior written notice.",
                "",
            ),
        ],
        indent=0.25,
    )
    clause_paragraph(
        doc,
        [
            (
                "4.2  The Parties acknowledge that Supplier does not require access to, and Customer "
                "shall not transmit to Supplier, any patient records, protected health information, or "
                "other special categories of personal data in connection with the Services. Should the "
                "Parties later require such processing, they shall execute a separate business associate "
                "agreement before any such data is transmitted.",
                "",
            ),
        ],
        indent=0.25,
    )
    comment_paragraph(
        doc,
        "Confirming with our privacy office that no PHI is in scope for the 2026 automation "
        "programme. If that changes, a BAA is required before go-live.",
    )

    clause_heading(doc, 5, "Limitation of Liability")
    clause_paragraph(
        doc,
        [
            (
                "5.1  EXCEPT FOR EXCLUDED CLAIMS, EACH PARTY'S TOTAL AGGREGATE LIABILITY ARISING OUT OF "
                "OR RELATED TO THIS AGREEMENT SHALL NOT EXCEED THE FEES PAID OR PAYABLE UNDER THE "
                "AFFECTED ORDER FORM IN THE TWELVE (12) MONTHS PRECEDING THE FIRST EVENT GIVING RISE TO "
                "LIABILITY.",
                "strike",
            ),
        ],
        indent=0.25,
        space_after=4,
    )
    clause_paragraph(
        doc,
        [
            (
                "5.1  SUPPLIER'S LIABILITY ARISING OUT OF OR RELATED TO THIS AGREEMENT SHALL BE "
                "UNLIMITED, AND SUPPLIER SHALL BE LIABLE FOR ALL DIRECT AND INDIRECT DAMAGES, INCLUDING "
                "LOST REVENUE, LOST PROFITS, AND ANY REGULATORY FINES OR PENALTIES IMPOSED ON CUSTOMER.",
                "insert",
            ),
        ],
        indent=0.25,
    )
    comment_paragraph(
        doc,
        "Cap deleted in its entirety and replaced with uncapped liability including consequential "
        "damages and regulatory penalties. Northstar treats this as a condition of signature.",
    )

    clause_heading(doc, 6, "Term and Termination")
    clause_paragraph(
        doc,
        [
            (
                "6.1  This Agreement commences on the Effective Date and continues for an initial term "
                "of thirty-six (36) months (the “Initial Term”), unless earlier terminated in "
                "accordance with its terms. Thereafter each Order Form renews automatically for "
                "successive periods of twelve (12) months unless either Party gives written notice of "
                "non-renewal at least ninety (90) days before the end of the then-current term.",
                "",
            ),
        ],
        indent=0.25,
    )
    clause_paragraph(
        doc,
        [
            (
                "6.2  Either Party may terminate this Agreement for material breach that remains uncured "
                "thirty (30) days after written notice.",
                "",
            ),
            (
                " Customer may additionally terminate this Agreement or any Order Form for convenience "
                "upon thirty (30) days' written notice, whereupon Supplier shall refund all prepaid fees "
                "on a pro rata basis.",
                "insert",
            ),
        ],
        indent=0.25,
    )

    clause_heading(doc, 7, "Notices")
    clause_paragraph(
        doc,
        [
            (
                "7.1  All notices under this Agreement shall be in writing and delivered to the "
                "addresses below, or to such other address as a Party may designate in writing. Notice "
                "by electronic mail is effective upon confirmed transmission.",
                "",
            ),
        ],
        indent=0.25,
    )
    clause_paragraph(
        doc,
        [(
            "For Customer:  Alex Mendoza, Director of Procurement, Northstar Health, 500 Riverside "
            "Avenue, Minneapolis, Minnesota, United States. Email: alex.mendoza@northstar.example.",
            "",
        )],
        indent=0.5,
        space_after=4,
        justify=False,
    )
    clause_paragraph(
        doc,
        [(
            "For Supplier:  Contracts Administration, Acme Robotics, Inc., 1 Innovation Way, "
            "Wilmington, Delaware, United States. Email: contracts@acmerobotics.example.",
            "",
        )],
        indent=0.5,
        justify=False,
    )

    clause_heading(doc, 8, "Governing Law and Venue")
    clause_paragraph(
        doc,
        [
            ("8.1  This Agreement is governed by the laws of the State of ", ""),
            ("Delaware", "strike"),
            (" ", ""),
            ("Minnesota", "insert"),
            (", without regard to its conflict-of-laws rules. The Parties submit to the exclusive "
             "jurisdiction of the state and federal courts located in ", ""),
            ("Wilmington, Delaware", "strike"),
            (" ", ""),
            ("Hennepin County, Minnesota", "insert"),
            (".", ""),
        ],
        indent=0.25,
    )

    clause_heading(doc, 9, "Entire Agreement")
    clause_paragraph(
        doc,
        [(
            "9.1  This Agreement, together with all Order Forms and exhibits, constitutes the entire "
            "agreement between the Parties and supersedes all prior proposals and understandings, "
            "including the Master Service Agreements dated July 31, 2024 and July 31, 2025 between "
            "the same Parties, which are superseded as of the Effective Date.",
            "",
        )],
        indent=0.25,
    )

    signature = doc.add_paragraph()
    signature.paragraph_format.space_before = Pt(18)
    signature.paragraph_format.space_after = Pt(6)
    serif_run(signature, "IN WITNESS WHEREOF", size=10.5, bold=True)
    serif_run(
        signature,
        ", the Parties have caused this Agreement to be executed by their duly authorised "
        "representatives. THIS DRAFT IS UNSIGNED AND CREATES NO OBLIGATION.",
        size=10.5,
    )

    block = doc.add_table(rows=1, cols=2)
    for index, (party, entity) in enumerate((("ACME ROBOTICS, INC.", "Supplier"), ("NORTHSTAR HEALTH", "Customer"))):
        cell = block.rows[0].cells[index]
        cell.paragraphs[0].paragraph_format.space_after = Pt(2)
        serif_run(cell.paragraphs[0], party, size=10, bold=True)
        for label in (f"({entity})", "", "By: ____________________________", "Name:", "Title:", "Date:"):
            paragraph = cell.add_paragraph()
            paragraph.paragraph_format.space_after = Pt(2)
            serif_run(paragraph, label, size=10)
    set_table_geometry(block, [4680, 4680])
    for row in block.rows:
        for cell in row.cells:
            shade(cell, "FFFFFF")

    exhibit = doc.add_paragraph()
    exhibit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    exhibit.paragraph_format.page_break_before = True
    exhibit.paragraph_format.space_after = Pt(10)
    serif_run(exhibit, "EXHIBIT A - INITIAL ORDER FORM", size=12, bold=True)

    clause_paragraph(
        doc,
        [(
            "This Order Form is entered into under and incorporates the Master Services Agreement "
            "bearing Agreement Reference No. CLM-SAMPLE-NST-001 between Acme Robotics, Inc. and "
            "Northstar Health, and is issued in connection with the Northstar Master Service "
            "Agreement 2026 procurement programme.",
            "",
        )],
        space_after=10,
    )
    clause_paragraph(
        doc,
        [(
            "A.1  Services. Robotics automation platform subscription, integration services, and "
            "standard support for deployment across Customer's facilities in the United States.",
            "",
        )],
        indent=0.25,
        space_after=6,
    )
    clause_paragraph(
        doc,
        [(
            "A.2  Term. The Initial Term is thirty-six (36) months commencing on the Effective Date "
            "of August 1, 2026. The Parties are working toward signature by December 31, 2026.",
            "",
        )],
        indent=0.25,
        space_after=6,
    )
    clause_paragraph(
        doc,
        [(
            "A.3  Fees. Total fees for the Initial Term are Two Hundred Fifty Thousand Dollars "
            "($250,000.00), invoiced annually in advance in United States dollars.",
            "",
        )],
        indent=0.25,
        space_after=6,
    )
    clause_paragraph(
        doc,
        [(
            "A.4  Territory. The Services are provided solely within the United States. No data is "
            "processed outside the United States without Customer's prior written consent.",
            "",
        )],
        indent=0.25,
        space_after=6,
    )
    clause_paragraph(
        doc,
        [(
            "A.5  Customer Contacts. Procurement and contract notices: Alex Mendoza, Director of "
            "Procurement (alex.mendoza@northstar.example). Contract owner of record: Northstar "
            "Master Contract Owner.",
            "",
        )],
        indent=0.25,
        space_after=6,
    )
    clause_paragraph(
        doc,
        [(
            "A.6  Data Categories. The Services do not involve the processing of protected health "
            "information or any other special category of personal data. No such data is in scope "
            "for this Order Form.",
            "",
        )],
        indent=0.25,
        space_after=14,
    )

    footnote = doc.add_paragraph()
    footnote.paragraph_format.space_before = Pt(6)
    serif_run(
        footnote,
        "Drafting note: struck-through text marks language Northstar proposes to delete; "
        "underlined text marks language Northstar proposes to insert. Bracketed comments are "
        "Northstar counsel's. This draft remains under negotiation and is not executed.",
        size=8.5,
        italic=True,
        color=GRAY,
    )
    return doc


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    templates = {
        "clm-approval-memo-template.docx": approval_memo(),
        "clm-order-summary-template.docx": order_summary(),
        "clm-renewal-notice-template.docx": renewal_notice(),
        "northstar-msa-2026-redline.docx": msa_redline(),
    }
    for name, document in templates.items():
        document.core_properties.title = name.removesuffix(".docx").replace("-", " ").title()
        document.core_properties.subject = "Box DocGen template for the Northstar CLM demo"
        document.core_properties.author = "Acme Robotics CLM Demo"
        document.save(OUTPUT / name)
        print(OUTPUT / name)


if __name__ == "__main__":
    main()
