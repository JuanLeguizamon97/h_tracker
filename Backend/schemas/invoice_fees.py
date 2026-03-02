# schemas/invoice_fees.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class InvoiceFeeBase(BaseModel):
    invoice_id: str
    label: str
    quantity: float
    unit_price_usd: float
    description: Optional[str] = None
    fee_total: float


class InvoiceFeeCreate(InvoiceFeeBase):
    pass


class InvoiceFeeUpdate(BaseModel):
    invoice_id: Optional[str] = None
    label: Optional[str] = None
    quantity: Optional[float] = None
    unit_price_usd: Optional[float] = None
    description: Optional[str] = None
    fee_total: Optional[float] = None


class InvoiceFeeOut(InvoiceFeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
