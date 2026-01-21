# routers/invoice.py
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import db_session

from services.invoice import (
    create_invoice,
    get_invoices,               
    get_invoice,                  
    update_invoice,
    delete_invoice,
)
from schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceOut


invoice_router = APIRouter(
    prefix="/invoice",
    tags=["invoice"],
)


@invoice_router.post(
    "/",
    response_model=InvoiceOut,
    status_code=status.HTTP_201_CREATED,
)
def create_new_invoice(
    invoice_in: InvoiceCreate,
    db: Session = Depends(db_session),
):
    try:
        return create_invoice(db, invoice_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@invoice_router.get(
    "/",
    response_model=List[InvoiceOut],
    status_code=status.HTTP_200_OK,
)
def list_invoices(
    id_client: Optional[str] = None,
    status_filter: Optional[str] = None,
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
    db: Session = Depends(db_session),
):
    return get_invoices(           
        db,
        id_client=id_client,
        status=status_filter,
        period_start=period_start,
        period_end=period_end,
    )


@invoice_router.get(
    "/{id_invoice}",
    response_model=InvoiceOut,
    status_code=status.HTTP_200_OK,
)
def get_invoice_detail(
    id_invoice: str,
    db: Session = Depends(db_session),
):
    invoice = get_invoice(db, id_invoice)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@invoice_router.put(
    "/{id_invoice}",
    response_model=InvoiceOut,
    status_code=status.HTTP_200_OK,
)
def update_invoice_detail(
    id_invoice: str,
    invoice_in: InvoiceUpdate,
    db: Session = Depends(db_session),
):
    invoice = update_invoice(db, id_invoice, invoice_in)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@invoice_router.delete(
    "/{id_invoice}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_invoice_detail(
    id_invoice: str,
    db: Session = Depends(db_session),
):
    deleted = delete_invoice(db, id_invoice)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return
