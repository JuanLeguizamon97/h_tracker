"""Excel invoice export using openpyxl — IPC_Invoice_System_v4 structure."""
from io import BytesIO
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter

# Brand colours (ARGB: FF + hex)
BLUE = "FF1e3a5f"
LIGHT_BLUE = "FFe8f0fe"
GREY = "FF6b7280"
LIGHT_GREY = "FFf9fafb"
WHITE = "FFFFFFFF"
RED = "FFdc2626"
HEADER_FONT = Font(name="Calibri", bold=True, color=WHITE, size=10)
BLUE_FILL = PatternFill("solid", fgColor=BLUE)
LIGHT_BLUE_FILL = PatternFill("solid", fgColor=LIGHT_BLUE)
STRIPE_FILL = PatternFill("solid", fgColor=LIGHT_GREY)
LABEL_FONT = Font(name="Calibri", bold=True, size=9, color=BLUE)
BODY_FONT = Font(name="Calibri", size=9)
GREY_FONT = Font(name="Calibri", size=9, color=GREY)
TITLE_FONT = Font(name="Calibri", bold=True, size=14, color=BLUE)
TOTAL_FONT = Font(name="Calibri", bold=True, size=11, color=BLUE)

CENTER = Alignment(horizontal="center", vertical="center")
LEFT = Alignment(horizontal="left", vertical="center")
RIGHT = Alignment(horizontal="right", vertical="center")
WRAP = Alignment(wrap_text=True, vertical="top")

MONEY_FMT = '#,##0.00'
DATE_FMT = 'YYYY-MM-DD'


def _thin_border(sides="all"):
    thin = Side(style="thin", color="FFd1d5db")
    b = Border()
    if "all" in sides or "left" in sides:
        b.left = thin
    if "all" in sides or "right" in sides:
        b.right = thin
    if "all" in sides or "top" in sides:
        b.top = thin
    if "all" in sides or "bottom" in sides:
        b.bottom = thin
    return b


def _set_col_widths(ws, widths: dict[str, float]):
    for col_letter, width in widths.items():
        ws.column_dimensions[col_letter].width = width


def _header_row(ws, row: int, headers: list[str], fill=BLUE_FILL, font=HEADER_FONT):
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col_idx, value=header)
        cell.font = font
        cell.fill = fill
        cell.alignment = CENTER
        cell.border = _thin_border()


def _data_row(ws, row: int, values: list[Any], stripe: bool = False):
    fill = STRIPE_FILL if stripe else PatternFill("solid", fgColor=WHITE)
    border = _thin_border()
    for col_idx, val in enumerate(values, 1):
        cell = ws.cell(row=row, column=col_idx, value=val)
        cell.font = BODY_FONT
        cell.fill = fill
        cell.border = border
        cell.alignment = LEFT
        if isinstance(val, float) and col_idx > 1:
            cell.number_format = MONEY_FMT
            cell.alignment = RIGHT


def _money(val) -> float:
    return round(float(val or 0), 2)


