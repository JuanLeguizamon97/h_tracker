from config.database import Base
from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime, timezone
import uuid


class SchedulerLog(Base):
    __tablename__ = "scheduler_log"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    period_start = Column(String, nullable=False)
    period_end = Column(String, nullable=False)
    invoices_generated = Column(Integer, nullable=False, default=0)
    invoices_skipped = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="success")  # "success" | "error"
    error_message = Column(String, nullable=True)
