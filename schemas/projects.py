# schemas/projects.py
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class ProjectBase(BaseModel):
    id_client: int
    project_name: str
    billable_default: bool = True
    hourly_rate: Optional[Decimal] = None
    active: bool = True


class ProjectCreate(ProjectBase):
    # Aquí no pedimos id_project: lo genera la BD
    pass


class ProjectUpdate(BaseModel):
    id_client: Optional[int] = None
    project_name: Optional[str] = None
    billable_default: Optional[bool] = None
    hourly_rate: Optional[Decimal] = None
    active: Optional[bool] = None


class ProjectOut(ProjectBase):
    id_project: int

    class Config:
        from_attributes = True  # Pydantic v2 (equivale a orm_mode=True en v1)
