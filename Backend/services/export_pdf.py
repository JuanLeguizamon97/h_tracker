"""PDF invoice export using reportlab."""
from io import BytesIO
from datetime import date
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

# Brand colours
BLUE = colors.HexColor("#1e3a5f")
LIGHT_BLUE = colors.HexColor("#e8f0fe")
GREY = colors.HexColor("#6b7280")
LIGHT_GREY = colors.HexColor("#f9fafb")
RED = colors.HexColor("#dc2626")
BLACK = colors.black
WHITE = colors.white

EXPENSE_CATEGORIES = ["Airfare", "Hotel", "Parking / Transportation", "Meals", "Other"]

styles = getSampleStyleSheet()

def _style(name, **kw):
    s = ParagraphStyle(name, parent=styles["Normal"], **kw)
    return s

H1 = _style("H1", fontSize=18, textColor=BLUE, fontName="Helvetica-Bold", spaceAfter=2)
H2 = _style("H2", fontSize=11, textColor=BLUE, fontName="Helvetica-Bold", spaceAfter=4)
BODY = _style("Body", fontSize=9, textColor=BLACK, leading=13)
BODY_GREY = _style("BodyGrey", fontSize=9, textColor=GREY, leading=13)
BODY_RIGHT = _style("BodyRight", fontSize=9, textColor=BLACK, leading=13, alignment=TA_RIGHT)
LABEL = _style("Label", fontSize=7, textColor=GREY, fontName="Helvetica", leading=10)
TOTAL = _style("Total", fontSize=12, textColor=BLUE, fontName="Helvetica-Bold", alignment=TA_RIGHT)
SECTION = _style("Section", fontSize=8, textColor=GREY, fontName="Helvetica-Bold",
                 spaceAfter=2, spaceBefore=8)


def _money(val: float) -> str:
    return f"${val:,.2f}"


def _fmt_date(d) -> str:
    if not d:
        return "—"
    if isinstance(d, str):
        return d
    return d.strftime("%B %d, %Y")


def _table_style(header_bg=BLUE, stripe=LIGHT_GREY):
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, stripe]),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, BLUE),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
    ])


