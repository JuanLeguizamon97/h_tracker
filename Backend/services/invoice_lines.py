from typing import List, Optional
from sqlalchemy.orm import Session

from models.invoice_lines import InvoiceLine
from schemas.invoice_lines import InvoiceLineCreate, InvoiceLineUpdate


def create_invoice_line(db: Session, line_in: InvoiceLineCreate) -> InvoiceLine:
    data = line_in.model_dump(exclude_unset=True)
    db_line = InvoiceLine(**data)
    db.add(db_line)
    db.commit()
    db.refresh(db_line)
    return db_line


def bulk_create_invoice_lines(db: Session, lines_in: List[InvoiceLineCreate]) -> List[InvoiceLine]:
    created = []
    for line_in in lines_in:
        data = line_in.model_dump(exclude_unset=True)
        db_line = InvoiceLine(**data)
        db.add(db_line)
        created.append(db_line)
    db.commit()
    for line in created:
        db.refresh(line)
    return created


def get_invoice_lines(db: Session, invoice_id: Optional[str] = None) -> List[InvoiceLine]:
    query = db.query(InvoiceLine)
    if invoice_id is not None:
        query = query.filter(InvoiceLine.invoice_id == invoice_id)
    return query.all()


def get_invoice_line(db: Session, line_id: str) -> Optional[InvoiceLine]:
    return db.query(InvoiceLine).filter(InvoiceLine.id == line_id).first()


def update_invoice_line(db: Session, line_id: str, line_in: InvoiceLineUpdate) -> Optional[InvoiceLine]:
    db_line = get_invoice_line(db, line_id)
    if not db_line:
        return None
    data = line_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_line, field, value)
    db.commit()
    db.refresh(db_line)
    return db_line


def delete_invoice_line(db: Session, line_id: str) -> bool:
    db_line = get_invoice_line(db, line_id)
    if not db_line:
        return False
    db.delete(db_line)
    db.commit()
    return True
