# schemas/employees.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class EmployeeBase(BaseModel):
    name: str
    email: str
    hourly_rate: Optional[float] = None
    is_active: bool = True
    supervisor_id: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    user_id: Optional[str] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    hourly_rate: Optional[float] = None
    is_active: Optional[bool] = None
    supervisor_id: Optional[str] = None
    user_id: Optional[str] = None


class EmployeeOut(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
