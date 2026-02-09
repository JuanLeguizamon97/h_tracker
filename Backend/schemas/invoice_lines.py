# schemas/invoice_lines.py
from __future__ import annotations
from typing import Optional

from pydantic import BaseModel


class InvoiceLineBase(BaseModel):
    id_invoice: str
    id_employee: str
    id_project: str

    role_title: Optional[str] = None
    hourly_rate: float
    hours: float
    discount: float = 0.0


class InvoiceLineCreate(InvoiceLineBase):
    """
    Subtotal y total se calculan en el service:
    subtotal = hours * hourly_rate
    total = subtotal - discount
    """
    pass


class InvoiceLineUpdate(BaseModel):
    role_title: Optional[str] = None
    hourly_rate: Optional[float] = None
    hours: Optional[float] = None
    discount: Optional[float] = None


class InvoiceLineOut(BaseModel):
    id_invoice_line: str
    id_invoice: str
    id_employee: str
    id_project: str

    role_title: Optional[str]
    hourly_rate: float
    hours: float
    subtotal: float
    discount: float
    total: float

    class Config:
        from_attributes = True
