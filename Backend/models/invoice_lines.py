from config.database import Base
from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
import uuid

class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id_invoice_line = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    id_invoice = Column(String, ForeignKey("invoices.id_invoice"), nullable=False)
    id_employee = Column(String, ForeignKey("employees.id_employee"), nullable=False)
    id_project = Column(String, ForeignKey("projects.id_project"), nullable=False)
    role_title = Column(String, nullable=True)
    hourly_rate = Column(Numeric(10, 2), nullable=False)
    hours = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)
    discount = Column(Numeric(12, 2), nullable=False, default=0)
    total = Column(Numeric(12, 2), nullable=False)


    invoice = relationship("Invoice", back_populates="lines")
    employee = relationship("Employees")
    project = relationship("Project")
