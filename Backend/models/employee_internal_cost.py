from config.database import Base
from sqlalchemy import Column, String, Numeric, Date, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


class EmployeeInternalCost(Base):
    __tablename__ = "employee_internal_costs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    cost_type = Column(String(20), nullable=True, default="hourly")  # hourly | monthly | project
    internal_hourly = Column(Numeric(10, 2), nullable=True)
    monthly_salary = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(10), nullable=True, default="USD")
    reference_billing_rate = Column(Numeric(10, 2), nullable=True)
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    internal_notes = Column(Text, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    employee = relationship("Employee", back_populates="internal_costs")
