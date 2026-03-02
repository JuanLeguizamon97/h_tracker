from config.database import Base
from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


class InvoiceFee(Base):

    __tablename__ = "invoice_fees"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False)
    label = Column(String, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price_usd = Column(Numeric(10, 2), nullable=False)
    description = Column(String, nullable=True)
    fee_total = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    invoice = relationship("Invoice", back_populates="fees")
    attachments = relationship("InvoiceFeeAttachment", back_populates="fee", cascade="all, delete-orphan")
