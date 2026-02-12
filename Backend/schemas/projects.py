# schemas/projects.py
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class ProjectBase(BaseModel):
    id_client: str
    project_name: str
    billable_default: bool = True
    hourly_rate: Optional[Decimal] = None
    active: bool = True


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    id_client: Optional[str] = None
    project_name: Optional[str] = None
    billable_default: Optional[bool] = None
    hourly_rate: Optional[Decimal] = None
    active: Optional[bool] = None


class ProjectOut(ProjectBase):
    id_project: str

    class Config:
        from_attributes = True
