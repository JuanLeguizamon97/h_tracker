# services/projects.py
from typing import List, Optional
from sqlalchemy.orm import Session

from models.projects import Project
from schemas.projects import ProjectCreate, ProjectUpdate


def create_project(db: Session, project_in: ProjectCreate) -> Project:
    """
    Crea un nuevo proyecto.
    """
    db_project = Project(**project_in.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_projects(
    db: Session,
    active: Optional[bool] = None,
    id_client: Optional[int] = None,
) -> List[Project]:
    """
    Lista proyectos, con filtros opcionales por 'active' y 'id_client'.
    """
    query = db.query(Project)
    if active is not None:
        query = query.filter(Project.active == active)
    if id_client is not None:
        query = query.filter(Project.id_client == id_client)
    return query.all()


def get_project(db: Session, id_project: int) -> Optional[Project]:
    """
    Obtiene un proyecto por su ID.
    """
    return (
        db.query(Project)
        .filter(Project.id_project == id_project)
        .first()
    )


def update_project(
    db: Session,
    id_project: int,
    project_in: ProjectUpdate,
) -> Optional[Project]:
    """
    Actualiza parcialmente un proyecto.
    """
    db_project = get_project(db, id_project)
    if not db_project:
        return None

    data = project_in.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(db_project, field, value)

    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, id_project: int) -> bool:
    """
    Elimina un proyecto por ID.
    """
    db_project = get_project(db, id_project)
    if not db_project:
        return False

    db.delete(db_project)
    db.commit()
    return True
