from config.database import Base
from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey, DateTime, Date, Integer
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    skill_catalog_id = Column(String, ForeignKey("skill_catalog.id"), nullable=True)
    skill_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    proficiency_level = Column(Integer, nullable=False, default=1)
    years_experience = Column(Numeric(4, 1), nullable=True)
    certified = Column(Boolean, nullable=False, default=False)
    certificate_name = Column(String, nullable=True)
    cert_expiry_date = Column(Date, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    employee = relationship("Employee", back_populates="skills")
    catalog_item = relationship("SkillCatalog")
