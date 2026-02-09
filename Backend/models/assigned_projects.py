from config.database import Base
from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import uuid

class AssignedProject(Base):

    __tablename__ = "assigned_projects"

    id = Column(String, nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey("employees.id_employee"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id_project"), nullable=False)
    client_id = Column(String, ForeignKey("clients.second_id_client"), nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    employee = relationship("Employees", back_populates="assigned_projects")
    project = relationship("Project", back_populates="assigned_projects")
    client = relationship("Client", back_populates="assigned_projects")