from typing import List, Optional
from sqlalchemy.orm import Session
import uuid

from models.employees import Employee
from schemas.employees import EmployeeCreate, EmployeeUpdate


def create_employee(db: Session, employee_in: EmployeeCreate) -> Employee:
    data = employee_in.model_dump(exclude_unset=True)
    db_employee = Employee(**data)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def get_employees(db: Session, active: Optional[bool] = None) -> List[Employee]:
    query = db.query(Employee)
    if active is not None:
        query = query.filter(Employee.is_active == active)
    return query.order_by(Employee.name).all()


def get_employee(db: Session, employee_id: str) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.id == employee_id).first()


def get_employee_by_user_id(db: Session, user_id: str) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.user_id == user_id).first()


def get_employee_by_email(db: Session, email: str) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.email == email).first()


def get_or_create_employee_by_email(db: Session, email: str, name: str) -> Employee:
    employee = get_employee_by_email(db, email)
    if employee:
        return employee
    new_id = str(uuid.uuid4())
    db_employee = Employee(
        id=new_id,
        user_id=new_id,
        name=name,
        email=email,
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(db: Session, employee_id: str, employee_in: EmployeeUpdate) -> Optional[Employee]:
    db_employee = get_employee(db, employee_id)
    if not db_employee:
        return None
    data = employee_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_employee, field, value)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, employee_id: str) -> bool:
    db_employee = get_employee(db, employee_id)
    if not db_employee:
        return False
    db.delete(db_employee)
    db.commit()
    return True
