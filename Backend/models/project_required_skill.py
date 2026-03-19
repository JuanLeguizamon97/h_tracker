from config.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


class ProjectRequiredSkill(Base):
    __tablename__ = "project_required_skills"
    __table_args__ = (
        UniqueConstraint("project_id", "skill_id", name="uq_project_required_skill"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(String, ForeignKey("skill_catalog.id", ondelete="CASCADE"), nullable=False)
    min_level = Column(Integer, nullable=True, default=2)  # 1=Beginner 2=Intermediate 3=Advanced 4=Expert
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="required_skills")
    skill = relationship("SkillCatalog")
