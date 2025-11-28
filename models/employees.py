from config.database import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

class Employees(Base):

    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True)
    employee_name = Column(String, unique=True, nullable=False)
    employee_email = Column(String, unique=True, nullable=False)
    area= Column(String, nullable=False)
    contractor = Column(Boolean, nullable=False)
    country = Column(Integer, nullable=False)

    #Pendiente revisar como podemos obtener los datos de latitud y longitud del API de Google maps para geolocalización

    orders = relationship("Order", back_populates="user")