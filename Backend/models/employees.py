from config.database import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
import uuid

class Employees(Base):

    __tablename__ = "employees"

    id_employee = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_name = Column(String, nullable=False)
    employee_email = Column(String, nullable=False, unique=True)
    home_state = Column(String, nullable=True)
    home_country = Column(String, nullable=True)

    assigned_projects = relationship("AssignedProject", back_populates="employee")
    time_entries = relationship("TimeEntry", back_populates="employee")

    #Pendiente revisar como podemos obtener los datos de latitud y longitud del API de Google maps para geolocalización