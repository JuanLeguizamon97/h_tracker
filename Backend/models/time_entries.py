from config.database import Base
from sqlalchemy import Column, String, Boolean, Date, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


class TimeEntry(Base):

    __tablename__ = "time_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("employees.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    role_id = Column(String, ForeignKey("project_roles.id"), nullable=True)
    date = Column(Date, nullable=False)
    hours = Column(Numeric(6, 2), nullable=False)
    billable = Column(Boolean, nullable=False, default=True)
    notes = Column(String, nullable=True)
    status = Column(String, nullable=False, default="normal")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    employee = relationship("Employee", back_populates="time_entries")
    project = relationship("Project", back_populates="time_entries")
    role = relationship("ProjectRole")
