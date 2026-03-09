from typing import List, Optional
from sqlalchemy.orm import Session

from models.projects import Project
from schemas.projects import ProjectCreate, ProjectUpdate


def create_project(db: Session, project_in: ProjectCreate) -> Project:
    data = project_in.model_dump(exclude_unset=True)
    db_project = Project(**data)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_projects(
    db: Session,
    active: Optional[bool] = None,
    client_id: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Project]:
    query = db.query(Project)
    if active is not None:
        query = query.filter(Project.is_active == active)
    if client_id is not None:
        query = query.filter(Project.client_id == client_id)
    if status is not None:
        query = query.filter(Project.status == status)
    return query.order_by(Project.name).all()


def get_project(db: Session, project_id: str) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id).first()


def update_project(db: Session, project_id: str, project_in: ProjectUpdate) -> Optional[Project]:
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    data = project_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_project, field, value)
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: str) -> bool:
    db_project = get_project(db, project_id)
    if not db_project:
        return False
    db.delete(db_project)
    db.commit()
    return True
