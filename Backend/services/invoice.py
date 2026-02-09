# services/invoice.py
from typing import List, Optional
from datetime import date

from sqlalchemy.orm import Session

from models.invoice import Invoice 
from schemas.invoice import InvoiceCreate, InvoiceUpdate


def create_invoice(db: Session, invoice_in: InvoiceCreate) -> Invoice:
    """
    Crea una factura (solo cabecera)
    """
    data = invoice_in.model_dump()

    # Si no se envía issue_date, usa hoy
    if not data.get("issue_date"):
        from datetime import date as _date
        data["issue_date"] = _date.today()

    invoice = Invoice(**data)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def get_invoices(
    db: Session,
    primary_id_client: Optional[str] = None,
    second_id_client: Optional[str] = None,
    status: Optional[str] = None,
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
) -> List[Invoice]:
    query = db.query(Invoice)

    if primary_id_client and second_id_client:
        query = query.filter(
            Invoice.primary_id_client == primary_id_client,
            Invoice.second_id_client == second_id_client
        )
    if status:
        query = query.filter(Invoice.status == status)
    if period_start:
        query = query.filter(Invoice.period_start >= period_start)
    if period_end:
        query = query.filter(Invoice.period_end <= period_end)

    return query.order_by(Invoice.issue_date.desc()).all()


def get_invoice(db: Session, id_invoice: str) -> Optional[Invoice]:
    return db.query(Invoice).filter(Invoice.id_invoice == id_invoice).first()


def update_invoice(db: Session, id_invoice: str, invoice_in: InvoiceUpdate) -> Optional[Invoice]:
    invoice = get_invoice(db, id_invoice)
    if not invoice:
        return None

    data = invoice_in.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(invoice, field, value)

    db.commit()
    db.refresh(invoice)
    return invoice


def delete_invoice(db: Session, id_invoice: str) -> bool:
    invoice = get_invoice(db, id_invoice)
    if not invoice:
        return False

    db.delete(invoice)
    db.commit()
    return True
