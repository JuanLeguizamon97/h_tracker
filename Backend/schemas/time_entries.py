# schemas/time_entries.py
from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


class TimeEntryBase(BaseModel):
    id_employee: str
    id_project: str
    id_client: str
    week_start: date
    total_hours: Decimal
    billable: bool = True
    location_type: str
    location_value: Optional[str] = None
    is_split_month: bool = False
    month_a_hours: Optional[Decimal] = None
    month_b_hours: Optional[Decimal] = None


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryUpdate(BaseModel):
    id_employee: Optional[str] = None
    id_project: Optional[str] = None
    id_client: Optional[str] = None
    week_start: Optional[date] = None
    total_hours: Optional[Decimal] = None
    billable: Optional[bool] = None
    location_type: Optional[str] = None
    location_value: Optional[str] = None
    is_split_month: Optional[bool] = None
    month_a_hours: Optional[Decimal] = None
    month_b_hours: Optional[Decimal] = None


class TimeEntryOut(TimeEntryBase):
    id_hours: str
    created_at: datetime

    class Config:
        from_attributes = True
