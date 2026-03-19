"""Service for invoice_hours_on_hold upserts, deletes, and queries."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.invoice_hours_on_hold import InvoiceHoursOnHold


def get_on_hold_for_invoice(db: Session, invoice_id: str) -> list[InvoiceHoursOnHold]:
    return (
        db.query(InvoiceHoursOnHold)
        .filter(InvoiceHoursOnHold.invoice_id == invoice_id)
        .order_by(InvoiceHoursOnHold.employee_name)
        .all()
    )


def upsert_on_hold_entry(
    db: Session,
    invoice_id: str,
    line_id: str,
    employee_name: str,
    original_hours: float,
    billed_hours: float,
    rate: float,
    reason: str | None = None,
) -> InvoiceHoursOnHold:
    """Create or update an on-hold record for a (invoice, line) pair."""
    on_hold_hours = round(original_hours - billed_hours, 4)
    on_hold_amount = round(on_hold_hours * rate, 4)
    now = datetime.now(timezone.utc)

    existing = (
        db.query(InvoiceHoursOnHold)
        .filter(
            InvoiceHoursOnHold.invoice_id == invoice_id,
            InvoiceHoursOnHold.line_id == line_id,
        )
        .first()
    )

    if existing:
        existing.employee_name = employee_name
        existing.original_hours = original_hours
        existing.billed_hours = billed_hours
        existing.on_hold_hours = on_hold_hours
        existing.rate = rate
        existing.on_hold_amount = on_hold_amount
        existing.reason = reason
        existing.updated_at = now
        return existing
    else:
        record = InvoiceHoursOnHold(
            id=str(uuid.uuid4()),
            invoice_id=invoice_id,
            line_id=line_id,
            employee_name=employee_name,
            original_hours=original_hours,
            billed_hours=billed_hours,
            on_hold_hours=on_hold_hours,
            rate=rate,
            on_hold_amount=on_hold_amount,
            reason=reason,
            created_at=now,
            updated_at=now,
        )
        db.add(record)
        return record


def delete_on_hold_entry(db: Session, invoice_id: str, line_id: str) -> None:
    """Remove on-hold record for a specific line (hours restored to original)."""
    db.query(InvoiceHoursOnHold).filter(
        InvoiceHoursOnHold.invoice_id == invoice_id,
        InvoiceHoursOnHold.line_id == line_id,
    ).delete()
