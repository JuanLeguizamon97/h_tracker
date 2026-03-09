from config.database import Base
from sqlalchemy import Column, String, Date, DateTime, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


class InvoiceExpense(Base):

    __tablename__ = "invoice_expenses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False)
    date = Column(Date, nullable=False)
    professional = Column(String, nullable=True)
    vendor = Column(String, nullable=True)
    description = Column(String, nullable=True)
    category = Column(String, nullable=False)
    amount_usd = Column(Numeric(12, 2), nullable=False, default=0)
    payment_source = Column(String, nullable=True)
    receipt_attached = Column(Boolean, nullable=False, default=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    invoice = relationship("Invoice", back_populates="expenses")
