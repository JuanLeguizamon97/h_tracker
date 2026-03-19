from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class InvoiceHoursOnHoldOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    invoice_id: str
    line_id: str
    employee_name: str
    original_hours: float
    billed_hours: float
    on_hold_hours: float
    rate: float
    on_hold_amount: float
    reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
