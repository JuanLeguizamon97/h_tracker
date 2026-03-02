from config.database import Base
from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


class InvoiceManualLine(Base):

    __tablename__ = "invoice_manual_lines"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False)
    person_name = Column(String, nullable=False)
    hours = Column(Numeric(10, 2), nullable=False)
    rate_usd = Column(Numeric(10, 2), nullable=False)
    description = Column(String, nullable=True)
    line_total = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    invoice = relationship("Invoice", back_populates="manual_lines")
