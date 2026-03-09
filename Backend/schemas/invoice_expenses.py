# schemas/invoice_expenses.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime

EXPENSE_CATEGORIES = ["Airfare", "Hotel", "Parking / Transportation", "Meals", "Other"]


class InvoiceExpenseBase(BaseModel):
    invoice_id: str
    date: date
    professional: Optional[str] = None
    vendor: Optional[str] = None
    description: Optional[str] = None
    category: str
    amount_usd: float
    payment_source: Optional[str] = None
    receipt_attached: bool = False
    notes: Optional[str] = None


class InvoiceExpenseCreate(InvoiceExpenseBase):
    pass


class InvoiceExpenseUpdate(BaseModel):
    date: Optional[date] = None
    professional: Optional[str] = None
    vendor: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    amount_usd: Optional[float] = None
    payment_source: Optional[str] = None
    receipt_attached: Optional[bool] = None
    notes: Optional[str] = None


class InvoiceExpenseOut(InvoiceExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
