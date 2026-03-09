# schemas/invoice.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
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
    cap_amount: Optional[float] = None
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
    cap_amount: Optional[float] = None
    notes: Optional[str] = None
    invoice_number: Optional[str] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime


# ── Edit-data composite response ──

class InvoiceEditClient(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None


class InvoiceEditProject(BaseModel):
    id: str
    name: str
    client_id: str


class InvoiceEditLine(BaseModel):
    id: str
    user_id: str
    employee_name: str
    title: Optional[str] = None
    role: Optional[str] = None
    hours: float
    hourly_rate: float
    discount_type: Optional[str] = None
    discount_value: float = 0
    amount: float


class InvoiceEditExpense(BaseModel):
    id: str
    date: date
    professional: Optional[str] = None
    vendor: Optional[str] = None
    description: Optional[str] = None
    category: str
    amount_usd: float
    payment_source: Optional[str] = None
    receipt_attached: bool = False
    notes: Optional[str] = None


class InvoiceEditDataOut(BaseModel):
    invoice: InvoiceOut
    client: Optional[InvoiceEditClient] = None
    project: Optional[InvoiceEditProject] = None
    lines: List[InvoiceEditLine] = []
    expenses: List[InvoiceEditExpense] = []


# ── PATCH payload ──

class InvoiceLinePatch(BaseModel):
    id: str
    hours: Optional[float] = None
    rate_snapshot: Optional[float] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None


class InvoiceExpensePatch(BaseModel):
    id: Optional[str] = None  # null = create new
    invoice_id: Optional[str] = None
    date: Optional[date] = None
    professional: Optional[str] = None
    vendor: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    amount_usd: Optional[float] = None
    payment_source: Optional[str] = None
    receipt_attached: Optional[bool] = None
    notes: Optional[str] = None


class InvoicePatch(BaseModel):
    status: Optional[str] = None
    cap_amount: Optional[float] = None
    invoice_number: Optional[str] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None
    lines: Optional[List[InvoiceLinePatch]] = None
    expenses: Optional[List[InvoiceExpensePatch]] = None
