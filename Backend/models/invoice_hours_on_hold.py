from config.database import Base
from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


class InvoiceHoursOnHold(Base):
    __tablename__ = "invoice_hours_on_hold"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(String, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    line_id = Column(String, ForeignKey("invoice_lines.id", ondelete="CASCADE"), nullable=False)
    employee_name = Column(String, nullable=False)
    original_hours = Column(Numeric(8, 2), nullable=False)
    billed_hours = Column(Numeric(8, 2), nullable=False)
    on_hold_hours = Column(Numeric(8, 2), nullable=False)
    rate = Column(Numeric(10, 2), nullable=False)
    on_hold_amount = Column(Numeric(12, 2), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False,
                        default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    invoice = relationship("Invoice", back_populates="hours_on_hold")