def generate_invoice_pdf(edit_data: dict) -> bytes:
    """
    Generate a PDF for an invoice given the edit-data dict (from InvoiceEditDataOut).
    Returns raw PDF bytes.
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    invoice = edit_data.get("invoice", {})
    client = edit_data.get("client") or {}
    project = edit_data.get("project") or {}
    lines = edit_data.get("lines", [])
    expenses = edit_data.get("expenses", [])

    inv_number = invoice.get("invoice_number") or invoice.get("id", "")[:8]
    inv_label = f"INV-{inv_number}" if inv_number else "INVOICE"
    status = (invoice.get("status") or "draft").upper()
    issue_date = _fmt_date(invoice.get("issue_date"))
    due_date = _fmt_date(invoice.get("due_date"))
    cap_amount: Optional[float] = invoice.get("cap_amount")
    notes = invoice.get("notes") or ""

    client_name = client.get("name") or "—"
    client_email = client.get("email") or ""
    client_phone = client.get("phone") or ""
    project_name = project.get("name") or "—"

    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    header_data = [
        [
            Paragraph("<b>Impact Point Co., LLC</b>", _style("Co", fontSize=14, textColor=BLUE,
                                                              fontName="Helvetica-Bold")),
            Paragraph(inv_label, _style("InvLabel", fontSize=20, textColor=BLUE,
                                        fontName="Helvetica-Bold", alignment=TA_RIGHT)),
        ]
    ]
    header_table = Table(header_data, colWidths=["55%", "45%"])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=2, color=BLUE))
    story.append(Spacer(1, 8))

    # ── Invoice meta + client side by side ─────────────────────────────────
    meta_left = [
        [Paragraph("BILL TO", LABEL)],
        [Paragraph(f"<b>{client_name}</b>", BODY)],
    ]
    if client_email:
        meta_left.append([Paragraph(client_email, BODY_GREY)])
    if client_phone:
        meta_left.append([Paragraph(client_phone, BODY_GREY)])
    meta_left.append([Paragraph(f"Project: {project_name}", BODY_GREY)])

    meta_right = [
        [Paragraph("INVOICE DATE", LABEL), Paragraph(issue_date, BODY_RIGHT)],
        [Paragraph("DUE DATE", LABEL), Paragraph(due_date, BODY_RIGHT)],
        [Paragraph("STATUS", LABEL),
         Paragraph(f"<b>{status}</b>",
                   _style("St", fontSize=9, textColor=BLUE if status == "APPROVED" else GREY,
                          fontName="Helvetica-Bold", alignment=TA_RIGHT))],
    ]

    left_tbl = Table(meta_left, colWidths=["100%"])
    left_tbl.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    right_tbl = Table(meta_right, colWidths=["50%", "50%"])
    right_tbl.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    meta_wrapper = Table([[left_tbl, right_tbl]], colWidths=["55%", "45%"])
    meta_wrapper.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(meta_wrapper)
    story.append(Spacer(1, 14))

    # ── Professionals ───────────────────────────────────────────────────────
    ROLE_SECTION_LABELS = {
        "manager": "Hours Cost per Employee",
        "contractor": "Professional Fees",
        "employee": "Billable Hours",
    }

    # Group lines by role
    groups: dict[str, list] = {}
    for line in lines:
        key = (line.get("role") or "employee").lower()
        groups.setdefault(key, []).append(line)

    total_fees = 0.0
    total_discounts = 0.0

    if groups:
        story.append(Paragraph("PROFESSIONALS", SECTION))
        for role_key, role_lines in groups.items():
            section_label = ROLE_SECTION_LABELS.get(role_key, role_key.title())
            story.append(Paragraph(f"<i>{section_label}</i>",
                                   _style("RoleHdr", fontSize=8, textColor=GREY,
                                          fontName="Helvetica-Oblique", spaceBefore=4, spaceAfter=2)))

            rows = [["Professional", "Role", "Hours", "Rate", "Subtotal", "Discount", "Total"]]
            for line in role_lines:
                hours = float(line.get("hours", 0) or 0)
                rate = float(line.get("hourly_rate", 0) or 0)
                subtotal = hours * rate
                disc_type = line.get("discount_type") or "amount"
                disc_val = float(line.get("discount_value", 0) or 0)
                disc_dollars = (subtotal * disc_val / 100) if disc_type == "percent" else disc_val
                disc_hours = disc_dollars / rate if rate > 0 else 0
                line_total = max(0, subtotal - disc_dollars)
                total_fees += line_total
                total_discounts += disc_dollars

                disc_label = f"{disc_hours:.2f}h / {_money(disc_dollars)}" if disc_dollars > 0 else "—"
                rows.append([
                    Paragraph(f"<b>{line.get('employee_name', '')}</b><br/>"
                              f"<font size='7' color='grey'>{line.get('title', '')}</font>",
                              BODY),
                    (line.get("role") or "").capitalize(),
                    f"{hours:.1f}",
                    _money(rate),
                    _money(subtotal),
                    Paragraph(disc_label,
                              _style("DiscLabel", fontSize=8, textColor=GREY, alignment=TA_RIGHT)),
                    Paragraph(f"<b>{_money(line_total)}</b>", BODY_RIGHT),
                ])

            col_widths = [2.1 * inch, 0.9 * inch, 0.55 * inch, 0.7 * inch, 0.75 * inch, 1.1 * inch, 0.9 * inch]
            tbl = Table(rows, colWidths=col_widths, repeatRows=1)
            tbl.setStyle(_table_style())
            # Right-align numeric cols
            for col in [2, 3, 4, 6]:
                tbl.setStyle(TableStyle([("ALIGN", (col, 0), (col, -1), "RIGHT")]))
            story.append(tbl)
            story.append(Spacer(1, 6))

    # ── Expenses ─────────────────────────────────────────────────────────────
    total_expenses = 0.0
    if expenses:
        story.append(Spacer(1, 6))
        story.append(Paragraph("EXPENSES", SECTION))

        exp_rows = [["Date", "Professional", "Vendor", "Description", "Category", "Amount"]]
        for exp in expenses:
            amount = float(exp.get("amount_usd", 0) or 0)
            total_expenses += amount
            exp_rows.append([
                _fmt_date(exp.get("date")),
                exp.get("professional") or "—",
                exp.get("vendor") or "—",
                Paragraph(exp.get("description") or "—", BODY),
                exp.get("category") or "—",
                Paragraph(_money(amount), BODY_RIGHT),
            ])

        # Category subtotals row
        cat_totals: dict[str, float] = {}
        for exp in expenses:
            cat = exp.get("category") or "Other"
            cat_totals[cat] = cat_totals.get(cat, 0) + float(exp.get("amount_usd", 0) or 0)
        cat_label = "  |  ".join(
            f"{c}: {_money(v)}" for c, v in cat_totals.items() if v > 0
        )

        exp_col_widths = [0.7*inch, 1.1*inch, 1.1*inch, 2.0*inch, 1.0*inch, 0.9*inch]
        exp_tbl = Table(exp_rows, colWidths=exp_col_widths, repeatRows=1)
        exp_tbl.setStyle(_table_style())
        exp_tbl.setStyle(TableStyle([("ALIGN", (5, 0), (5, -1), "RIGHT")]))
        story.append(exp_tbl)

        if cat_label:
            story.append(Spacer(1, 3))
            story.append(Paragraph(cat_label, BODY_GREY))

    # ── Totals ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BLUE))
    story.append(Spacer(1, 8))

    subtotal_fees = total_fees
    if cap_amount is not None:
        capped_fees = min(subtotal_fees, float(cap_amount))
    else:
        capped_fees = subtotal_fees
    total_due = capped_fees + total_expenses

    summary_rows = [
        ["", "Total Fees:", _money(total_fees + total_discounts)],
        ["", "Total Discounts:", f"-{_money(total_discounts)}"],
    ]
    if cap_amount is not None:
        summary_rows.append(["", "Cap Amount:", _money(float(cap_amount))])
    summary_rows.append(["", "Total Expenses:", _money(total_expenses)])
    summary_rows.append(["", "", ""])  # spacer row
    summary_rows.append(["", "TOTAL DUE:", _money(total_due)])

    sum_tbl = Table(summary_rows, colWidths=["55%", "25%", "20%"])
    sum_style = TableStyle([
        ("ALIGN", (1, 0), (2, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, -2), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -2), 9),
        ("TEXTCOLOR", (1, 1), (2, 1), RED),  # discounts in red
        ("LINEABOVE", (1, -1), (2, -1), 1, BLUE),
        ("FONTNAME", (1, -1), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (1, -1), (2, -1), 12),
        ("TEXTCOLOR", (1, -1), (2, -1), BLUE),
        ("TOPPADDING", (0, -1), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -2), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ])
    sum_tbl.setStyle(sum_style)
    story.append(sum_tbl)

    # ── Notes ──────────────────────────────────────────────────────────────
    if notes:
        story.append(Spacer(1, 14))
        story.append(Paragraph("NOTES", SECTION))
        story.append(Paragraph(notes, BODY_GREY))

    # ── Footer ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#d1d5db")))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Impact Point Co., LLC  •  Generated by H_TRACKER",
        _style("Footer", fontSize=7, textColor=GREY, alignment=TA_CENTER),
    ))

    doc.build(story)
    return buf.getvalue()
