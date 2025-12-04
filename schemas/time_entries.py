# schemas/time_entries.py
from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


class TimeEntryBase(BaseModel):
    id_employee: int
    id_project: int
    id_client: int
    week_start: date
    total_hours: Decimal
    billable: bool = True
    location_type: str
    location_value: Optional[str] = None
    is_split_month: bool = False
    month_a_hours: Optional[Decimal] = None
    month_b_hours: Optional[Decimal] = None


class TimeEntryCreate(TimeEntryBase):
    # created_at lo dejamos que lo maneje la BD con su default
    pass


class TimeEntryUpdate(BaseModel):
    id_employee: Optional[int] = None
    id_project: Optional[int] = None
    id_client: Optional[int] = None
    week_start: Optional[date] = None
    total_hours: Optional[Decimal] = None
    billable: Optional[bool] = None
    location_type: Optional[str] = None
    location_value: Optional[str] = None
    is_split_month: Optional[bool] = None
    month_a_hours: Optional[Decimal] = None
    month_b_hours: Optional[Decimal] = None


class TimeEntryOut(TimeEntryBase):
    id_hours: int
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2
