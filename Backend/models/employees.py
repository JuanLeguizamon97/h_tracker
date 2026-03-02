from config.database import Base
from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


class Employee(Base):

    __tablename__ = "employees"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    hourly_rate = Column(Numeric(10, 2), nullable=True, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    supervisor_id = Column(String, ForeignKey("employees.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    assigned_projects = relationship("EmployeeProject", back_populates="employee")
    time_entries = relationship("TimeEntry", back_populates="employee")
    supervisor = relationship("Employee", remote_side=[id])
