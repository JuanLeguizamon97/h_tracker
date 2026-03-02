# schemas/project_roles.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProjectRoleBase(BaseModel):
    project_id: str
    name: str
    hourly_rate_usd: float


class ProjectRoleCreate(ProjectRoleBase):
    pass


class ProjectRoleUpdate(BaseModel):
    name: Optional[str] = None
    hourly_rate_usd: Optional[float] = None


class ProjectRoleOut(ProjectRoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
