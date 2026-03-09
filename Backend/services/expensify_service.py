"""
Expensify API integration service.

Docs: https://integrations.expensify.com/Integration-Server/doc/
Authentication: partnerUserID + partnerUserSecret via form POST.
Only APPROVED expense reports are imported (never Reimbursed, Open, Submitted, etc.)
"""
import os
import json
import logging
from datetime import date
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

EXPENSIFY_BASE = "https://integrations.expensify.com/Integration-Server/ExpensifyIntegrations"
APPROVED_STATUSES = {"APPROVED"}  # Expensify statuses to accept

PARTNER_USER_ID = os.getenv("EXPENSIFY_PARTNER_USER_ID", "")
PARTNER_USER_SECRET = os.getenv("EXPENSIFY_PARTNER_USER_SECRET", "")
COP_TO_USD_RATE = float(os.getenv("COP_TO_USD_RATE", "4200"))
EUR_TO_USD_RATE = float(os.getenv("EUR_TO_USD_RATE", "1.08"))


def _credentials_configured() -> bool:
    return bool(PARTNER_USER_ID and PARTNER_USER_SECRET)


def convert_to_usd(amount: float, currency: str, rates: dict | None = None) -> tuple[float, str]:
    """
    Convert amount to USD. Returns (usd_amount, note).
    rates dict can override default env-var rates: {"COP": 4200, "EUR": 1.08}
    """
    currency = (currency or "USD").upper()
    if currency == "USD":
        return amount, ""
    r = rates or {}
    if currency == "COP":
        rate = r.get("COP", COP_TO_USD_RATE)
        usd = round(amount / rate, 2)
        return usd, f"Converted from COP {amount:,.0f} @ {rate:,.0f} COP/USD"
    if currency == "EUR":
        rate = r.get("EUR", EUR_TO_USD_RATE)
        usd = round(amount * rate, 2)
        return usd, f"Converted from EUR {amount:,.2f} @ {rate} EUR/USD"
    # Unknown currency — return as-is with note
    return amount, f"Currency {currency} not converted (stored as-is)"


def _build_report_request(
    project_code: Optional[str],
    employee_email: Optional[str],
    date_from: Optional[str],
    date_to: Optional[str],
) -> dict:
    """Build the Expensify requestJobDescription payload for fetching expense reports."""
    filters: dict = {"status": "APPROVED"}
    if employee_email:
        filters["submittedBy"] = employee_email
    if date_from:
        filters["startDate"] = date_from
    if date_to:
        filters["endDate"] = date_to
    if project_code:
        filters["tag"] = project_code  # Expensify uses tags to match projects

    return {
        "type": "get",
        "credentials": {
            "partnerUserID": PARTNER_USER_ID,
            "partnerUserSecret": PARTNER_USER_SECRET,
        },
        "onReceive": {"immediateResponse": ["returnRandomFileName"]},
        "inputSettings": {
            "type": "combinedReportData",
            "reportState": "APPROVED",
            "filters": filters,
        },
        "outputSettings": {"fileExtension": "json"},
    }


async def fetch_expense_reports(
    project_code: Optional[str] = None,
    employee_email: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> list[dict]:
    """
    Fetch APPROVED expense reports from Expensify API.
    Returns a list of expense report dicts (normalized).
    Raises ValueError if credentials not configured.
    """
    if not _credentials_configured():
        raise ValueError(
            "Expensify credentials not configured. "
            "Set EXPENSIFY_PARTNER_USER_ID and EXPENSIFY_PARTNER_USER_SECRET."
        )

    job_desc = _build_report_request(project_code, employee_email, date_from, date_to)

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            EXPENSIFY_BASE,
            data={"requestJobDescription": json.dumps(job_desc)},
        )
        resp.raise_for_status()

    raw = resp.text.strip()

    # Expensify may return a filename (string) or JSON
    if raw.startswith("{") or raw.startswith("["):
        data = json.loads(raw)
    else:
        logger.warning("Expensify returned unexpected format: %s", raw[:200])
        return []

    # Normalize: Expensify combinedReportData returns {"reports": [...]}
    reports_raw = data if isinstance(data, list) else data.get("reports", [])
    return _normalize_reports(reports_raw)


def _normalize_reports(reports_raw: list) -> list[dict]:
    """Convert Expensify raw report objects into our internal format."""
    normalized = []
    for report in reports_raw:
        status = (report.get("status") or report.get("reportStatus") or "").upper()
        if status not in APPROVED_STATUSES:
            continue  # only APPROVED

        report_id = report.get("reportID") or report.get("id") or ""
        report_name = report.get("reportName") or report.get("name") or ""
        submitted_by = report.get("submitterEmail") or report.get("email") or ""
        submitted_date = report.get("created") or report.get("submitted") or ""
        currency = report.get("currency") or "USD"
        total_amount = float(report.get("total") or report.get("totalAmount") or 0)
        usd_total, conversion_note = convert_to_usd(total_amount, currency)

        expenses = []
        for exp in report.get("expenses") or report.get("transactionList") or []:
            exp_currency = exp.get("currency") or currency
            exp_amount = float(exp.get("amount") or exp.get("convertedAmount") or 0)
            # Expensify stores amounts in cents sometimes
            if exp_amount > 10000 and exp_currency == "COP":
                pass  # COP amounts are large by nature
            elif exp_amount > 1000 and exp_currency in ("USD", "EUR"):
                exp_amount = exp_amount / 100  # convert cents to dollars

            exp_usd, exp_note = convert_to_usd(exp_amount, exp_currency)

            expenses.append({
                "expense_id": exp.get("transactionID") or exp.get("id") or "",
                "date": exp.get("created") or exp.get("date") or submitted_date,
                "merchant": exp.get("merchant") or exp.get("vendor") or "",
                "description": exp.get("comment") or exp.get("description") or "",
                "category": exp.get("category") or "Other",
                "original_amount": exp_amount,
                "original_currency": exp_currency,
                "amount_usd": exp_usd,
                "conversion_note": exp_note,
                "receipt_url": exp.get("receiptURL") or "",
                "tag": exp.get("tag") or "",
            })

        normalized.append({
            "report_id": report_id,
            "report_name": report_name,
            "submitted_by": submitted_by,
            "submitted_date": submitted_date,
            "status": status,
            "currency": currency,
            "total_original": total_amount,
            "total_usd": usd_total,
            "conversion_note": conversion_note,
            "expenses": expenses,
        })

    return normalized


def filter_approved_only(reports: list[dict]) -> list[dict]:
    """Filter to only APPROVED reports (belt-and-suspenders — already filtered in fetch)."""
    return [r for r in reports if r.get("status", "").upper() in APPROVED_STATUSES]
