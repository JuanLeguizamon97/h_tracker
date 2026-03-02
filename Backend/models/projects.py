from config.database import Base
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


class Project(Base):

    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    is_internal = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    client = relationship("Client", back_populates="projects")
    roles = relationship("ProjectRole", back_populates="project", cascade="all, delete-orphan")
    assigned_projects = relationship("EmployeeProject", back_populates="project")
    time_entries = relationship("TimeEntry", back_populates="project")
    invoices = relationship("Invoice", back_populates="project")
