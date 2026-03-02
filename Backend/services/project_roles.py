from typing import List, Optional
from sqlalchemy.orm import Session

from models.project_roles import ProjectRole
from schemas.project_roles import ProjectRoleCreate, ProjectRoleUpdate


def create_project_role(db: Session, role_in: ProjectRoleCreate) -> ProjectRole:
    data = role_in.model_dump(exclude_unset=True)
    db_role = ProjectRole(**data)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_project_roles(db: Session, project_id: Optional[str] = None) -> List[ProjectRole]:
    query = db.query(ProjectRole)
    if project_id is not None:
        query = query.filter(ProjectRole.project_id == project_id)
    return query.order_by(ProjectRole.name).all()


def get_project_role(db: Session, role_id: str) -> Optional[ProjectRole]:
    return db.query(ProjectRole).filter(ProjectRole.id == role_id).first()


def update_project_role(db: Session, role_id: str, role_in: ProjectRoleUpdate) -> Optional[ProjectRole]:
    db_role = get_project_role(db, role_id)
    if not db_role:
        return None
    data = role_in.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_role, field, value)
    db.commit()
    db.refresh(db_role)
    return db_role


def delete_project_role(db: Session, role_id: str) -> bool:
    db_role = get_project_role(db, role_id)
    if not db_role:
        return False
    db.delete(db_role)
    db.commit()
    return True
