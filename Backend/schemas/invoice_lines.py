# schemas/invoice_lines.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class InvoiceLineBase(BaseModel):
    invoice_id: str
    user_id: str
    employee_name: str
    role_name: Optional[str] = None
    hours: float
    rate_snapshot: float
    amount: float
    discount: float = 0
    discount_type: str = 'fixed'  # 'fixed' or 'percentage'


class InvoiceLineCreate(InvoiceLineBase):
    pass


class InvoiceLineUpdate(BaseModel):
    invoice_id: Optional[str] = None
    user_id: Optional[str] = None
    employee_name: Optional[str] = None
    role_name: Optional[str] = None
    hours: Optional[float] = None
    rate_snapshot: Optional[float] = None
    amount: Optional[float] = None
    discount: Optional[float] = None
    discount_type: Optional[str] = None


class InvoiceLineOut(InvoiceLineBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
