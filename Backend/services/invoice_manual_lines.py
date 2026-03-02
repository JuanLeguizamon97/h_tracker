from typing import List, Optional
from sqlalchemy.orm import Session

from models.invoice_manual_lines import InvoiceManualLine
from schemas.invoice_manual_lines import InvoiceManualLineCreate, InvoiceManualLineUpdate


def create_invoice_manual_line(db: Session, line_in: InvoiceManualLineCreate) -> InvoiceManualLine:
    data = line_in.model_dump(exclude_unset=True)
    db_line = InvoiceManualLine(**data)
    db.add(db_line)
    db.commit()
    db.refresh(db_line)
    return db_line


def get_invoice_manual_lines(db: Session, invoice_id: Optional[str] = None) -> List[InvoiceManualLine]:
    query = db.query(InvoiceManualLine)
    if invoice_id is not None:
        query = query.filter(InvoiceManualLine.invoice_id == invoice_id)
    return query.all()


def get_invoice_manual_line(db: Session, line_id: str) -> Optional[InvoiceManualLine]:
    return db.query(InvoiceManualLine).filter(InvoiceManualLine.id == line_id).first()


def update_invoice_manual_line(db: Session, line_id: str, line_in: InvoiceManualLineUpdate) -> Optional[InvoiceManualLine]:
    db_line = get_invoice_manual_line(db, line_id)
    if not db_line:
        return None
    data = line_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_line, field, value)
    db.commit()
    db.refresh(db_line)
    return db_line


def delete_invoice_manual_line(db: Session, line_id: str) -> bool:
    db_line = get_invoice_manual_line(db, line_id)
    if not db_line:
        return False
    db.delete(db_line)
    db.commit()
    return True
