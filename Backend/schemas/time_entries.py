# schemas/time_entries.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime


class TimeEntryBase(BaseModel):
    user_id: str
    project_id: str
    role_id: Optional[str] = None
    date: date
    hours: float
    billable: bool = True
    notes: Optional[str] = None
    status: str = "normal"


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryUpdate(BaseModel):
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    role_id: Optional[str] = None
    date: Optional[date] = None
    hours: Optional[float] = None
    billable: Optional[bool] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class TimeEntryOut(TimeEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
