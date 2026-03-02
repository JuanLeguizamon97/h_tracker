# schemas/invoice_manual_lines.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class InvoiceManualLineBase(BaseModel):
    invoice_id: str
    person_name: str
    hours: float
    rate_usd: float
    description: Optional[str] = None
    line_total: float


class InvoiceManualLineCreate(InvoiceManualLineBase):
    pass


class InvoiceManualLineUpdate(BaseModel):
    invoice_id: Optional[str] = None
    person_name: Optional[str] = None
    hours: Optional[float] = None
    rate_usd: Optional[float] = None
    description: Optional[str] = None
    line_total: Optional[float] = None


class InvoiceManualLineOut(InvoiceManualLineBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
