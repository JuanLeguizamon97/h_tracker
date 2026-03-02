from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from services.invoice import create_invoice, get_invoices, get_invoice, update_invoice, delete_invoice
from schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceOut

invoice_router = APIRouter(prefix="/invoices", tags=["invoices"])


@invoice_router.post("/", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def create_new_invoice(invoice_in: InvoiceCreate, db: Session = Depends(get_db)):
    return create_invoice(db, invoice_in)


@invoice_router.get("/", response_model=List[InvoiceOut])
def list_invoices(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return get_invoices(db, project_id=project_id, status=status)


@invoice_router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice_detail(invoice_id: str, db: Session = Depends(get_db)):
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice


@invoice_router.put("/{invoice_id}", response_model=InvoiceOut)
def update_invoice_detail(invoice_id: str, invoice_in: InvoiceUpdate, db: Session = Depends(get_db)):
    invoice = update_invoice(db, invoice_id, invoice_in)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice


@invoice_router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice_detail(invoice_id: str, db: Session = Depends(get_db)):
    if not delete_invoice(db, invoice_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
