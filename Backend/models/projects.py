from config.database import Base
from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import relationship
import uuid


class Project(Base):

    __tablename__ = "projects"

    # Mejor un entero autoincremental que un uuid casteado a int
    id_project = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # OJO: esto asume que en Client tienes clients.id_client como PK (INT)
    id_client = Column(String, ForeignKey("clients.second_id_client"), nullable=False)

    project_name = Column(String, nullable=False)
    billable_default = Column(Boolean, nullable=False, default=True)
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    active = Column(Boolean, nullable=False, default=True)

    # Relaciones
    client = relationship("Client", back_populates="projects")
    assigned_projects = relationship("AssignedProject", back_populates="project")
    time_entries = relationship("TimeEntry", back_populates="project")
