"""
PDF invoice generator using xhtml2pdf (HTML → PDF).

Produces a 2-page PDF:
  Page 1 — Cover letter with logo, client address, body text, and signature.
  Page 2 — Invoice detail: period, fees table, total-due box, ACH instructions.
"""

import base64
import logging
import os
import re
from io import BytesIO
from datetime import date, datetime
from typing import Optional

from xhtml2pdf import pisa

from services.invoice_config import (
    ASSETS_DIR, SIGNATURES_DIR, LOGOS_DIR, LOGO_FILE,
    SIGNATURE_FILES, COMPANY_INFO, BANK_INFO, COMPANY_PROFILES,
)

logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_currency(value: float) -> str:
    """Format as $1,234.56 — negative values as ($1,234.56)."""
    if value < 0:
        return f"(${abs(value):,.2f})"
    return f"${value:,.2f}"


def _format_date_long(d) -> str:
    """Format as 'December 30, 2025' (no leading zero on day)."""
    if not d:
        return ""
    if isinstance(d, str):
        try:
            d = date.fromisoformat(d)
        except ValueError:
            return d
    if isinstance(d, (date, datetime)):
        # %-d removes leading zero on Linux; %#d on Windows — use lstrip
        return d.strftime("%B {day}, %Y").replace("{day}", str(d.day))
    return str(d)


def _sanitize_filename(name: str) -> str:
    """Make a string safe for use in file/path names."""
    return re.sub(r'[^\w\-]', '_', name).strip('_')


def _get_image_base64(filepath: str) -> Optional[str]:
    """Read an image file and return a base64 data-URI string, or None if missing."""
    try:
        if not os.path.isfile(filepath):
            return None
        with open(filepath, "rb") as f:
            data = base64.b64encode(f.read()).decode("ascii")
        ext = os.path.splitext(filepath)[1].lstrip(".").lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}.get(ext, "image/png")
        return f"data:{mime};base64,{data}"
    except Exception as exc:
        logger.warning("Could not read image %s: %s", filepath, exc)
        return None


def _get_signature_base64(signatory_name: str) -> Optional[str]:
    """Look up the signature file for a signatory and return base64 data-URI."""
    filename = SIGNATURE_FILES.get(signatory_name)
    if filename:
        path = os.path.join(SIGNATURES_DIR, filename)
        result = _get_image_base64(path)
        if result:
            return result
    # Fallback
    fallback = os.path.join(SIGNATURES_DIR, "signature_default.png")
    return _get_image_base64(fallback)


# ── HTML Template ─────────────────────────────────────────────────────────────

_INVOICE_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<style>
  @page {{
    size: letter;
    margin: 0.75in;
  }}
  body {{
    font-family: "Times New Roman", Times, serif;
    font-size: 11pt;
    color: #000000;
    margin: 0;
    padding: 0;
  }}
  .page-break {{
    page-break-after: always;
  }}

  /* ── Header ── */
  table.header-table {{
    width: 100%;
    border-collapse: collapse;
  }}
  .company-block {{
    font-size: 10pt;
    line-height: 1.5;
  }}
  .company-name {{
    font-size: 12pt;
    font-weight: bold;
  }}
  .logo-img {{
    max-height: 60px;
    margin-bottom: 4pt;
    display: block;
  }}

  /* ── Invoice title / date ── */
  .invoice-title {{
    text-align: center;
    font-size: 13pt;
    font-weight: bold;
    margin-top: 22pt;
    margin-bottom: 4pt;
  }}
  .invoice-date-center {{
    text-align: center;
    font-size: 11pt;
    margin-bottom: 22pt;
  }}

  /* ── Client block ── */
  .client-block {{
    margin-bottom: 18pt;
    line-height: 1.7;
    font-size: 11pt;
  }}

  /* ── Body text ── */
  .body-text {{
    margin-top: 10pt;
    margin-bottom: 10pt;
    line-height: 1.8;
    font-size: 11pt;
    text-align: justify;
  }}

  /* ── Signature section ── */
  .signature-section {{
    margin-top: 28pt;
    font-size: 11pt;
    line-height: 1.8;
  }}
  .signature-img {{
    max-height: 55px;
    display: block;
    margin: 6pt 0 2pt 0;
  }}

  /* ── Period table ── */
  table.period-table {{
    border-collapse: collapse;
    margin-bottom: 14pt;
    font-size: 10pt;
  }}
  table.period-table th {{
    background-color: #000000;
    color: #ffffff;
    padding: 4pt 12pt;
    border: 1pt solid #000000;
    text-align: left;
    font-weight: bold;
  }}
  table.period-table td {{
    border: 1pt solid #000000;
    padding: 4pt 12pt;
  }}

  /* ── Fees table ── */
  table.fees-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 10pt;
    margin-bottom: 6pt;
  }}
  table.fees-table th {{
    background-color: #000000;
    color: #ffffff;
    border: 1pt solid #000000;
    padding: 4pt 6pt;
    text-align: left;
    font-weight: bold;
  }}
  table.fees-table td {{
    border: 1pt solid #cccccc;
    padding: 4pt 6pt;
  }}
  table.fees-table tr.total-row td {{
    border: 1pt solid #000000;
    background-color: #f0f0f0;
    font-weight: bold;
  }}
  .text-right {{
    text-align: right;
  }}

  /* ── Total-due box ── */
  .total-due-box {{
    background-color: #FFFFCC;
    border: 2pt solid #000000;
    text-align: center;
    font-weight: bold;
    font-size: 13pt;
    padding: 8pt 12pt;
    margin-top: 12pt;
    margin-bottom: 18pt;
  }}

  /* ── ACH section ── */
  .ach-section {{
    margin-top: 16pt;
    font-size: 10pt;
  }}
  .ach-title {{
    font-weight: bold;
    font-size: 11pt;
    margin-bottom: 6pt;
  }}
  table.ach-table {{
    border-collapse: collapse;
    font-size: 10pt;
  }}
  table.ach-table td {{
    padding: 2pt 10pt 2pt 0;
  }}
