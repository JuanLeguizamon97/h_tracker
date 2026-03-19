import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from config.database import get_db
from services.employees import (
    create_employee, get_employees, get_employee, get_or_create_employee_by_email,
    update_employee, delete_employee,
)
from services.skills import (
    get_employee_skills, create_employee_skill, update_employee_skill, delete_employee_skill,
)
from services.employee_internal_cost import (
    get_current_internal_cost, get_internal_cost_history, upsert_internal_cost,
)
from schemas.employees import EmployeeCreate, EmployeeUpdate, EmployeeOut
from schemas.skills import EmployeeSkillCreate, EmployeeSkillUpdate, EmployeeSkillOut
from schemas.employee_internal_cost import EmployeeInternalCostCreate, EmployeeInternalCostOut
from models.employees import Employee
from models.user_roles import UserRole

AUTH_MODE = os.getenv("AUTH_MODE", "azure")

employees_router = APIRouter(prefix="/employees", tags=["employees"])

_MOCK_EMPLOYEE = {"email": "dev@impactpoint.dev", "name": "Dev Admin"}


# ── Admin guard dependency ────────────────────────────────────────────────────

async def require_admin(request: Request, db: Session = Depends(get_db)):
    """Raises 403 if the requesting user is not an admin."""
    if AUTH_MODE == "mock":
        email = request.headers.get("X-Dev-User-Email", _MOCK_EMPLOYEE["email"])
        emp = db.query(Employee).filter(Employee.email == email).first()
        if not emp:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        role_record = db.query(UserRole).filter(UserRole.user_id == emp.id).first()
        if not role_record or role_record.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    # Azure mode: token authentication enforced by Azure AD;
    # per-role enforcement would require additional claim integration.


def _get_actor_id(request: Request, db: Session) -> str | None:
    """Return the employee.id of the requester (used for audit fields)."""
    if AUTH_MODE == "mock":
        email = request.headers.get("X-Dev-User-Email", _MOCK_EMPLOYEE["email"])
        emp = db.query(Employee).filter(Employee.email == email).first()
        return emp.id if emp else None
    return None


# ── /me  (open to all authenticated users) ────────────────────────────────────

@employees_router.get("/me", response_model=EmployeeOut)
async def get_current_employee(request: Request, db: Session = Depends(get_db)):
    if AUTH_MODE == "mock":
        email = request.headers.get("X-Dev-User-Email", _MOCK_EMPLOYEE["email"])
        name = request.headers.get("X-Dev-User-Name", _MOCK_EMPLOYEE["name"])
    else:
        from utils.auth_microsoft import azure_scheme
        user = await azure_scheme(request)
        email = user.claims.get("preferred_username") or user.claims.get("email", "")
        name = user.claims.get("name", email.split("@")[0])
    return get_or_create_employee_by_email(db, email=email, name=name)


# ── Admin-only CRUD ───────────────────────────────────────────────────────────

@employees_router.post(
    "/",
    response_model=EmployeeOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_new_employee(employee_in: EmployeeCreate, db: Session = Depends(get_db)):
    return create_employee(db, employee_in)


@employees_router.get(
    "/",
    response_model=List[EmployeeOut],
    dependencies=[Depends(require_admin)],
)
def list_employees(
    active: Optional[bool] = None,
    user_role: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Employee)
    if active is not None:
        query = query.filter(Employee.is_active == active)
    if user_role:
        query = query.join(UserRole, UserRole.user_id == Employee.id).filter(
            UserRole.role == user_role
        )
    if search:
        query = query.filter(Employee.name.ilike(f"%{search}%"))
    return query.order_by(Employee.name).all()


@employees_router.get(
    "/{employee_id}",
    response_model=EmployeeOut,
    dependencies=[Depends(require_admin)],
)
def get_employee_detail(employee_id: str, db: Session = Depends(get_db)):
    emp = get_employee(db, employee_id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return emp


@employees_router.put(
    "/{employee_id}",
    response_model=EmployeeOut,
    dependencies=[Depends(require_admin)],
)
def update_employee_detail(employee_id: str, employee_in: EmployeeUpdate, db: Session = Depends(get_db)):
    emp = update_employee(db, employee_id, employee_in)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return emp


@employees_router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_employee_detail(employee_id: str, db: Session = Depends(get_db)):
    if not delete_employee(db, employee_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")


# ── Internal Cost (admin-only) ────────────────────────────────────────────────

@employees_router.get(
    "/{employee_id}/internal-cost",
    response_model=EmployeeInternalCostOut,
    dependencies=[Depends(require_admin)],
)
def get_employee_internal_cost(employee_id: str, db: Session = Depends(get_db)):
    record = get_current_internal_cost(db, employee_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cost record found")
    return record


@employees_router.post(
    "/{employee_id}/internal-cost",
    response_model=EmployeeInternalCostOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
)
def upsert_employee_internal_cost(
    employee_id: str,
    cost_in: EmployeeInternalCostCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    emp = get_employee(db, employee_id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    actor_id = _get_actor_id(request, db)
    return upsert_internal_cost(db, employee_id, cost_in, actor_id=actor_id)


@employees_router.get(
    "/{employee_id}/internal-cost/history",
    response_model=List[EmployeeInternalCostOut],
    dependencies=[Depends(require_admin)],
)
def get_employee_internal_cost_history(employee_id: str, db: Session = Depends(get_db)):
    return get_internal_cost_history(db, employee_id)


# ── Skills (admin-only) ───────────────────────────────────────────────────────

@employees_router.get(
    "/{employee_id}/skills",
    response_model=List[EmployeeSkillOut],
    dependencies=[Depends(require_admin)],
)
def list_employee_skills(employee_id: str, db: Session = Depends(get_db)):
    return get_employee_skills(db, employee_id)


@employees_router.post(
    "/{employee_id}/skills",
    response_model=EmployeeSkillOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def add_employee_skill(employee_id: str, skill_in: EmployeeSkillCreate, db: Session = Depends(get_db)):
    emp = get_employee(db, employee_id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return create_employee_skill(db, employee_id, skill_in)


@employees_router.patch(
    "/{employee_id}/skills/{skill_id}",
    response_model=EmployeeSkillOut,
    dependencies=[Depends(require_admin)],
)
def update_skill(employee_id: str, skill_id: str, skill_in: EmployeeSkillUpdate, db: Session = Depends(get_db)):
    skill = update_employee_skill(db, skill_id, skill_in)
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return skill


@employees_router.delete(
    "/{employee_id}/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_skill(employee_id: str, skill_id: str, db: Session = Depends(get_db)):
    if not delete_employee_skill(db, skill_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
