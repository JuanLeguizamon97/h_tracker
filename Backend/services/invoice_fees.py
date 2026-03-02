from typing import List, Optional
from sqlalchemy.orm import Session

from models.invoice_fees import InvoiceFee
from schemas.invoice_fees import InvoiceFeeCreate, InvoiceFeeUpdate


def create_invoice_fee(db: Session, fee_in: InvoiceFeeCreate) -> InvoiceFee:
    data = fee_in.model_dump(exclude_unset=True)
    db_fee = InvoiceFee(**data)
    db.add(db_fee)
    db.commit()
    db.refresh(db_fee)
    return db_fee


def get_invoice_fees(db: Session, invoice_id: Optional[str] = None) -> List[InvoiceFee]:
    query = db.query(InvoiceFee)
    if invoice_id is not None:
        query = query.filter(InvoiceFee.invoice_id == invoice_id)
    return query.all()


def get_invoice_fee(db: Session, fee_id: str) -> Optional[InvoiceFee]:
    return db.query(InvoiceFee).filter(InvoiceFee.id == fee_id).first()


def update_invoice_fee(db: Session, fee_id: str, fee_in: InvoiceFeeUpdate) -> Optional[InvoiceFee]:
    db_fee = get_invoice_fee(db, fee_id)
    if not db_fee:
        return None
    data = fee_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_fee, field, value)
    db.commit()
    db.refresh(db_fee)
    return db_fee


def delete_invoice_fee(db: Session, fee_id: str) -> bool:
    db_fee = get_invoice_fee(db, fee_id)
    if not db_fee:
        return False
    db.delete(db_fee)
    db.commit()
    return True
