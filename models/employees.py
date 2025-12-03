from config.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
import uuid

class Employees(Base):

    __tablename__ = "employees"

    id_employee = Column(Integer, primary_key=True, default=lambda: int(uuid.uuid4()))
    employee_name = Column(String, nullable=False)
    employee_email = Column(String, nullable=False, unique=True)
    home_state = Column(String, nullable=True)
    home_country = Column(String, nullable=True)

    assigned_projects = relationship("AssignedProject", back_populates="assigned_projects")

    #Pendiente revisar como podemos obtener los datos de latitud y longitud del API de Google maps para geolocalización