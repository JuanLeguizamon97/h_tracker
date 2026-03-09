import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from config.database import get_db
from services.employees import (
    create_employee, get_employees, get_employee, get_or_create_employee_by_email,
    update_employee, delete_employee,
)
from schemas.employees import EmployeeCreate, EmployeeUpdate, EmployeeOut
from models.employees import Employee
from models.user_roles import UserRole

AUTH_MODE = os.getenv("AUTH_MODE", "azure")

employees_router = APIRouter(prefix="/employees", tags=["employees"])

_MOCK_EMPLOYEE = {"email": "dev@impactpoint.dev", "name": "Dev Admin"}


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


@employees_router.post("/", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_new_employee(employee_in: EmployeeCreate, db: Session = Depends(get_db)):
    return create_employee(db, employee_in)


@employees_router.get("/", response_model=List[EmployeeOut])
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


@employees_router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee_detail(employee_id: str, db: Session = Depends(get_db)):
    emp = get_employee(db, employee_id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return emp


@employees_router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee_detail(employee_id: str, employee_in: EmployeeUpdate, db: Session = Depends(get_db)):
    emp = update_employee(db, employee_id, employee_in)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return emp


@employees_router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_detail(employee_id: str, db: Session = Depends(get_db)):
    if not delete_employee(db, employee_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
