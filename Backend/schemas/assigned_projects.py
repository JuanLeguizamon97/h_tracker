from pydantic import BaseModel
from typing import Optional, List


class AssignedProjectBase(BaseModel):
    project_id: str
    client_id: str
    active: bool = True


class AssignedProjectCreate(AssignedProjectBase):
    employee_id: Optional[str] = None


class AssignedProjectOut(AssignedProjectBase):
    id: str
    employee_id: str

    class Config:
        from_attributes = True


class AssignedProjectWithDetails(BaseModel):
    id: str
    employee_id: str
    project_id: str
    client_id: str
    active: bool
    project_name: str
    client_name: str

    class Config:
        from_attributes = True


class BulkAssignItem(BaseModel):
    project_id: str
    client_id: str


class BulkAssignRequest(BaseModel):
    assignments: List[BulkAssignItem]
