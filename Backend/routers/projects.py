from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from services.projects import create_project, get_projects, get_project, update_project, delete_project
from schemas.projects import ProjectCreate, ProjectUpdate, ProjectOut, ProjectCategoryOut, ProjectAssignmentOut
from models.employees import Employee
from models.employee_projects import EmployeeProject
from models.project_roles import ProjectRole
from models.project_categories import ProjectCategory

projects_router = APIRouter(prefix="/projects", tags=["projects"])


def _with_manager_name(project, db: Session) -> ProjectOut:
    """Build ProjectOut from ORM object, resolving manager_name from Employee table."""
    data = {c.name: getattr(project, c.name) for c in project.__table__.columns}
    if project.manager_id:
        manager = db.query(Employee).filter(Employee.id == project.manager_id).first()
        data["manager_name"] = manager.name if manager else None
    else:
        data["manager_name"] = None
    return ProjectOut.model_validate(data)


# ── Category endpoint (before /{project_id} to avoid route conflict) ────────

@projects_router.get("/categories", response_model=List[ProjectCategoryOut])
def list_project_categories(
    type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(ProjectCategory).filter(ProjectCategory.active == True)
    if type:
        q = q.filter(ProjectCategory.type == type)
    return q.order_by(ProjectCategory.value).all()


# ── CRUD ────────────────────────────────────────────────────────────────────

@projects_router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_new_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    project = create_project(db, project_in)
    return _with_manager_name(project, db)


@projects_router.get("/", response_model=List[ProjectOut])
def list_projects(
    active: Optional[bool] = None,
    client_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    projects = get_projects(db, active=active, client_id=client_id, status=status)
    return [_with_manager_name(p, db) for p in projects]


@projects_router.get("/{project_id}/assignments", response_model=List[ProjectAssignmentOut])
def get_project_assignments(project_id: str, db: Session = Depends(get_db)):
    """Return all employee assignments for a project with employee names resolved."""
    assignments = (
        db.query(EmployeeProject)
        .filter(EmployeeProject.project_id == project_id)
        .all()
    )
    result = []
    for a in assignments:
        employee = db.query(Employee).filter(Employee.id == a.user_id).first()
        role = db.query(ProjectRole).filter(ProjectRole.id == a.role_id).first() if a.role_id else None
        result.append(ProjectAssignmentOut(
            id=a.id,
            user_id=a.user_id,
            employee_name=employee.name if employee else "Unknown",
            project_id=a.project_id,
            role_id=a.role_id,
            role_name=role.name if role else None,
            rate=float(role.hourly_rate_usd) if role and role.hourly_rate_usd else None,
        ))
    return result


@projects_router.get("/{project_id}", response_model=ProjectOut)
def get_project_detail(project_id: str, db: Session = Depends(get_db)):
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return _with_manager_name(project, db)


@projects_router.put("/{project_id}", response_model=ProjectOut)
def update_project_detail(project_id: str, project_in: ProjectUpdate, db: Session = Depends(get_db)):
    project = update_project(db, project_id, project_in)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return _with_manager_name(project, db)


@projects_router.patch("/{project_id}", response_model=ProjectOut)
def patch_project_detail(project_id: str, project_in: ProjectUpdate, db: Session = Depends(get_db)):
    project = update_project(db, project_id, project_in)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return _with_manager_name(project, db)


@projects_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_detail(project_id: str, db: Session = Depends(get_db)):
    if not delete_project(db, project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
