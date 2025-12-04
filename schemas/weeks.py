# schemas/weeks.py
from pydantic import BaseModel
from datetime import date
from typing import Optional


class WeekBase(BaseModel):
    week_end: date
    week_number: int
    year_number: int
    is_split_month: bool = False
    month_a_key: Optional[int] = None
    month_b_key: Optional[int] = None
    qty_days_a: Optional[int] = None
    qty_days_b: Optional[int] = None


class WeekCreate(WeekBase):
    # PK: se debe enviar al crear
    week_start: date


class WeekUpdate(BaseModel):
    week_end: Optional[date] = None
    week_number: Optional[int] = None
    year_number: Optional[int] = None
    is_split_month: Optional[bool] = None
    month_a_key: Optional[int] = None
    month_b_key: Optional[int] = None
    qty_days_a: Optional[int] = None
    qty_days_b: Optional[int] = None


class WeekOut(WeekBase):
    week_start: date

    class Config:
        from_attributes = True
