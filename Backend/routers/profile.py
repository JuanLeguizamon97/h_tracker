"""
Profile router — authenticated employee manages their own profile.

All routes resolve the current user from the session/token, so no
employee_id is ever accepted from the client.

Allowed self-edit fields (personal info + location + emergency contact).
Corporate/admin fields are intentionally excluded from PATCH.
"""
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import date

from config.database import get_db
from models.employees import Employee
from models.user_roles import UserRole
from schemas.employees import EmployeeOut
from schemas.skills import EmployeeSkillCreate, EmployeeSkillUpdate, EmployeeSkillOut
from services.skills import (
    get_employee_skills,
    create_employee_skill,
    update_employee_skill,
    delete_employee_skill,
)

AUTH_MODE = os.getenv("AUTH_MODE", "azure")
_MOCK_EMPLOYEE = {"email": "dev@impactpoint.dev"}

profile_router = APIRouter(prefix="/profile", tags=["profile"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _current_employee(request: Request, db: Session) -> Employee:
    """Resolve current user from mock header or Azure token."""
    if AUTH_MODE == "mock":
        email = request.headers.get("X-Dev-User-Email", _MOCK_EMPLOYEE["email"])
        emp = db.query(Employee).filter(Employee.email == email).first()
        if not emp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee profile not found")
        return emp
    # Azure: integrate token claims here
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Azure profile lookup not yet wired")


def _is_admin(emp: Employee, db: Session) -> bool:
    role = db.query(UserRole).filter(UserRole.user_id == emp.id).first()
    return role is not None and role.role == "admin"


# ── Profile patch schema (self-editable fields only) ─────────────────────────

class ProfilePatch(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    personal_email: Optional[str] = None
    personal_phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    street_address: Optional[str] = None
    zip_code: Optional[str] = None
    work_mode: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


_SELF_EDITABLE = set(ProfilePatch.model_fields.keys())


# ── Routes ────────────────────────────────────────────────────────────────────

@profile_router.get("/", response_model=EmployeeOut)
def get_profile(request: Request, db: Session = Depends(get_db)):
    """Return the logged-in employee's full record."""
    return _current_employee(request, db)


@profile_router.patch("/", response_model=EmployeeOut)
def patch_profile(request: Request, patch: ProfilePatch, db: Session = Depends(get_db)):
    """Update only the self-editable fields of the logged-in employee."""
    emp = _current_employee(request, db)
    for field, value in patch.model_dump(exclude_unset=True).items():
        if field in _SELF_EDITABLE:
            setattr(emp, field, value)
    db.commit()
    db.refresh(emp)
    return emp


# ── Skills ────────────────────────────────────────────────────────────────────

@profile_router.get("/skills", response_model=List[EmployeeSkillOut])
def list_my_skills(request: Request, db: Session = Depends(get_db)):
    emp = _current_employee(request, db)
    return get_employee_skills(db, emp.id)


@profile_router.post("/skills", response_model=EmployeeSkillOut, status_code=status.HTTP_201_CREATED)
def add_skill(request: Request, skill_in: EmployeeSkillCreate, db: Session = Depends(get_db)):
    emp = _current_employee(request, db)
    return create_employee_skill(db, emp.id, skill_in)


@profile_router.patch("/skills/{skill_id}", response_model=EmployeeSkillOut)
def edit_skill(skill_id: str, request: Request, skill_in: EmployeeSkillUpdate, db: Session = Depends(get_db)):
    from models.employee_skills import EmployeeSkill
    emp = _current_employee(request, db)
    skill = db.query(EmployeeSkill).filter(
        EmployeeSkill.id == skill_id,
        EmployeeSkill.employee_id == emp.id,
    ).first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    updated = update_employee_skill(db, skill_id, skill_in)
    return updated


@profile_router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_skill(skill_id: str, request: Request, db: Session = Depends(get_db)):
    from models.employee_skills import EmployeeSkill
    emp = _current_employee(request, db)
    skill = db.query(EmployeeSkill).filter(
        EmployeeSkill.id == skill_id,
        EmployeeSkill.employee_id == emp.id,
    ).first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    delete_employee_skill(db, skill_id)
