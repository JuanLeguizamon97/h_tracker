from config.database import Base
from sqlalchemy import Column, String, Boolean
import uuid


class ProjectCategory(Base):
    __tablename__ = "project_categories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String, nullable=False)   # "area_category" | "business_unit"
    value = Column(String, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
