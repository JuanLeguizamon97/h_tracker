from typing import List, Optional
from sqlalchemy.orm import Session

from models.employee_projects import EmployeeProject
from models.projects import Project
from models.clients import Client
from schemas.employee_projects import EmployeeProjectCreate


def create_employee_project(db: Session, ep_in: EmployeeProjectCreate) -> EmployeeProject:
    data = ep_in.model_dump(exclude_unset=True)
    db_ep = EmployeeProject(**data)
    db.add(db_ep)
    db.commit()
    db.refresh(db_ep)
    return db_ep


def get_employee_projects(
    db: Session,
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> List[EmployeeProject]:
    query = db.query(EmployeeProject)
    if user_id is not None:
        query = query.filter(EmployeeProject.user_id == user_id)
    if project_id is not None:
        query = query.filter(EmployeeProject.project_id == project_id)
    return query.all()


def get_employee_project(db: Session, ep_id: str) -> Optional[EmployeeProject]:
    return db.query(EmployeeProject).filter(EmployeeProject.id == ep_id).first()


def get_employee_projects_with_details(db: Session, user_id: str) -> List[dict]:
    results = (
        db.query(
            EmployeeProject.id,
            EmployeeProject.user_id,
            EmployeeProject.project_id,
            EmployeeProject.role_id,
            EmployeeProject.assigned_at,
            EmployeeProject.assigned_by,
            Project.name.label("project_name"),
            Project.client_id,
            Client.name.label("client_name"),
        )
        .join(Project, EmployeeProject.project_id == Project.id)
        .join(Client, Project.client_id == Client.id)
        .filter(EmployeeProject.user_id == user_id)
        .all()
    )
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "project_id": r.project_id,
            "role_id": r.role_id,
            "assigned_at": r.assigned_at,
            "assigned_by": r.assigned_by,
            "project_name": r.project_name,
            "client_id": r.client_id,
            "client_name": r.client_name,
        }
        for r in results
    ]


def update_employee_project(db: Session, ep_id: str, updates: dict) -> Optional[EmployeeProject]:
    db_ep = get_employee_project(db, ep_id)
    if not db_ep:
        return None
    for field, value in updates.items():
        setattr(db_ep, field, value)
    db.commit()
    db.refresh(db_ep)
    return db_ep


def delete_employee_project(db: Session, ep_id: str) -> bool:
    db_ep = get_employee_project(db, ep_id)
    if not db_ep:
        return False
    db.delete(db_ep)
    db.commit()
    return True


def bulk_replace_assignments(
    db: Session,
    user_id: str,
    assignments: List[dict],
) -> List[EmployeeProject]:
    db.query(EmployeeProject).filter(EmployeeProject.user_id == user_id).delete()
    new_records = []
    for item in assignments:
        record = EmployeeProject(
            user_id=user_id,
            project_id=item["project_id"],
            role_id=item.get("role_id"),
            assigned_by=item.get("assigned_by"),
        )
        db.add(record)
        new_records.append(record)
    db.commit()
    for r in new_records:
        db.refresh(r)
    return new_records
