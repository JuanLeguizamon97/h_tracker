# schemas/employee_projects.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class EmployeeProjectBase(BaseModel):
    user_id: str
    project_id: str
    role_id: Optional[str] = None


class EmployeeProjectCreate(EmployeeProjectBase):
    pass


class EmployeeProjectUpdate(BaseModel):
    role_id: Optional[str] = None


class EmployeeProjectOut(EmployeeProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assigned_at: datetime
    assigned_by: Optional[str] = None


class EmployeeProjectWithDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    project_id: str
    role_id: Optional[str] = None
    assigned_at: datetime
    assigned_by: Optional[str] = None
    project_name: str
    client_id: str
    client_name: str


class BulkAssignItem(BaseModel):
    project_id: str
    role_id: Optional[str] = None


class BulkAssignRequest(BaseModel):
    assignments: List[BulkAssignItem]
