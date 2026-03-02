from typing import List
from sqlalchemy.orm import Session

from models.invoice_time_entries import InvoiceTimeEntry


def get_invoice_time_entries(db: Session, invoice_id: str) -> List[InvoiceTimeEntry]:
    return db.query(InvoiceTimeEntry).filter(InvoiceTimeEntry.invoice_id == invoice_id).all()


def get_all_linked_entry_ids(db: Session) -> List[str]:
    rows = db.query(InvoiceTimeEntry.time_entry_id).all()
    return [r[0] for r in rows]


def bulk_link_time_entries(db: Session, invoice_id: str, time_entry_ids: List[str]) -> List[InvoiceTimeEntry]:
    created = []
    for entry_id in time_entry_ids:
        db_link = InvoiceTimeEntry(invoice_id=invoice_id, time_entry_id=entry_id)
        db.add(db_link)
        created.append(db_link)
    db.commit()
    for link in created:
        db.refresh(link)
    return created


def delete_invoice_time_entry(db: Session, link_id: str) -> bool:
    db_link = db.query(InvoiceTimeEntry).filter(InvoiceTimeEntry.id == link_id).first()
    if not db_link:
        return False
    db.delete(db_link)
    db.commit()
    return True
