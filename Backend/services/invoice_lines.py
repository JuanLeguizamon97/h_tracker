# services/invoice_lines.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models.invoice_lines import InvoiceLine 
from schemas.invoice_lines import InvoiceLineCreate, InvoiceLineUpdate


def create_invoice_line(db: Session, line_in: InvoiceLineCreate) -> InvoiceLine:
    data = line_in.model_dump()

    #subtotal 
    hours = data["hours"]
    rate = data["hourly_rate"]
    discount = data.get("discount") or 0.0

    subtotal = hours * rate
    total = subtotal - discount

    line = InvoiceLine(
        **data,
        subtotal=subtotal,
        total=total,
    )

    db.add(line)
    db.commit()
    db.refresh(line)
    return line


def get_invoice_lines(
    db: Session,
    id_invoice: Optional[str] = None,
    id_employee: Optional[str] = None,
    id_project: Optional[str] = None,
) -> List[InvoiceLine]:
    query = db.query(InvoiceLine)

    if id_invoice:
        query = query.filter(InvoiceLine.id_invoice == id_invoice)
    if id_employee:
        query = query.filter(InvoiceLine.id_employee == id_employee)
    if id_project:
        query = query.filter(InvoiceLine.id_project == id_project)

    return query.all()


def get_invoice_line(db: Session, id_invoice_line: str) -> Optional[InvoiceLine]:
    return (
        db.query(InvoiceLine)
        .filter(InvoiceLine.id_invoice_line == id_invoice_line)
        .first()
    )


def update_invoice_line(
    db: Session,
    id_invoice_line: str,
    line_in: InvoiceLineUpdate,
) -> Optional[InvoiceLine]:
    line = get_invoice_line(db, id_invoice_line)
    if not line:
        return None

    data = line_in.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(line, field, value)

    # Recalcular subtotal/total si cambió
    if any(k in data for k in ("hourly_rate", "hours", "discount")):
        hours = line.hours
        rate = line.hourly_rate
        discount = line.discount or 0
        line.subtotal = hours * rate
        line.total = line.subtotal - discount

    db.commit()
    db.refresh(line)
    return line


def delete_invoice_line(db: Session, id_invoice_line: str) -> bool:
    line = get_invoice_line(db, id_invoice_line)
    if not line:
        return False

    db.delete(line)
    db.commit()
    return True
