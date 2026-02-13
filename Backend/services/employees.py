# services/employees.py
from typing import List, Optional
from sqlalchemy.orm import Session

from models.employees import Employees
from schemas.employees import EmployeeCreate, EmployeeUpdate


def create_employee(db: Session, employee_in: EmployeeCreate) -> Employees:
    db_employee = Employees(**employee_in.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def get_employees(db: Session) -> List[Employees]:
    return db.query(Employees).all()


def get_employee(db: Session, id_employee: str) -> Optional[Employees]:
    return (
        db.query(Employees)
        .filter(Employees.id_employee == id_employee)
        .first()
    )


def update_employee(
    db: Session,
    id_employee: str,
    employee_in: EmployeeUpdate,
) -> Optional[Employees]:
    db_employee = get_employee(db, id_employee)
    if not db_employee:
        return None

    data = employee_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_employee, field, value)

    db.commit()
    db.refresh(db_employee)
    return db_employee


def get_employee_by_email(db: Session, email: str) -> Optional[Employees]:
    return (
        db.query(Employees)
        .filter(Employees.employee_email == email)
        .first()
    )


def get_or_create_employee_by_email(
    db: Session,
    email: str,
    name: str,
    role: str = "employee",
) -> Employees:
    employee = get_employee_by_email(db, email)
    if employee:
        return employee

    db_employee = Employees(
        employee_name=name,
        employee_email=email,
        role=role,
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, id_employee: str) -> bool:
    db_employee = get_employee(db, id_employee)
    if not db_employee:
        return False

    db.delete(db_employee)
    db.commit()
    return True
