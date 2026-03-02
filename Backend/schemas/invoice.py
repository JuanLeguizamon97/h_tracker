# schemas/invoice.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime


class InvoiceBase(BaseModel):
    project_id: str
    status: str = "draft"
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    project_id: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    subtotal: Optional[float] = None
    discount: Optional[float] = None
    total: Optional[float] = None
    invoice_number: Optional[str] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    status: str
    subtotal: float
    discount: float
    total: float
    notes: Optional[str] = None
    invoice_number: Optional[str] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
