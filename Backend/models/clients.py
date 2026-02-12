from config.database import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
import uuid

class Client(Base):

    __tablename__ = "clients"

    # Claves de negocio (entidad / grupo), ya NO como PK
    primary_id_client = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) #entidad
    second_id_client = Column(String, primary_key=True, default=lambda: str(uuid.uuid4())) #grupo
    client_name = Column(String, nullable=False)
    contact_name = Column(String, nullable=True)
    contact_title = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    billing_address_line1 = Column(String, nullable=True)
    billing_address_line2 = Column(String, nullable=True)
    billing_city = Column(String, nullable=True)
    billing_state = Column(String, nullable=True)
    billing_postal_code = Column(Integer, nullable=True)
    billing_country = Column(String, nullable=True)
    active = Column(Boolean, nullable=False, default=True)

    # Relaciones: deben coincidir con lo que pusimos en Project y TimeEntry
    projects = relationship("Project", back_populates="client")
    assigned_projects = relationship("AssignedProject", back_populates="client")
    time_entries = relationship("TimeEntry", back_populates="client")
    invoices = relationship("Invoice", back_populates="client")
    assigned_projects = relationship("AssignedProject", back_populates="client")