def generate_invoice_xlsx(edit_data: dict) -> bytes:
    """
    Generate a .xlsx export for an invoice. Returns raw bytes.
    """
    invoice = edit_data.get("invoice", {})
    client = edit_data.get("client") or {}
    project = edit_data.get("project") or {}
    lines = edit_data.get("lines", [])
    expenses = edit_data.get("expenses", [])

    inv_number = invoice.get("invoice_number") or invoice.get("id", "")[:8]
    inv_label = f"INV-{inv_number}"
    status = invoice.get("status") or "draft"
    cap_amount = invoice.get("cap_amount")

    wb = Workbook()
    wb.remove(wb.active)  # remove default sheet

    # ─────────────────────────── Sheet: Invoice ──────────────────────────────
    ws_inv = wb.create_sheet("Invoice")
    ws_inv.sheet_view.showGridLines = False

    # Title block
    ws_inv.merge_cells("A1:G1")
    c = ws_inv["A1"]
    c.value = "Impact Point Co., LLC"
    c.font = TITLE_FONT
    c.alignment = LEFT

    ws_inv.merge_cells("A2:G2")
    c = ws_inv["A2"]
    c.value = inv_label
    c.font = Font(name="Calibri", bold=True, size=12, color=BLUE)
    c.alignment = LEFT

    # Meta fields
    meta = [
        ("Status:", status.upper()),
        ("Issue Date:", invoice.get("issue_date")),
        ("Due Date:", invoice.get("due_date")),
        ("Client:", client.get("name", "")),
        ("Project:", project.get("name", "")),
        ("Notes:", invoice.get("notes", "")),
    ]
    for i, (label, val) in enumerate(meta, 4):
        ws_inv.cell(row=i, column=1, value=label).font = LABEL_FONT
        c = ws_inv.cell(row=i, column=2, value=val)
        c.font = BODY_FONT
        c.alignment = LEFT

    ws_inv.column_dimensions["A"].width = 14
    ws_inv.column_dimensions["B"].width = 28
    ws_inv.row_dimensions[1].height = 22
    ws_inv.row_dimensions[2].height = 18

    # ─────────────────────────── Sheet: Time_Detail ──────────────────────────
    ws_time = wb.create_sheet("Time_Detail")
    ws_time.sheet_view.showGridLines = False

    headers_time = [
        "Invoice", "Employee", "Title", "Role",
        "Hours", "Rate (USD)", "Subtotal", "Disc. Type", "Disc. Value",
        "Disc. ($)", "Total"
    ]
    _header_row(ws_time, 1, headers_time)

    ROLE_LABELS = {
        "manager": "Hours Cost per Employee",
        "contractor": "Professional Fees",
        "employee": "Billable Hours",
    }

    total_fees = 0.0
    total_discounts = 0.0
    for i, line in enumerate(lines, 2):
        hours = _money(line.get("hours", 0))
        rate = _money(line.get("hourly_rate", 0))
        subtotal = hours * rate
        disc_type = line.get("discount_type") or "amount"
        disc_val = _money(line.get("discount_value", 0))
        disc_dollars = (subtotal * disc_val / 100) if disc_type == "percent" else disc_val
        line_total = max(0.0, subtotal - disc_dollars)
        total_fees += line_total
        total_discounts += disc_dollars

        role_key = (line.get("role") or "employee").lower()
        _data_row(ws_time, i, [
            inv_label,
            line.get("employee_name", ""),
            line.get("title", ""),
            ROLE_LABELS.get(role_key, role_key.title()),
            hours,
            rate,
            subtotal,
            disc_type,
            disc_val,
            disc_dollars,
            line_total,
        ], stripe=i % 2 == 0)

    # Totals row
    totals_row = len(lines) + 2
    ws_time.cell(row=totals_row, column=1, value="TOTALS").font = LABEL_FONT
    for col, val in [(7, total_fees + total_discounts), (10, total_discounts), (11, total_fees)]:
        c = ws_time.cell(row=totals_row, column=col, value=_money(val))
        c.font = TOTAL_FONT
        c.number_format = MONEY_FMT
        c.alignment = RIGHT
        c.fill = LIGHT_BLUE_FILL

    _set_col_widths(ws_time, {
        "A": 16, "B": 22, "C": 20, "D": 22,
        "E": 8, "F": 11, "G": 11, "H": 10,
        "I": 10, "J": 11, "K": 11,
    })

    # ─────────────────────────── Sheet: Expense_Details ──────────────────────
    ws_exp = wb.create_sheet("Expense_Details")
    ws_exp.sheet_view.showGridLines = False

    headers_exp = [
        "Invoice", "Date", "Professional", "Vendor",
        "Description", "Category", "Amount (USD)",
        "Payment Source", "Receipt Attached", "Notes"
    ]
    _header_row(ws_exp, 1, headers_exp)

    total_expenses = 0.0
    for i, exp in enumerate(expenses, 2):
        amount = _money(exp.get("amount_usd", 0))
        total_expenses += amount
        _data_row(ws_exp, i, [
            inv_label,
            exp.get("date"),
            exp.get("professional") or "",
            exp.get("vendor") or "",
            exp.get("description") or "",
            exp.get("category") or "",
            amount,
            exp.get("payment_source") or "",
            "Yes" if exp.get("receipt_attached") else "No",
            exp.get("notes") or "",
        ], stripe=i % 2 == 0)

    # Expense totals
    exp_totals_row = len(expenses) + 2
    ws_exp.cell(row=exp_totals_row, column=1, value="TOTAL").font = LABEL_FONT
    c = ws_exp.cell(row=exp_totals_row, column=7, value=_money(total_expenses))
    c.font = TOTAL_FONT
    c.number_format = MONEY_FMT
    c.alignment = RIGHT
    c.fill = LIGHT_BLUE_FILL

    # Category subtotals
    cat_totals: dict[str, float] = {}
    for exp in expenses:
        cat = exp.get("category") or "Other"
        cat_totals[cat] = cat_totals.get(cat, 0) + _money(exp.get("amount_usd", 0))
    sub_row = exp_totals_row + 2
    ws_exp.cell(row=sub_row, column=1, value="By Category:").font = LABEL_FONT
    for j, (cat, val) in enumerate(cat_totals.items(), 2):
        ws_exp.cell(row=sub_row, column=j, value=f"{cat}: ${val:,.2f}").font = GREY_FONT

    _set_col_widths(ws_exp, {
        "A": 16, "B": 12, "C": 18, "D": 18,
        "E": 26, "F": 20, "G": 13, "H": 16,
        "I": 16, "J": 22,
    })

    # ─────────────────────────── Sheet: Summary ──────────────────────────────
    ws_sum = wb.create_sheet("Summary")
    ws_sum.sheet_view.showGridLines = False

    ws_sum.merge_cells("A1:C1")
    c = ws_sum["A1"]
    c.value = f"Invoice Summary — {inv_label}"
    c.font = TITLE_FONT

    summary_data = [
        ("Invoice Number", inv_label),
        ("Status", status.upper()),
        ("Client", client.get("name", "")),
        ("Project", project.get("name", "")),
        ("Issue Date", str(invoice.get("issue_date") or "")),
        ("Due Date", str(invoice.get("due_date") or "")),
        (None, None),
        ("Total Fees (gross)", _money(total_fees + total_discounts)),
        ("Total Discounts", _money(total_discounts)),
        ("Subtotal Fees (net)", _money(total_fees)),
    ]
    if cap_amount is not None:
        summary_data.append(("Cap Amount", _money(cap_amount)))
        capped = min(total_fees, _money(cap_amount))
    else:
        capped = total_fees

    summary_data.append(("Total Expenses", _money(total_expenses)))
    summary_data.append((None, None))
    summary_data.append(("TOTAL DUE", _money(capped + total_expenses)))

    for i, (label, val) in enumerate(summary_data, 3):
        if label is None:
            continue
        c_label = ws_sum.cell(row=i, column=1, value=label)
        c_val = ws_sum.cell(row=i, column=2, value=val)
        if label in ("TOTAL DUE",):
            c_label.font = TOTAL_FONT
            c_val.font = TOTAL_FONT
            c_val.number_format = MONEY_FMT
            c_label.fill = LIGHT_BLUE_FILL
            c_val.fill = LIGHT_BLUE_FILL
        elif isinstance(val, float):
            c_label.font = BODY_FONT
            c_val.font = BODY_FONT
            c_val.number_format = MONEY_FMT
            c_val.alignment = RIGHT
        else:
            c_label.font = LABEL_FONT
            c_val.font = BODY_FONT

    _set_col_widths(ws_sum, {"A": 26, "B": 18, "C": 10})
    ws_sum.row_dimensions[1].height = 22

    # ─────────────────────────── Sheet: Clients ──────────────────────────────
    ws_cli = wb.create_sheet("Clients")
    ws_cli.sheet_view.showGridLines = False
    _header_row(ws_cli, 1, ["Client Name", "Email", "Phone", "Project"])
    _data_row(ws_cli, 2, [
        client.get("name", ""),
        client.get("email", ""),
        client.get("phone", ""),
        project.get("name", ""),
    ])
    _set_col_widths(ws_cli, {"A": 24, "B": 26, "C": 16, "D": 24})

    # ─────────────────────────── Sheet: Professionals ────────────────────────
    ws_pro = wb.create_sheet("Professionals")
    ws_pro.sheet_view.showGridLines = False
    _header_row(ws_pro, 1, ["Employee", "Title", "Role", "Hourly Rate", "Total Hours", "Net Total"])

    seen: dict[str, dict] = {}
    for line in lines:
        uid = line.get("user_id") or line.get("employee_name")
        if uid not in seen:
            seen[uid] = {
                "name": line.get("employee_name", ""),
                "title": line.get("title", ""),
                "role": line.get("role", ""),
                "rate": _money(line.get("hourly_rate", 0)),
                "hours": 0.0,
                "total": 0.0,
            }
        seen[uid]["hours"] += _money(line.get("hours", 0))
        hours = _money(line.get("hours", 0))
        rate = _money(line.get("hourly_rate", 0))
        subtotal = hours * rate
        disc_type = line.get("discount_type") or "amount"
        disc_val = _money(line.get("discount_value", 0))
        disc_dollars = (subtotal * disc_val / 100) if disc_type == "percent" else disc_val
        seen[uid]["total"] += max(0.0, subtotal - disc_dollars)

    for i, pro in enumerate(seen.values(), 2):
        _data_row(ws_pro, i, [
            pro["name"], pro["title"], pro["role"],
            pro["rate"], pro["hours"], pro["total"],
        ], stripe=i % 2 == 0)

    _set_col_widths(ws_pro, {"A": 22, "B": 24, "C": 18, "D": 13, "E": 13, "F": 13})

    # ─────────────────────────── Sheet: Config ───────────────────────────────
    ws_cfg = wb.create_sheet("Config")
    ws_cfg.sheet_view.showGridLines = False
    _header_row(ws_cfg, 1, ["Key", "Value"])
    config_rows = [
        ("Company", "Impact Point Co., LLC"),
        ("Export Tool", "H_TRACKER v1.0"),
        ("Invoice", inv_label),
        ("Generated", str(__import__("datetime").date.today())),
    ]
    for i, (k, v) in enumerate(config_rows, 2):
        _data_row(ws_cfg, i, [k, v])
    _set_col_widths(ws_cfg, {"A": 20, "B": 30})

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
