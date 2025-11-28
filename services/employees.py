from sqlalchemy.orm import Session
from models.employees import Employees
from schemas.employees import EmployeeProfile

def create_business(db: Session, employees: EmployeeProfile):
    db_employees = Employees(
        employee_id = employees.employee_id,
        employee_email = employees.employee_email
    )

    db.add(db_employees)
    db.commit()
    db.refresh(db_employees)
    return db_employees

def get_business(db: Session):
    return db.query(Employees).all()