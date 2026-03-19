from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime


class EmployeeInternalCostBase(BaseModel):
    cost_type: str = "hourly"
    internal_hourly: Optional[float] = None
    monthly_salary: Optional[float] = None
    currency: str = "USD"
    reference_billing_rate: Optional[float] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    internal_notes: Optional[str] = None


class EmployeeInternalCostCreate(EmployeeInternalCostBase):
    pass


class EmployeeInternalCostOut(EmployeeInternalCostBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    employee_id: str
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
