# services/projects.py
from typing import List, Optional
from sqlalchemy.orm import Session

from models.projects import Project
from schemas.projects import ProjectCreate, ProjectUpdate


def create_project(db: Session, project_in: ProjectCreate) -> Project:
    db_project = Project(**project_in.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_projects(
    db: Session,
    active: Optional[bool] = None,
    id_client: Optional[str] = None,
) -> List[Project]:
    query = db.query(Project)
    if active is not None:
        query = query.filter(Project.active == active)
    if id_client is not None:
        query = query.filter(Project.id_client == id_client)
    return query.all()


def get_project(db: Session, id_project: str) -> Optional[Project]:
    return (
        db.query(Project)
        .filter(Project.id_project == id_project)
        .first()
    )


def update_project(
    db: Session,
    id_project: str,
    project_in: ProjectUpdate,
) -> Optional[Project]:
    db_project = get_project(db, id_project)
    if not db_project:
        return None

    data = project_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_project, field, value)

    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, id_project: str) -> bool:
    db_project = get_project(db, id_project)
    if not db_project:
        return False

    db.delete(db_project)
    db.commit()
    return True
