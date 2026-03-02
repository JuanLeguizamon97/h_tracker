from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from models.invoice import Invoice
from schemas.invoice import InvoiceCreate, InvoiceUpdate


def create_invoice(db: Session, invoice_in: InvoiceCreate) -> Invoice:
    data = invoice_in.model_dump(exclude_unset=True)
    invoice = Invoice(**data)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def get_invoices(
    db: Session,
    project_id: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Invoice]:
    query = db.query(Invoice)
    if project_id is not None:
        query = query.filter(Invoice.project_id == project_id)
    if status is not None:
        query = query.filter(Invoice.status == status)
    return query.order_by(Invoice.created_at.desc()).all()


def get_invoice(db: Session, invoice_id: str) -> Optional[Invoice]:
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()


def update_invoice(db: Session, invoice_id: str, invoice_in: InvoiceUpdate) -> Optional[Invoice]:
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return None
    data = invoice_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(invoice, field, value)
    db.commit()
    db.refresh(invoice)
    return invoice


def delete_invoice(db: Session, invoice_id: str) -> bool:
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        return False
    db.delete(invoice)
    db.commit()
    return True
