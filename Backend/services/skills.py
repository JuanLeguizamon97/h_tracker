from typing import List, Optional
from sqlalchemy.orm import Session
import uuid

from models.skill_catalog import SkillCatalog
from models.employee_skills import EmployeeSkill
from schemas.skills import SkillCatalogCreate, EmployeeSkillCreate, EmployeeSkillUpdate


def list_skill_catalog(db: Session, search: Optional[str] = None) -> List[SkillCatalog]:
    q = db.query(SkillCatalog)
    if search:
        q = q.filter(SkillCatalog.name.ilike(f"%{search}%"))
    return q.order_by(SkillCatalog.category, SkillCatalog.name).all()


def get_or_create_skill_catalog(db: Session, name: str, category: str) -> SkillCatalog:
    skill = db.query(SkillCatalog).filter(SkillCatalog.name.ilike(name)).first()
    if skill:
        return skill
    skill = SkillCatalog(id=str(uuid.uuid4()), name=name, category=category)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


def get_employee_skills(db: Session, employee_id: str) -> List[EmployeeSkill]:
    return (
        db.query(EmployeeSkill)
        .filter(EmployeeSkill.employee_id == employee_id)
        .order_by(EmployeeSkill.proficiency_level.desc(), EmployeeSkill.skill_name)
        .all()
    )


def create_employee_skill(db: Session, employee_id: str, skill_in: EmployeeSkillCreate) -> EmployeeSkill:
    skill_catalog_id = skill_in.skill_catalog_id
    if not skill_catalog_id:
        catalog = get_or_create_skill_catalog(db, skill_in.skill_name, skill_in.category)
        skill_catalog_id = catalog.id

    data = skill_in.model_dump(exclude={'skill_catalog_id'})
    db_skill = EmployeeSkill(
        id=str(uuid.uuid4()),
        employee_id=employee_id,
        skill_catalog_id=skill_catalog_id,
        **data,
    )
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill


def update_employee_skill(db: Session, skill_id: str, skill_in: EmployeeSkillUpdate) -> Optional[EmployeeSkill]:
    db_skill = db.query(EmployeeSkill).filter(EmployeeSkill.id == skill_id).first()
    if not db_skill:
        return None
    for field, value in skill_in.model_dump(exclude_unset=True).items():
        setattr(db_skill, field, value)
    db.commit()
    db.refresh(db_skill)
    return db_skill


def delete_employee_skill(db: Session, skill_id: str) -> bool:
    db_skill = db.query(EmployeeSkill).filter(EmployeeSkill.id == skill_id).first()
    if not db_skill:
        return False
    db.delete(db_skill)
    db.commit()
    return True
