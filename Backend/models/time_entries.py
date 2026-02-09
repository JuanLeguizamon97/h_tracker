from config.database import Base
from sqlalchemy import Column, Boolean, Date, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


class TimeEntry(Base):
    __tablename__ = "time_entries"

    id_hours = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    id_employee = Column(String, ForeignKey("employees.id_employee"), nullable=False)
    id_project = Column(String, ForeignKey("projects.id_project"), nullable=False)
    id_client = Column(String, ForeignKey("clients.second_id_client"), nullable=False)
    week_start = Column(Date, ForeignKey("weeks.week_start"), nullable=False)
    total_hours = Column(Numeric(6, 2), nullable=False) 
    billable = Column(Boolean, nullable=False, default=True)
    location_type = Column(String, nullable=False)  
    location_value = Column(String, nullable=True)  
    is_split_month = Column(Boolean, nullable=False, default=False)
    month_a_hours = Column(Numeric(6, 2), nullable=True)
    month_b_hours = Column(Numeric(6, 2), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    employee = relationship("Employees", back_populates="time_entries")
    project = relationship("Project", back_populates="time_entries")
    client = relationship("Client", back_populates="time_entries")
    week = relationship("Week", back_populates="time_entries")