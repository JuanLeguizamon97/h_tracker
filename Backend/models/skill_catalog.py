from config.database import Base
from sqlalchemy import Column, String, DateTime
from datetime import datetime, timezone
import uuid


class SkillCatalog(Base):
    __tablename__ = "skill_catalog"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
