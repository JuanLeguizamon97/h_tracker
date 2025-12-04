from config.database import Base
from sqlalchemy import Column, String, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
import uuid

class AssignedProject(Base):

    __tablename__ = "assigned_projects"

    id = Column(String, nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(Integer, ForeignKey("employees.id_employee"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id_project"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id_client"), nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    employee = relationship("Employee", back_populates="employee")
    project = relationship("Project", back_populates="projects")
    client = relationship("Client", back_populates="clients")