</style>
</head>
<body>

<!-- ============================================================ -->
<!-- PAGE 1: COVER LETTER                                         -->
<!-- ============================================================ -->
<div class="page-break">

  <!-- Header -->
  <table class="header-table">
    <tr>
      <td>{logo_block}</td>
      <td style="text-align:right; vertical-align:top;">&nbsp;</td>
    </tr>
  </table>

  <!-- Invoice number + date (centered) -->
  <div class="invoice-title">Invoice {invoice_number}</div>
  <div class="invoice-date-center">{invoice_date}</div>

  <!-- Client contact block -->
  <div class="client-block">
    {client_contact}<br/>
    {client_title}<br/>
    {client_company}<br/>
    {client_address}<br/>
    {client_city_state_zip}
  </div>

  <!-- Opening salutation -->
  <p class="body-text">Dear {client_contact},</p>

  <!-- Body -->
  <p class="body-text">
    Attached, please find our invoice for services rendered during the period
    from <b>{period_from}</b> through <b>{period_to}</b>.
  </p>

  <p class="body-text">
    If you have any questions, please do not hesitate to contact us.
  </p>

  <!-- Signature -->
  <div class="signature-section">
    <p>Sincerely,</p>
    {signature_block}
    <p><b>{signatory_name}</b><br/>{signatory_title}</p>
  </div>

</div><!-- end page 1 -->


<!-- ============================================================ -->
<!-- PAGE 2: INVOICE DETAIL                                       -->
<!-- ============================================================ -->
<div>

  <!-- Header (same as page 1) -->
  <table class="header-table">
    <tr>
      <td>{logo_block}</td>
      <td style="text-align:right; vertical-align:top;">&nbsp;</td>
    </tr>
  </table>

  <!-- Invoice number + date -->
  <div class="invoice-title">Invoice {invoice_number}</div>
  <div class="invoice-date-center">{invoice_date}</div>

  <!-- Client block -->
  <div class="client-block">
    {client_contact}<br/>
    {client_title}<br/>
    {client_company}<br/>
    {client_address}<br/>
    {client_city_state_zip}
  </div>

  <!-- Period table -->
  <table class="period-table">
    <tr>
      <th>Period From</th>
      <th>Period To</th>
    </tr>
    <tr>
      <td>{period_from}</td>
      <td>{period_to}</td>
    </tr>
  </table>

  <!-- Fees table -->
  <table class="fees-table">
    <colgroup>
      <col style="width:32%;"/>
      <col style="width:14%;"/>
      <col style="width:10%;"/>
      <col style="width:14%;"/>
      <col style="width:14%;"/>
      <col style="width:16%;"/>
    </colgroup>
    <tr>
      <th>Fees</th>
      <th class="text-right">Hourly Rate</th>
      <th class="text-right">Hours</th>
      <th class="text-right">Subtotal</th>
      <th class="text-right">Discount</th>
      <th class="text-right">Total</th>
    </tr>
    {professional_rows}
    <tr class="total-row">
      <td colspan="3">Total Fees Due</td>
      <td class="text-right">{total_fees}</td>
      <td class="text-right">{total_discount}</td>
      <td class="text-right">{total_due_fees}</td>
    </tr>
  </table>

  <!-- Total due box -->
  <div class="total-due-box">
    TOTAL DUE UPON RECEIPT: {total_due}
  </div>

  <!-- ACH Instructions -->
  <div class="ach-section">
    <div class="ach-title">ACH Instructions:</div>
    <table class="ach-table">
      <tr>
        <td><b>Bank:</b></td>
        <td>{bank_name}</td>
      </tr>
      <tr>
        <td><b>ABA:</b></td>
        <td>{bank_aba}</td>
      </tr>
      <tr>
        <td><b>Account Name:</b></td>
        <td>{bank_account_name}</td>
      </tr>
      <tr>
        <td><b>Account Number:</b></td>
        <td>{bank_account_number}</td>
      </tr>
    </table>
  </div>

