# schemas/projects.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProjectBase(BaseModel):
    client_id: str
    name: str
    description: Optional[str] = None
    is_active: bool = True
    is_internal: bool = False


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    client_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_internal: Optional[bool] = None


class ProjectOut(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
