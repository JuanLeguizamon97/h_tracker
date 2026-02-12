# services/assigned_projects.py
from typing import List, Optional
from sqlalchemy.orm import Session
from models.assigned_projects import AssignedProject
from models.projects import Project
from models.clients import Client
from schemas.assigned_projects import AssignedProjectCreate


def create_assigned_project(db: Session, payload: AssignedProjectCreate) -> AssignedProject:
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


def get_assigned_projects(db: Session, employee_id: Optional[str] = None) -> List[AssignedProject]:
    query = db.query(AssignedProject)
    if employee_id:
        query = query.filter(AssignedProject.employee_id == employee_id)
    return query.all()


def get_assigned_projects_by_employee(db: Session, employee_id: str) -> list[AssignedProject]:
    return (
        db.query(AssignedProject)
        .filter(AssignedProject.employee_id == employee_id)
        .all()
    )


def get_assigned_projects_with_details(db: Session, employee_id: str) -> list[dict]:
    results = (
        db.query(
            AssignedProject.id,
            AssignedProject.employee_id,
            AssignedProject.project_id,
            AssignedProject.client_id,
            AssignedProject.active,
            Project.project_name,
            Client.client_name,
        )
        .join(Project, AssignedProject.project_id == Project.id_project)
        .join(Client, AssignedProject.client_id == Client.second_id_client)
        .filter(AssignedProject.employee_id == employee_id)
        .all()
    )
    return [
        {
            "id": r.id,
            "employee_id": r.employee_id,
            "project_id": r.project_id,
            "client_id": r.client_id,
            "active": r.active,
            "project_name": r.project_name,
            "client_name": r.client_name,
        }
        for r in results
    ]


def delete_assigned_project(db: Session, assignment_id: str) -> bool:
    assignment = db.query(AssignedProject).filter(AssignedProject.id == assignment_id).first()
    if not assignment:
        return False
    db.delete(assignment)
    db.commit()
    return True


def bulk_replace_assignments(
    db: Session,
    employee_id: str,
    assignments: list[dict],
) -> list[AssignedProject]:
    # Delete existing assignments for this employee
    db.query(AssignedProject).filter(
        AssignedProject.employee_id == employee_id
    ).delete()

    # Insert new ones
    new_records = []
    for item in assignments:
        record = AssignedProject(
            employee_id=employee_id,
            project_id=item["project_id"],
            client_id=item["client_id"],
            active=True,
        )
        db.add(record)
        new_records.append(record)

    db.commit()
    for r in new_records:
        db.refresh(r)
    return new_records
