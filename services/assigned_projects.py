# services/assigned_projects.py
from sqlalchemy.orm import Session
from models.assigned_projects import AssignedProject
from schemas.assigned_projects import (
    AssignedProjectCreate,
)

def create_assigned_project(db: Session, payload: AssignedProjectCreate) -> AssignedProject:
    """
    Crea una nueva asignación empleado–proyecto–cliente.
    """
    db_assigned = AssignedProject(
        employee_id=payload.employee_id,
        project_id=payload.project_id,
        client_id=payload.client_id,
        active=payload.active,
    )

    db.add(db_assigned)
    db.commit()
    db.refresh(db_assigned)
    return db_assigned


def get_assigned_projects(db: Session) -> list[AssignedProject]:
    """
    Devuelve todas las asignaciones (puedes filtrar por employee_id en otro método).
    """
    return db.query(AssignedProject).all()


def get_assigned_projects_by_employee(db: Session, employee_id: int) -> list[AssignedProject]:
    """
    Devuelve las asignaciones de un empleado específico.
    Ideal para el Project Design del empleado logueado.
    """
    return (
        db.query(AssignedProject)
        .filter(AssignedProject.employee_id == employee_id)
        .all()
    )
