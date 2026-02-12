# routers/assigned_projects.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from services.assigned_projects import (
    get_assigned_projects,
    create_assigned_project,
    get_assigned_projects_with_details,
    delete_assigned_project,
    bulk_replace_assignments,
)
from schemas.assigned_projects import (
    AssignedProjectCreate,
    AssignedProjectOut,
    AssignedProjectWithDetails,
    BulkAssignRequest,
)

aprojects_router = APIRouter(
    prefix="/assigned-projects",
    tags=["assigned_projects"],
)


@aprojects_router.get(
    "/",
    response_model=List[AssignedProjectOut],
    status_code=status.HTTP_200_OK,
)
def list_assigned_projects(
    employee_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return get_assigned_projects(db, employee_id=employee_id)


@aprojects_router.get(
    "/employee/{employee_id}",
    response_model=List[AssignedProjectWithDetails],
    status_code=status.HTTP_200_OK,
)
def list_employee_assignments_with_details(
    employee_id: str,
    db: Session = Depends(get_db),
):
    return get_assigned_projects_with_details(db, employee_id)


@aprojects_router.post(
    "/",
    response_model=AssignedProjectOut,
    status_code=status.HTTP_201_CREATED,
)
def assign_project(
    payload: AssignedProjectCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_assigned_project(db, payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@aprojects_router.put(
    "/employee/{employee_id}/bulk",
    response_model=List[AssignedProjectOut],
    status_code=status.HTTP_200_OK,
)
def bulk_assign_projects(
    employee_id: str,
    body: BulkAssignRequest,
    db: Session = Depends(get_db),
):
    try:
        assignments = [item.model_dump() for item in body.assignments]
        return bulk_replace_assignments(db, employee_id, assignments)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@aprojects_router.delete(
    "/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
):
    deleted = delete_assigned_project(db, assignment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )
    return
