from config.database import Base
from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import relationship
import uuid

class Project(Base):

    __tablename__ = "projects"

    id_project = Column(Integer, primary_key=True, default=lambda: int(uuid.uuid4()))
    id_client = Column(Integer, ForeignKey("clients.id_client"), nullable=False)
    project_name = Column(String, nullable=False)
    billable_default = Column(Boolean, nullable=False, default=True)
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    active = Column(Boolean, nullable=False, default=True)

    client = relationship("Client", back_populates="clients")
    assigned_employees = relationship("AssignedProject", back_populates="assigned_projects")
    time_entries = relationship("TimeEntry", back_populates="time_entries")