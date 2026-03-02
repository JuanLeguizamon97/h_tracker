from typing import List, Optional
from sqlalchemy.orm import Session

from models.user_roles import UserRole
from schemas.user_roles import UserRoleCreate


def get_all_user_roles(db: Session) -> List[UserRole]:
    return db.query(UserRole).all()


def get_user_role(db: Session, user_id: str) -> Optional[UserRole]:
    return db.query(UserRole).filter(UserRole.user_id == user_id).first()


def upsert_user_role(db: Session, user_id: str, role: str) -> UserRole:
    existing = get_user_role(db, user_id)
    if existing:
        existing.role = role
        db.commit()
        db.refresh(existing)
        return existing
    db_role = UserRole(user_id=user_id, role=role)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def delete_user_role(db: Session, user_id: str) -> bool:
    existing = get_user_role(db, user_id)
    if not existing:
        return False
    db.delete(existing)
    db.commit()
    return True