</div><!-- end page 2 -->

</body>
</html>
"""


# ── Template data builder ─────────────────────────────────────────────────────

def _build_professional_rows(lines: list) -> tuple[str, float, float, float]:
    """
    Build HTML <tr> rows for the fees table.
    Returns (html_rows, total_subtotal, total_discount_dollars, total_after_discount).
    """
    rows_html = []
    total_subtotal = 0.0
    total_discount = 0.0
    total_net = 0.0

    for line in lines:
        hours = float(line.get("hours", 0) or 0)
        rate = float(line.get("hourly_rate", 0) or line.get("rate_snapshot", 0) or 0)
        subtotal = hours * rate

        disc_type = line.get("discount_type") or "amount"
        disc_val = float(line.get("discount_value", 0) or 0)
        disc_dollars = (subtotal * disc_val / 100) if disc_type == "percent" else disc_val
        net = max(0.0, subtotal - disc_dollars)

        total_subtotal += subtotal
        total_discount += disc_dollars
        total_net += net

        name = line.get("employee_name") or line.get("person_name") or "—"
        role = line.get("title") or line.get("role_name") or ""
        name_cell = f"{name}" + (f"<br/><small style='color:#555'>{role}</small>" if role else "")

        disc_label = _format_currency(disc_dollars) if disc_dollars > 0 else "—"

        rows_html.append(
            f"<tr>"
            f"<td>{name_cell}</td>"
            f"<td class='text-right'>{_format_currency(rate)}</td>"
            f"<td class='text-right'>{hours:.2f}</td>"
            f"<td class='text-right'>{_format_currency(subtotal)}</td>"
            f"<td class='text-right'>{disc_label}</td>"
            f"<td class='text-right'><b>{_format_currency(net)}</b></td>"
            f"</tr>"
        )

    return "".join(rows_html), total_subtotal, total_discount, total_net


def generate_invoice_html(edit_data: dict) -> str:
    """Fill the HTML template with invoice data and return the complete HTML string."""
    invoice = edit_data.get("invoice", {})
    client = edit_data.get("client") or {}
    lines = edit_data.get("lines", [])
    expenses = edit_data.get("expenses", [])

    # ── Invoice fields ────────────────────────────────────────────────────────
    invoice_number = invoice.get("invoice_number") or invoice.get("id", "")[:8]
    invoice_date = _format_date_long(invoice.get("issue_date"))
    period_from = _format_date_long(invoice.get("period_start")) or invoice_date
    period_to = _format_date_long(invoice.get("period_end")) or _format_date_long(invoice.get("due_date")) or invoice_date

    signatory_name = invoice.get("signatory_name") or ""
    signatory_title = invoice.get("signatory_title") or ""

    # ── Client fields ─────────────────────────────────────────────────────────
    client_company = client.get("name") or "—"
    client_contact = client.get("manager_name") or client.get("name") or "—"
    client_title = client.get("job_title") or client.get("manager_title") or ""

    addr1 = client.get("street_address_1") or ""
    addr2 = client.get("street_address_2") or ""
    client_address = ", ".join(part for part in [addr1, addr2] if part) or client.get("address") or ""
    city = client.get("city") or ""
    state = client.get("state") or ""
    zip_ = client.get("zip") or ""
    client_city_state_zip = ", ".join(part for part in [city, state] if part)
    if zip_:
        client_city_state_zip = f"{client_city_state_zip} {zip_}".strip(", ")

    # ── Company profile ───────────────────────────────────────────────────────
    owner_company = invoice.get("owner_company") or "IPC"
    profile = COMPANY_PROFILES.get(owner_company, COMPANY_PROFILES["IPC"])
    bank = profile["bank"]

    # ── Logo ──────────────────────────────────────────────────────────────────
    logo_file = profile.get("logo_file") or LOGO_FILE
    logo_uri = _get_image_base64(logo_file)
    if logo_uri is None and owner_company != "IPC":
        logger.warning("⚠️ %s not found in assets/logos/ — using text fallback", logo_file)
    if logo_uri:
        logo_block = (
            f'<img src="{logo_uri}" class="logo-img" alt="Logo"/>'
            f'<div class="company-block">'
            f'<span class="company-name">{profile["name"]}</span><br/>'
            f'{profile["address"]}<br/>'
            f'{profile["city_state_zip"]}<br/>'
            f'{profile["phone"]}'
            f'</div>'
        )
    else:
        logo_block = (
            f'<div class="company-block">'
            f'<span class="company-name">{profile["name"]}</span><br/>'
            f'{profile["address"]}<br/>'
            f'{profile["city_state_zip"]}<br/>'
            f'{profile["phone"]}'
            f'</div>'
        )

    # ── Signature ─────────────────────────────────────────────────────────────
    sig_uri = _get_signature_base64(signatory_name) if signatory_name else None
    if sig_uri:
        signature_block = f'<img src="{sig_uri}" class="signature-img" alt="Signature"/>'
    else:
        signature_block = ""

    # ── Fee rows ──────────────────────────────────────────────────────────────
    all_lines = list(lines)
    # Also include manual lines if present
    for ml in edit_data.get("manual_lines", []):
        all_lines.append({
            "employee_name": ml.get("person_name") or ml.get("employee_name") or "—",
            "title": ml.get("description") or "",
            "hours": ml.get("hours") or 0,
            "hourly_rate": ml.get("rate_usd") or ml.get("rate_snapshot") or 0,
            "discount_value": 0,
        })

    professional_rows, total_fees, total_discount, total_net = _build_professional_rows(all_lines)
    if not professional_rows:
        professional_rows = "<tr><td colspan='6' style='text-align:center;color:#999'>No line items</td></tr>"

    # Total including expenses
    total_expenses = sum(float(e.get("amount_usd", 0) or 0) for e in expenses)
    cap = invoice.get("cap_amount")
    capped_fees = min(total_net, float(cap)) if cap is not None else total_net
    total_due_val = capped_fees + total_expenses

    return _INVOICE_HTML_TEMPLATE.format(
        # Header / logo
        logo_block=logo_block,
        # Invoice meta
        invoice_number=invoice_number,
        invoice_date=invoice_date or "—",
        period_from=period_from or "—",
        period_to=period_to or "—",
        # Client
        client_company=client_company,
        client_contact=client_contact,
        client_title=client_title,
        client_address=client_address,
        client_city_state_zip=client_city_state_zip,
        # Signature
        signature_block=signature_block,
        signatory_name=signatory_name or "—",
        signatory_title=signatory_title or "—",
        # Fees
        professional_rows=professional_rows,
        total_fees=_format_currency(total_fees + total_discount),
        total_discount=_format_currency(total_discount),
        total_due_fees=_format_currency(total_net),
        total_due=_format_currency(total_due_val),
        # ACH
        bank_name=bank["bank_name"],
        bank_aba=bank["aba"],
        bank_account_name=bank["account_name"],
        bank_account_number=bank["account_number"],
    )


def html_to_pdf(html_content: str) -> bytes:
    """Convert an HTML string to PDF bytes using xhtml2pdf."""
    buf = BytesIO()
    result = pisa.CreatePDF(html_content, dest=buf, encoding="UTF-8")
    if result.err:
        raise RuntimeError(f"xhtml2pdf error code {result.err}")
    return buf.getvalue()


def generate_invoice_pdf(edit_data: dict) -> bytes:
    """
    Entry point called by the router.
    Accepts the edit_data dict from _build_edit_data() and returns PDF bytes.
    """
    html = generate_invoice_html(edit_data)
    return html_to_pdf(html)
