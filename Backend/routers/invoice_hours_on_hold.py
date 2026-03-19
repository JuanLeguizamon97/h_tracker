from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from services.invoice_hours_on_hold import get_on_hold_for_invoice
from schemas.invoice_hours_on_hold import InvoiceHoursOnHoldOut

on_hold_router = APIRouter(prefix="/invoice-hours-on-hold", tags=["invoice-hours-on-hold"])


@on_hold_router.get("/", response_model=List[InvoiceHoursOnHoldOut])
def list_on_hold(invoice_id: str, db: Session = Depends(get_db)):
    return get_on_hold_for_invoice(db, invoice_id)
