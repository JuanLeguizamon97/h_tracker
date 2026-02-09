# schemas/employees.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal


class EmployeeBase(BaseModel):
    employee_name: str
    employee_email: EmailStr
    home_state: Optional[str] = None
    home_country: Optional[str] = None
    role: str = "employee"
    hourly_rate: Optional[Decimal] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    employee_name: Optional[str] = None
    employee_email: Optional[EmailStr] = None
    home_state: Optional[str] = None
    home_country: Optional[str] = None
    role: Optional[str] = None
    hourly_rate: Optional[Decimal] = None


class EmployeeOut(EmployeeBase):
    id_employee: str

    class Config:
        from_attributes = True
