from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class InvoiceBase(BaseModel):
    invoice_number: Optional[str] = None
    primary_id_client: str 
    second_id_client: str  
    period_start: date
    period_end: date
    issue_date: date
    total_hours: Decimal = Decimal("0.00")
    total_fees: Decimal = Decimal("0.00")
    currency: str = "USD"
    status: str = "draft"
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = None
    primary_id_client: Optional[str] = None  
    second_id_client: Optional[str] = None 
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    issue_date: Optional[date] = None
    total_hours: Optional[Decimal] = None
    total_fees: Optional[Decimal] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class InvoiceOut(InvoiceBase):
    id_invoice: str
    created_at: datetime

    class Config:
        from_attributes = True