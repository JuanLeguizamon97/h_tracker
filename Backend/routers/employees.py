# routers/employees.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_azure_auth.user import User

from config.database import get_db
from utils.auth_microsoft import azure_scheme

from services.employees import (
    create_employee,
    get_employees,
    get_employee as get_employee_service,
    get_or_create_employee_by_email,
    update_employee as update_employee_service,
    delete_employee as delete_employee_service,
)
from schemas.employees import EmployeeCreate, EmployeeUpdate, EmployeeOut


employees_router = APIRouter(
    prefix="/employees",
    tags=["employees"],
)


@employees_router.get(
    "/me",
    response_model=EmployeeOut,
    status_code=status.HTTP_200_OK,
)
async def get_current_employee(
    user: User = Depends(azure_scheme),
    db: Session = Depends(get_db),
):
    email = user.claims.get("preferred_username") or user.claims.get("email", "")
    name = user.claims.get("name", email.split("@")[0])

    employee = get_or_create_employee_by_email(db, email=email, name=name)
    return employee


@employees_router.post(
    "/",
    response_model=EmployeeOut,
    status_code=status.HTTP_201_CREATED,
)
def create_new_employee(
    employee_in: EmployeeCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_employee(db, employee_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@employees_router.get(
    "/",
    response_model=List[EmployeeOut],
    status_code=status.HTTP_200_OK,
)
def list_employees(
    db: Session = Depends(get_db),
):
    return get_employees(db)


@employees_router.get(
    "/{id_employee}",
    response_model=EmployeeOut,
    status_code=status.HTTP_200_OK,
)
def get_employee_detail(
    id_employee: str,
    db: Session = Depends(get_db),
):
    employee = get_employee_service(db, id_employee)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    return employee


@employees_router.put(
    "/{id_employee}",
    response_model=EmployeeOut,
    status_code=status.HTTP_200_OK,
)
def update_employee_detail(
    id_employee: str,
    employee_in: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    employee = update_employee_service(db, id_employee, employee_in)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    return employee


@employees_router.delete(
    "/{id_employee}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_employee_detail(
    id_employee: str,
    db: Session = Depends(get_db),
):
    deleted = delete_employee_service(db, id_employee)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    return
